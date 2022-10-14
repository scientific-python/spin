import os
import sys
from glob import glob

import click
import toml

from . import cmds
from .cmds import *


if __name__ == "__main__":
    if not os.path.exists('pyproject.toml'):
        print('Error: cannot find [pyproject.toml]')
        sys.exit(1)

    with open('pyproject.toml', 'r') as f:
        try:
            toml_config = toml.load(f)
        except:
            print('Cannot parse [pyproject.toml]')
            sys.exit(1)

    try:
        project_config = toml_config['project']
        config = toml_config['tool']['dev']['py']
    except KeyError:
        print('No configuration found in [pyproject.toml] for [tool.dev.py]')
        sys.exit(1)

    commands = {
        f'dev.py.{name}': getattr(cmds, name)
        for name in dir(cmds)
        if not name.startswith('_')
    }

    @click.group(help=f"Developer tool for {project_config['name']}")
    def group():
        pass

    for cmd in config['commands']:
        group.add_command(commands[cmd])

    group()
