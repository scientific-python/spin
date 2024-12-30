import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from spin.cmds.util import run

from .testutil import (
    skip_on_windows,
    skip_py_lt_311,
    skip_unless_linux,
    skip_unless_macos,
    spin,
    stdout,
)


def test_basic_build(example_pkg):
    """Does the package build?"""
    spin("build")

    assert Path("build").exists(), "`build` folder not created after `spin build`"
    assert Path(
        "build-install"
    ).exists(), "`build-install` folder not created after `spin build`"


def test_debug_builds(example_pkg):
    """Does spin generate gcov debug output files?"""
    spin("build", "--gcov")

    debug_files = Path(".").rglob("*.gcno")
    assert len(list(debug_files)) != 0, "debug files not generated for gcov build"


def test_prefix_builds(example_pkg):
    """does spin build --prefix create a build-install directory with the correct structure?"""
    prefix = Path.cwd() / "build-install" / "foobar"
    spin("build", f"--prefix={prefix}")
    assert (Path("build-install") / Path("foobar")).exists()


def test_coverage_builds(example_pkg):
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
def test_coverage_reports(example_pkg, report_type, output_file):
    """Does gcov test generate coverage reports?"""
    spin("test", "--gcov", f"--gcov-format={report_type}")

    coverage_report = Path("./build/meson-logs", output_file)
    assert (
        coverage_report.exists()
    ), f"coverage report not generated for gcov build ({report_type})"


def test_expand_pythonpath(example_pkg):
    """Does an $ENV_VAR get expanded in `spin run`?"""
    output = spin("run", "echo $PYTHONPATH")
    assert any(
        p in stdout(output) for p in ("site-packages", "dist-packages")
    ), f"Expected value of $PYTHONPATH, got {stdout(output)} instead"


def test_run_stdout(example_pkg):
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
def test_recommend_run_python(example_pkg):
    """If `spin run file.py` is called, is `spin run python file.py` recommended?"""
    with tempfile.NamedTemporaryFile(suffix=".py") as f:
        p = spin("run", f.name, sys_exit=False)
        assert "Did you mean to call" in stdout(
            p
        ), "Failed to recommend `python run python file.py`"


def test_sdist(example_pkg):
    spin("sdist")


def test_example(example_pkg):
    spin("example")


def test_docs(example_pkg):
    run(["pip", "install", "--quiet", "sphinx"])
    spin("docs")


def test_spin_install(example_pkg):
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
def test_gdb(example_pkg):
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
def test_lldb(example_pkg):
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


@skip_py_lt_311  # python command does not run on older pythons
def test_parallel_builds(example_pkg):
    spin("build")
    spin("build", "-C", "parallel/build")
    p = spin("python", "--", "-c", "import example_pkg; print(example_pkg.__file__)")
    example_pkg_path = stdout(p).split("\n")[-1]
    p = spin(
        "python",
        "-C",
        "parallel/build",
        "--",
        "-c",
        "import example_pkg; print(example_pkg.__file__)",
    )
    example_pkg_parallel_path = stdout(p).split("\n")[-1]
    assert "build-install" in example_pkg_path
    assert "parallel/build-install" in example_pkg_parallel_path
    assert "parallel/build-install" not in example_pkg_path
