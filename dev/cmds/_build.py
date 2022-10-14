import subprocess
import os

import click

from .util import run


@click.command()
@click.option('--build-dir', default='build', help='Build directory; default is `$PWD/build`')
@click.option('-j', '--jobs', help='Nr of parallel tasks to launch', type=int)
def build(build_dir, jobs=None):
    """🔧 Build package with Meson/ninja"""
    build_dir = os.path.abspath(build_dir)
    build_cmd = ['meson', f'--prefix={build_dir}', 'build']
    if os.path.exists(build_dir):
        build_cmd += ['--reconfigure']
    run(build_cmd)
    run(['ninja', '-C', build_dir])
    run(['meson', f'--prefix={build_dir}', 'install'])
