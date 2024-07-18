import subprocess
import sys

import pytest

from spin.cmds.util import run

skip_on_windows = pytest.mark.skipif(
    sys.platform.startswith("win"), reason="Skipped; platform is Windows"
)

skip_unless_linux = pytest.mark.skipif(
    not sys.platform.startswith("linux"), reason="Skipped; platform not Linux"
)

skip_unless_macos = pytest.mark.skipif(
    not sys.platform.startswith("darwin"), reason="Skipped; platform not macOS"
)

skip_py38 = pytest.mark.skipif(
    sys.version_info[:2] == (3, 8), reason="Skipped; Python 3.8"
)


def spin(*args, **user_kwargs):
    args = (str(el) for el in args)
    default_kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "sys_exit": True,
    }
    return run(["spin"] + list(args), **{**default_kwargs, **user_kwargs})


def stdout(p):
    return p.stdout.decode("utf-8").strip()


def stderr(p):
    return p.stderr.decode("utf-8").strip()
