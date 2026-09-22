import pytest
from flowlang.lexer import Lexer
from flowlang.parser import Parser
from flowlang.environment import Environment
from flowlang.interpreter import Interpreter
from flowlang.ast_nodes import (
    LiteralNode, VarAccessNode, ListNode, UnaryOpNode, BinaryOpNode,
    VarDeclNode, VarAssignNode, ShowNode, WhenNode
)

def run_code(code: str) -> Interpreter:
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.evaluate(ast)
    return interp

def test_evaluate_literals():
    interp = Interpreter()
    assert interp.evaluate(LiteralNode(42)) == 42
    assert interp.evaluate(LiteralNode(3.14)) == 3.14
    assert interp.evaluate(LiteralNode("hello")) == "hello"
    assert interp.evaluate(LiteralNode(True)) is True

def test_evaluate_var_access():
    interp = Interpreter()
    env = Environment()
    env.define("x", 100)

    assert interp.evaluate(VarAccessNode("x"), env) == 100

def test_evaluate_list_node():
    interp = Interpreter()
    node = ListNode([LiteralNode(1), LiteralNode(2), LiteralNode(3)])
    assert interp.evaluate(node) == [1, 2, 3]

def test_evaluate_arithmetic():
    interp = Interpreter()

    # 2 + 3 * 4 -> 14
    expr = BinaryOpNode(
        LiteralNode(2),
        "+",
        BinaryOpNode(LiteralNode(3), "*", LiteralNode(4))
    )
    assert interp.evaluate(expr) == 14

def test_evaluate_unary_minus():
    interp = Interpreter()
    expr = UnaryOpNode("-", LiteralNode(10))
    assert interp.evaluate(expr) == -10

def test_evaluate_comparisons():
    interp = Interpreter()

    assert interp.evaluate(BinaryOpNode(LiteralNode(5), ">", LiteralNode(2))) is True
    assert interp.evaluate(BinaryOpNode(LiteralNode(10), "==", LiteralNode(10))) is True
    assert interp.evaluate(BinaryOpNode(LiteralNode(5), "<=", LiteralNode(3))) is False

def test_evaluate_logical_ops():
    interp = Interpreter()

    # true and false -> False
    assert interp.evaluate(BinaryOpNode(LiteralNode(True), "and", LiteralNode(False))) is False
    # true or false -> True
    assert interp.evaluate(BinaryOpNode(LiteralNode(True), "or", LiteralNode(False))) is True
    # not false -> True
    assert interp.evaluate(UnaryOpNode("not", LiteralNode(False))) is True

def test_division_by_zero_error():
    interp = Interpreter()
    expr = BinaryOpNode(LiteralNode(10), "/", LiteralNode(0))
    with pytest.raises(ZeroDivisionError, match="Division by zero"):
        interp.evaluate(expr)

def test_statement_var_decl_and_assign():
    code = """let age <- 21
age <- 22"""
    interp = run_code(code)
    assert interp.global_env.get("age") == 22

def test_statement_show():
    code = 'show "Hello Flowlang"'
    interp = run_code(code)
    assert interp.output_buffer == ["Hello Flowlang"]

def test_statement_when_then_branch():
    code = """let age <- 21
when age >= 18:
    show "Adult"
otherwise:
    show "Minor" """
    interp = run_code(code)
    assert interp.output_buffer == ["Adult"]

def test_statement_when_otherwise_branch():
    code = """let age <- 15
when age >= 18:
    show "Adult"
otherwise:
    show "Minor" """
    interp = run_code(code)
    assert interp.output_buffer == ["Minor"]

def test_function_declaration_and_call():
    code = """define square(x):
    give x * x

let result <- square(5)
show result"""
    interp = run_code(code)
    assert interp.global_env.get("result") == 25
    assert interp.output_buffer == ["25"]

def test_pipeline_keep_and_transform_into():
    code = """let numbers <- [1, 2, 3, 4, 5]

numbers
  |> keep x where x > 2
  |> transform x into x * 10
  |> show"""
    interp = run_code(code)
    assert interp.output_buffer == ["[30, 40, 50]"]

def test_pipeline_transform_using():
    code = """define double(x):
    give x * 2

let data <- [5, 10, 15]

data
  |> transform x using double
  |> show"""
    interp = run_code(code)
    assert interp.output_buffer == ["[10, 20, 30]"]

def test_full_example_01_hello_world():
    with open("examples/01_hello_world.flow", "r") as f:
        code = f.read()
    interp = run_code(code)
    assert interp.output_buffer == ["Hello, Flowlang!", "0.1"]
