import os
import click

from .util import run, get_config, get_site_packages


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
        pytest_args = (cfg['tool.dev.py.package'],)

    p = get_site_packages(build_dir)

    env = os.environ
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{p}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = p

    print(f"$ export PYTHONPATH=\"{env['PYTHONPATH']}\"")
    run(["pytest", f"--rootdir={p}"] + list(pytest_args), cwd=p, env=env)
