import pytest
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer, SemanticError

def analyze_code(code: str) -> None:
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

def test_valid_program_passes():
    code = """let age <- 21
when age >= 18:
    show "Adult"
otherwise:
    show "Minor" """
    analyze_code(code)  # Should not raise any error

def test_valid_function_and_pipeline_passes():
    code = """define double(x):
    give x * 2

let nums <- [1, 2, 3]
nums
  |> keep item where item > 1
  |> transform item using double
  |> show"""
    analyze_code(code)  # Should not raise any error

def test_undefined_variable_error():
    code = "show total + 5"
    with pytest.raises(SemanticError, match="Undefined variable 'total'"):
        analyze_code(code)

def test_duplicate_variable_declaration_error():
    code = """let x <- 10
let x <- 20"""
    with pytest.raises(SemanticError, match="Variable 'x' is already declared in this scope"):
        analyze_code(code)

def test_assign_to_undefined_variable_error():
    code = "y <- 5"
    with pytest.raises(SemanticError, match="Cannot assign to undefined variable 'y'"):
        analyze_code(code)

def test_undefined_function_error():
    code = "let res <- unknown_func(10)"
    with pytest.raises(SemanticError, match="Undefined function 'unknown_func'"):
        analyze_code(code)

def test_function_argument_mismatch_error():
    code = """define square(x):
    give x * x

let val <- square(5, 10)"""
    with pytest.raises(SemanticError, match="Function 'square' expects 1 arguments, but got 2"):
        analyze_code(code)

def test_give_outside_function_error():
    code = "give 42"
    with pytest.raises(SemanticError, match="'give' statement cannot be used outside of a function"):
        analyze_code(code)

def test_pipeline_transform_using_undefined_function_error():
    code = """let items <- [1, 2]
items |> transform x using missing_func"""
    with pytest.raises(SemanticError, match="Pipeline 'transform using' refers to undefined function 'missing_func'"):
        analyze_code(code)

def test_pipeline_transform_using_invalid_param_count_error():
    code = """define add(a, b):
    give a + b

let items <- [1, 2]
items |> transform x using add"""
    with pytest.raises(SemanticError, match="Function 'add' used in pipeline must take exactly 1 parameter, but takes 2"):
        analyze_code(code)
