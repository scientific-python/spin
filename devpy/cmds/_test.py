import os
import sys
import click

from .util import run, get_config, set_pythonpath, get_site_packages


@click.command()
@click.option(
    "--build-dir", default="build", help="Build directory; default is `$PWD/build`"
)
@click.argument("pytest_args", nargs=-1)
def test(build_dir, pytest_args):
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

    site_path = get_site_packages(build_dir)
    set_pythonpath(build_dir)

    print(f'$ export PYTHONPATH="{site_path}"')
    run(
        ["python", "-m", "pytest", f"--rootdir={site_path}"] + list(pytest_args),
        cwd=site_path,
    )
