import contextlib
import json
import os
import shutil
import sys

import click

from .util import get_commands, get_config
from .util import run as _run

install_dir = "build-install"


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


def _set_pythonpath(quiet=False):
    """Set first entry of PYTHONPATH to site packages directory.

    Returns
    -------
    site_packages
    """
    site_packages = _get_site_packages()
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


def _get_site_packages():
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


def _meson_version_configured():
    try:
        meson_info_fn = os.path.join("build", "meson-info", "meson-info.json")
        with open(meson_info_fn) as f:
            meson_info = json.load(f)
        return meson_info["meson_version"]["full"]
    except:
        pass


@click.command()
@click.option("-j", "--jobs", help="Number of parallel tasks to launch", type=int)
@click.option("--clean", is_flag=True, help="Clean build directory before build")
@click.option(
    "-v", "--verbose", is_flag=True, help="Print detailed build and installation output"
)
@click.argument("meson_args", nargs=-1)
def build(meson_args, jobs=None, clean=False, verbose=False, quiet=False):
    """🔧 Build package with Meson/ninja and install

    MESON_ARGS are passed through e.g.:

      spin build -- -Dpkg_config_path=/lib64/pkgconfig

    The package is installed to build-install

    By default meson-python does release builds. To be able to use a debugger,
    tell meson to build in debug mode:

      spin build -- -Dbuildtype=debug

    or set CFLAGS appropriately:

      CFLAGS="-O0 -g" spin build
    """
    build_dir = "build"
    setup_cmd = _meson_cli() + ["setup", build_dir, "--prefix=/usr"] + list(meson_args)

    if clean:
        print(f"Removing `{build_dir}`")
        if os.path.isdir(build_dir):
            shutil.rmtree(build_dir)
        print(f"Removing `{install_dir}`")
        if os.path.isdir(install_dir):
            shutil.rmtree(install_dir)

    if not (os.path.exists(build_dir) and _meson_version_configured()):
        p = _run(setup_cmd, sys_exit=False, output=not quiet)
        if p.returncode != 0:
            raise RuntimeError(
                "Meson configuration failed; please try `spin build` again with the `--clean` flag."
            )
    else:
        # Build dir has been configured; check if it was configured by
        # current version of Meson

        if _meson_version() != _meson_version_configured():
            _run(setup_cmd + ["--reconfigure"], output=not quiet)

        # Any other conditions that warrant a reconfigure?

    compile_flags = ["-v"] if verbose else []
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
            f"../{install_dir}",
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
        "Number of parallel jobs for testing. " "Can be set to `auto` to use all cores."
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
    help="Generate a coverage report of executed tests. An HTML copy of the report is written to `build/coverage`.",
)
@click.pass_context
def test(ctx, pytest_args, n_jobs, tests, verbose, coverage=False):
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

    build_cmd = _get_configured_command("build")
    if build_cmd:
        click.secho(
            "Invoking `build` prior to running tests:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd)

    package = cfg.get("tool.spin.package", None)
    if (not pytest_args) and (not tests):
        pytest_args = (package,)
        if pytest_args == (None,):
            print(
                "Please specify `package = packagename` under `tool.spin` section of `pyproject.toml`"
            )
            sys.exit(1)

    site_path = _set_pythonpath()

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

    if tests and "--pyargs" not in pytest_args:
        pytest_args = ("--pyargs", tests) + pytest_args

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

    print(f'$ export PYTHONPATH="{site_path}"')
    _run(
        [sys.executable, "-m", "pytest", f"--rootdir={site_path}"] + list(pytest_args),
        cwd=site_path,
        replace=True,
    )


@click.command()
@click.option("--code", "-c", help="Python program passed in as a string")
@click.argument("gdb_args", nargs=-1)
@click.pass_context
def gdb(ctx, code, gdb_args):
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
        ctx.invoke(build_cmd)

    _set_pythonpath()
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
@click.pass_context
def ipython(ctx, ipython_args):
    """💻 Launch IPython shell with PYTHONPATH set

    IPYTHON_ARGS are passed through directly to IPython, e.g.:

    spin ipython -- -i myscript.py
    """
    build_cmd = _get_configured_command("build")
    if build_cmd:
        click.secho(
            "Invoking `build` prior to invoking ipython:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd)

    p = _set_pythonpath()
    print(f'💻 Launching IPython with PYTHONPATH="{p}"')
    _run(["ipython", "--ignore-cwd"] + list(ipython_args), replace=True)


@click.command()
@click.argument("shell_args", nargs=-1)
@click.pass_context
def shell(ctx, shell_args=[]):
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
        ctx.invoke(build_cmd)

    p = _set_pythonpath()
    shell = os.environ.get("SHELL", "sh")
    cmd = [shell] + list(shell_args)
    print(f'💻 Launching shell with PYTHONPATH="{p}"')
    print("⚠  Change directory to avoid importing source instead of built package")
    print("⚠  Ensure that your ~/.shellrc does not unset PYTHONPATH")
    _run(cmd, replace=True)


@click.command()
@click.argument("python_args", nargs=-1)
@click.pass_context
def python(ctx, python_args):
    """🐍 Launch Python shell with PYTHONPATH set

    PYTHON_ARGS are passed through directly to Python, e.g.:

    spin python -- -c 'import sys; print(sys.path)'
    """
    build_cmd = _get_configured_command("build")
    if build_cmd:
        click.secho(
            "Invoking `build` prior to invoking Python:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd)

    p = _set_pythonpath()
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

    print(f'🐍 Launching Python with PYTHONPATH="{p}"')

    _run(["/usr/bin/env", "python", "-P"] + list(python_args), replace=True)


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
@click.pass_context
def run(ctx, args):
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
            ctx.invoke(build_cmd, quiet=True)

    is_posix = sys.platform in ("linux", "darwin")
    shell = len(args) == 1
    if shell:
        args = args[0]

    if shell and not is_posix:
        # On Windows, we're going to try to use bash
        args = ["bash", "-c", args]

    _set_pythonpath(quiet=True)
    _run(args, echo=False, shell=shell)


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
@click.pass_context
def docs(ctx, sphinx_target, clean, first_build, jobs, sphinx_gallery_plot):
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
        doc_dirs = [
            "./doc/build/",
            "./doc/source/api/",
            "./doc/source/auto_examples/",
            "./doc/source/jupyterlite_contents/",
        ]
        for doc_dir in doc_dirs:
            if os.path.isdir(doc_dir):
                print(f"Removing {doc_dir!r}")
                shutil.rmtree(doc_dir)

    build_cmd = _get_configured_command("build")

    if build_cmd and first_build:
        click.secho(
            "Invoking `build` prior to building docs:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd)

    try:
        site_path = _get_site_packages()
    except FileNotFoundError:
        print("No built numpy found; run `spin build` first.")
        sys.exit(1)

    opts = os.environ.get("SPHINXOPTS", "-W")
    if not sphinx_gallery_plot:
        opts = f"{opts} -D plot_gallery=0"

    os.environ["SPHINXOPTS"] = f"{opts} -j {jobs}"

    click.secho(
        f"$ export SPHINXOPTS={os.environ['SPHINXOPTS']}", bold=True, fg="bright_blue"
    )

    os.environ["PYTHONPATH"] = f'{site_path}{os.sep}:{os.environ.get("PYTHONPATH", "")}'
    click.secho(
        f"$ export PYTHONPATH={os.environ['PYTHONPATH']}", bold=True, fg="bright_blue"
    )
    _run(["make", "-C", "doc", sphinx_target], replace=True)


@click.command()
@click.option("--code", "-c", help="Python program passed in as a string")
@click.argument("lldb_args", nargs=-1)
@click.pass_context
def lldb(ctx, code, lldb_args):
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
        ctx.invoke(build_cmd)

    _set_pythonpath()
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
