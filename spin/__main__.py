import collections
import importlib
import importlib.util
import os
import sys

import click

from spin import __version__
from spin import cmds as _cmds
from spin.color_format import ColorHelpFormatter
from spin.containers import DotDict
from spin.sectioned_help import SectionedHelpGroup

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

click.Context.formatter_class = ColorHelpFormatter


def main():
    # Alias `spin help` to `spin --help`
    if (len(sys.argv) == 2) and (sys.argv[1] == "help"):
        sys.argv[1] = "--help"

    def error(message):
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)

    def load_toml(filename):
        if not os.path.exists(filename):
            return None
        with open(filename, "rb") as f:
            try:
                return tomllib.load(f)
            except tomllib.TOMLDecodeError:
                error("cannot parse [{filename}]")

    toml_config = collections.ChainMap()
    toml_config.maps.extend(
        DotDict(cfg)
        for filename in (
            ".spin.toml",
            "spin.toml",
            "pyproject.toml",
        )
        if (cfg := load_toml(filename))
    )

    # Basic configuration validation
    if "tool.spin" not in toml_config:
        error(
            "needs valid configuration in [.spin.toml], [spin.toml] or [pyproject.toml]"
        )
    if "tool.spin.commands" not in toml_config:
        error("configuration is missing section [tool.spin.commands]")

    spin_config = toml_config["tool.spin"]
    proj_name = (
        toml_config.get("project.name")
        or spin_config.get("package")
        or "unknown project"
    )

    @click.group(help=f"Developer tool for {proj_name}", cls=SectionedHelpGroup)
    @click.version_option(__version__, message="%(prog)s %(version)s")
    @click.pass_context
    def group(ctx):
        ctx.meta["config"] = toml_config
        ctx.meta["commands"] = ctx.command.section_commands
        ctx.show_default = True

    config_cmds = spin_config["commands"]
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
        error(f"{e}; aborting.")


if __name__ == "__main__":
    main()
