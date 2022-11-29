import sys
import os

import click

from . import util


@click.command()
@click.option(
    "--build-dir", default="build", help="Build directory; default is `$PWD/build`"
)
@click.option(
    "--clean", is_flag=True, help="Clean previously built docs before building"
)
@click.argument("targets", required=False, nargs=-1)
def doc(build_dir, targets, clean=False):
    """📖 Build documentation

    Set the PYTHONPATH to the build path, and invoke `make` in the
    `doc` directory.

    For a list of Sphinx make targets:

      ./dev.py doc help
    """
    if not targets:
        targets = ["html"]
    if clean:
        doc_dir = "./doc/build"
        if os.path.isdir(doc_dir):
            print(f"Removing `{doc_dir}`")
            shutil.rmtree(doc_dir)

    util.set_pythonpath(build_dir)

    print("$ export SPHINXOPTS='-W'")
    os.environ["SPHINXOPTS"] = "-W"
    util.run(["make", "-C", "doc"] + list(targets), replace=True)
