import click
import pytest

from spin import cmds
from spin.cmds.util import extend_command

from .testutil import get_usage, spin


def test_override_add_option():
    @click.option("-e", "--extra", help="Extra test flag")
    @extend_command(cmds.meson.build)
    def build_ext(*, parent_callback, extra=None, **kwargs):
        pass

    assert "--extra" in get_usage(build_ext)
    assert "--extra" not in get_usage(cmds.meson.build)


def test_doc_setter():
    @click.option("-e", "--extra", help="Extra test flag")
    @extend_command(cmds.meson.build)
    def build_ext(*, parent_callback, extra=None, **kwargs):
        """
        Additional docstring
        """
        pass

    assert "Additional docstring" in get_usage(build_ext)
    assert "Additional docstring" not in get_usage(cmds.meson.build)

    @extend_command(cmds.meson.build, doc="Hello world")
    def build_ext(*, parent_callback, extra=None, **kwargs):
        """
        Additional docstring
        """
        pass

    doc = get_usage(build_ext)
    assert "Hello world\n" in doc
    assert "\n  Additional docstring" in doc


def test_ext_additional_args():
    @click.option("-e", "--extra", help="Extra test flag", type=int)
    @extend_command(cmds.meson.build)
    def build_ext(*, parent_callback, extra=None, **kwargs):
        """
        Additional docstring
        """
        assert extra == 5

    ctx = build_ext.make_context(
        None,
        [
            "--extra=5",
        ],
    )
    ctx.forward(build_ext)

    # And ensure that option didn't leak into original command
    with pytest.raises(click.exceptions.NoSuchOption):
        cmds.meson.build.make_context(
            None,
            [
                "--extra=5",
            ],
        )


def test_cli_additional_arg(example_pkg):
    p = spin("build-ext", "--extra=3")
    assert b"Preparing for build with extra=3" in p.stdout
    assert b"meson compile" in p.stdout
