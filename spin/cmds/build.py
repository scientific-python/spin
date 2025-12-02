import click

from .util import run


@click.command()
@click.argument("pyproject-build-args", metavar="", nargs=-1)
def sdist(pyproject_build_args):
    """📦 Build a source distribution in `dist/`

    Extra arguments are passed to `pyproject-build`, e.g.

      spin sdist -- -x -n
    """
    run(["pyproject-build", ".", "--sdist"] + list(pyproject_build_args))


@click.command()
@click.argument("pyproject-build-args", metavar="", nargs=-1)
def wheel(pyproject_build_args):
    """📦 Build a wheel distribution in `dist/`

    Extra arguments are passed to `pyproject-build`, e.g.

      spin wheel -- -x -n
    """
    run(["pyproject-build", ".", "--wheel"] + list(pyproject_build_args))
