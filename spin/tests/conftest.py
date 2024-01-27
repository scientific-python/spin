import os
from pathlib import Path

import pytest

from spin.cmds import util

PKG_NAME = "example_pkg"


class RunCommand:
    PKG_NAME = PKG_NAME

    @staticmethod
    def run_and_assert(cmd, *args, **kwargs) -> str:
        cwd = Path.cwd()
        p = util.run(
            cmd,
            cwd=PKG_NAME,
            replace=False,
            sys_exit=False,
            output=False,
            echo=True,
            *args,
            **kwargs,
        )
        os.chdir(cwd)
        assert (
            p.returncode == 0
        ), f"{cmd} failed with non-zero exit status with error: {p.stderr}"
        return p.stdout.decode("utf-8").strip()

    @staticmethod
    def clean_up():
        cwd = os.getcwd()
        clean_up = util.run(["git", "clean", "-xdf"], cwd=PKG_NAME)
        os.chdir(cwd)


@pytest.fixture
def run_command():
    return RunCommand
