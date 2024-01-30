from pathlib import Path

from util import PKG_NAME, assert_cmd

import spin


def test_get_version():
    output = assert_cmd(["spin", "--version"])
    assert output == f"spin {spin.__version__}"


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
