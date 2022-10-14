import os
import subprocess
import click
from pathlib import Path


def run(cmd, cwd=None, *args, **kwargs):
    if cwd:
        print(f"$ cd {cwd}")
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, *args, **kwargs)


def get_config():
    return click.get_current_context().meta['config']


def get_site_packages(build_dir):
    for root, dirs, files in os.walk(build_dir):
        for subdir in dirs:
            if subdir == 'site-packages':
                return os.path.abspath(os.path.join(root, subdir))
