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

    p = run(build_cmd + flags, sys_exit=False)
    if p.returncode != 0 and "--reconfigure" in flags:
        click.confirm(
            f"\nMeson failed; perhaps due to an invalid build tree. OK to remove `{build_dir}` and try again?",
            abort=True,
        )
        shutil.rmtree(build_dir)
        run(build_cmd)

    run(["ninja", "-C", build_dir])
    run(["meson", "install", f"-C", build_dir], output=False)
