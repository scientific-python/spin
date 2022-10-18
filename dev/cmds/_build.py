import os
import sys
import shutil
import click
from .util import run


@click.command()
@click.option(
    "--build-dir", default="build", help="Build directory; default is `$PWD/build`"
)
@click.option("-j", "--jobs", help="Nr of parallel tasks to launch", type=int)
def build(build_dir, jobs=None):
    """🔧 Build package with Meson/ninja"""
    build_dir = os.path.abspath(build_dir)
    build_cmd = ["meson", f"--prefix={build_dir}", "build"]
    flags = []

    if os.path.exists(build_dir):
        flags += ["--reconfigure"]
    p = run(build_cmd + flags, capture_output=True)
    print(p.stderr.decode("utf-8"))
    if b"does not contain a valid build tree" in p.stderr:
        if not click.confirm(
            f"Invalid build tree.\nOK to remove `{build_dir}` and try again?"
        ):
            sys.exit(-1)
        shutil.rmtree(build_dir)
        p = run(build_cmd)
    if not p.returncode == 0:
        print("Could not build Meson project")
        sys.exit(-1)
    run(["ninja", "-C", build_dir])
    run(["meson", "install", f"-C", build_dir])
