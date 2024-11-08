from testutil import spin, stdout

import spin as libspin


def test_get_version(example_pkg):
    p = spin("--version")
    assert stdout(p) == f"spin {libspin.__version__}"


def test_arg_override(example_pkg):
    p = spin("example")
    assert "--test is: default override" in stdout(p)
    assert "Default kwd is: 3" in stdout(p)

    p = spin("example", "-t", 6)
    assert "--test is: 6" in stdout(p)
