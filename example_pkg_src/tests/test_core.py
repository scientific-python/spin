from example_pkg import echo  # type: ignore[attr-defined]


def test_core():
    ans = echo("hello world")
    assert ans == 42
