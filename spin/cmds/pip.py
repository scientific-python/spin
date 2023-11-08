import click

from .util import run as _run


@click.command()
@click.option(
    "-v", "--verbose", is_flag=True, help="Print detailed build and installation output"
)
@click.argument("-e", "--editable", is_flag=True, help="Install in editable mode")
@click.argument("pip_args", nargs=-1)
def install(pip_args, verbose=False, editable=True):
    """💽 Install package and also build.

    pip arguments are passed through in the same manner as you would pip e.g.:

        spin install -- --no-clean

    which would be translated to the following pip command:

        pip install . --no-build-isolation --editable --no-clean

    The package is by default installed in editable mode, but you can disable this
    by passing the `--editable` flag and setting it to ``false``.
    """
    pip_args = list(pip_args)
    pip_cmd = ["pip", "install", ".", "--no-build-isolation"]
    if editable:
        pip_args += ["--editable"]

    pip_cmd += pip_args
    pip_cmd += ["-v"] if verbose else []

    _run(pip_cmd, sys_exit=False, replace=True)
