from example_pkg import echo


def test_core():
    ans = echo("hello world")
    assert ans == 42
