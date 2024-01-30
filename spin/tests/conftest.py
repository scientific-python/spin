import os

import pytest
from util import PKG_NAME

from spin import util


@pytest.fixture(autouse=True)
def pre_post_test():
    # Pre-test code
    cwd = os.getcwd()

    yield

    # Post test code
    util.run(["git", "clean", "-xdf"], cwd=PKG_NAME)
    os.chdir(cwd)
