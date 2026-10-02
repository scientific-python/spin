import os
import sys
import tempfile
from os.path import join as pjoin
from os.path import normpath

import click
import pytest

from spin.cmds import meson
from spin.containers import DotDict


@pytest.fixture
def failing_meson(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONIOENCODING", "utf-8")
    script = tmp_path / "meson.py"
    script.write_text(
        "import sys\n"
        "print('Meson setup: configuration error – wrong Cython version')\n"
        "print('Diagnostic from stderr', file=sys.stderr)\n"
        "sys.exit(1)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(meson, "_meson_cli", lambda: [sys.executable, str(script)])
    monkeypatch.setattr(meson, "get_config", lambda: DotDict({}))
    return str(tmp_path / "build")


@pytest.mark.parametrize("quiet", [False, True])
def test_configuration_failure_output(failing_meson, capfd, quiet):
    with pytest.raises(RuntimeError, match="Meson configuration failed"):
        meson.build.callback(
            meson_args=(), build_dir=failing_meson, prefix="/usr", quiet=quiet
        )
    captured = capfd.readouterr()
    output = captured.out + captured.err
    assert output.count("Meson setup: configuration error – wrong Cython version") == 1
    assert output.count("Diagnostic from stderr") == 1


def test_run_configuration_failure_output(failing_meson, monkeypatch, capfd):
    monkeypatch.setattr(meson, "_get_configured_command", lambda name: meson.build)
    with (
        click.Context(meson.run),
        pytest.raises(RuntimeError, match="Meson configuration failed"),
    ):
        meson.run.callback(
            args=("unused-command",), build=True, build_dir=failing_meson
        )
    captured = capfd.readouterr()
    assert "configuration error – wrong Cython version" in captured.err
    assert "Diagnostic from stderr" in captured.err
    assert "configuration error" not in captured.out


def test_successful_quiet_build_output(failing_meson, capfd):
    script = os.path.join(os.path.dirname(failing_meson), "meson.py")
    with open(script, "w", encoding="utf-8") as file:
        file.write("print('Successful build output')\n")
    meson.build.callback(
        meson_args=(), build_dir=failing_meson, prefix="/usr", quiet=True
    )
    captured = capfd.readouterr()
    assert "Successful build output" not in captured.out + captured.err


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
