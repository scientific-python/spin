import os
import sys
import click

from .util import run, get_config, get_commands, set_pythonpath, get_site_packages


@click.command()
@click.argument("pytest_args", nargs=-1)
@click.pass_context
def test(ctx, pytest_args):
    """🔧 Run tests

    PYTEST_ARGS are passed through directly to pytest, e.g.:

    ./dev.py test -- -v

    By default, runs the full test suite. To skip "slow" tests, run

    ./dev.py test -- -m "not slow"
    """
    cfg = get_config()

    command_groups = get_commands()
    commands = [cmd for section in command_groups for cmd in command_groups[section]]
    build_cmd = next((cmd for cmd in commands if cmd.name == "build"), None)
    if build_cmd:
        click.secho(
            f"Invoking `build` prior to running tests:", bold=True, fg="bright_green"
        )
        ctx.invoke(build_cmd)

    if not pytest_args:
        pytest_args = (cfg.get("tool.devpy.package", None),)
        if pytest_args == (None,):
            print(
                "Please specify `package = packagename` under `tool.devpy` section of `pyproject.toml`"
            )
            sys.exit(1)

    site_path = get_site_packages()
    set_pythonpath()

    print(f'$ export PYTHONPATH="{site_path}"')
    run(
        [sys.executable, "-m", "pytest", f"--rootdir={site_path}"] + list(pytest_args),
        cwd=site_path,
    )
