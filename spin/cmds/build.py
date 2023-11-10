import click

from .util import run


@click.command()
def sdist():
    """📦 Build a source distribution in `dist/`"""
    run(["pyproject-build", ".", "--sdist"])
