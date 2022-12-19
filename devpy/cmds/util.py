import os
import sys
import subprocess
import shlex
from pathlib import Path

import click


def run(cmd, cwd=None, replace=False, sys_exit=True, output=True, *args, **kwargs):
    if cwd:
        click.secho(f"$ cd {cwd}", bold=True, fg="bright_blue")
        os.chdir(cwd)
    click.secho(f"$ {shlex.join(cmd)}", bold=True, fg="bright_blue")

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
    candidate_paths = []
    for root, dirs, files in os.walk(install_dir(build_dir)):
        for subdir in dirs:
            if subdir == "site-packages":
                candidate_paths.append(os.path.abspath(os.path.join(root, subdir)))

    if len(candidate_paths) == 0:
        return None

    # Prefer paths with current Python version in them
    X, Y = sys.version_info.major, sys.version_info.minor
    candidate_paths = sorted(candidate_paths, key=lambda p: f"python{X}.{Y}" in p)
    candidate_paths = sorted(candidate_paths, key=lambda p: f"python{X}" in p)
    return candidate_paths[-1]


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


def install_dir(build_dir):
    return os.path.join(
        build_dir,
        os.path.abspath(f"{build_dir}/../{os.path.basename(build_dir)}-install"),
    )
