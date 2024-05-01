import pytest
from testutil import spin, stdout

from spin.cmds.util import run


@pytest.fixture
def editable_install():
    run(["pip", "install", "--quiet", "--no-build-isolation", "-e", "."])
    yield
    run(["pip", "uninstall", "--quiet", "-y", "example_pkg"])


def test_detect_editable(editable_install):
    assert "Editable install of same source detected" in stdout(
        spin("build")
    ), "Failed to detect and warn about editable install"


def test_editable_tests(editable_install):
    spin("test")
