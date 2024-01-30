import os

import pytest
from util import PKG_NAME

from spin import util


@pytest.fixture(autouse=True)
def pre_post_test():
    # Pre-test code

    yield

    # Post test code
    cwd = os.getcwd()
    util.run(["git", "clean", "-xdf"], cwd=PKG_NAME)
    os.chdir(cwd)
