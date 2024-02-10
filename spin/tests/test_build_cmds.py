import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

import spin as libspin
from spin.cmds.util import run

skip_on_windows = pytest.mark.skipif(
    sys.platform.startswith("win"), reason="Skipped; platform is Windows"
)

on_linux = pytest.mark.skipif(
    not sys.platform.startswith("linux"), reason="Skipped; platform not Linux"
)


def spin(*args, **user_kwargs):
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
        sys.executable,
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
        p = spin("run", f.name, sys_exit=False)
        assert "Did you mean to call" in stdout(
            p
        ), "Failed to recommend `python run python file.py`"


def test_test():
    """Does the test command run?"""
    spin("test")


def test_test_with_pythonpath():
    """Does `spin test` work when PYTHONPATH is set?"""
    spin("test", env={**os.environ, "PYTHONPATH": "/tmp"})


def test_sdist():
    spin("sdist")


def test_example():
    spin("example")


def test_docs():
    run(["pip", "install", "--quiet", "sphinx"])
    spin("docs")


def test_spin_install():
    cwd = os.getcwd()
    spin("install")
    with tempfile.TemporaryDirectory() as d:
        try:
            os.chdir(d)
            p = run(
                [
                    sys.executable,
                    "-c",
                    "import example_pkg; print(example_pkg.__version__)",
                ],
                stdout=subprocess.PIPE,
            )
            assert stdout(p) == "0.0.0dev0"
        finally:
            os.chdir(cwd)
            run(["pip", "uninstall", "-y", "--quiet", "example_pkg"])


@on_linux
def test_gdb():
    p = spin(
        "gdb",
        "-c",
        'import example_pkg; example_pkg.echo("hi")',
        "--",
        "--eval",
        "run",
        "--batch",
    )
    assert "hi" in stdout(p)
