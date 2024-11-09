import os

from .testutil import spin


def test_test(example_pkg):
    """Does the test command run?"""
    spin("test")


def test_test_with_pythonpath(example_pkg):
    """Does `spin test` work when PYTHONPATH is set?"""
    p = spin("test", env={**os.environ, "PYTHONPATH": "/tmp"})
    # Ensure more than zero tests ran
    assert b"passed" in p.stdout


def test_test_file_spec(example_pkg):
    p = spin("test", "example_pkg/submodule/tests/test_submodule.py")
    # Ensure more than zero tests ran
    assert b"passed" in p.stdout


def test_test_module_spec(example_pkg):
    p = spin("test", "example_pkg.submodule")
    # Ensure more than zero tests ran
    assert b"passed" in p.stdout


def test_test_editable_file_spec(example_pkg, editable_install):
    p = spin("test", "example_pkg/submodule/tests/test_submodule.py")
    # Ensure more than zero tests ran
    assert b"passed" in p.stdout


def test_test_editable_module_spec(example_pkg, editable_install):
    p = spin("test", "example_pkg.submodule")
    # Ensure more than zero tests ran
    assert b"passed" in p.stdout


def test_test_source_layout(example_pkg_src_layout):
    p = spin("test")
    # Ensure more than zero tests ran
    assert b"passed" in p.stdout


def test_test_source_layout_explicit(example_pkg_src_layout):
    p = spin("test", "tests")
    # Ensure more than zero tests ran
    assert b"passed" in p.stdout
