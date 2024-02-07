from pathlib import Path

from util import PKG_NAME, assert_cmd

import spin


def stdout(p):
    return p.stdout.decode("utf-8")


def test_get_version():
    p = assert_cmd(["spin", "--version"])
    assert stdout(p) == f"spin {spin.__version__}"


def test_basic_build():
    assert_cmd(["spin", "build"])

    assert Path(
        PKG_NAME, "build"
    ).exists(), "`build` folder not created after `spin build`"
    assert Path(
        PKG_NAME, "build-install"
    ).exists(), "`build-install` folder not created after `spin build`"


def test_debug_builds():
    assert_cmd(["spin", "build", "--gcov"])

    debug_files = Path(PKG_NAME).rglob("*.gcno")
    assert len(list(debug_files)) != 0, "debug files not generated for gcov build"


def test_expand_pythonpath():
    output = assert_cmd(["spin", "run", "echo $PYTHONPATH"])
    assert "build-install" in stdout(
        output
    ), f"Expected value of $PYTHONPATH, got {output} instead"
