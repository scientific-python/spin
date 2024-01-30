import os

from spin.cmds import util

PKG_NAME = "example_pkg"


def assert_cmd(cmd, *args, **kwargs) -> str:
    cwd = os.getcwd()
    p = util.run(
        cmd,
        *args,
        cwd=PKG_NAME,
        replace=False,
        sys_exit=False,
        output=False,
        echo=True,
        **kwargs,
    )
    assert (
        p.returncode == 0
    ), f"{cmd} failed with non-zero exit status with error: {p.stderr}"
    os.chdir(cwd)
    return p.stdout.decode("utf-8").strip()
