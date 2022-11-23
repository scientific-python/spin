import click
from devpy import util


@click.command()
@click.option("-f", "--flag")
def example(flag):
    """🧪 Example custom command.

    Accepts arbitrary flags, and shows how to access `pyproject.toml`
    config.
    """
    print("Running example custom command")
    config = util.get_config()
    print("Flag provided is:", flag)
    print("Tool config is:")
    print(config["tool.devpy"])
