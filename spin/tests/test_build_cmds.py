import subprocess
from pathlib import Path

import spin as libspin
from spin.cmds.util import run


def spin(*args):
    return run(["spin"] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def stdout(p):
    return p.stdout.decode("utf-8").strip()


def test_get_version():
    p = spin("--version")
    assert stdout(p) == f"spin {libspin.__version__}"


def test_basic_build():
    spin("build")

    assert Path("build").exists(), "`build` folder not created after `spin build`"
    assert Path(
        "build-install"
    ).exists(), "`build-install` folder not created after `spin build`"


def test_debug_builds():
    spin("build", "--gcov")

    debug_files = Path(".").rglob("*.gcno")
    assert len(list(debug_files)) != 0, "debug files not generated for gcov build"


def test_expand_pythonpath():
    output = spin("run", "echo $PYTHONPATH")
    assert any(
        p in stdout(output) for p in ("site-packages", "dist-packages")
    ), f"Expected value of $PYTHONPATH, got {stdout(output)} instead"


def test_run_stdout():
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
    try:
        run(["pip", "install", "--quiet", "-e", "."])
        assert "Warning! An editable installation" in stdout(
            spin("run", "ls")
        ), "Failed to detect and warn about editable install"
    finally:
        run(["pip", "uninstall", "--quiet", "-y", "example_pkg"])
