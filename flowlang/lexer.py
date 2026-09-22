from typing import List, Optional
from .tokens import Token, TokenType, KEYWORDS

class Lexer:
    """
    Lexical Analyzer for Flowlang.
    Converts source code text into a list of Tokens.
    """
    def __init__(self, source: str):
        self.source: str = source
        self.length: int = len(source)
        self.pos: int = 0
        self.line: int = 1
        self.column: int = 1
        self.indent_stack: List[int] = [0]
        self.at_line_start: bool = True
        self.open_brackets: int = 0

    def peek(self, offset: int = 0) -> str:
        """Returns character at pos + offset without advancing."""
        idx = self.pos + offset
        if idx >= self.length:
            return '\0'
        return self.source[idx]

    def advance(self) -> str:
        """Advances cursor and returns current character."""
        if self.pos >= self.length:
            return '\0'
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def match(self, expected: str) -> bool:
        """If current char matches expected, advances and returns True."""
        if self.peek() == expected:
            self.advance()
            return True
        return False

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while self.pos < self.length:
            if self.at_line_start:
                self._handle_indentation(tokens)
                if self.pos >= self.length:
                    break

            ch = self.peek()

            # Skip spaces and tabs (non-line-start)
            if ch in (' ', '\t'):
                self.advance()
                continue

            # Comments (# ...)
            if ch == '#':
                self._skip_comment()
                continue

            # Newline
            if ch == '\n':
                line_no = self.line
                col_no = self.column
                self.advance()
                if self.open_brackets == 0:
                    # Avoid duplicate NEWLINE tokens or leading NEWLINE at start of file / after INDENT
                    if tokens and tokens[-1].type not in (TokenType.NEWLINE, TokenType.INDENT):
                        tokens.append(Token(TokenType.NEWLINE, "\n", line_no, col_no))
                self.at_line_start = True
                continue

            # Numbers
            if ch.isdigit():
                tokens.append(self._scan_number())
                continue

            # Identifiers and Keywords
            if ch.isalpha() or ch == '_':
                tokens.append(self._scan_identifier_or_keyword())
                continue

            # Strings
            if ch == '"':
                tokens.append(self._scan_string())
                continue

            # Operators and Punctuation
            tok = self._scan_operator_or_punctuation()
            if tok:
                tokens.append(tok)
                continue

            raise SyntaxError(
                f"Unexpected character '{ch}' at line {self.line}, column {self.column}"
            )

        # Handle remaining DEDENTs at EOF
        if tokens and tokens[-1].type != TokenType.NEWLINE:
            tokens.append(Token(TokenType.NEWLINE, "\n", self.line, self.column))

        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, "", self.line, self.column))

        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens

    def _handle_indentation(self, tokens: List[Token]) -> None:
        """Tracks leading spaces and emits INDENT / DEDENT tokens."""
        indent_col = self.column
        indent_count = 0

        # Peek ahead to count spaces/tabs
        idx = self.pos
        while idx < self.length and self.source[idx] in (' ', '\t'):
            if self.source[idx] == ' ':
                indent_count += 1
            elif self.source[idx] == '\t':
                indent_count += 4  # Standard tab width 4 spaces
            idx += 1

        # Check if line is empty or purely a comment
        if idx >= self.length or self.source[idx] in ('\n', '#'):
            # Skip empty / comment lines without altering indent state
            self.pos = idx
            return

        # Advance pos by leading space count
        for _ in range(indent_count):
            self.advance()

        self.at_line_start = False

        # Ignore indentation inside parens/brackets
        if self.open_brackets > 0:
            return

        current_indent = self.indent_stack[-1]
        if indent_count > current_indent:
            self.indent_stack.append(indent_count)
            tokens.append(Token(TokenType.INDENT, " " * indent_count, self.line, indent_col))
        elif indent_count < current_indent:
            while indent_count < self.indent_stack[-1]:
                self.indent_stack.pop()
                tokens.append(Token(TokenType.DEDENT, "", self.line, indent_col))
            if indent_count != self.indent_stack[-1]:
                raise SyntaxError(
                    f"IndentationError at line {self.line}: unindent does not match any outer indentation level"
                )

    def _skip_comment(self) -> None:
        """Skips `# ...` until end of line."""
        while self.pos < self.length and self.peek() != '\n':
            self.advance()

    def _scan_number(self) -> Token:
        start_line = self.line
        start_col = self.column
        num_str = ""

        while self.peek().isdigit():
            num_str += self.advance()

        # Float checking
        if self.peek() == '.' and self.peek(1).isdigit():
            num_str += self.advance()  # consume '.'
            while self.peek().isdigit():
                num_str += self.advance()
            return Token(TokenType.FLOAT, float(num_str), start_line, start_col)

        return Token(TokenType.INT, int(num_str), start_line, start_col)

    def _scan_identifier_or_keyword(self) -> Token:
        start_line = self.line
        start_col = self.column
        word = ""

        while self.peek().isalnum() or self.peek() == '_':
            word += self.advance()

        # Check if keyword
        if word in KEYWORDS:
            tok_type = KEYWORDS[word]
            if tok_type == TokenType.BOOLEAN:
                val = True if word == "true" else False
                return Token(TokenType.BOOLEAN, val, start_line, start_col)
            return Token(tok_type, word, start_line, start_col)

        return Token(TokenType.IDENTIFIER, word, start_line, start_col)

    def _scan_string(self) -> Token:
        start_line = self.line
        start_col = self.column
        self.advance()  # Consume opening quote '"'
        val = ""

        while self.pos < self.length and self.peek() != '"':
            if self.peek() == '\n':
                raise SyntaxError(
                    f"Unterminated string literal starting at line {start_line}, column {start_col}"
                )
            if self.peek() == '\\':
                self.advance()
                escaped = self.advance()
                if escaped == 'n':
                    val += '\n'
                elif escaped == 't':
                    val += '\t'
                elif escaped == '"':
                    val += '"'
                elif escaped == '\\':
                    val += '\\'
                else:
                    val += escaped
            else:
                val += self.advance()

        if self.pos >= self.length:
            raise SyntaxError(
                f"Unterminated string literal starting at line {start_line}, column {start_col}"
            )

        self.advance()  # Consume closing quote '"'
        return Token(TokenType.STRING, val, start_line, start_col)

    def _scan_operator_or_punctuation(self) -> Optional[Token]:
        start_line = self.line
        start_col = self.column
        ch = self.peek()

        # 2-character operators (Maximal Munch)
        if ch == '<':
            self.advance()
            if self.match('-'):
                return Token(TokenType.ASSIGN, "<-", start_line, start_col)
            if self.match('='):
                return Token(TokenType.LESS_EQUAL, "<=", start_line, start_col)
            return Token(TokenType.LESS, "<", start_line, start_col)

        if ch == '|':
            self.advance()
            if self.match('>'):
                return Token(TokenType.PIPE, "|>", start_line, start_col)
            raise SyntaxError(f"Unexpected character '|' at line {start_line}, column {start_col}")

        if ch == '=':
            self.advance()
            if self.match('='):
                return Token(TokenType.EQUAL_EQUAL, "==", start_line, start_col)
            raise SyntaxError(f"Unexpected character '=' at line {start_line}, column {start_col}. Did you mean '==' or '<-'?")

        if ch == '!':
            self.advance()
            if self.match('='):
                return Token(TokenType.NOT_EQUAL, "!=", start_line, start_col)
            raise SyntaxError(f"Unexpected character '!' at line {start_line}, column {start_col}. Did you mean '!=' or 'not'?")

        if ch == '>':
            self.advance()
            if self.match('='):
                return Token(TokenType.GREATER_EQUAL, ">=", start_line, start_col)
            return Token(TokenType.GREATER, ">", start_line, start_col)

        # 1-character tokens
        self.advance()
        if ch == '+':
            return Token(TokenType.PLUS, "+", start_line, start_col)
        if ch == '-':
            return Token(TokenType.MINUS, "-", start_line, start_col)
        if ch == '*':
            return Token(TokenType.STAR, "*", start_line, start_col)
        if ch == '/':
            return Token(TokenType.SLASH, "/", start_line, start_col)
        if ch == '%':
            return Token(TokenType.PERCENT, "%", start_line, start_col)
        if ch == ':':
            return Token(TokenType.COLON, ":", start_line, start_col)
        if ch == ',':
            return Token(TokenType.COMMA, ",", start_line, start_col)
        if ch == '(':
            self.open_brackets += 1
            return Token(TokenType.LPAREN, "(", start_line, start_col)
        if ch == ')':
            if self.open_brackets > 0:
                self.open_brackets -= 1
            return Token(TokenType.RPAREN, ")", start_line, start_col)
        if ch == '[':
            self.open_brackets += 1
            return Token(TokenType.LBRACK, "[", start_line, start_col)
        if ch == ']':
            if self.open_brackets > 0:
                self.open_brackets -= 1
            return Token(TokenType.RBRACK, "]", start_line, start_col)

        return None
