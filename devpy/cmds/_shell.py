import os
import sys
import copy

import click

from .util import run, get_config, get_site_packages, set_pythonpath


@click.command()
@click.option(
    "--build-dir", default="build", help="Build directory; default is `$PWD/build`"
)
@click.argument("ipython_args", nargs=-1)
def ipython(build_dir, ipython_args):
    """💻 Launch IPython shell with PYTHONPATH set

    IPYTHON_ARGS are passed through directly to IPython, e.g.:

    ./dev.py ipython -- -i myscript.py
    """
    p = set_pythonpath(build_dir)
    print(f'💻 Launching IPython with PYTHONPATH="{p}"')
    run(["ipython", "--ignore-cwd"] + list(ipython_args), replace=True)


@click.command()
@click.option(
    "--build-dir", default="build", help="Build directory; default is `$PWD/build`"
)
@click.argument("shell_args", nargs=-1)
def shell(build_dir, shell_args=[]):
    """💻 Launch shell with PYTHONPATH set

    SHELL_ARGS are passed through directly to the shell, e.g.:

    ./dev.py shell -- -c 'echo $PYTHONPATH'

    Ensure that your shell init file (e.g., ~/.zshrc) does not override
    the PYTHONPATH.
    """
    p = set_pythonpath(build_dir)
    shell = os.environ.get("SHELL", "sh")
    cmd = [shell] + list(shell_args)
    print(f'💻 Launching shell with PYTHONPATH="{p}"')
    print(f"⚠  Change directory to avoid importing source instead of built package")
    print(f"⚠  Ensure that your ~/.shellrc does not unset PYTHONPATH")
    run(cmd, replace=True)


@click.command()
@click.option(
    "--build-dir", default="build", help="Build directory; default is `$PWD/build`"
)
@click.argument("python_args", nargs=-1)
def python(build_dir, python_args):
    """🐍 Launch Python shell with PYTHONPATH set

    PYTHON_ARGS are passed through directly to Python, e.g.:

    ./dev.py python -- -c 'import sys; print(sys.path)'
    """
    p = set_pythonpath(build_dir)
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
