import os
import sys
import subprocess
import shlex
import sysconfig
from pathlib import Path

import click


def run(cmd, cwd=None, replace=False, sys_exit=True, output=True, *args, **kwargs):
    if cwd:
        click.secho(f"$ cd {cwd}", bold=True, fg="bright_blue")
        os.chdir(cwd)
    cmdstr = " ".join(shlex.quote(arg) for arg in cmd)
    click.secho(f"$ {cmdstr}", bold=True, fg="bright_blue")

    if output is False:
        output_kwargs = {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT}
        kwargs = {**output_kwargs, **kwargs}

    if replace:
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
    return click.get_current_context().meta["config"]


def get_commands():
    return click.get_current_context().meta["commands"]
