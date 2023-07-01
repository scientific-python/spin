import os
import sys
import tempfile
from os.path import join as pjoin
from os.path import normpath

import pytest

from spin.cmds import meson


def make_paths(root, paths):
    for p in paths:
        os.makedirs(pjoin(root, p.lstrip("/")))


def test_path_discovery(monkeypatch):
    version = sys.version_info
    X, Y = version.major, version.minor

    # With multiple site-packages, choose the one that
    # matches the current Python version
    with tempfile.TemporaryDirectory() as d:
        with monkeypatch.context() as m:
            install_dir = pjoin(d, "build-install")
            m.setattr(meson, "install_dir", install_dir)

            make_paths(
                install_dir,
                [
                    f"/usr/lib64/python{X}.{Y}/site-packages",
                    f"/usr/lib64/python{X}.{Y + 1}/site-packages",
                    f"/usr/lib64/python{X}.{Y + 2}/site-packages",
                ],
            )
            assert (
                normpath(f"/usr/lib64/python{X}.{Y}/site-packages")
                in meson._get_site_packages()
            )

    # Debian uses dist-packages
    with tempfile.TemporaryDirectory() as d:
        with monkeypatch.context() as m:
            install_dir = pjoin(d, "build-install")
            m.setattr(meson, "install_dir", install_dir)

            make_paths(
                install_dir,
                [
                    f"/usr/lib64/python{X}.{Y}/dist-packages",
                ],
            )
            assert (
                normpath(f"/usr/lib64/python{X}.{Y}/dist-packages")
                in meson._get_site_packages()
            )

    # If there is no version information in site-packages,
    # use whatever site-packages can be found
    with tempfile.TemporaryDirectory() as d:
        with monkeypatch.context() as m:
            install_dir = pjoin(d, "build-install")
            m.setattr(meson, "install_dir", install_dir)

            make_paths(install_dir, ["/Python3/site-packages"])
            assert normpath("/Python3/site-packages") in meson._get_site_packages()

    # Raise if no site-package directory present
    with tempfile.TemporaryDirectory() as d:
        with monkeypatch.context() as m:
            install_dir = pjoin(d, "build-install")
            m.setattr(meson, "install_dir", install_dir)

            with pytest.raises(FileNotFoundError):
                meson._get_site_packages()

    # If there are multiple site-package paths, but without version information,
    # refuse the temptation to guess
    with tempfile.TemporaryDirectory() as d:
        install_dir = pjoin(d, "build-install")
        make_paths(
            install_dir, ["/Python3/x/site-packages", "/Python3/y/site-packages"]
        )
        with pytest.raises(FileNotFoundError):
            meson._get_site_packages()

    # Multiple site-package paths found, but none that matches our Python
    with tempfile.TemporaryDirectory() as d:
        with monkeypatch.context() as m:
            install_dir = pjoin(d, "build-install")
            m.setattr(meson, "install_dir", install_dir)

            make_paths(
                install_dir,
                [
                    f"/usr/lib64/python{X}.{Y + 1}/site-packages",
                    f"/usr/lib64/python{X}.{Y + 2}/site-packages",
                ],
            )
            with pytest.raises(FileNotFoundError):
                meson._get_site_packages()
