import os
import subprocess
import click
from pathlib import Path


def run(cmd, cwd=None, replace=False, *args, **kwargs):
    env = kwargs.pop('env', os.environ)
    if cwd:
        print(f"$ cd {cwd}")
    print(f"$ {' '.join(cmd)}")
    if replace:
        print(env['PYTHONPATH'])
        os.execvpe(cmd[0], cmd, env=env, *args, **kwargs)
    else:
        subprocess.run(cmd, cwd=cwd, *args, **kwargs)


def get_config():
    return click.get_current_context().meta['config']


def get_site_packages(build_dir):
    for root, dirs, files in os.walk(build_dir):
        for subdir in dirs:
            if subdir == 'site-packages':
                return os.path.abspath(os.path.join(root, subdir))


def set_pythonpath(build_dir):
    site_packages = get_site_packages(build_dir)
    env = os.environ

    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{site_packages}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = site_packages

    return env['PYTHONPATH']
