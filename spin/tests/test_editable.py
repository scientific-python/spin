from testutil import spin, stdout


def test_detect_editable(editable_install):
    assert "Editable install of same source detected" in stdout(
        spin("build")
    ), "Failed to detect and warn about editable install"


def test_editable_tests(editable_install):
    spin("test")
