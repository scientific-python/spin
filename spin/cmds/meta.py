import inspect

import click

from .util import get_commands, get_config


def _highlight(src):
    from pygments import highlight
    from pygments.formatters import TerminalFormatter
    from pygments.lexers import PythonLexer

    return highlight(src, PythonLexer(), TerminalFormatter())


@click.command()
@click.argument("cmd", nargs=1)
def introspect(*, cmd):
    """🔍 Print a command's location and source code."""
    cmds_by_section = get_commands()
    overrides = get_config().get("tool.spin.kwargs")

    cmds = {}
    for section in cmds_by_section:
        cmds.update({cmd.name: cmd for cmd in cmds_by_section[section]})

    if cmd not in cmds:
        raise SystemExit(f"Command `{cmd}` not found. Exiting.")

    cmd_func = cmds[cmd]
    try:
        if hasattr(cmd_func.callback, "_parent"):
            # `util.extend_command` was used
            code = inspect.getsource(cmd_func.callback._parent)
        else:
            code = inspect.getsource(cmd_func.callback)
    except TypeError:
        # Perhaps a partial, try again
        code = inspect.getsource(cmd_func.callback.func)

    try:
        code = _highlight(code)
    except ImportError:
        pass

    print(code)

    click.secho(
        f"The `{cmd}` command is defined as `{cmd_func.spec}`.",
        bold=True,
        fg="magenta",
    )

    click.secho(
        f"The code is in `{cmd_func.module.__file__}`.", bold=True, fg="magenta"
    )

    if cmd_func.spec in overrides:
        click.secho(
            "\nThe function has the following keyword overrides defined:\n",
            bold=True,
            fg="magenta",
        )
        print("  ", overrides[cmd_func.spec], "\n")
