import collections
import importlib
import importlib.util
import os
import sys

import click

from spin import cmds as _cmds
from spin.color_format import ColorHelpFormatter
from spin.sectioned_help import SectionedHelpGroup

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

click.Context.formatter_class = ColorHelpFormatter


class DotDict(collections.UserDict):
    def __getitem__(self, key):
        subitem = self.data
        for subkey in key.split("."):
            try:
                subitem = subitem[subkey]
            except KeyError:
                raise KeyError(f"`{key}` not found in configuration") from None
        return subitem

    # Fix for Python 3.12
    # See https://github.com/python/cpython/issues/105524
    def __contains__(self, key):
        subitem = self.data
        for subkey in key.split("."):
            try:
                subitem = subitem[subkey]
            except KeyError:
                return False
        return True


def main():
    if not os.path.exists("pyproject.toml"):
        print("Error: cannot find [pyproject.toml]")
        sys.exit(1)

    with open("pyproject.toml", "rb") as f:
        try:
            toml_config = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            print("Cannot parse [pyproject.toml]")
            sys.exit(1)

    project_config = toml_config.get("project", {})

    try:
        config = toml_config["tool"]["spin"]
    except KeyError:
        print("No configuration found in [pyproject.toml] for [tool.spin]")
        sys.exit(1)

    proj_name = project_config.get("name", config["package"])

    @click.group(help=f"Developer tool for {proj_name}", cls=SectionedHelpGroup)
    @click.pass_context
    def group(ctx):
        ctx.meta["config"] = DotDict(toml_config)
        ctx.meta["commands"] = ctx.command.section_commands
        ctx.show_default = True

    config_cmds = config["commands"]
    # Commands can be provided as a list, or as a dictionary
    # so that they can be sorted into sections
    if isinstance(config_cmds, list):
        config_cmds = {"Commands": config_cmds}

    # Backward compatibility workaround
    # Originally, you could specify any of these commands as `spin.cmd`
    # and we'd fetch it from util
    commands = {
        "spin.build": _cmds.meson.build,
        "spin.test": _cmds.meson.test,
        "spin.ipython": _cmds.meson.ipython,
        "spin.python": _cmds.meson.python,
        "spin.shell": _cmds.meson.shell,
    }

    for section, cmds in config_cmds.items():
        for cmd in cmds:
            if cmd not in commands:
                # First, see if we can directly import the command
                if ":" not in cmd:
                    path, func = cmd.rsplit(".", maxsplit=1)
                    try:
                        mod = importlib.import_module(path)
                    except ImportError:
                        print(
                            f"!! Could not import module `{path}` to load command `{cmd}`"
                        )
                        continue
                else:
                    try:
                        path, func = cmd.split(":")
                        spec = importlib.util.spec_from_file_location(
                            "custom_mod", path
                        )
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
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

                try:
                    cmd_func = getattr(mod, func)
                except AttributeError:
                    print(f"!! Could not load command `{func}` from file `{path}`.\n")
                    continue

                commands[cmd] = cmd_func

            group.add_command(commands[cmd], section=section)

    try:
        group()
    except Exception as e:
        print(f"{e}; aborting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
