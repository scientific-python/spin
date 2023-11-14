import copy
import functools
import json
import os
import shutil
import sys

import click

from . import generic
from .util import get_config
from .util import run as _run

install_dir = "build-install"


# Allow specification of meson binary in configuration
# This is necessary for packages like NumPy that vendor meson
def _meson_cli():
    cfg = get_config()
    meson_cli = os.path.expanduser(cfg.get("tool.spin.meson.cli", "meson"))

    # Handle Python runner, mainly for Windows
    if meson_cli.endswith(".py"):
        return [sys.executable, meson_cli]
    else:
        return [meson_cli]


def _set_pythonpath(quiet=False):
    """Set first entry of PYTHONPATH to site packages directory.

    Returns
    -------
    site_packages
    """
    site_packages = _get_site_packages()
    env = os.environ

    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{site_packages}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = site_packages

    if not quiet:
        click.secho(
            f'$ export PYTHONPATH="{env["PYTHONPATH"]}"', bold=True, fg="bright_blue"
        )

    return site_packages


def _get_site_packages():
    candidate_paths = []
    for root, dirs, _files in os.walk(install_dir):
        for subdir in dirs:
            if subdir == "site-packages" or subdir == "dist-packages":
                candidate_paths.append(os.path.abspath(os.path.join(root, subdir)))

    X, Y = sys.version_info.major, sys.version_info.minor

    site_packages = None
    if any(f"python{X}." in p for p in candidate_paths):
        # We have a system that uses `python3.X/site-packages` or `python3.X/dist-packages`
        site_packages = [p for p in candidate_paths if f"python{X}.{Y}" in p]
        if len(site_packages) == 0:
            raise FileNotFoundError(
                f"No site-packages found in {install_dir} for Python {X}.{Y}"
            )
        else:
            site_packages = site_packages[0]
    else:
        # A naming scheme that does not encode the Python major/minor version is used, so return
        # whatever site-packages path was found
        if len(candidate_paths) > 1:
            raise FileNotFoundError(
                f"Multiple `site-packages` found in `{install_dir}`, but cannot use Python version to disambiguate"
            )
        elif len(candidate_paths) == 1:
            site_packages = candidate_paths[0]

    if site_packages is None:
        raise FileNotFoundError(
            f"No `site-packages` or `dist-packages` found under `{install_dir}`"
        )

    return site_packages


def _meson_version():
    try:
        p = _run(_meson_cli() + ["--version"], output=False, echo=False)
        return p.stdout.decode("ascii").strip()
    except:
        pass


def _meson_version_configured():
    try:
        meson_info_fn = os.path.join("build", "meson-info", "meson-info.json")
        with open(meson_info_fn) as f:
            meson_info = json.load(f)
        return meson_info["meson_version"]["full"]
    except:
        pass


@click.command()
@click.option("-j", "--jobs", help="Number of parallel tasks to launch", type=int)
@click.option("--clean", is_flag=True, help="Clean build directory before build")
@click.option(
    "-v", "--verbose", is_flag=True, help="Print detailed build and installation output"
)
@click.argument("meson_args", nargs=-1)
def build(meson_args, jobs=None, clean=False, verbose=False, quiet=False):
    """🔧 Build package with Meson/ninja and install

    MESON_ARGS are passed through e.g.:

      spin build -- -Dpkg_config_path=/lib64/pkgconfig

    The package is installed to build-install

    By default meson-python does release builds. To be able to use a debugger,
    tell meson to build in debug mode:

      spin build -- -Dbuildtype=debug

    or set CFLAGS appropriately:

      CFLAGS="-O0 -g" spin build
    """
    build_dir = "build"
    setup_cmd = _meson_cli() + ["setup", build_dir, "--prefix=/usr"] + list(meson_args)

    if clean:
        print(f"Removing `{build_dir}`")
        if os.path.isdir(build_dir):
            shutil.rmtree(build_dir)
        print(f"Removing `{install_dir}`")
        if os.path.isdir(install_dir):
            shutil.rmtree(install_dir)

    if not (os.path.exists(build_dir) and _meson_version_configured()):
        p = _run(setup_cmd, sys_exit=False, output=not quiet)
        if p.returncode != 0:
            raise RuntimeError(
                "Meson configuration failed; please try `spin build` again with the `--clean` flag."
            )
    else:
        # Build dir has been configured; check if it was configured by
        # current version of Meson

        if _meson_version() != _meson_version_configured():
            _run(setup_cmd + ["--reconfigure"], output=not quiet)

        # Any other conditions that warrant a reconfigure?

    compile_flags = ["-v"] if verbose else []
    p = _run(
        _meson_cli() + ["compile"] + compile_flags + ["-C", build_dir],
        sys_exit=True,
        output=not quiet,
    )
    p = _run(
        _meson_cli()
        + [
            "install",
            "--only-changed",
            "-C",
            build_dir,
            "--destdir",
            f"../{install_dir}",
        ],
        output=(not quiet) and verbose,
    )


def _meson_path_setter(func):
    @functools.wraps(func)
    def with_meson_path_setter(*args, **kwargs):
        kwargs["_path_setter"] = _set_pythonpath
        func(*args, **kwargs)

    return with_meson_path_setter


generic_funcs = ("test", "ipython", "python", "shell", "run", "docs", "gdb", "lldb")
for func_name in generic_funcs:
    func = copy.copy(getattr(generic, func_name))
    # In Click, the callback is the actual function being executed when the
    # command is invoked. We added a `_path_setter` attribute to
    # function definitions in `generic`.
    callback = func.callback
    # Replace the callback, but set the default for kwarg `_path_setter`
    # to the Meson `_set_pythonpath`
    func.callback = _meson_path_setter(callback)
    globals()[func_name] = func
