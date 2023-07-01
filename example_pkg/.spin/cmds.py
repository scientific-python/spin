import json

import click

from spin import util


@click.command()
@click.option("-f", "--flag")
def example(flag):
    """🧪 Example custom command.

    Accepts arbitrary flags, and shows how to access `pyproject.toml`
    config.
    """
    click.secho("Running example custom command", bold=True, fg="bright_blue")
    print()
    config = util.get_config()
    commands = util.get_commands()
    click.secho("Flag provided with --flag is: ", fg="yellow", nl=False)
    print(flag or None)

    click.secho("\nDefined commands:", fg="yellow")
    for section in commands:
        print(f"  {section}: ", end="")
        print(", ".join(cmd.name for cmd in commands[section]))

    click.secho("\nTool config is:", fg="yellow")
    print(json.dumps(config["tool.spin"], indent=2))
