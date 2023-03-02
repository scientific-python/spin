import os
import sys
import shutil

import click

from .util import run, get_config, get_commands


install_dir = "build-install"


def set_pythonpath():
    site_packages = get_site_packages()
    env = os.environ

    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{site_packages}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = site_packages

    return env["PYTHONPATH"]


def get_site_packages():
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

    ./dev.py build -- -Dpkg_config_path=/lib64/pkgconfig

    The package is installed to build-install

    By default builds for release, to be able to use a debugger set CFLAGS
    appropriately. For example, for linux use

    CFLAGS="-O0 -g" ./dev.py build
    """
    build_dir = os.path.abspath("build")
    build_cmd = ["meson", "setup", build_dir, "--prefix=/usr"] + list(meson_args)
    flags = []

    if clean:
        print(f"Removing `{build_dir}`")
        if os.path.isdir(build_dir):
            shutil.rmtree(build_dir)
        print(f"Removing `{install_dir}`")
        if os.path.isdir(install_dir):
            shutil.rmtree(install_dir)

    if os.path.exists(build_dir):
        flags += ["--reconfigure"]

    p = run(build_cmd + flags, sys_exit=False)
    if p.returncode != 0 and "--reconfigure" in flags:
        click.confirm(
            f"\nMeson failed; perhaps due to an invalid build tree. OK to remove `{build_dir}` and try again?",
            abort=True,
        )
        shutil.rmtree(build_dir)
        run(build_cmd)

    run(["meson", "compile", "-C", build_dir])
    run(
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


@click.command()
@click.argument("pytest_args", nargs=-1)
@click.pass_context
def test(ctx, pytest_args):
    """🔧 Run tests

    PYTEST_ARGS are passed through directly to pytest, e.g.:

    ./dev.py test -- -v

    By default, runs the full test suite. To skip "slow" tests, run

    ./dev.py test -- -m "not slow"
    """
    cfg = get_config()

    command_groups = get_commands()
    commands = [cmd for section in command_groups for cmd in command_groups[section]]
    build_cmd = next((cmd for cmd in commands if cmd.name == "build"), None)
    if build_cmd:
        click.secho(
            f"Invoking `build` prior to running tests:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd)

    if not pytest_args:
        pytest_args = (cfg.get("tool.devpy.package", None),)
        if pytest_args == (None,):
            print(
                "Please specify `package = packagename` under `tool.devpy` section of `pyproject.toml`"
            )
            sys.exit(1)

    site_path = get_site_packages()
    set_pythonpath()

    print(f'$ export PYTHONPATH="{site_path}"')
    run(
        [sys.executable, "-m", "pytest", f"--rootdir={site_path}"] + list(pytest_args),
        cwd=site_path,
        replace=True,
    )


@click.command()
@click.argument("ipython_args", nargs=-1)
def ipython(ipython_args):
    """💻 Launch IPython shell with PYTHONPATH set

    IPYTHON_ARGS are passed through directly to IPython, e.g.:

    ./dev.py ipython -- -i myscript.py
    """
    p = set_pythonpath()
    print(f'💻 Launching IPython with PYTHONPATH="{p}"')
    run(["ipython", "--ignore-cwd"] + list(ipython_args), replace=True)


@click.command()
@click.argument("shell_args", nargs=-1)
def shell(shell_args=[]):
    """💻 Launch shell with PYTHONPATH set

    SHELL_ARGS are passed through directly to the shell, e.g.:

    ./dev.py shell -- -c 'echo $PYTHONPATH'

    Ensure that your shell init file (e.g., ~/.zshrc) does not override
    the PYTHONPATH.
    """
    p = set_pythonpath()
    shell = os.environ.get("SHELL", "sh")
    cmd = [shell] + list(shell_args)
    print(f'💻 Launching shell with PYTHONPATH="{p}"')
    print(f"⚠  Change directory to avoid importing source instead of built package")
    print(f"⚠  Ensure that your ~/.shellrc does not unset PYTHONPATH")
    run(cmd, replace=True)


@click.command()
@click.argument("python_args", nargs=-1)
def python(python_args):
    """🐍 Launch Python shell with PYTHONPATH set

    PYTHON_ARGS are passed through directly to Python, e.g.:

    ./dev.py python -- -c 'import sys; print(sys.path)'
    """
    p = set_pythonpath()
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

    run(["/usr/bin/env", "python", "-P"] + list(python_args), replace=True)
