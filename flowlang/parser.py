from typing import List, Optional
from .tokens import Token, TokenType
from .ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, VarAssignNode, ShowNode,
    WhenNode, FunctionDeclNode, GiveNode, PipelineNode, KeepStageNode,
    TransformIntoStageNode, TransformUsingStageNode, ShowStageNode,
    BinaryOpNode, UnaryOpNode, LiteralNode, VarAccessNode,
    FunctionCallNode, ListNode
)

class Parser:
    """
    Recursive Descent Parser for Flowlang.
    Converts a List[Token] into an Abstract Syntax Tree (AST).
    """
    def __init__(self, tokens: List[Token]):
        self.tokens: List[Token] = tokens
        self.pos: int = 0

    def peek(self) -> Token:
        """Returns current token without advancing."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF token

    def peek_next(self) -> Token:
        """Returns next token without advancing."""
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[-1]

    def advance(self) -> Token:
        """Consumes and returns current token."""
        tok = self.peek()
        if self.pos < len(self.tokens):
            self.pos += 1
        return tok

    def check(self, token_type: TokenType) -> bool:
        """Returns True if current token is of token_type."""
        return self.peek().type == token_type

    def match(self, *token_types: TokenType) -> bool:
        """If current token matches any expected type, advances and returns True."""
        for tt in token_types:
            if self.check(tt):
                self.advance()
                return True
        return False

    def consume(self, token_type: TokenType, error_message: str) -> Token:
        """Consumes expected token type or raises SyntaxError."""
        if self.check(token_type):
            return self.advance()
        tok = self.peek()
        raise SyntaxError(
            f"Parse Error at line {tok.line}, col {tok.column}: {error_message}. Got {tok.type.name} ('{tok.value}')"
        )

    def parse(self) -> ProgramNode:
        """Parses full program from token stream."""
        statements: List[ASTNode] = []

        while not self.check(TokenType.EOF):
            # Skip newlines and structural indents between top-level statements
            if self.match(TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT):
                continue
            stmt = self.statement()
            if stmt:
                statements.append(stmt)

        return ProgramNode(statements)

    def statement(self) -> ASTNode:
        """Parses a single statement."""
        if self.match(TokenType.LET):
            return self.var_declaration()
        if self.match(TokenType.SHOW):
            return self.show_statement()
        if self.match(TokenType.WHEN):
            return self.when_statement()
        if self.match(TokenType.DEFINE):
            return self.function_declaration()
        if self.match(TokenType.GIVE):
            return self.return_statement()

        # Identifier could be assignment `x <- ...` or expression `x + 1`
        if self.check(TokenType.IDENTIFIER) and self.peek_next().type == TokenType.ASSIGN:
            return self.var_assignment()

        expr = self.expression()
        self.match(TokenType.NEWLINE)
        return expr

    def var_declaration(self) -> VarDeclNode:
        """Parses `let <var> <- <expression>`"""
        name_tok = self.consume(TokenType.IDENTIFIER, "Expected variable name after 'let'")
        self.consume(TokenType.ASSIGN, "Expected '<-' after variable name")
        val_expr = self.expression()
        self.match(TokenType.NEWLINE)
        return VarDeclNode(name_tok.value, val_expr)

    def var_assignment(self) -> VarAssignNode:
        """Parses `<var> <- <expression>`"""
        name_tok = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        self.consume(TokenType.ASSIGN, "Expected '<-'")
        val_expr = self.expression()
        self.match(TokenType.NEWLINE)
        return VarAssignNode(name_tok.value, val_expr)

    def show_statement(self) -> ShowNode:
        """Parses `show <expression>`"""
        expr = self.expression()
        self.match(TokenType.NEWLINE)
        return ShowNode(expr)

    def when_statement(self) -> WhenNode:
        """Parses `when <cond>: NEWLINE block (otherwise: NEWLINE block)?`"""
        condition = self.expression()
        self.consume(TokenType.COLON, "Expected ':' after when condition")
        self.consume(TokenType.NEWLINE, "Expected newline after ':'")
        then_block = self.block()

        otherwise_block: Optional[List[ASTNode]] = None
        # Skip trailing newlines before checking otherwise
        while self.check(TokenType.NEWLINE):
            self.advance()

        if self.match(TokenType.OTHERWISE):
            self.consume(TokenType.COLON, "Expected ':' after 'otherwise'")
            self.consume(TokenType.NEWLINE, "Expected newline after ':'")
            otherwise_block = self.block()

        return WhenNode(condition, then_block, otherwise_block)

    def function_declaration(self) -> FunctionDeclNode:
        """Parses `define <name>(<params>): NEWLINE block`"""
        name_tok = self.consume(TokenType.IDENTIFIER, "Expected function name after 'define'")
        self.consume(TokenType.LPAREN, "Expected '(' after function name")

        params: List[str] = []
        if not self.check(TokenType.RPAREN):
            param_tok = self.consume(TokenType.IDENTIFIER, "Expected parameter name")
            params.append(param_tok.value)
            while self.match(TokenType.COMMA):
                p_tok = self.consume(TokenType.IDENTIFIER, "Expected parameter name after ','")
                params.append(p_tok.value)

        self.consume(TokenType.RPAREN, "Expected ')' after parameters")
        self.consume(TokenType.COLON, "Expected ':' after function signature")
        self.consume(TokenType.NEWLINE, "Expected newline after ':'")
        body_block = self.block()

        return FunctionDeclNode(name_tok.value, params, body_block)

    def return_statement(self) -> GiveNode:
        """Parses `give <expression>`"""
        expr = self.expression()
        self.match(TokenType.NEWLINE)
        return GiveNode(expr)

    def block(self) -> List[ASTNode]:
        """Parses an indented block of statements."""
        self.consume(TokenType.INDENT, "Expected indented block")
        statements: List[ASTNode] = []

        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                continue
            stmt = self.statement()
            if stmt:
                statements.append(stmt)

        self.consume(TokenType.DEDENT, "Expected unindent at end of block")
        return statements

    def expression(self) -> ASTNode:
        """Parses pipeline expression."""
        return self.pipeline_expression()

    def pipeline_expression(self) -> ASTNode:
        """Parses `expr (|> stage)*`"""
        target = self.logic_or()

        stages: List[ASTNode] = []
        while True:
            # Peek ahead past any newlines/indents/dedents to check for PIPE operator
            look_pos = self.pos
            while look_pos < len(self.tokens) and self.tokens[look_pos].type in (TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT):
                look_pos += 1

            if look_pos < len(self.tokens) and self.tokens[look_pos].type == TokenType.PIPE:
                self.pos = look_pos + 1  # Advance past line breaks and consume PIPE
                stage = self.pipeline_stage()
                stages.append(stage)
            else:
                break

        if stages:
            return PipelineNode(target, stages)
        return target

    def pipeline_stage(self) -> ASTNode:
        """Parses a single pipeline stage (`keep`, `transform`, or `show`)."""
        if self.match(TokenType.KEEP):
            var_tok = self.consume(TokenType.IDENTIFIER, "Expected variable name after 'keep'")
            self.consume(TokenType.WHERE, "Expected 'where' clause in keep stage")
            cond_expr = self.logic_or()
            return KeepStageNode(var_tok.value, cond_expr)

        if self.match(TokenType.TRANSFORM):
            var_tok = self.consume(TokenType.IDENTIFIER, "Expected variable name after 'transform'")
            if self.match(TokenType.INTO):
                tf_expr = self.logic_or()
                return TransformIntoStageNode(var_tok.value, tf_expr)
            if self.match(TokenType.USING):
                func_tok = self.consume(TokenType.IDENTIFIER, "Expected function name after 'using'")
                return TransformUsingStageNode(var_tok.value, func_tok.value)
            raise SyntaxError("Expected 'into' or 'using' in transform stage")

        if self.match(TokenType.SHOW):
            return ShowStageNode()

        tok = self.peek()
        raise SyntaxError(f"Parse Error at line {tok.line}: Invalid pipeline stage token '{tok.value}'")

    def logic_or(self) -> ASTNode:
        """Parses `expr or expr`"""
        left = self.logic_and()
        while self.match(TokenType.OR):
            op = "or"
            right = self.logic_and()
            left = BinaryOpNode(left, op, right)
        return left

    def logic_and(self) -> ASTNode:
        """Parses `expr and expr`"""
        left = self.logic_not()
        while self.match(TokenType.AND):
            op = "and"
            right = self.logic_not()
            left = BinaryOpNode(left, op, right)
        return left

    def logic_not(self) -> ASTNode:
        """Parses `not expr`"""
        if self.match(TokenType.NOT):
            operand = self.logic_not()
            return UnaryOpNode("not", operand)
        return self.comparison()

    def comparison(self) -> ASTNode:
        """Parses comparison operators (`==`, `!=`, `<`, `<=`, `>`, `>=`)"""
        left = self.term()
        while self.check(TokenType.EQUAL_EQUAL) or self.check(TokenType.NOT_EQUAL) or \
              self.check(TokenType.LESS) or self.check(TokenType.LESS_EQUAL) or \
              self.check(TokenType.GREATER) or self.check(TokenType.GREATER_EQUAL):
            op_tok = self.advance()
            right = self.term()
            left = BinaryOpNode(left, op_tok.value, right)
        return left

    def term(self) -> ASTNode:
        """Parses additive operators (`+`, `-`)"""
        left = self.factor()
        while self.check(TokenType.PLUS) or self.check(TokenType.MINUS):
            op_tok = self.advance()
            right = self.factor()
            left = BinaryOpNode(left, op_tok.value, right)
        return left

    def factor(self) -> ASTNode:
        """Parses multiplicative operators (`*`, `/`, `%`)"""
        left = self.unary()
        while self.check(TokenType.STAR) or self.check(TokenType.SLASH) or self.check(TokenType.PERCENT):
            op_tok = self.advance()
            right = self.unary()
            left = BinaryOpNode(left, op_tok.value, right)
        return left

    def unary(self) -> ASTNode:
        """Parses unary minus `-expr`"""
        if self.match(TokenType.MINUS):
            operand = self.unary()
            return UnaryOpNode("-", operand)
        return self.primary()

    def primary(self) -> ASTNode:
        """Parses literals, variables, lists, function calls, and parentheses."""
        if self.match(TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.BOOLEAN):
            tok = self.tokens[self.pos - 1]
            return LiteralNode(tok.value)

        if self.match(TokenType.LBRACK):
            elements: List[ASTNode] = []
            if not self.check(TokenType.RBRACK):
                elements.append(self.expression())
                while self.match(TokenType.COMMA):
                    elements.append(self.expression())
            self.consume(TokenType.RBRACK, "Expected ']' at end of list")
            return ListNode(elements)

        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        if self.match(TokenType.IDENTIFIER):
            name_tok = self.tokens[self.pos - 1]
            # Function Call
            if self.match(TokenType.LPAREN):
                args: List[ASTNode] = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.expression())
                self.consume(TokenType.RPAREN, "Expected ')' after function arguments")
                return FunctionCallNode(name_tok.value, args)

            return VarAccessNode(name_tok.value)

        tok = self.peek()
        raise SyntaxError(f"Parse Error at line {tok.line}, col {tok.column}: Unexpected token '{tok.value}'")
