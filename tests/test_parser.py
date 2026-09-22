import pytest
from lexer import Lexer
from parser import Parser
from ast_nodes import (
    ProgramNode, VarDeclNode, VarAssignNode, ShowNode, WhenNode,
    FunctionDeclNode, GiveNode, PipelineNode, KeepStageNode,
    TransformIntoStageNode, ShowStageNode, BinaryOpNode, UnaryOpNode,
    LiteralNode, VarAccessNode, FunctionCallNode, ListNode
)

def parse_code(code: str) -> ProgramNode:
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()

def test_var_declaration_and_assignment():
    code = "let age <- 21\nage <- 22"
    ast = parse_code(code)

    assert ast == ProgramNode([
        VarDeclNode("age", LiteralNode(21)),
        VarAssignNode("age", LiteralNode(22))
    ])

def test_show_statement():
    code = 'show "Hello World"'
    ast = parse_code(code)

    assert ast == ProgramNode([
        ShowNode(LiteralNode("Hello World"))
    ])

def test_operator_precedence():
    code = "show 2 + 3 * 4"
    ast = parse_code(code)

    # Precedence: 2 + (3 * 4)
    expected_expr = BinaryOpNode(
        LiteralNode(2),
        "+",
        BinaryOpNode(LiteralNode(3), "*", LiteralNode(4))
    )
    assert ast == ProgramNode([ShowNode(expected_expr)])

def test_unary_minus():
    code = "let x <- -10 + 5"
    ast = parse_code(code)

    expected_expr = BinaryOpNode(
        UnaryOpNode("-", LiteralNode(10)),
        "+",
        LiteralNode(5)
    )
    assert ast == ProgramNode([VarDeclNode("x", expected_expr)])

def test_conditionals():
    code = """when age >= 18:
    show "Adult"
otherwise:
    show "Minor" """
    ast = parse_code(code)

    expected = ProgramNode([
        WhenNode(
            condition=BinaryOpNode(VarAccessNode("age"), ">=", LiteralNode(18)),
            then_block=[ShowNode(LiteralNode("Adult"))],
            otherwise_block=[ShowNode(LiteralNode("Minor"))]
        )
    ])
    assert ast == expected

def test_function_declaration():
    code = """define square(x):
    give x * x"""
    ast = parse_code(code)

    expected = ProgramNode([
        FunctionDeclNode(
            name="square",
            params=["x"],
            body_block=[
                GiveNode(BinaryOpNode(VarAccessNode("x"), "*", VarAccessNode("x")))
            ]
        )
    ])
    assert ast == expected

def test_pipeline_parsing():
    code = """numbers
  |> keep x where x > 2
  |> transform x into x * 10
  |> show"""
    ast = parse_code(code)

    expected = ProgramNode([
        PipelineNode(
            target_expr=VarAccessNode("numbers"),
            stages=[
                KeepStageNode("x", BinaryOpNode(VarAccessNode("x"), ">", LiteralNode(2))),
                TransformIntoStageNode("x", BinaryOpNode(VarAccessNode("x"), "*", LiteralNode(10))),
                ShowStageNode()
            ]
        )
    ])
    assert ast == expected

def test_list_literals():
    code = "let nums <- [1, 2, 3]"
    ast = parse_code(code)

    assert ast == ProgramNode([
        VarDeclNode("nums", ListNode([LiteralNode(1), LiteralNode(2), LiteralNode(3)]))
    ])
