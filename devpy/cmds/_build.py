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
@click.argument("meson_args", nargs=-1)
def build(build_dir, meson_args, jobs=None):
    """🔧 Build package with Meson/ninja

    MESON_ARGS are passed through directly to pytest, e.g.:

    ./dev.py build -- -Dpkg_config_path=/lib64/pkgconfig

    """
    build_dir = os.path.abspath(build_dir)
    build_cmd = ["meson", f"--prefix={build_dir}", "build"] + list(meson_args)
    flags = []

    if os.path.exists(build_dir):
        flags += ["--reconfigure"]
    p = run(build_cmd + flags, capture_output=True)
    if p.stderr:
        print(p.stderr.decode("utf-8"))
    if p.stdout:
        print(p.stdout.decode("utf-8"))
    if b"does not contain a valid build tree" in p.stderr:
        click.confirm(
            f"Invalid build tree.\nOK to remove `{build_dir}` and try again?",
            abort=True,
        )
        shutil.rmtree(build_dir)
        p = run(build_cmd)
    if not p.returncode == 0:
        print("Could not build Meson project")
        sys.exit(-1)
    run(["ninja", "-C", build_dir])
    run(["meson", "install", f"-C", build_dir])
