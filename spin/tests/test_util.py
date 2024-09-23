import pytest

from spin.cmds import util


def test_cmd_not_found(capsys):
    with pytest.raises(SystemExit):
        util.run(["gdb1", "-e", "script"])
    output = capsys.readouterr()
    assert "executable not found" in output.out
