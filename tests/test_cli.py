import sys
import pytest
from cli import main, run_file

def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Flowlang v0.1.0" in captured.out or "Flowlang v0.1.0" in captured.err

def test_cli_help(capsys):
    ret = main([])
    assert ret == 0
    captured = capsys.readouterr()
    assert "usage: flowlang" in captured.out

def test_cli_file_default_vm(capsys):
    ret = main(["examples/01_hello_world.flow"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Hello, Flowlang!" in captured.out
    assert "0.1" in captured.out

def test_cli_file_interp_mode(capsys):
    ret = main(["examples/01_hello_world.flow", "--mode", "interp"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Hello, Flowlang!" in captured.out
    assert "0.1" in captured.out

def test_cli_dump_ast(capsys):
    ret = main(["examples/01_hello_world.flow", "--dump-ast"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "ABSTRACT SYNTAX TREE" in captured.out
    assert "ProgramNode" in captured.out

def test_cli_dump_bytecode(capsys):
    ret = main(["examples/01_hello_world.flow", "--dump-bytecode"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "BYTECODE DISASSEMBLY" in captured.out
    assert "LOAD_CONST" in captured.out

def test_cli_file_not_found(capsys):
    ret = main(["examples/non_existent_file.flow"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err

def test_cli_syntax_error(tmp_path, capsys):
    bad_file = tmp_path / "bad.flow"
    bad_file.write_text("let <- 123", encoding="utf-8")
    ret = main([str(bad_file)])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Flowlang Error" in captured.err
