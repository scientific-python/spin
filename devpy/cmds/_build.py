import os
import sys
import shutil
import click
from .util import run, install_dir


@click.command()
@click.option(
    "--build-dir", default="build", help="Build directory; default is `$PWD/build`"
)
@click.option("-j", "--jobs", help="Number of parallel tasks to launch", type=int)
@click.option("--clean", is_flag=True, help="Clean build directory before build")
@click.option(
    "-v", "--verbose", is_flag=True, help="Print all build output, even installation"
)
@click.argument("meson_args", nargs=-1)
def build(build_dir, meson_args, jobs=None, clean=False, verbose=False):
    """🔧 Build package with Meson/ninja and install

    MESON_ARGS are passed through e.g.:

    ./dev.py build -- -Dpkg_config_path=/lib64/pkgconfig

    The package is installed to BUILD_DIR-install

    By default builds for release, to be able to use a debugger set CFLAGS
    appropriately. For example, for linux use

    CFLAGS="-O0 -g" ./dev.py build
    """
    build_dir = os.path.abspath(build_dir)
    inst_dir = install_dir(build_dir)
    build_cmd = ["meson", "setup", build_dir, "--prefix=/usr"] + list(meson_args)
    flags = []

    if clean:
        print(f"Removing `{build_dir}`")
        if os.path.isdir(build_dir):
            shutil.rmtree(build_dir)
        print(f"Removing `{inst_dir}`")
        if os.path.isdir(inst_dir):
            shutil.rmtree(inst_dir)

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
    run(
        [
            "meson",
            "install",
            "--only-changed",
            "-C",
            build_dir,
            "--destdir",
            install_dir(build_dir),
        ],
        output=verbose,
    )
