import os
import sys
import click

from .util import run, get_config, set_pythonpath, get_site_packages


@click.command()
@click.option(
    "--build-dir", default="build", help="Build directory; default is `$PWD/build`"
)
@click.option(
    "--site-path", help="For devpy testing only; installed package path", hidden=True
)
@click.argument("pytest_args", nargs=-1)
def test(build_dir, site_path, pytest_args):
    """🔧 Run tests

    PYTEST_ARGS are passed through directly to pytest, e.g.:

    ./dev.py test -- -v
    """
    cfg = get_config()

    if not pytest_args:
        pytest_args = (cfg.get("tool.devpy.package", None),)
        if pytest_args == (None,):
            print(
                "Please specify `package = packagename` under `tool.devpy` section of `pyproject.toml`"
            )
            sys.exit(1)

    if not site_path:
        site_path = get_site_packages(build_dir)
        set_pythonpath(build_dir)

    print(f'$ export PYTHONPATH="{site_path}"')
    run(["pytest", f"--rootdir={site_path}"] + list(pytest_args), cwd=site_path)
