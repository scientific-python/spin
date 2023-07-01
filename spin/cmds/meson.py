import os
import sys
import shutil
import json
import shlex

import click

from .util import run as _run, get_config, get_commands


install_dir = "build-install"


def _set_pythonpath(quiet=False):
    site_packages = _get_site_packages()
    env = os.environ

    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{site_packages}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = site_packages

    if not quiet:
        click.secho(
            f'$ export PYTHONPATH="{site_packages}"', bold=True, fg="bright_blue"
        )

    return env["PYTHONPATH"]


def _get_site_packages():
    candidate_paths = []
    for root, dirs, files in os.walk(install_dir):
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
        p = _run(["meson", "--version"], output=False, echo=False)
        return p.stdout.decode("ascii").strip()
    except:
        pass


def _meson_version_configured():
    try:
        meson_info_fn = os.path.join("build", "meson-info", "meson-info.json")
        meson_info = json.load(open(meson_info_fn))
        return meson_info["meson_version"]["full"]
    except:
        pass


@click.command()
@click.option("-j", "--jobs", help="Number of parallel tasks to launch", type=int)
@click.option("--clean", is_flag=True, help="Clean build directory before build")
@click.option(
    "-v", "--verbose", is_flag=True, help="Print all build output, even installation"
)
@click.argument("meson_args", nargs=-1)
def build(meson_args, jobs=None, clean=False, verbose=False):
    """🔧 Build package with Meson/ninja and install

    MESON_ARGS are passed through e.g.:

    spin build -- -Dpkg_config_path=/lib64/pkgconfig

    The package is installed to build-install

    By default builds for release, to be able to use a debugger set CFLAGS
    appropriately. For example, for linux use

    CFLAGS="-O0 -g" spin build
    """
    build_dir = "build"
    setup_cmd = ["meson", "setup", build_dir, "--prefix=/usr"] + list(meson_args)

    if clean:
        print(f"Removing `{build_dir}`")
        if os.path.isdir(build_dir):
            shutil.rmtree(build_dir)
        print(f"Removing `{install_dir}`")
        if os.path.isdir(install_dir):
            shutil.rmtree(install_dir)

    if not (os.path.exists(build_dir) and _meson_version_configured()):
        p = _run(setup_cmd, sys_exit=False)
        if p.returncode != 0:
            raise RuntimeError(
                "Meson configuration failed; please try `spin build` again with the `--clean` flag."
            )
    else:
        # Build dir has been configured; check if it was configured by
        # current version of Meson

        if _meson_version() != _meson_version_configured():
            _run(setup_cmd + ["--reconfigure"])

        # Any other conditions that warrant a reconfigure?

    p = _run(["meson", "compile", "-C", build_dir], sys_exit=False)
    p = _run(
        [
            "meson",
            "install",
            "--only-changed",
            "-C",
            build_dir,
            "--destdir",
            f"../{install_dir}",
        ],
        output=verbose,
    )


def _get_configured_command(command_name):
    command_groups = get_commands()
    commands = [cmd for section in command_groups for cmd in command_groups[section]]
    return next((cmd for cmd in commands if cmd.name == command_name), None)


@click.command()
@click.argument("pytest_args", nargs=-1)
@click.pass_context
def test(ctx, pytest_args):
    """🔧 Run tests

    PYTEST_ARGS are passed through directly to pytest, e.g.:

    spin test -- -v

    By default, runs the full test suite. To skip "slow" tests, run

    spin test -- -m "not slow"
    """
    cfg = get_config()

    build_cmd = _get_configured_command("build")
    if build_cmd:
        click.secho(
            f"Invoking `build` prior to running tests:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd)

    package = cfg.get("tool.spin.package", None)
    if not pytest_args:
        pytest_args = (package,)
        if pytest_args == (None,):
            print(
                "Please specify `package = packagename` under `tool.spin` section of `pyproject.toml`"
            )
            sys.exit(1)

    site_path = _set_pythonpath()

    # Sanity check that library built properly
    if sys.version_info[:2] >= (3, 11):
        p = _run([sys.executable, "-P", "-c", f"import {package}"], sys_exit=False)
        if p.returncode != 0:
            print(f"As a sanity check, we tried to import {package}.")
            print("Stopping. Please investigate the build error.")
            sys.exit(1)

    print(f'$ export PYTHONPATH="{site_path}"')
    _run(
        [sys.executable, "-m", "pytest", f"--rootdir={site_path}"] + list(pytest_args),
        cwd=site_path,
        replace=True,
    )


@click.command()
@click.argument("ipython_args", nargs=-1)
def ipython(ipython_args):
    """💻 Launch IPython shell with PYTHONPATH set

    IPYTHON_ARGS are passed through directly to IPython, e.g.:

    spin ipython -- -i myscript.py
    """
    p = _set_pythonpath()
    print(f'💻 Launching IPython with PYTHONPATH="{p}"')
    _run(["ipython", "--ignore-cwd"] + list(ipython_args), replace=True)


@click.command()
@click.argument("shell_args", nargs=-1)
def shell(shell_args=[]):
    """💻 Launch shell with PYTHONPATH set

    SHELL_ARGS are passed through directly to the shell, e.g.:

    spin shell -- -c 'echo $PYTHONPATH'

    Ensure that your shell init file (e.g., ~/.zshrc) does not override
    the PYTHONPATH.
    """
    p = _set_pythonpath()
    shell = os.environ.get("SHELL", "sh")
    cmd = [shell] + list(shell_args)
    print(f'💻 Launching shell with PYTHONPATH="{p}"')
    print(f"⚠  Change directory to avoid importing source instead of built package")
    print(f"⚠  Ensure that your ~/.shellrc does not unset PYTHONPATH")
    _run(cmd, replace=True)


@click.command()
@click.argument("python_args", nargs=-1)
def python(python_args):
    """🐍 Launch Python shell with PYTHONPATH set

    PYTHON_ARGS are passed through directly to Python, e.g.:

    spin python -- -c 'import sys; print(sys.path)'
    """
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
def run(args):
    """🏁 Run a shell command with PYTHONPATH set

    \b
    spin run make
    spin run 'echo $PYTHONPATH'
    spin run python -c 'import sys; del sys.path[0]; import mypkg'

    If you'd like to expand shell variables, like `$PYTHONPATH` in the example
    above, you need to provide a single, quoted command to `run`:

    spin run 'echo $SHELL && echo $PWD'

    On Windows, all commands are run via Bash.
    Install Git for Windows if you don't have Bash already.
    """
    if not len(args) > 0:
        raise RuntimeError("No command given")

    is_posix = sys.platform in ("linux", "darwin")
    shell = len(args) == 1

    if not is_posix:
        # On Windows, we're going to try to use bash
        args = ["bash", "-c"] + args
        shell = True
    else:
        if shell:
            args = args[0]

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
    help="Build numpy before generating docs",
)
@click.option("--jobs", "-j", default="auto", help="Number of parallel build jobs")
@click.pass_context
def docs(ctx, sphinx_target, clean, first_build, jobs):
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
    os.environ["SPHINXOPTS"] = f"{opts} -j {jobs}"
    click.secho(
        f"$ export SPHINXOPTS={os.environ['SPHINXOPTS']}", bold=True, fg="bright_blue"
    )

    os.environ["PYTHONPATH"] = f'{site_path}{os.sep}:{os.environ.get("PYTHONPATH", "")}'
    click.secho(
        f"$ export PYTHONPATH={os.environ['PYTHONPATH']}", bold=True, fg="bright_blue"
    )
    _run(["make", "-C", "doc", sphinx_target], replace=True)
