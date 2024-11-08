import json

import click

from spin import util


@click.command()
@click.option("-f", "--flag")
@click.option("-t", "--test", default="not set")
def example(flag, test, default_kwd=None):
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

    click.secho("Flag provided with --test is: ", fg="yellow", nl=False)
    print(test or None)

    click.secho(f"Default kwd is: {default_kwd}")

    click.secho("\nDefined commands:", fg="yellow")
    for section in commands:
        print(f"  {section}: ", end="")
        print(", ".join(cmd.name for cmd in commands[section]))

    click.secho("\nTool config is:", fg="yellow")
    print(json.dumps(config["tool.spin"], indent=2))
