import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from testutil import skip_on_windows, skip_unless_linux, skip_unless_macos, spin, stdout

from spin.cmds.util import run


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


def test_coverage_builds():
    """Does gcov test generate coverage files?"""
    spin("test", "--gcov")

    coverage_files = Path(".").rglob("*.gcda")
    assert len(list(coverage_files)) != 0, "coverage files not generated for gcov build"


@pytest.mark.parametrize(
    "report_type,output_file",
    [
        ("html", Path("coveragereport/index.html")),
        ("xml", Path("coverage.xml")),
        ("text", Path("coverage.txt")),
        ("sonarqube", Path("sonarqube.xml")),
    ],
)
def test_coverage_reports(report_type, output_file):
    """Does gcov test generate coverage reports?"""
    spin("test", "--gcov", f"--gcov-format={report_type}")

    coverage_report = Path("./build/meson-logs", output_file)
    assert (
        coverage_report.exists()
    ), f"coverage report not generated for gcov build ({report_type})"


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


@skip_unless_linux
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


@skip_unless_macos
def test_lldb():
    p = spin(
        "lldb",
        "-c",
        'import example_pkg; example_pkg.echo("hi")',
        "--",
        "-o",
        "run",
        "--batch",
    )
    assert "hi" in stdout(p)
