import click
from dev.py import util


@click.command()
@click.option("-f", "--flag")
def example(flag):
    """A custom command. Accepts arbitrary flags, can access pyproject.toml config.
    """
    print("Running example custom command")
    config = util.get_config()
    print('Flag provided is:', flag)
    print('Tool config is:')
    print(config['tool.dev.py'])
