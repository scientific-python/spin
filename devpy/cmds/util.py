import os
import sys
import subprocess
import shlex
import sysconfig
from pathlib import Path

import click


install_dir = "build-install"


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


def get_site_packages():
    candidate_paths = []
    for root, dirs, files in os.walk(install_dir):
        for subdir in dirs:
            if subdir == "site-packages" or subdir == "dist-packages":
                candidate_paths.append(os.path.abspath(os.path.join(root, subdir)))

    X, Y = sys.version_info.major, sys.version_info.minor

    site_packages = None
    if any(f"python{X}." in p for p in candidate_paths):
        # We have a system that uses `python3.X/site-packages` or `python3.X/dist-packages`
        site_packages = [p for p in candidate_paths if f"python{X}.{Y}" in p]
        if len(site_packages) == 0:
            raise FileNotFoundError(
                f"No site-packages found in {install_dir} for Python {X}.{Y}"
            )
        else:
            site_packages = site_packages[0]
    else:
        # A naming scheme that does not encode the Python major/minor version is used, so return
        # whatever site-packages path was found
        if len(candidate_paths) > 1:
            raise FileNotFoundError(
                f"Multiple `site-packages` found in `{install_dir}`, but cannot use Python version to disambiguate"
            )
        elif len(candidate_paths) == 1:
            site_packages = candidate_paths[0]

    if site_packages is None:
        raise FileNotFoundError(
            f"No `site-packages` or `dist-packages` found under `{install_dir}`"
        )

    return site_packages


def set_pythonpath():
    site_packages = get_site_packages()
    env = os.environ

    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{site_packages}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = site_packages

    return env["PYTHONPATH"]
