import collections
import importlib
import importlib.util
import os
import pathlib
import sys
import textwrap
import traceback

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

config_filenames = (
    ".spin.toml",
    "spin.toml",
    "pyproject.toml",
)


def _detect_config_dir(path: pathlib.Path) -> pathlib.Path | None:
    path = path.resolve()
    files = os.listdir(path)
    if any(f in files for f in config_filenames):
        return path
    elif path.parent != path:
        return _detect_config_dir(path.parent)
    else:
        return None


def main():
    # Alias `spin help` to `spin --help`
    if (len(sys.argv) == 2) and (sys.argv[1] == "help"):
        sys.argv[1] = "--help"

    def load_toml(filename):
        if not os.path.exists(filename):
            return None
        with open(filename, "rb") as f:
            try:
                return tomllib.load(f)
            except tomllib.TOMLDecodeError:
                print(f"Error: cannot parse [{filename}]", file=sys.stderr)

    toml_config = collections.ChainMap()
    toml_config.maps.extend(
        DotDict(cfg) for filename in config_filenames if (cfg := load_toml(filename))
    )

    if not toml_config:
        click.secho(
            f"Could not load configuration from one of: {', '.join(config_filenames)}",
            file=sys.stderr,
            fg="red",
        )
        config_dir = _detect_config_dir(pathlib.Path("."))
        if config_dir:
            print()
            print(
                "Are you running `spin` from the correct directory? Perhaps you'd like to\n"
            )
            click.secho(f" $ cd {os.path.relpath(config_dir, '.')}\n")
            print("and try again.")
        sys.exit(1)

    # Basic configuration validation
    version_query = len(sys.argv) == 2 and (sys.argv[1] == "--version")

    spin_config = {}
    if not version_query:
        if "tool.spin" in toml_config:
            spin_config = toml_config["tool.spin"]
            if "tool.spin.commands" not in toml_config:
                click.secho(
                    "Error: configuration is missing section [tool.spin.commands]\n"
                    "See https://github.com/scientific-python/spin/blob/main/README.md\n",
                    file=sys.stderr,
                    fg="red",
                )
        else:
            click.secho(
                "Error: need valid configuration in [.spin.toml], [spin.toml], or [pyproject.toml]\n"
                "See https://github.com/scientific-python/spin/blob/main/README.md\n",
                file=sys.stderr,
                fg="red",
            )

    proj_name = (
        toml_config.get("project.name")
        or spin_config.get("package")
        or "[unknown project]"
    )

    @click.group(help=f"Developer tool for {proj_name}", cls=SectionedHelpGroup)
    @click.version_option(__version__, message="%(prog)s %(version)s")
    @click.pass_context
    def group(ctx):
        ctx.meta["config"] = toml_config
        ctx.meta["commands"] = ctx.command.section_commands
        ctx.show_default = True

    config_cmds = spin_config.get("commands", [])
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
    cmd_default_kwargs = toml_config.get("tool.spin.kwargs", {})

    custom_module_cache = {}

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

                        if path not in custom_module_cache:
                            spec = importlib.util.spec_from_file_location(
                                "custom_mod", path
                            )
                            mod = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(mod)
                            custom_module_cache[path] = mod
                        else:
                            mod = custom_module_cache[path]

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
                    cmd_func.module = mod  # metadata for use by `introspect` command
                except AttributeError:
                    print(f"!! Could not load command `{func}` from file `{path}`.\n")
                    continue

                # Save command definition for use in `introspect`
                cmd_func.spec = cmd

                default_kwargs = cmd_default_kwargs.get(cmd)
                import functools

                if default_kwargs:
                    callback = cmd_func.callback
                    cmd_func.callback = functools.partial(callback, **default_kwargs)

                    # Also override option defaults
                    for option in cmd_func.params:
                        if option.name in default_kwargs:
                            option.default = default_kwargs[option.name]

                commands[cmd] = cmd_func

            group.add_command(commands[cmd], section=section)

    try:
        group()
    except Exception:
        click.secho(
            "\n" + "".join(traceback.format_exception(*sys.exc_info(), limit=-1)),
            fg="red",
            bold=True,
            file=sys.stderr,
        )

        click.secho(
            textwrap.dedent(f"""\
            If you suspect this is a bug in `spin`, please file a report at:

              https://github.com/scientific-python/spin

            including the above traceback and the following information:

              spin: {__version__}, package: {proj_name}

            Aborting."""),
            fg="yellow",
            bold=True,
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
