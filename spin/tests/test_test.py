import os

from testutil import spin


def test_test():
    """Does the test command run?"""
    spin("test")


def test_test_with_pythonpath():
    """Does `spin test` work when PYTHONPATH is set?"""
    spin("test", env={**os.environ, "PYTHONPATH": "/tmp"})


def test_test_file_spec():
    spin("test", "example_pkg/submodule/tests/test_submodule.py")


def test_test_module_spec():
    spin("test", "example_pkg.submodule")


def test_test_editable_file_spec(editable_install):
    spin("test", "example_pkg/submodule/tests/test_submodule.py")


def test_test_editable_module_spec(editable_install):
    spin("test", "example_pkg.submodule")
