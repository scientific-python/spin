from __future__ import (
    annotations,  # noqa: F401  # TODO: remove once only >3.8 is supported
)

import os
import shlex
import subprocess
import sys

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
        os.execvp(cmd[0], cmd)
        print(f"Failed to launch `{cmd}`")
        sys.exit(-1)
    else:
        p = subprocess.run(cmd, *args, **kwargs)
        if p.returncode != 0 and sys_exit:
            # Output was suppressed, but the process failed, so print it anyway
            if output is False:
                print(p.stdout.decode("utf-8"), end="")
            sys.exit(p.returncode)
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
