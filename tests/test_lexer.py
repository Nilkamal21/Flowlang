import pytest
from lexer import Lexer
from tokens import TokenType

def test_basic_variables():
    code = 'let age <- 21\nlet name <- "Nilkamal"'
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    types = [t.type for t in tokens]
    assert types == [
        TokenType.LET, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.INT, TokenType.NEWLINE,
        TokenType.LET, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.STRING, TokenType.NEWLINE,
        TokenType.EOF
    ]
    assert tokens[1].value == "age"
    assert tokens[3].value == 21
    assert tokens[6].value == "name"
    assert tokens[8].value == "Nilkamal"

def test_maximal_munch_operators():
    code = "x <- 10 |> show == <= >="
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    types = [t.type for t in tokens]
    assert types == [
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.INT,
        TokenType.PIPE,
        TokenType.SHOW,
        TokenType.EQUAL_EQUAL,
        TokenType.LESS_EQUAL,
        TokenType.GREATER_EQUAL,
        TokenType.NEWLINE,
        TokenType.EOF
    ]

def test_comments_and_whitespace():
    code = """# This is a comment
let x <- 10 # trailing comment
"""
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    types = [t.type for t in tokens]
    assert types == [
        TokenType.LET, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.INT, TokenType.NEWLINE,
        TokenType.EOF
    ]

def test_indentation_block():
    code = """when age >= 18:
    show "Adult"
otherwise:
    show "Minor"
"""
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    types = [t.type for t in tokens]
    assert types == [
        TokenType.WHEN, TokenType.IDENTIFIER, TokenType.GREATER_EQUAL, TokenType.INT, TokenType.COLON, TokenType.NEWLINE,
        TokenType.INDENT, TokenType.SHOW, TokenType.STRING, TokenType.NEWLINE, TokenType.DEDENT,
        TokenType.OTHERWISE, TokenType.COLON, TokenType.NEWLINE,
        TokenType.INDENT, TokenType.SHOW, TokenType.STRING, TokenType.NEWLINE, TokenType.DEDENT,
        TokenType.EOF
    ]

def test_pipeline_tokens():
    code = """numbers
  |> keep x where x > 2
  |> transform x into x * 10
  |> show"""
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    types = [t.type for t in tokens]
    assert TokenType.PIPE in types
    assert TokenType.KEEP in types
    assert TokenType.WHERE in types
    assert TokenType.TRANSFORM in types
    assert TokenType.INTO in types
    assert TokenType.SHOW in types

def test_function_definition_tokens():
    code = """define square(x):
    give x * x"""
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    types = [t.type for t in tokens]
    assert types == [
        TokenType.DEFINE, TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.IDENTIFIER, TokenType.RPAREN, TokenType.COLON, TokenType.NEWLINE,
        TokenType.INDENT, TokenType.GIVE, TokenType.IDENTIFIER, TokenType.STAR, TokenType.IDENTIFIER, TokenType.NEWLINE, TokenType.DEDENT,
        TokenType.EOF
    ]

def test_floats_and_booleans():
    code = "let pi <- 3.14\nlet is_valid <- true"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    assert tokens[3].type == TokenType.FLOAT
    assert tokens[3].value == 3.14
    assert tokens[8].type == TokenType.BOOLEAN
    assert tokens[8].value is True

def test_unterminated_string_error():
    code = 'let msg <- "hello world'
    lexer = Lexer(code)
    with pytest.raises(SyntaxError, match="Unterminated string literal"):
        lexer.tokenize()

def test_invalid_character_error():
    code = "let x @ 5"
    lexer = Lexer(code)
    with pytest.raises(SyntaxError, match="Unexpected character '@'"):
        lexer.tokenize()
