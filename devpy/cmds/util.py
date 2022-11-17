import os
import sys
import subprocess
import shlex
from pathlib import Path

import click


def run(cmd, cwd=None, replace=False, sys_exit=True, output=True, *args, **kwargs):
    if cwd:
        print(f"$ cd {cwd}", flush=True)
        os.chdir(cwd)
    print(f"$ {shlex.join(cmd)}", flush=True)

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


def get_site_packages(build_dir):
    for root, dirs, files in os.walk(build_dir):
        for subdir in dirs:
            if subdir == "site-packages":
                return os.path.abspath(os.path.join(root, subdir))


def set_pythonpath(build_dir):
    site_packages = get_site_packages(build_dir)
    if site_packages is None:
        print(f"No `site-packages` directory found under {build_dir}; aborting")
        sys.exit(1)

    env = os.environ

    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{site_packages}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = site_packages

    return env["PYTHONPATH"]
