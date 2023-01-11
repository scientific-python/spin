import tempfile
import sys
import os
from os.path import join as pjoin

import pytest

from devpy import util


def make_paths(root, paths):
    for p in paths:
        os.makedirs(pjoin(root, p.lstrip("/")))


def test_path_discovery():
    version = sys.version_info
    X, Y = version.major, version.minor

    # With multiple site-packages, choose the one that
    # matches the current Python version
    with tempfile.TemporaryDirectory() as d:
        build_dir = pjoin(d, "build")
        install_dir = pjoin(d, "build-install")
        make_paths(
            install_dir,
            [
                f"/usr/lib64/python{X}.{Y}/site-packages",
                f"/usr/lib64/python{X}.{Y + 1}/site-packages",
                f"/usr/lib64/python{X}.{Y + 2}/site-packages",
            ],
        )
        assert f"/usr/lib64/python{X}.{Y}/site-packages" in util.get_site_packages(
            build_dir
        )

    # Debian uses dist-packages
    with tempfile.TemporaryDirectory() as d:
        build_dir = pjoin(d, "build")
        install_dir = pjoin(d, "build-install")
        make_paths(
            install_dir,
            [
                f"/usr/lib64/python{X}.{Y}/dist-packages",
            ],
        )
        assert f"/usr/lib64/python{X}.{Y}/dist-packages" in util.get_site_packages(
            build_dir
        )

    # If there is no version information in site-packages,
    # use whatever site-packages can be found
    with tempfile.TemporaryDirectory() as d:
        build_dir = pjoin(d, "build")
        install_dir = pjoin(d, "build-install")
        make_paths(install_dir, ["/Python3/site-packages"])
        assert "/Python3/site-packages" in util.get_site_packages(build_dir)

    # Raise if no site-package directory present
    with tempfile.TemporaryDirectory() as d:
        build_dir = pjoin(d, "build")
        with pytest.raises(FileNotFoundError):
            util.get_site_packages(build_dir)

    # If there are multiple site-package paths, but without version information,
    # refuse the temptation to guess
    with tempfile.TemporaryDirectory() as d:
        build_dir = pjoin(d, "build")
        install_dir = pjoin(d, "build-install")
        make_paths(
            install_dir, [f"/Python3/x/site-packages", f"/Python3/y/site-packages"]
        )
        with pytest.raises(FileNotFoundError):
            util.get_site_packages(build_dir)

    # Multiple site-package paths found, but none that matches our Python
    with tempfile.TemporaryDirectory() as d:
        build_dir = pjoin(d, "build")
        install_dir = pjoin(d, "build-install")
        make_paths(
            install_dir,
            [
                f"/usr/lib64/python{X}.{Y + 1}/site-packages",
                f"/usr/lib64/python{X}.{Y + 2}/site-packages",
            ],
        )
        with pytest.raises(FileNotFoundError):
            util.get_site_packages(build_dir)
