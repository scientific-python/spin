import os
import sys
import click
from .util import run


@click.command()
@click.option(
    "-t",
    "--list-targets",
    default=False,
    is_flag=True,
    help="List doc targets",
)
@click.option(
    "-j",
    "--parallel",
    help="Number of parallel jobs",
    type=int,
    default=1,
)
@click.argument("args", nargs=-1)
def doc(list_targets, parallel, args):
    """🔧 Build documentation

    PYTHON is set as sys.executable and number of jobs are passed as SPHINXOPTS

    To set PYTHONPATH, use:

    PYTHONPATH="/usr/lib/python3/dist-packages/" ./dev.py build
    """

    if list_targets:  # list MAKE targets, remove default target
        targets = ""
    else:
        targets = " ".join(args) if args else "html"

    make_params = [f'PYTHON="{sys.executable}"']
    if parallel:
        make_params.append(f'SPHINXOPTS="-j{parallel}"')

    os.chdir("doc")
    run(["make", *make_params, targets])
