import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

import spin as libspin
from spin.cmds.util import run

skip_on_windows = pytest.mark.skipif(
    sys.platform.startswith("win"), reason="Skipped on Windows"
)


def spin(*args):
    return run(
        ["spin"] + list(args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        sys_exit=False,
    )


def stdout(p):
    return p.stdout.decode("utf-8").strip()


def stderr(p):
    return p.stderr.decode("utf-8").strip()


def test_get_version():
    p = spin("--version")
    assert stdout(p) == f"spin {libspin.__version__}"


def test_basic_build():
    """Does the package build?"""
    spin("build")

    assert Path("build").exists(), "`build` folder not created after `spin build`"
    assert Path(
        "build-install"
    ).exists(), "`build-install` folder not created after `spin build`"


def test_debug_builds():
    """Does spin generate gcov debug output files?"""
    spin("build", "--gcov")

    debug_files = Path(".").rglob("*.gcno")
    assert len(list(debug_files)) != 0, "debug files not generated for gcov build"


def test_expand_pythonpath():
    """Does an $ENV_VAR get expanded in `spin run`?"""
    output = spin("run", "echo $PYTHONPATH")
    assert any(
        p in stdout(output) for p in ("site-packages", "dist-packages")
    ), f"Expected value of $PYTHONPATH, got {stdout(output)} instead"


def test_run_stdout():
    """Ensure `spin run` only includes command output on stdout."""
    p = spin(
        "run",
        "python",
        "-c",
        "import sys; del sys.path[0]; import example_pkg; print(example_pkg.__version__)",
    )
    assert (
        stdout(p) == "0.0.0dev0"
    ), f"`spin run` stdout did not yield version, but {stdout(p)}"


def test_editable_conflict():
    """Do we warn when a conflicting editable install is present?"""
    try:
        run(["pip", "install", "--quiet", "-e", "."])
        assert "Warning! An editable installation" in stdout(
            spin("run", "ls")
        ), "Failed to detect and warn about editable install"
    finally:
        run(["pip", "uninstall", "--quiet", "-y", "example_pkg"])


# Detecting whether a file is executable is not that easy on Windows,
# as it seems to take into consideration whether that file is associated as an executable.
@skip_on_windows
def test_recommend_run_python():
    """If `spin run file.py` is called, is `spin run python file.py` recommended?"""
    with tempfile.NamedTemporaryFile(suffix=".py") as f:
        p = spin("run", f.name)
        assert "Did you mean to call" in stdout(
            p
        ), "Failed to recommend `python run python file.py`"
