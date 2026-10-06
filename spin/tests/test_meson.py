import os
import sys
import tempfile
from os.path import join as pjoin
from os.path import normpath

import click
import pytest

from spin.cmds import meson
from spin.containers import DotDict

# Fake meson: prints to stdout and stderr, and fails for subcommands in FAILING_CMDS
FAKE_MESON = """
import sys

FAILING_CMDS = {failing_cmds!r}

subcommand = sys.argv[1]
print("fake meson " + subcommand + ": stdout")
print("fake meson " + subcommand + ": stderr", file=sys.stderr)
sys.exit(1 if subcommand in FAILING_CMDS else 0)
"""


@pytest.fixture
def fake_meson(tmp_path, monkeypatch):
    """Return a factory that installs a fake meson and returns a build dir."""

    def make(failing_cmds=()):
        script = tmp_path / "meson.py"
        script.write_text(FAKE_MESON.format(failing_cmds=list(failing_cmds)))
        # Run the fake script in place of the meson binary
        monkeypatch.setattr(meson, "_meson_cli", lambda: [sys.executable, str(script)])
        monkeypatch.setattr(meson, "get_config", lambda: DotDict({}))
        return str(tmp_path / "build")

    return make


def test_quiet_configuration_failure_output(fake_meson, capfd):
    build_dir = fake_meson(failing_cmds=["setup"])
    with pytest.raises(RuntimeError, match="Meson configuration failed"):
        meson.build.callback(
            meson_args=(), build_dir=build_dir, prefix="/usr", quiet=True
        )
    captured = capfd.readouterr()
    output = captured.out + captured.err
    assert output.count("fake meson setup: stdout") == 1
    assert output.count("fake meson setup: stderr") == 1


def test_run_configuration_failure_output(fake_meson, monkeypatch, capfd):
    build_dir = fake_meson(failing_cmds=["setup"])
    monkeypatch.setattr(meson, "_get_configured_command", lambda name: meson.build)
    with (
        click.Context(meson.run),
        pytest.raises(RuntimeError, match="Meson configuration failed"),
    ):
        meson.run.callback(args=("unused-command",), build=True, build_dir=build_dir)
    captured = capfd.readouterr()
    assert "fake meson setup: stdout" in captured.err
    assert "fake meson setup: stderr" in captured.err
    assert "fake meson setup" not in captured.out


def test_successful_quiet_build_output(fake_meson, capfd):
    build_dir = fake_meson()
    meson.build.callback(meson_args=(), build_dir=build_dir, prefix="/usr", quiet=True)
    captured = capfd.readouterr()
    assert "fake meson" not in captured.out + captured.err


def make_paths(root, paths):
    for p in paths:
        os.makedirs(pjoin(root, p.lstrip("/")))


def test_path_discovery():
    version = sys.version_info
    X, Y = version.major, version.minor

    # With multiple site-packages, choose the one that matches the
    # current Python version
    with tempfile.TemporaryDirectory() as d:
        build_dir = pjoin(d, "./build")
        install_dir = pjoin(d, "./build-install")

        make_paths(
            install_dir,
            [
                f"/usr/lib64/python{X}.{Y}/site-packages",
                f"/usr/lib64/python{X}.{Y + 1}/site-packages",
                f"/usr/lib64/python{X}.{Y + 2}/site-packages",
            ],
        )
        assert normpath(
            f"/usr/lib64/python{X}.{Y}/site-packages"
        ) in meson._get_site_packages(build_dir)

    # Debian uses dist-packages
    with tempfile.TemporaryDirectory() as d:
        build_dir = pjoin(d, "./build")
        install_dir = pjoin(d, "./build-install")

        make_paths(
            install_dir,
            [
                f"/usr/lib64/python{X}.{Y}/dist-packages",
            ],
        )
        assert normpath(
            f"/usr/lib64/python{X}.{Y}/dist-packages"
        ) in meson._get_site_packages(build_dir)

    # If there is no version information in site-packages,
    # use whatever site-packages can be found
    with tempfile.TemporaryDirectory() as d:
        build_dir = pjoin(d, "./build")
        install_dir = pjoin(d, "./build-install")

        make_paths(install_dir, ["/Python3/site-packages"])
        assert normpath("/Python3/site-packages") in meson._get_site_packages(build_dir)

    # Raise if no site-package directory present
    with tempfile.TemporaryDirectory() as d:
        install_dir = pjoin(d, "-install")

        with pytest.raises(FileNotFoundError):
            meson._get_site_packages(build_dir)

    # If there are multiple site-package paths, but without version information,
    # refuse the temptation to guess
    with tempfile.TemporaryDirectory() as d:
        build_dir = pjoin(d, "./build")
        install_dir = pjoin(d, "./build-install")
        make_paths(
            install_dir, ["/Python3/x/site-packages", "/Python3/y/site-packages"]
        )
        with pytest.raises(FileNotFoundError):
            meson._get_site_packages(build_dir)

    # Multiple site-package paths found, but none that matches our Python
    with tempfile.TemporaryDirectory() as d:
        build_dir = pjoin(d, "./build")
        install_dir = pjoin(d, "./build-install")

        make_paths(
            install_dir,
            [
                f"/usr/lib64/python{X}.{Y + 1}/site-packages",
                f"/usr/lib64/python{X}.{Y + 2}/site-packages",
            ],
        )
        with pytest.raises(FileNotFoundError):
            meson._get_site_packages(build_dir)


def test_meson_cli_discovery(monkeypatch):
    config0 = DotDict({"tool": {"spin": {"meson": {"cli": "~/envs/py311/bin/meson"}}}})
    config1 = DotDict(
        {"tool": {"spin": {"meson": {"cli": "~/envs/py311/bin/meson.py"}}}}
    )

    with monkeypatch.context() as m:
        m.setattr(meson, "get_config", lambda: config0)
        assert meson._meson_cli()[0] == os.path.expanduser("~/envs/py311/bin/meson")

        m.setattr(meson, "get_config", lambda: config1)
        assert meson._meson_cli()[0] == sys.executable
