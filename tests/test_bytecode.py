import pytest
from flowlang.bytecode import Opcode, Instruction

def test_opcode_enum_members():
    assert Opcode.LOAD_CONST.name == "LOAD_CONST"
    assert Opcode.BINARY_ADD.name == "BINARY_ADD"
    assert Opcode.STORE_FAST.name == "STORE_FAST"
    assert Opcode.JUMP_IF_FALSE.name == "JUMP_IF_FALSE"

def test_instruction_creation_and_repr():
    instr1 = Instruction(Opcode.LOAD_CONST, 42, line=1)
    instr2 = Instruction(Opcode.BINARY_ADD, line=1)

    assert repr(instr1) == "Instruction(LOAD_CONST, 42)"
    assert repr(instr2) == "Instruction(BINARY_ADD)"

def test_instruction_equality():
    instr1 = Instruction(Opcode.LOAD_FAST, "age")
    instr2 = Instruction(Opcode.LOAD_FAST, "age")
    instr3 = Instruction(Opcode.LOAD_FAST, "name")

    assert instr1 == instr2
    assert instr1 != instr3
