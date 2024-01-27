from pathlib import Path

import pytest

import spin


class TestBuildCmds:
    def test_get_version(self, run_command):
        output = run_command.run_and_assert(["spin", "--version"])
        assert output == f"spin {spin.__version__}"

    def test_basic_build(self, run_command):
        run_command.clean_up()
        output = run_command.run_and_assert(["spin", "build"])

        assert Path(
            run_command.PKG_NAME, "build"
        ).exists(), "`build` folder not created after `spin build`"
        assert Path(
            run_command.PKG_NAME, "build-install"
        ).exists(), "`build-install` folder not created after `spin build`"

    def test_debug_builds(self, run_command):
        run_command.clean_up()
        output = run_command.run_and_assert(["spin", "build", "--gcov"])

        debug_files = Path(run_command.PKG_NAME).rglob("*.gcno")
        assert len(list(debug_files)) != 0, "debug files not generated for gcov build"
