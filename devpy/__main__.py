import os
import sys
import importlib
from glob import glob

import click
import toml

from . import cmds
from .cmds import util
from .cmds import *
from .sectioned_help import SectionedHelpGroup
from .color_format import ColorHelpFormatter


click.Context.formatter_class = ColorHelpFormatter


class DotDict(dict):
    def __getitem__(self, key):
        subitem = self
        for subkey in key.split("."):
            try:
                subitem = dict.__getitem__(subitem, subkey)
            except KeyError:
                raise KeyError(f"`{key}` not found in configuration") from None
        return subitem

    def get(self, key, default=None, /):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


if __name__ == "__main__":
    if not os.path.exists("pyproject.toml"):
        print("Error: cannot find [pyproject.toml]")
        sys.exit(1)

    with open("pyproject.toml") as f:
        try:
            toml_config = toml.load(f)
        except:
            print("Cannot parse [pyproject.toml]")
            sys.exit(1)

    try:
        project_config = toml_config["project"]
    except KeyError:
        print("No project section found in pyproject.toml")
        sys.exit(1)

    try:
        config = toml_config["tool"]["devpy"]
    except KeyError:
        print("No configuration found in [pyproject.toml] for [tool.devpy]")
        sys.exit(1)

    commands = {
        f"devpy.{name}": getattr(cmds, name)
        for name in dir(cmds)
        if not name.startswith("_")
    }

    @click.group(
        help=f"Developer tool for {project_config['name']}", cls=SectionedHelpGroup
    )
    @click.pass_context
    def group(ctx):
        ctx.meta["config"] = DotDict(toml_config)
        ctx.show_default = True

    config_cmds = config["commands"]
    # Commands can be provided as a list, or as a dictionary
    # so that they can be sorted into sections
    if isinstance(config_cmds, list):
        config_cmds = {"Commands": config_cmds}

    for section, cmds in config_cmds.items():
        for cmd in cmds:
            if cmd not in commands:
                try:
                    path, func = cmd.split(":")
                    spec = importlib.util.spec_from_file_location("custom_mod", path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    try:
                        cmd_func = getattr(mod, func)
                    except AttributeError:
                        print(
                            f"!! Could not load command `{func}` from file `{path}`.\n"
                        )
                        continue
                except FileNotFoundError:
                    print(
                        f"!! Could not find file `{path}` to load custom command `{cmd}`.\n"
                    )
                    continue
                except Exception as e:
                    print(
                        f"!! Could not import file `{path}` to load custom command `{cmd}`.\n"
                    )
                    raise e

                commands[cmd] = cmd_func

            group.add_command(commands[cmd], section=section)

    group()
