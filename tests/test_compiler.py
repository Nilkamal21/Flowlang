import pytest
from flowlang.lexer import Lexer
from flowlang.parser import Parser
from flowlang.compiler import Compiler, FunctionCode
from flowlang.bytecode import Opcode, Instruction

def compile_code(code: str) -> list[Instruction]:
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    compiler = Compiler()
    return compiler.compile(ast)

def test_compile_arithmetic_precedence():
    code = "show 2 + 3 * 4"
    instructions = compile_code(code)

    opcodes = [i.opcode for i in instructions]
    assert opcodes == [
        Opcode.LOAD_CONST,  # 2
        Opcode.LOAD_CONST,  # 3
        Opcode.LOAD_CONST,  # 4
        Opcode.BINARY_MUL,
        Opcode.BINARY_ADD,
        Opcode.SHOW_OUTPUT
    ]
    assert instructions[0].operand == 2
    assert instructions[1].operand == 3
    assert instructions[2].operand == 4

def test_compile_variable_declaration_and_access():
    code = "let age <- 21\nshow age"
    instructions = compile_code(code)

    opcodes = [i.opcode for i in instructions]
    assert opcodes == [
        Opcode.LOAD_CONST,
        Opcode.STORE_FAST,
        Opcode.LOAD_FAST,
        Opcode.SHOW_OUTPUT
    ]
    assert instructions[1].operand == "age"
    assert instructions[2].operand == "age"

def test_compile_conditional_jump_patching():
    code = """when age >= 18:
    show "Adult"
otherwise:
    show "Minor" """
    instructions = compile_code(code)

    opcodes = [i.opcode for i in instructions]
    assert Opcode.JUMP_IF_FALSE in opcodes
    assert Opcode.JUMP in opcodes

    # Check that JUMP_IF_FALSE points past 'then' block to start of 'otherwise' block
    jump_if_false_instr = [i for i in instructions if i.opcode == Opcode.JUMP_IF_FALSE][0]
    assert isinstance(jump_if_false_instr.operand, int)
    assert jump_if_false_instr.operand > 0

def test_compile_function_declaration():
    code = """define square(x):
    give x * x"""
    instructions = compile_code(code)

    opcodes = [i.opcode for i in instructions]
    assert opcodes == [
        Opcode.MAKE_FUNCTION,
        Opcode.STORE_FAST
    ]
    func_code = instructions[0].operand
    assert isinstance(func_code, FunctionCode)
    assert func_code.name == "square"
    assert func_code.params == ["x"]
    sub_opcodes = [i.opcode for i in func_code.instructions]
    assert Opcode.RETURN_VALUE in sub_opcodes

def test_compile_pipeline():
    code = """numbers
  |> keep x where x > 2
  |> show"""
    instructions = compile_code(code)

    opcodes = [i.opcode for i in instructions]
    assert opcodes == [
        Opcode.LOAD_FAST,
        Opcode.PIPELINE_KEEP,
        Opcode.SHOW_OUTPUT
    ]
