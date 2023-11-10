import click

from .util import run as _run


@click.command()
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Print detailed build and installation output",
)
@click.option(
    "--editable/--no-editable",
    is_flag=True,
    default=True,
    help="Install in editable mode",
)
@click.argument("pip_args", nargs=-1)
def install(pip_args, verbose, editable):
    """💽 Build and install package using pip.

    By default, the package is installed in editable mode.

    Arguments after `--` are passed through to pip, e.g.:

      spin install -- --no-clean

    would translated to:

      pip install . --no-build-isolation --editable --no-clean
    """
    pip_args = list(pip_args)
    pip_cmd = ["pip", "install"]
    pip_args += ["--no-build-isolation"]
    if editable:
        pip_args += ["--editable"]

    pip_args = (["-v"] if verbose else []) + pip_args

    _run(pip_cmd + pip_args + ["."], sys_exit=False, replace=True)
