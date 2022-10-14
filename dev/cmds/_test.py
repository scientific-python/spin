import click

from .util import run


@click.command()
@click.argument("pytest_args", nargs=-1)
def test(pytest_args):
    """🔧 Run tests

    PYTEST_ARGS are passed through directly to pytest.
    """
    if not pytest_args:
        pytest_args = ("TODO__PROJECT_NAME_FROM_CONFIG",)
    run(["pytest"] + list(pytest_args))
