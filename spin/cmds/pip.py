import sys

import click

from .util import run as _run


@click.command()
@click.option(
    "--editable/--no-editable",
    default=True,
    help="Install in editable mode.",
)
@click.option(
    "-v/-q",
    "--verbose/--quiet",
    is_flag=True,
    default=True,
    help="Print detailed build output.",
)
@click.option(
    "--verbose-import/--no-verbose-import",
    is_flag=True,
    default=True,
    help="Meson only: importing an editable install may trigger a build. This flag determines whether to print that build's output.",
)
@click.argument("pip_args", nargs=-1)
def install(*, pip_args, editable, verbose, verbose_import):
    """💽 Build and install package using pip.

    By default, the package is installed in editable mode.

    Arguments after `--` are passed through to pip, e.g.:

      spin install -- --no-clean

    would translated to:

      pip install . --no-build-isolation --editable --no-clean
    """
    pip_args = list(pip_args)
    pip_cmd = [sys.executable, "-m", "pip", "install"]
    pip_args += ["--no-build-isolation"]

    if editable:
        pip_args += ["--editable"]

        if verbose_import:
            pip_args = ["--config-settings=editable-verbose=true"] + pip_args

    if verbose:
        pip_args = ["-v"] + pip_args

    if "." in pip_args:
        pip_args.remove(".")

    _run(pip_cmd + pip_args + ["."], sys_exit=False, replace=True)
