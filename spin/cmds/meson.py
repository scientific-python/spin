import contextlib
import copy
import json
import os
import re
import shutil
import sys
from enum import Enum
from pathlib import Path

import click

from .util import get_commands, get_config
from .util import run as _run


class GcovReportFormat(str, Enum):
    html = "html"
    xml = "xml"
    text = "text"
    sonarqube = "sonarqube"


# Allow specification of meson binary in configuration
# This is necessary for packages like NumPy that vendor meson
def _meson_cli():
    cfg = get_config()
    meson_cli = os.path.expanduser(cfg.get("tool.spin.meson.cli", "meson"))

    # Handle Python runner, mainly for Windows
    if meson_cli.endswith(".py"):
        return [sys.executable, meson_cli]
    else:
        return [meson_cli]


def _editable_install_path(distname):
    import importlib_metadata

    try:
        dist = importlib_metadata.Distribution.from_name(distname)
    except importlib_metadata.PackageNotFoundError:
        return None

    if dist.origin is None:
        return None

    if hasattr(dist.origin, "dir_info") and getattr(
        dist.origin.dir_info, "editable", False
    ):
        if sys.platform == "win32":
            return dist.origin.url.removeprefix("file:///")
        else:
            return dist.origin.url.removeprefix("file://")
    else:
        return None


def _is_editable_install(distname):
    return _editable_install_path(distname) is not None


def _is_editable_install_of_same_source(distname):
    editable_path = _editable_install_path(distname)
    return editable_path and os.path.samefile(_editable_install_path(distname), ".")


def _set_pythonpath(build_dir, quiet=False):
    """Set first entry of PYTHONPATH to site packages directory.

    For editable installs, leave the PYTHONPATH alone.

    Returns
    -------
    site_packages
    """
    cfg = get_config()
    distname = cfg.get("project.name", None)
    if distname:
        if _is_editable_install(distname):
            if _is_editable_install_of_same_source(distname):
                if not (quiet):
                    click.secho(
                        "Editable install of same source directory detected; not setting PYTHONPATH",
                        fg="bright_red",
                    )
                return ""
            else:
                # Ignoring the quiet flag, because picking up the wrong package is problematic
                click.secho(
                    f"Warning! Editable install of `{distname}`, from a different source location, detected.",
                    fg="bright_red",
                )
                click.secho("Spin commands will pick up that version.", fg="bright_red")
                click.secho(
                    f"Try removing the other installation by switching to its source and running `pip uninstall {distname}`.",
                    fg="bright_red",
                )

    site_packages = _get_site_packages(build_dir)
    env = os.environ

    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{site_packages}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = site_packages

    if not quiet:
        click.secho(
            f'$ export PYTHONPATH="{env["PYTHONPATH"]}"', bold=True, fg="bright_blue"
        )

    return site_packages


def _get_install_dir(build_dir):
    return f"{build_dir}-install"


def _get_site_packages(build_dir):
    install_dir = _get_install_dir(build_dir)
    try:
        cfg = get_config()
        distname = cfg.get("project.name", None)
        if _is_editable_install_of_same_source(distname):
            return ""
    except RuntimeError:
        # Probably not running in click
        pass

    candidate_paths = []
    for root, dirs, _files in os.walk(install_dir):
        for subdir in dirs:
            if subdir == "site-packages" or subdir == "dist-packages":
                candidate_paths.append(os.path.abspath(os.path.join(root, subdir)))

    X, Y = sys.version_info.major, sys.version_info.minor

    site_packages = None
    if any(f"python{X}." in p for p in candidate_paths):
        # We have a system that uses `python3.X/site-packages` or `python3.X/dist-packages`
        site_packages = [p for p in candidate_paths if f"python{X}.{Y}" in p]
        if len(site_packages) == 0:
            raise FileNotFoundError(
                f"No site-packages found in {install_dir} for Python {X}.{Y}"
            )
        else:
            site_packages = site_packages[0]
    else:
        # A naming scheme that does not encode the Python major/minor version is used, so return
        # whatever site-packages path was found
        if len(candidate_paths) > 1:
            raise FileNotFoundError(
                f"Multiple `site-packages` found in `{install_dir}`, but cannot use Python version to disambiguate"
            )
        elif len(candidate_paths) == 1:
            site_packages = candidate_paths[0]

    if site_packages is None:
        raise FileNotFoundError(
            f"No `site-packages` or `dist-packages` found under `{install_dir}`"
        )

    return site_packages


def _meson_version():
    try:
        p = _run(_meson_cli() + ["--version"], output=False, echo=False)
        return p.stdout.decode("ascii").strip()
    except:
        pass


def _meson_version_configured(build_dir):
    try:
        meson_info_fn = os.path.join(build_dir, "meson-info", "meson-info.json")
        with open(meson_info_fn) as f:
            meson_info = json.load(f)
        return meson_info["meson_version"]["full"]
    except:
        pass


def _meson_coverage_configured() -> bool:
    try:
        build_options_fn = os.path.join(
            "build", "meson-info", "intro-buildoptions.json"
        )
        with open(build_options_fn) as f:
            build_options = json.load(f)
        for b in build_options:
            if (b["name"] == "b_coverage") and (b["value"] is True):
                return True
    except:
        pass

    return False


def _check_coverage_tool_installation(coverage_type: GcovReportFormat, build_dir):
    requirements = {  # https://github.com/mesonbuild/meson/blob/6e381714c7cb15877e2bcaa304b93c212252ada3/docs/markdown/Unit-tests.md?plain=1#L49-L62
        GcovReportFormat.html: ["Gcovr/GenHTML", "lcov"],
        GcovReportFormat.xml: ["Gcovr (version 3.3 or higher)"],
        GcovReportFormat.text: ["Gcovr (version 3.3 or higher)"],
        GcovReportFormat.sonarqube: ["Gcovr (version 4.2 or higher)"],
    }

    # First check the presence of a valid build
    if not (os.path.exists(build_dir)):
        raise click.ClickException(
            f"`{build_dir}` folder not found, cannot generate coverage reports. "
            "Generate coverage artefacts by running `spin test --gcov`"
        )

    debug_files = Path(build_dir).rglob("*.gcno")
    if len(list(debug_files)) == 0:
        raise click.ClickException(
            "Debug build not found, cannot generate coverage reports.\n\n"
            "Please rebuild using `spin build --clean --gcov` first."
        )

    # Verify the tools are installed prior to the build
    p = _run(["ninja", "-C", build_dir, "-t", "targets", "all"], output=False)
    if f"coverage-{coverage_type}" not in p.stdout.decode("ascii"):
        raise click.ClickException(
            f"coverage-{coverage_type} is not supported... "
            f"Ensure the following are installed: {', '.join(requirements[coverage_type])} "
            "and rerun `spin test --gcov`"
        )


if sys.platform.startswith("win"):
    DEFAULT_PREFIX = "C:/"
else:
    DEFAULT_PREFIX = "/usr"

build_dir_option = click.option(
    "-C",
    "--build-dir",
    default="build",
    show_envvar=True,
    envvar="SPIN_BUILD_DIR",
    help="Meson build directory; package is installed into './{build-dir}-install'.",
)


@click.command()
@click.option("-j", "--jobs", help="Number of parallel tasks to launch", type=int)
@click.option("--clean", is_flag=True, help="Clean build directory before build")
@click.option(
    "-v", "--verbose", is_flag=True, help="Print detailed build and installation output"
)
@click.option(
    "--gcov",
    is_flag=True,
    help="Enable C code coverage using `gcov`. Use `spin test --gcov` to generate reports.",
)
@click.option(
    "--prefix",
    help="The build prefix, passed directly to meson.",
    type=str,
    default=DEFAULT_PREFIX,
)
@click.argument("meson_args", nargs=-1)
@build_dir_option
def build(
    *,
    meson_args,
    jobs=None,
    clean=False,
    verbose=False,
    gcov=False,
    quiet=False,
    build_dir=None,
    prefix=None,
):
    """🔧 Build package with Meson/ninja

    The package is installed to `build-install` (unless a different
    build directory is specified with `-C`).

    MESON_ARGS are passed through e.g.:

      spin build -- -Dpkg_config_path=/lib64/pkgconfig

    By default meson-python does release builds. To be able to use a debugger,
    tell meson to build in debug mode:

      spin build -- -Dbuildtype=debug

    or set CFLAGS appropriately:

      CFLAGS="-O0 -g" spin build

    Build into a different build/build-install directory via the
    `-C/--build-dir` flag:

      spin build -C build-for-feature-x

    This feature is useful in combination with a shell alias, e.g.:

      $ alias spin-clang="SPIN_BUILD_DIR=build-clang CC=clang spin"

    Which can then be used to build (`spin-clang build`), to test (`spin-clang test ...`), etc.

    """
    abs_build_dir = os.path.abspath(build_dir)
    install_dir = _get_install_dir(build_dir)
    abs_install_dir = os.path.abspath(install_dir)

    cfg = get_config()
    distname = cfg.get("project.name", None)
    if distname and _is_editable_install_of_same_source(distname):
        if not quiet:
            click.secho(
                "Editable install of same source detected; skipping build",
                fg="bright_red",
            )
        return

    meson_args = list(meson_args)

    if gcov:
        meson_args = meson_args + ["-Db_coverage=true"]

    setup_cmd = _meson_cli() + ["setup", build_dir, f"--prefix={prefix}"] + meson_args

    if clean:
        print(f"Removing `{build_dir}`")
        if os.path.isdir(build_dir):
            shutil.rmtree(build_dir)
        print(f"Removing `{install_dir}`")
        if os.path.isdir(install_dir):
            shutil.rmtree(install_dir)

    if not (os.path.exists(build_dir) and _meson_version_configured(build_dir)):
        p = _run(setup_cmd, sys_exit=False, output=not quiet)
        if p.returncode != 0:
            raise RuntimeError(
                "Meson configuration failed; please try `spin build` again with the `--clean` flag."
            )
    else:
        # Build dir has been configured; check if it was configured by
        # current version of Meson

        if (_meson_version() != _meson_version_configured(build_dir)) or (
            gcov and not _meson_coverage_configured()
        ):
            _run(setup_cmd + ["--reconfigure"], output=not quiet)

        # Any other conditions that warrant a reconfigure?

    compile_flags = ["-v"] if verbose else []
    if jobs:
        compile_flags += ["-j", str(jobs)]

    p = _run(
        _meson_cli() + ["compile"] + compile_flags + ["-C", build_dir],
        sys_exit=True,
        output=not quiet,
    )
    p = _run(
        _meson_cli()
        + [
            "install",
            "--only-changed",
            "-C",
            build_dir,
            "--destdir",
            install_dir
            if os.path.isabs(install_dir)
            else os.path.relpath(abs_install_dir, abs_build_dir),
        ],
        output=(not quiet) and verbose,
    )


def _get_configured_command(command_name):
    command_groups = get_commands()
    commands = [cmd for section in command_groups for cmd in command_groups[section]]
    return next((cmd for cmd in commands if cmd.name == command_name), None)


@click.command()
@click.argument("pytest_args", nargs=-1)
@click.option(
    "-j",
    "n_jobs",
    metavar="N_JOBS",
    default="1",
    help=(
        "Number of parallel jobs for testing. Can be set to `auto` to use all cores."
    ),
)
@click.option(
    "--tests",
    "-t",
    metavar="TESTS",
    help=(
        """
Which tests to run. Can be a module, function, class, or method:

 \b
 numpy.random
 numpy.random.tests.test_generator_mt19937
 numpy.random.tests.test_generator_mt19937::TestMultivariateHypergeometric
 numpy.random.tests.test_generator_mt19937::TestMultivariateHypergeometric::test_edge_cases
 \b
"""
    ),
)
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option(
    "-c",
    "--coverage",
    is_flag=True,
    help="Generate a Python coverage report of executed tests. An HTML copy of the report is written to `build/coverage`.",
)
@click.option(
    "--gcov",
    is_flag=True,
    help="Generate a C coverage report in `build/meson-logs/coveragereport`.",
)
@click.option(
    "--gcov-format",
    type=click.Choice([e.name for e in GcovReportFormat]),
    default="html",
    help=f"Format of the gcov report. Can be one of {', '.join(e.value for e in GcovReportFormat)}.",
)
@build_dir_option
@click.pass_context
def test(
    ctx,
    *,
    pytest_args,
    n_jobs,
    tests,
    verbose,
    coverage=False,
    gcov=None,
    gcov_format=None,
    build_dir=None,
):
    """🔧 Run tests

    PYTEST_ARGS are passed through directly to pytest, e.g.:

      spin test -- --pdb

    To run tests on a directory or file:

     \b
     spin test numpy/linalg
     spin test numpy/linalg/tests/test_linalg.py

    To run test modules, functions, classes, or methods:

      spin -t numpy.random

    To report the durations of the N slowest tests:

      spin test -- --durations=N

    To run tests that match a given pattern:

     \b
     spin test -- -k "geometric"
     spin test -- -k "geometric and not rgeometric"

    To run tests with a given marker:

      \b
      spin test -- -m slow
      spin test -- -m "not slow"

    If python-xdist is installed, you can run tests in parallel:

      spin test -j auto

    For more, see `pytest --help`.
    """  # noqa: E501
    cfg = get_config()
    distname = cfg.get("project.name", None)
    pytest_args = pytest_args or ()

    # User specified tests without -t flag
    # Rewrite arguments as though they specified using -t and proceed
    if (len(pytest_args) == 1) and (not tests):
        tests = pytest_args[0]
        pytest_args = ()

    package = cfg.get("tool.spin.package", None)
    if package is None:
        click.secho(
            "Please specify `package = packagename` under `tool.spin` section of `pyproject.toml`",
            fg="bright_red",
        )
        raise SystemExit(1)

    # User did not specify what to test, so we test
    # the full package
    if not (pytest_args or tests):
        pytest_args = ("--pyargs", package)
    elif tests:
        if (os.path.sep in tests) or ("/" in tests):
            # Tests specified as file path
            pytest_args = pytest_args + (tests,)
        else:
            # Otherwise tests given as modules
            pytest_args = pytest_args + ("--pyargs", tests)

    is_editable_install = distname and _is_editable_install_of_same_source(distname)
    if gcov and is_editable_install:
        click.secho(
            "Error: cannot generate coverage report for editable installs",
            fg="bright_red",
        )
        raise SystemExit(1)

    build_cmd = _get_configured_command("build")
    if build_cmd:
        click.secho(
            "Invoking `build` prior to running tests:", bold=True, fg="bright_green"
        )
        if gcov is not None:
            ctx.invoke(build_cmd, build_dir=build_dir, gcov=bool(gcov))
        else:
            ctx.invoke(build_cmd, build_dir=build_dir)

    site_path = _set_pythonpath(build_dir)

    # Sanity check that library built properly
    #
    # We do this because `pytest` swallows exception messages originating from `conftest.py`.
    # This can sometimes suppress useful information raised by the package on init.
    if sys.version_info[:2] >= (3, 11):
        p = _run([sys.executable, "-P", "-c", f"import {package}"], sys_exit=False)
    else:
        p = _run(
            [sys.executable, "-c", f"import sys; del sys.path[0]; import {package}"],
            sys_exit=False,
        )
    if p.returncode != 0:
        print(f"As a sanity check, we tried to import {package}.")
        print("Stopping. Please investigate the build error.")
        sys.exit(1)

    if (n_jobs != "1") and ("-n" not in pytest_args):
        pytest_args = ("-n", str(n_jobs)) + pytest_args

    if not any("--import-mode" in arg for arg in pytest_args):
        pytest_args = ("--import-mode=importlib",) + pytest_args

    if verbose:
        pytest_args = ("-v",) + pytest_args

    if coverage:
        coverage_dir = os.path.join(os.getcwd(), "build/coverage/")
        if os.path.isdir(coverage_dir):
            print(f"Removing `{coverage_dir}`")
            shutil.rmtree(coverage_dir)
        os.makedirs(coverage_dir)
        pytest_args = [
            *pytest_args,
            "--cov-report=term",
            f"--cov-report=html:{coverage_dir}",
            f"--cov={package}",
        ]

    if sys.version_info[:2] >= (3, 11):
        cmd = [sys.executable, "-P", "-m", "pytest"]
    else:
        cmd = ["pytest"]

    install_dir = _get_install_dir(build_dir)
    if not os.path.exists(install_dir):
        os.mkdir(install_dir)

    cwd = os.getcwd()
    pytest_p = _run(cmd + list(pytest_args), cwd=site_path)
    os.chdir(cwd)

    if gcov:
        # Verify the tools are present
        click.secho(
            "Verifying gcov dependencies...",
            bold=True,
            fg="bright_yellow",
        )
        _check_coverage_tool_installation(gcov_format, build_dir)

        # Generate report
        click.secho(
            f"Generating {gcov_format} coverage report...",
            bold=True,
            fg="bright_yellow",
        )
        p = _run(
            [
                "ninja",
                "-C",
                build_dir,
                f"coverage-{gcov_format.lower()}",
            ],
            output=False,
        )
        coverage_folder = click.style(
            re.search(r"file://(.*)", p.stdout.decode("utf-8")).group(1),
            bold=True,
            fg="bright_yellow",
        )
        click.secho(
            f"Coverage report generated successfully and written to {coverage_folder}",
            bold=True,
            fg="bright_green",
        )

    raise SystemExit(pytest_p.returncode)


@click.command()
@click.option("--code", "-c", help="Python program passed in as a string")
@click.argument("gdb_args", nargs=-1)
@build_dir_option
@click.pass_context
def gdb(ctx, *, code, gdb_args, build_dir):
    """👾 Execute code through GDB

      spin gdb -c 'import numpy as np; print(np.__version__)'

    Or pass arguments to gdb:

      spin gdb -c 'import numpy as np; print(np.__version__)' -- --fullname

    Or run another program, they way you normally would with gdb:

     \b
     spin gdb ls
     spin gdb -- --args ls -al

    You can also run Python programs:

     \b
     spin gdb my_tests.py
     spin gdb -- my_tests.py --mytest-flag
    """
    build_cmd = _get_configured_command("build")
    if build_cmd:
        click.secho(
            "Invoking `build` prior to invoking gdb:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd, build_dir=build_dir)

    _set_pythonpath(build_dir)
    gdb_args = list(gdb_args)

    if gdb_args and gdb_args[0].endswith(".py"):
        gdb_args = ["--args", sys.executable] + gdb_args

    if sys.version_info[:2] >= (3, 11):
        PYTHON_FLAGS = ["-P"]
        code_prefix = ""
    else:
        PYTHON_FLAGS = []
        code_prefix = "import sys; sys.path.pop(0); "

    if code:
        PYTHON_ARGS = ["-c", code_prefix + code]
        gdb_args += ["--args", sys.executable] + PYTHON_FLAGS + PYTHON_ARGS

    gdb_cmd = ["gdb", "-ex", "set detach-on-fork on"] + gdb_args
    _run(gdb_cmd, replace=True)


@click.command()
@click.argument("ipython_args", nargs=-1)
@build_dir_option
@click.pass_context
def ipython(ctx, *, ipython_args, build_dir):
    """💻 Launch IPython shell with PYTHONPATH set

    IPYTHON_ARGS are passed through directly to IPython, e.g.:

    spin ipython -- -i myscript.py
    """
    build_cmd = _get_configured_command("build")
    if build_cmd:
        click.secho(
            "Invoking `build` prior to invoking ipython:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd, build_dir=build_dir)

    p = _set_pythonpath(build_dir)
    if p:
        print(f'💻 Launching IPython with PYTHONPATH="{p}"')
    _run(["ipython", "--ignore-cwd"] + list(ipython_args), replace=True)


@click.command()
@click.argument("shell_args", nargs=-1)
@build_dir_option
@click.pass_context
def shell(ctx, shell_args=[], build_dir=None):
    """💻 Launch shell with PYTHONPATH set

    SHELL_ARGS are passed through directly to the shell, e.g.:

    spin shell -- -c 'echo $PYTHONPATH'

    Ensure that your shell init file (e.g., ~/.zshrc) does not override
    the PYTHONPATH.
    """
    build_cmd = _get_configured_command("build")
    if build_cmd:
        click.secho(
            "Invoking `build` prior to invoking shell:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd, build_dir=build_dir)

    p = _set_pythonpath(build_dir)
    if p:
        print(f'💻 Launching shell with PYTHONPATH="{p}"')

    shell = os.environ.get("SHELL", "sh")
    cmd = [shell] + list(shell_args)
    print("⚠  Change directory to avoid importing source instead of built package")
    print("⚠  Ensure that your ~/.shellrc does not unset PYTHONPATH")
    _run(cmd, replace=True)


@click.command()
@click.argument("python_args", nargs=-1)
@build_dir_option
@click.pass_context
def python(ctx, *, python_args, build_dir):
    """🐍 Launch Python shell with PYTHONPATH set

    PYTHON_ARGS are passed through directly to Python, e.g.:

    spin python -- -c 'import sys; print(sys.path)'
    """
    build_cmd = _get_configured_command("build")
    if build_cmd:
        click.secho(
            "Invoking `build` prior to invoking Python:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd, build_dir=build_dir)

    p = _set_pythonpath(build_dir)
    if p:
        print(f'🐍 Launching Python with PYTHONPATH="{p}"')

    v = sys.version_info
    if (v.major < 3) or (v.major == 3 and v.minor < 11):
        print("We're sorry, but this feature only works on Python 3.11 and greater 😢")
        print()
        print(
            "Why? Because we need the '-P' flag so the interpreter doesn't muck with PYTHONPATH"
        )
        print()
        print("However! You can still launch your own interpreter:")
        print()
        print(f"  PYTHONPATH='{p}' python")
        print()
        print("And then call:")
        print()
        print("import sys; del(sys.path[0])")
        sys.exit(-1)

    _run([sys.executable, "-P"] + list(python_args), replace=True)


@click.command(context_settings={"ignore_unknown_options": True})
@build_dir_option
@click.argument("args", nargs=-1)
@click.pass_context
def run(ctx, *, args, build_dir=None):
    """🏁 Run a shell command with PYTHONPATH set

    \b
    spin run make
    spin run 'echo $PYTHONPATH'
    spin run python -c 'import sys; del sys.path[0]; import mypkg'

    If you'd like to expand shell variables, like `$PYTHONPATH` in the example
    above, you need to provide a single, quoted command to `run`:

    spin run 'echo $SHELL && echo $PWD'

    On Windows, all shell commands are run via Bash.
    Install Git for Windows if you don't have Bash already.
    """
    if not len(args) > 0:
        raise RuntimeError("No command given")

    build_cmd = _get_configured_command("build")
    if build_cmd:
        # Redirect spin generated output
        with contextlib.redirect_stdout(sys.stderr):
            # Also ask build to be quiet
            ctx.invoke(build_cmd, build_dir=build_dir, quiet=True)

    is_posix = sys.platform in ("linux", "darwin")
    shell = len(args) == 1
    cmd_args = copy.copy(args)
    if shell:
        cmd_args = args[0]
        if not is_posix:
            # On Windows, we're going to try to use bash
            cmd_args = ["bash", "-c", cmd_args]

    _set_pythonpath(build_dir, quiet=True)
    p = _run(cmd_args, echo=False, shell=shell, sys_exit=False)

    # Is the user trying to run a Python script, without calling the Python interpreter?
    executable = args[0]
    if (
        (p.returncode != 0)
        and args[0].endswith(".py")
        and os.path.exists(executable)
        and (not os.access(executable, os.X_OK))
    ):
        click.secho(
            f"Did you mean to call `spin run python {' '.join(args)}`?", fg="bright_red"
        )
    sys.exit(p.returncode)


@click.command()
@click.argument("sphinx_target", default="html")
@click.option(
    "--clean",
    is_flag=True,
    default=False,
    help="Clean previously built docs before building",
)
@click.option(
    "--build/--no-build",
    "first_build",
    default=True,
    help="Build project before generating docs",
)
@click.option(
    "--plot/--no-plot",
    "sphinx_gallery_plot",
    default=True,
    help="Sphinx gallery: enable/disable plots",
)
@click.option("--jobs", "-j", default="auto", help="Number of parallel build jobs")
@build_dir_option
@click.pass_context
def docs(
    ctx,
    *,
    sphinx_target,
    clean,
    first_build,
    jobs,
    sphinx_gallery_plot,
    clean_dirs=None,
    build_dir=None,
):
    """📖 Build Sphinx documentation

    By default, SPHINXOPTS="-W", raising errors on warnings.
    To build without raising on warnings:

      SPHINXOPTS="" spin docs

    To list all Sphinx targets:

      spin docs targets

    To build another Sphinx target:

      spin docs TARGET

    """
    # Detect docs dir
    doc_dir_candidates = ("doc", "docs")
    doc_dir = next((d for d in doc_dir_candidates if os.path.exists(d)), None)
    if doc_dir is None:
        print(
            f"No documentation folder found; one of {', '.join(doc_dir_candidates)} must exist"
        )
        sys.exit(1)

    if sphinx_target in ("targets", "help"):
        clean = False
        first_build = False
        sphinx_target = "help"

    if clean:
        if clean_dirs is None:
            clean_dirs = []
            for prefix in ("", "_"):
                clean_dirs += [
                    f"./{doc_dir}/{prefix}build/",
                    f"./{doc_dir}/{prefix}build/",
                    f"./{doc_dir}/{prefix}source/api/",
                    f"./{doc_dir}/{prefix}source/auto_examples/",
                    f"./{doc_dir}/{prefix}source/jupyterlite_contents/",
                ]

        for target_dir in clean_dirs:
            if os.path.isdir(target_dir):
                print(f"Removing {target_dir!r}")
                shutil.rmtree(target_dir)

    build_cmd = _get_configured_command("build")

    if build_cmd and first_build:
        click.secho(
            "Invoking `build` prior to building docs:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd, build_dir=build_dir)

    try:
        site_path = _get_site_packages(build_dir)
    except FileNotFoundError:
        cfg = get_config()
        distname = cfg.get("project.name", None)
        print(f"{distname} build not found; run `spin build` or `spin install` first.")
        sys.exit(1)

    opts = os.environ.get("SPHINXOPTS", "-W")
    if not sphinx_gallery_plot:
        opts = f"{opts} -D plot_gallery=0"

    os.environ["SPHINXOPTS"] = f"{opts} -j {jobs}"

    click.secho(
        f"$ export SPHINXOPTS={os.environ['SPHINXOPTS']}", bold=True, fg="bright_blue"
    )

    if site_path:
        os.environ["PYTHONPATH"] = (
            f'{site_path}{os.sep}:{os.environ.get("PYTHONPATH", "")}'
        )
        click.secho(
            f"$ export PYTHONPATH={os.environ['PYTHONPATH']}",
            bold=True,
            fg="bright_blue",
        )

    make_bat_exists = (Path(doc_dir) / "make.bat").exists()
    make_cmd = "make.bat" if sys.platform == "win32" and make_bat_exists else "make"
    _run([make_cmd, sphinx_target], cwd=doc_dir, replace=True)


@click.command()
@click.option("--code", "-c", help="Python program passed in as a string")
@click.argument("lldb_args", nargs=-1)
@build_dir_option
@click.pass_context
def lldb(ctx, *, code, lldb_args, build_dir=None):
    """👾 Execute code through LLDB

      spin lldb -c 'import numpy as np; print(np.__version__)'

    Or run another program, they way you normally would with LLDB:

     \b
     spin lldb -- ls -al

    You can also run Python programs:

     \b
     spin lldb -- my_tests.py
     spin lldb -- my_tests.py --mytest-flag

    And specify LLDB-specific flags:

     \b
     spin lldb -- --arch x86_64 -- ls -al
     spin lldb -- --arch x86_64 -- my_tests.py
     spin lldb -c 'import numpy as np; print(np.__version__)' -- --arch x86_64
    """
    build_cmd = _get_configured_command("build")
    if build_cmd:
        click.secho(
            "Invoking `build` prior to invoking lldb:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd, build_dir=build_dir)

    _set_pythonpath(build_dir)
    lldb_args = list(lldb_args)

    if code:
        if sys.version_info[:2] >= (3, 11):
            PYTHON_FLAGS = ["-P"]
            code_prefix = ""
        else:
            PYTHON_FLAGS = []
            code_prefix = "import sys; sys.path.pop(0); "

        PYTHON_ARGS = ["-c", code_prefix + code]
        program = [sys.executable] + PYTHON_FLAGS + PYTHON_ARGS
    else:
        if "--" in lldb_args:
            ix = lldb_args.index("--")
            lldb_args, program = lldb_args[:ix], lldb_args[ix + 1 :]
        else:
            program, lldb_args = lldb_args, []

    if program and program[0].endswith(".py"):
        program = [sys.executable] + program

    lldb_cmd = (
        ["lldb", "-O", "settings set target.process.follow-fork-mode child"]
        + lldb_args
        + ["--"]
        + program
    )
    _run(lldb_cmd, replace=True)
