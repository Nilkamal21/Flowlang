import pytest
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from compiler import Compiler
from vm import VirtualMachine

def run_vm(code: str) -> VirtualMachine:
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    # Static analysis check
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    # Compile AST to Bytecode
    compiler = Compiler()
    instructions = compiler.compile(ast)

    # Run Virtual Machine
    vm = VirtualMachine()
    vm.run(instructions)
    return vm

def test_vm_arithmetic():
    code = "let x <- 2 + 3 * 4"
    vm = run_vm(code)
    assert vm.globals["x"] == 14

def test_vm_variables_and_show():
    code = """let name <- "Nilkamal"
show name"""
    vm = run_vm(code)
    assert vm.globals["name"] == "Nilkamal"
    assert vm.output_buffer == ["Nilkamal"]

def test_vm_conditionals_then_branch():
    code = """let age <- 21
when age >= 18:
    show "Adult"
otherwise:
    show "Minor" """
    vm = run_vm(code)
    assert vm.output_buffer == ["Adult"]

def test_vm_conditionals_otherwise_branch():
    code = """let age <- 15
when age >= 18:
    show "Adult"
otherwise:
    show "Minor" """
    vm = run_vm(code)
    assert vm.output_buffer == ["Minor"]

def test_vm_function_declaration_and_call():
    code = """define square(x):
    give x * x

let result <- square(5)
show result"""
    vm = run_vm(code)
    assert vm.globals["result"] == 25
    assert vm.output_buffer == ["25"]

def test_vm_pipeline_keep_and_transform_into():
    code = """let numbers <- [1, 2, 3, 4, 5]

numbers
  |> keep x where x > 2
  |> transform x into x * 10
  |> show"""
    vm = run_vm(code)
    assert vm.output_buffer == ["[30, 40, 50]"]

def test_vm_pipeline_transform_using():
    code = """define double(x):
    give x * 2

let data <- [5, 10, 15]

data
  |> transform x using double
  |> show"""
    vm = run_vm(code)
    assert vm.output_buffer == ["[10, 20, 30]"]

def test_vm_full_example_01_hello_world():
    with open("examples/01_hello_world.flow", "r") as f:
        code = f.read()
    vm = run_vm(code)
    assert vm.output_buffer == ["Hello, Flowlang!", "0.1"]
