import os
import subprocess

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
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs,
    )
    os.chdir(cwd)
    stdout = p.stdout.decode("utf-8").strip()
    if not p.returncode == 0:
        print(stdout)
        raise AssertionError(f"[{cmd}] failed with exit code {p.returncode}")
    return p
