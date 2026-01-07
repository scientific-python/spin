from __future__ import (
    annotations,  # noqa: F401  # TODO: remove once only >3.14 is supported
)

import copy
import os
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable

import click


def run(
    cmd: list[str],
    cwd: str | None = None,  # in 3.10 and up: str | None
    replace: bool = False,
    sys_exit: bool = True,
    output: bool = True,
    echo: bool = True,
    *args,
    **kwargs,
) -> subprocess.CompletedProcess:
    """Run a shell command.

    Parameters
    ----------
    cmd : list of str
        Command to execute.
    cwd : str
        Change to this directory before execution.
    replace : bool
        Whether to replace the current process.
        Note that this has no effect on Windows.
    sys_exit : bool
        Whether to exit if the shell command returns with error != 0.
    output : bool
        Whether to display output as the process runs.
        If set to ``False``, can be accessed afterwards as
        ``p.stdout``.
        If `sys_exit` is True and the process fails, output is printed
        regardless.
    echo : bool
        Whether or not to echo commands.

    Other arguments and keywords are passed directly to `subprocess.run`.


    Returns
    -------
    p : CompletedProcess
    """
    if cwd:
        if echo:
            click.secho(f"$ cd {cwd}", bold=True, fg="bright_blue")
        os.chdir(cwd)

    cmdstr = " ".join(shlex.quote(arg) for arg in cmd)
    if echo:
        click.secho(f"$ {cmdstr}", bold=True, fg="bright_blue")

    if output is False:
        output_kwargs = {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT}
        kwargs = {**output_kwargs, **kwargs}

    if replace and (sys.platform in ("linux", "darwin")):
        if not shutil.which(cmd[0]):
            click.secho(
                f"`{cmd[0]}` executable not found; exiting.",
                fg="bright_red",
            )
            raise SystemExit(1) from None

        os.execvp(cmd[0], cmd)
        print(f"Failed to launch `{cmd}`; exiting.")
        sys.exit(-1)
    else:
        try:
            p = subprocess.run(cmd, *args, **kwargs)
        except FileNotFoundError:
            click.secho(f"`{cmd[0]}` executable not found. Exiting.", fg="bright_red")
            raise SystemExit(1) from None
        if p.returncode != 0 and sys_exit:
            # Output was suppressed, but the process failed, so print it anyway
            if output is False:
                print(p.stdout.decode("utf-8"), end="")
            raise SystemExit(p.returncode)
        return p


def get_config():
    """Return the pyproject.toml as a dictionary."""
    return click.get_current_context().meta["config"]


def get_commands():
    """Return a list of all commands.

    Returns
    -------
    cmds : dict
       The keys of the dictionary are the section names, the values
       lists of commands.

       If no sections are provided, all commands are listed under the
       ``commands`` key.
    """
    return click.get_current_context().meta["commands"]


Decorator = Callable[[Callable], Callable]


def extend_command(
    cmd: click.Command, doc: str | None = None, remove_args: tuple[str] | None = None
) -> Decorator:
    """This is a decorator factory.

    The resulting decorator lets the user derive their own command from `cmd`.
    The new command can support arguments not supported by `cmd`.

    Parameters
    ----------
    cmd : click.Command
        Command to extend.
    doc : str
        Replacement docstring.
        The decorated function's docstring is also appended.
        This is done so that two modes of documenting are enabled:

        1. Extend original command documentation.
           Do this by providing a docstring on the decorated function.
        2. Replace the original command's documentation.
           Do this either by setting ``doc`` to a docstring, or by
           setting ``doc=''`` and adding a docstring to the decorated function.
    remove_args : tuple of str
        List of arguments to remove from the parent command.
        These arguments can still be set explicitly by calling
        ``parent_callback(..., removed_flag=value)``.

    Examples
    --------

    @click.option("-e", "--extra", help="Extra test flag")
    @util.extend_cmd(
        spin.cmds.meson.build
    )
    @extend_cmd(spin.cmds.meson.build)
    def build(*, parent_callback, extra=None, **kwargs):
        '''
        Some extra documentation related to the constant flag.
        '''
        ...
        parent_callback(**kwargs)
        ...

    """
    my_cmd = copy.copy(cmd)

    # This is necessary to ensure that added options do not leak
    # to the original command
    my_cmd.params = copy.deepcopy(cmd.params)

    def decorator(user_func: Callable) -> click.Command:
        def callback_with_parent_callback(ctx, *args, **kwargs):
            """Wrap the user callback to receive a
            `parent_callback` keyword argument, containing the
            callback from the originally wrapped command."""

            def parent_cmd(*user_args, **user_kwargs):
                ctx.invoke(cmd.callback, *user_args, **user_kwargs)

            return user_func(*args, parent_callback=parent_cmd, **kwargs)

        my_cmd.callback = click.pass_context(callback_with_parent_callback)
        my_cmd.callback._parent = user_func  # type: ignore[attr-defined]

        if doc is not None:
            my_cmd.help = doc
        my_cmd.help = (my_cmd.help or "") + "\n\n" + (user_func.__doc__ or "")
        my_cmd.help = my_cmd.help.strip()

        my_cmd.name = user_func.__name__.replace("_", "-")

        if remove_args:
            my_cmd.params = [
                param for param in my_cmd.params if param.name not in remove_args
            ]

        return my_cmd

    return decorator
