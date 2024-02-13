import os

import pytest

from spin import util


@pytest.fixture(autouse=True)
def pre_post_test():
    # Pre-test code
    cwd = os.getcwd()
    os.chdir("example_pkg")

    try:
        yield
    finally:
        # Post test code
        os.chdir(cwd)
        util.run(["git", "clean", "-xdf"], cwd="example_pkg")
        os.chdir(cwd)
