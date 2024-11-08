import os

import pytest

from spin import util


def dir_switcher(path):
    # Pre-test code
    cwd = os.getcwd()
    os.chdir(path)

    try:
        yield
    finally:
        # Post test code
        os.chdir(cwd)
        util.run(["git", "clean", "-xdf"], cwd=path)
        os.chdir(cwd)


@pytest.fixture()
def example_pkg():
    yield from dir_switcher("example_pkg")


@pytest.fixture()
def example_pkg_src_layout():
    yield from dir_switcher("example_pkg_src")


@pytest.fixture
def editable_install():
    util.run(["pip", "install", "--quiet", "--no-build-isolation", "-e", "."])
    yield
    util.run(["pip", "uninstall", "--quiet", "-y", "example_pkg"])
