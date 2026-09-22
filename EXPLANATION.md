# Flowlang — Interview Revision Guide

A concise, beginner-friendly revision guide for Flowlang. Designed to be read in 10–15 minutes before a technical interview to revise system architecture, component design, and pipeline execution.

---

# Complete System Pipeline

```text
Flowlang Source Code
        ↓
     Lexer              <-- [IMPLEMENTED: Phase 2 (lexer.py)]
        ↓
    Tokens              <-- [IMPLEMENTED: Phase 1 (tokens.py)]
        ↓
    Parser              <-- [IMPLEMENTED: Phase 3 & 4 (parser.py)]
        ↓
     AST                <-- [IMPLEMENTED: Phase 3 & 4 (ast_nodes.py)]
        ↓
  Environment           <-- [IMPLEMENTED: Phase 5.1 (environment.py)]
        ↓
  Semantic Analyzer     <-- [IMPLEMENTED: Phase 6 (semantic.py)]
        ↓
  Interpreter           <-- [IMPLEMENTED: Phase 5 (interpreter.py)]
        ↓
     Output

Later Execution Path:

     AST
      ↓
Bytecode Compiler       <-- [IMPLEMENTED: Phase 7.2 (compiler.py)]
      ↓
Flowlang Bytecode       <-- [IMPLEMENTED: Phase 7.1 (bytecode.py)]
      ↓
Stack-Based VM          <-- [IMPLEMENTED: Phase 8 (vm.py)]
      ↓
     Output

CLI & Packaging Layer:

flowlang <file.flow>    <-- [IMPLEMENTED: Phase 9 (cli.py, flowlang.cmd, setup.py)]
```

---

# Phase 1: `tokens.py` (Token Definitions & Enums)

- **INPUT**: None (Data model & definition file).
- **OUTPUT**: `TokenType` Enum, `KEYWORDS` Dict, and `Token` Class used across the pipeline.

### 1. Flowchart

```text
Token Definitions (tokens.py)
   ├── TokenType Enum       ──> Categorizes words, symbols, and literals
   ├── KEYWORDS Dict        ──> Maps string keywords to TokenType
   └── Token Class          ──> Holds (type, value, line, column)
```

### 2. Functions & Classes

#### `TokenType` (Enum)
- **WHAT**: Defines all valid categories of tokens in Flowlang (keywords, literals, identifiers, operators, delimiters, structure).
- **WHY**: Provides type safety and fast comparisons for the Lexer and Parser.

#### `KEYWORDS` (Dictionary)
- **WHAT**: A lookup table mapping raw keyword text (e.g. `"let"`, `"when"`, `"keep"`) to `TokenType` enum members.
- **WHY**: Allows the scanner to distinguish reserved keywords from user-defined variable names instantly.

#### `Token` (Class)
- **WHAT**: Data structure representing a single token in source code.
- **WHY**: Encapsulates token value along with line/column coordinates for precise compiler error reporting.

##### `Token.__init__(type, value, line, column)`
- **WHAT**: Initializes a new Token instance.
- **WHY**: Stores token attributes (`type`, `value`, `line`, `column`) upon scanning.

##### `Token.__repr__()`
- **WHAT**: Generates a readable string representation of the token (e.g. `Token(LET, 'let', line=1, col=1)`).
- **WHY**: Used for debugging and inspecting token streams.

##### `Token.__eq__(other)`
- **WHAT**: Compares two Token objects for structural equality.
- **WHY**: Required for unit testing token lists against expected outputs.

### 3. Tiny Example

```text
Source snippet: "let age <- 21"

Mapped Tokens:
[
  Token(LET, 'let', line=1, col=1),
  Token(IDENTIFIER, 'age', line=1, col=5),
  Token(ASSIGN, '<-', line=1, col=9),
  Token(INT, 21, line=1, col=12)
]
```

### 4. Interview Key Point
`tokens.py` decouples raw text from grammar representation. Enums created with `auto()` guarantee unique token types, while the `Token` object carries source coordinates (`line`, `column`) required for meaningful error reporting.

---

# Phase 2: `lexer.py` (Lexical Analyzer)

- **INPUT**: Raw Flowlang source code (`str`).
- **OUTPUT**: Sequenced list of tokens (`List[Token]`) ending with an `EOF` token.

### 1. Flowchart

```text
Flowlang Source Code
        ↓
   tokenize()
        ↓
┌──────────┬──────────────┬──────────┬────────────────────────┐
│          │              │          │                        │
number   identifier     string    operator/punctuation    indentation
│          │              │          │                        │
↓          ↓              ↓          ↓                        ↓
_scan_   _scan_         _scan_     _scan_operator_        _handle_
number() identifier_    string()   or_punctuation()       indentation()
         or_keyword()
│          │              │          │                        │
└──────────┴──────────────┴──────────┴────────────────────────┘
        ↓
   TOKENS LIST
        ↓
    EOF Token
```

### 2. Functions & Classes

#### `Lexer` (Class)
- **WHAT**: The main stateful scanner that converts source code text into a token list.
- **WHY**: Simplifies raw characters into structured tokens so the parser does not scan raw text.

##### `Lexer.__init__(source)`
- **WHAT**: Initializes scanner cursor, line/column counters, bracket depth tracker, and indentation stack.
- **WHY**: Prepares state before scanning source text.

##### `Lexer.peek(offset=0)`
- **WHAT**: Returns the character at `pos + offset` without moving the cursor.
- **WHY**: Enables lookahead needed for multi-character operators (Maximal Munch).

##### `Lexer.advance()`
- **WHAT**: Consumes current character, advances position, and updates line/column numbers.
- **WHY**: Moves scanner forward through input string.

##### `Lexer.match(expected)`
- **WHAT**: Checks if current character matches `expected`. If so, advances cursor and returns `True`.
- **WHY**: Simplifies scanning two-character operators like `<-`, `|>`, `==`, `<=`.

##### `Lexer.tokenize()`
- **WHAT**: Primary scanning loop driving token extraction from start of file to EOF.
- **WHY**: Dispatches sub-scanners, processes newlines, handles line-start indentation, and appends final `EOF`.

##### `Lexer._handle_indentation(tokens)`
- **WHAT**: Counts leading spaces at line starts and manages `indent_stack`.
- **WHY**: Implements Python-style block indentation by emitting `INDENT` and `DEDENT` tokens.

##### `Lexer._skip_comment()`
- **WHAT**: Consumes `#` comments up to the newline.
- **WHY**: Ignores developer comments during code execution.

##### `Lexer._scan_number()`
- **WHAT**: Scans numeric digits into `INT` or `FLOAT` tokens.
- **WHY**: Converts digit characters into numerical token values.

##### `Lexer._scan_identifier_or_keyword()`
- **WHAT**: Scans alphanumeric words and checks the `KEYWORDS` dictionary.
- **WHY**: Distinguishes reserved keywords (e.g. `when`, `keep`) from variable names (e.g. `age`, `x`).

##### `Lexer._scan_string()`
- **WHAT**: Scans text enclosed in double quotes and processes escape sequences (`\n`, `\t`, `\"`, `\\`).
- **WHY**: Parses string literals safely with escape support.

##### `Lexer._scan_operator_or_punctuation()`
- **WHAT**: Scans multi-character (`<-`, `|>`, `==`, `!=`, `<=`, `>=`) and single-character operators/symbols.
- **WHY**: Uses Maximal Munch to prevent multi-character operators from being broken into separate single-character tokens.

### 3. Tiny Example

```text
Source Input:
when age >= 18:
    show "Adult"

Generated Tokens:
[
  Token(WHEN, 'when', line=1, col=1),
  Token(IDENTIFIER, 'age', line=1, col=6),
  Token(GREATER_EQUAL, '>=', line=1, col=10),
  Token(INT, 18, line=1, col=13),
  Token(COLON, ':', line=1, col=15),
  Token(NEWLINE, '\n', line=1, col=16),
  Token(INDENT, '    ', line=2, col=1),
  Token(SHOW, 'show', line=2, col=5),
  Token(STRING, 'Adult', line=2, col=10),
  Token(NEWLINE, '\n', line=2, col=17),
  Token(DEDENT, '', line=3, col=1),
  Token(EOF, '', line=3, col=1)
]
```

### 4. Interview Key Point
Flowlang's Lexer uses **Maximal Munch** for multi-character operators (`<-`, `|>`) and maintains an **`indent_stack`** to emit `INDENT`/`DEDENT` tokens for Python-style indentation blocks. Unary minus (e.g. `-10`) is scanned as `MINUS` followed by `INT(10)`, leaving unary expression assembly to the Parser.

---

# Phase 3: `ast_nodes.py` (Abstract Syntax Tree Nodes)

- **INPUT**: None (Tree node class definitions).
- **OUTPUT**: Immutable AST node instances representing language constructs.

### 1. Flowchart

```text
ast_nodes.py
     │
     ├── ProgramNode       → whole program
     ├── VarDeclNode       → create variable
     ├── VarAssignNode     → change variable
     ├── ShowNode          → show something
     ├── WhenNode          → condition
     ├── FunctionDeclNode  → define function
     ├── GiveNode          → return value
     │
     ├── PipelineNode      → |> pipeline
     ├── KeepStageNode     → keep
     ├── Transform...      → transform
     ├── ShowStageNode     → pipeline show
     │
     ├── BinaryOpNode      → 2 + 3
     ├── UnaryOpNode       → -5 / not
     ├── LiteralNode       → 21 / "hello"
     ├── VarAccessNode     → age
     ├── FunctionCallNode  → square(5)
     └── ListNode          → [1,2,3]
```

### 2. Functions & Classes

#### `ASTNode` (Base Class)
- **WHAT**: Common base class for all AST nodes.
- **WHY**: Allows generic type checking across the AST.

#### Statement Nodes
- **`ProgramNode(statements)`**: Root node holding the sequence of top-level statements.
- **`VarDeclNode(name, value_expr)`**: Represents variable declaration (`let x <- 10`).
- **`VarAssignNode(name, value_expr)`**: Represents variable re-assignment (`x <- 20`).
- **`ShowNode(expr)`**: Represents output statement (`show "Hello"`).
- **`WhenNode(condition, then_block, otherwise_block)`**: Represents conditional branch (`when condition: ... otherwise: ...`).
- **`FunctionDeclNode(name, params, body_block)`**: Represents function declaration (`define func(x): ...`).
- **`GiveNode(value_expr)`**: Represents return statement (`give x * 2`).

#### Pipeline Nodes
- **`PipelineNode(target_expr, stages)`**: Holds initial collection expression and ordered list of transformation stages.
- **`KeepStageNode(element_var, condition_expr)`**: Represents filter stage (`keep x where x > 2`).
- **`TransformIntoStageNode(element_var, transform_expr)`**: Represents expression mapping stage (`transform x into x * 10`).
- **`TransformUsingStageNode(element_var, function_name)`**: Represents function mapping stage (`transform x using process`).
- **`ShowStageNode()`**: Represents terminal output stage (`show`).

#### Expression Nodes
- **`BinaryOpNode(left, op, right)`**: Represents binary infix operation (`a + b`, `x == y`).
- **`UnaryOpNode(op, operand)`**: Represents unary prefix operation (`-10`, `not true`).
- **`LiteralNode(value)`**: Encapsulates atomic constant values (`42`, `3.14`, `"hello"`, `true`).
- **`VarAccessNode(name)`**: Represents reading a variable identifier (`x`).
- **`FunctionCallNode(callee_name, args)`**: Represents function invocation (`square(5)`).
- **`ListNode(elements)`**: Represents list literals (`[1, 2, 3]`).

### 3. Tiny Example

```text
Source snippet: "let age <- 21"

AST Node Structure:
VarDeclNode(
  name='age',
  value_expr=LiteralNode(21)
)
```

### 4. Interview Key Point
AST nodes represent the **structural meaning** of a program rather than raw text. Implementing `__eq__` on AST nodes allows direct structural assertion testing without needing visual string comparisons.

---

# Phase 4: `parser.py` (Recursive Descent Parser)

- **INPUT**: Sequenced list of tokens (`List[Token]`) from the Lexer.
- **OUTPUT**: Abstract Syntax Tree rooted at a `ProgramNode`.

### 1. Flowchart

```text
Token Stream (List[Token])
        ↓
     parse()
        ↓
   statement()
 ┌──────┬────────────┬─────────────┬─────────────┬──────────┐
 │      │            │             │             │          │
let    show        when         define        give     expression()
 │      │            │             │             │          │
 ↓      ↓            ↓             ↓             ↓          ↓
var_   show_       when_        function_      return_   pipeline_
decl() stmt()      stmt()       decl()         stmt()    expr()
 │      │            │             │             │          │
 └──────┴────────────┴─────────────┴─────────────┴──────────┘
                            ↓
                    ProgramNode(AST)
```

--------------------------------------------------------------------------------

                         TOKENS
                            ↓
                         parse()
                      [parse program]
                            ↓
                      statement()
                    [find statement type]
                            ↓
              ┌─────────────┼──────────────┐
              ↓             ↓              ↓
        declaration        when          function
        [declare variable] [check condition] [define function]
              ↓             ↓              ↓
        VarDeclNode      WhenNode     FunctionDeclNode
                            │
                            ↓
                      expression()
                    [parse an expression]
                            ↓
                 pipeline_expression()
                    [parse |> pipelines]
                            ↓
                      logic_or()
                    [handle OR logic]
                            ↓
                     logic_and()
                    [handle AND logic]
                            ↓
                     logic_not()
                    [handle NOT logic]
                            ↓
                     comparison()
                    [compare two values]
                            ↓
                         term()
                    [handle + and -]
                            ↓
                        factor()
                    [handle * / %]
                            ↓
                         unary()
                    [handle unary -]
                            ↓
                       primary()
                  [parse basic values]
                            ↓
                           AST
                    [program structure]

### 2. Functions & Classes

#### `Parser` (Class)
- **WHAT**: Recursive descent parser that enforces grammar rules and builds an AST.
- **WHY**: Converts flat token streams into structural execution trees while enforcing precedence rules.

##### `Parser.__init__(tokens)`
- **WHAT**: Initializes parser cursor over token list.
- **WHY**: Sets up state for parsing tokens.

##### `Parser.peek()`, `Parser.peek_next()`, `Parser.advance()`
- **WHAT**: Lookahead and cursor movement utilities.
- **WHY**: Allows looking ahead at upcoming tokens without consuming them.

##### `Parser.check(token_type)`, `Parser.match(*token_types)`, `Parser.consume(token_type, error_message)`
- **WHAT**: Token matching and assertion helpers.
- **WHY**: Validates grammar syntax and raises descriptive syntax errors when expected tokens are missing.

##### `Parser.parse()`
- **WHAT**: Entry point driving top-level program parsing until `EOF`.
- **WHY**: Collects top-level statements into a `ProgramNode`.

##### `Parser.statement()`
- **WHAT**: Dispatches statement parsing based on leading keyword (`let`, `show`, `when`, `define`, `give`, assignment, or expression).
- **WHY**: Routes parsing to appropriate statement sub-routines.

##### `Parser.var_declaration()`, `Parser.var_assignment()`, `Parser.show_statement()`, `Parser.return_statement()`
- **WHAT**: Parses variable declarations, assignments, output statements, and return statements.
- **WHY**: Constructs corresponding statement AST nodes.

##### `Parser.when_statement()`
- **WHAT**: Parses `when condition: block (otherwise: block)?`.
- **WHY**: Handles conditional branch structures into `WhenNode`.

##### `Parser.function_declaration()`
- **WHAT**: Parses `define name(params): block`.
- **WHY**: Captures function signatures and parameter lists into `FunctionDeclNode`.

##### `Parser.block()`
- **WHAT**: Consumes `INDENT`, parses statements until `DEDENT`.
- **WHY**: Encapsulates Python-style indented code blocks.

##### Precedence Hierarchy: `expression()` $\rightarrow$ `pipeline_expression()` $\rightarrow$ `logic_or()` $\rightarrow$ `logic_and()` $\rightarrow$ `logic_not()` $\rightarrow$ `comparison()` $\rightarrow$ `term()` $\rightarrow$ `factor()` $\rightarrow$ `unary()` $\rightarrow$ `primary()`
- **WHAT**: Nested expression parsing methods.
- **WHY**: Enforces operator precedence mathematically (e.g. `*` before `+`, `not` before `and`).

##### `Parser.pipeline_expression()`, `Parser.pipeline_stage()`
- **WHAT**: Parses pipeline target and stages (`|> keep`, `|> transform`, `|> show`).
- **WHY**: Implements Flowlang's signature pipeline syntax. Uses lookahead past line breaks to chain multi-line pipelines.

### 3. Tiny Example

```text
Tokens Input:
[WHEN, IDENTIFIER('age'), GREATER_EQUAL, INT(18), COLON, NEWLINE, INDENT, SHOW, STRING('Adult'), NEWLINE, DEDENT]

Parsed AST Output:
ProgramNode([
  WhenNode(
    condition=BinaryOpNode(VarAccessNode('age'), '>=', LiteralNode(18)),
    then_block=[ShowNode(LiteralNode('Adult'))],
    otherwise_block=None
  )
])
```

### 4. Interview Key Point
Flowlang uses a **Recursive Descent Parser** with explicit precedence levels. Multi-line pipeline operations (`|>`) use lookahead past line-control tokens (`NEWLINE`, `INDENT`, `DEDENT`) so pipeline chains are bound to the root target expression rather than capturing nested stage conditions.

---

# Phase 5: `interpreter.py` & `environment.py` (Tree-Walking Interpreter Overview)

### Phase 5 Complete Execution Workflow

```text
               AST (ProgramNode)
                      ↓
               evaluate(node, env)
                      │
   ┌──────────────────┼──────────────────┬──────────────────┐
   │                  │                  │                  │
[Statements]     [Expressions]       [Functions]        [Pipelines]
   │                  │                  │                  │
   ├── VarDeclNode    ├── LiteralNode    ├── FunctionDecl   ├── KeepStage
   │   (env.define)   │   (returns val)  │   (FunctionValue)│   (filters list)
   ├── VarAssignNode  ├── VarAccessNode  ├── FunctionCall   ├── TransformInto
   │   (env.set)      │   (env.get)      │   (creates frame)│   (maps expr)
   ├── ShowNode       ├── BinaryOpNode   └── GiveNode       ├── TransformUsing
   │   (print/buffer) │   (math/logic)       (ReturnExcept) │   (maps func)
   └── WhenNode       └── UnaryOpNode                       └── ShowStage
       (child_env)        (negation)                            (prints list)
                      │
                      ↓
           Program Result / Output
```

---

# Phase 5.1: `environment.py` (Runtime Scope & Memory Manager)

- **INPUT**: Variable/function names, values, and optional parent scope references (`Environment`).
- **OUTPUT**: Value lookups, variable re-assignments, or scope resolution errors (`NameError`).

### 1. Flowchart

```text
Environment (Lexical Scoping Chain)

Global Environment (parent = None)
   └── values: {"x": 100}
          ▲
          │ (parent pointer)
Local Environment
   └── values: {"y": 50}

  get("y")  ──> found in Local Environment (50)
  get("x")  ──> not in Local, follows parent ──> found in Global Environment (100)
```

### 2. Functions & Classes

#### `Environment` (Class)
- **WHAT**: Manages variable symbol tables (`values`) and lexical scope parent pointers (`parent`).
- **WHY**: Stores variables during execution and enables nested scoping (inner scopes reading outer scope variables).

##### `Environment.__init__(parent=None)`
- **WHAT**: Initializes an empty values dictionary and links to an optional parent environment.
- **WHY**: Sets up local environment memory and establishes the parent scope lookup chain.

##### `Environment.define(name, value)`
- **WHAT**: Binds a variable name to a value strictly in the **current local scope**.
- **WHY**: Used for `let` variable declarations and function parameter bindings, enabling local variable shadowing.

##### `Environment.set(name, value)`
- **WHAT**: Reassigns an existing variable. Searches current scope first, then recursively searches parent environments.
- **WHY**: Used for variable re-assignment (`x <- 20`) without creating accidental local duplicates.

##### `Environment.get(name)`
- **WHAT**: Retrieves a variable's value by searching the local scope and bubbling up through parent environments.
- **WHY**: Evaluates variable lookups in expressions and raises `NameError` if the variable is undefined.

### 3. Tiny Example

```text
Global Scope: define("age", 21)
Local Scope:  get("age") ──> 21 (bubbled up to parent)
Local Scope:  define("age", 25) ──> local shadowing (age=25 locally, age=21 globally)
```

### 4. Interview Key Point
Flowlang's `Environment` implements **Lexical Scoping** via a singly-linked list of scope objects. `define()` creates bindings strictly in the immediate local scope (enabling shadowing), while `get()` and `set()` traverse parent pointers upward until the target variable is found or a `NameError` is raised.

---

# Phase 5.2: `interpreter.py` (Part 1 — Expression & Binary Operation Evaluator)

- **INPUT**: AST expression nodes (`LiteralNode`, `VarAccessNode`, `ListNode`, `UnaryOpNode`, `BinaryOpNode`) and an `Environment`.
- **OUTPUT**: Evaluated runtime Python value (`int`, `float`, `str`, `bool`, `list`).

### 1. Flowchart & Tree-Walking Trace

```text
Evaluating: 2 + 3 * 4

                  BinaryOpNode('+')
                     /        \
          LiteralNode(2)   BinaryOpNode('*')
                              /        \
                    LiteralNode(3)   LiteralNode(4)

Execution Trace:
1. evaluate(BinaryOpNode('+')) ──> evaluates left child LiteralNode(2) ──> 2
2. evaluates right child BinaryOpNode('*'):
   ├── evaluates LiteralNode(3) ──> 3
   ├── evaluates LiteralNode(4) ──> 4
   └── computes 3 * 4 ──> 12
3. computes 2 + 12 ──> 14
```

### 2. Functions & Node Evaluation Rules

#### `Interpreter` (Class)
- **WHAT**: Stateful tree-walking execution engine for Flowlang.
- **WHY**: Recursively visits AST nodes and computes mathematical, logical, and variable values at runtime.

##### `Interpreter.__init__()`
- **WHAT**: Initializes the root `global_env` Environment.
- **WHY**: Provides top-level global memory scope for program execution.

##### `Interpreter.evaluate(node, env=None)`
Central recursive evaluator for all AST expression node types:

- **`LiteralNode`** (`42`, `"hello"`, `true`): Returns `node.value` directly.
- **`VarAccessNode`** (`age`): Calls `env.get(node.name)` to fetch value from memory.
- **`ListNode`** (`[1, 2, 3]`): Evaluates `[self.evaluate(elem, env) for elem in node.elements]`.
- **`UnaryOpNode`** (`-x`, `not b`): Evaluates operand first, then applies `-` (with `TypeError` check for non-numbers) or `not`.
- **`BinaryOpNode`** (`+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `<=`, `>`, `>=`, `and`, `or`):
  - *Short-Circuit Logic (`and`/`or`)*: Evaluates left first; if left determines outcome (`false` for `and`, `true` for `or`), returns early without evaluating right.
  - *Arithmetic*: Computes math (`2+3`), string concat (`"a"+"b"`), and list concat (`[1]+[2]`). Throws `ZeroDivisionError` if dividing or moduloing by `0`.
  - *Comparisons*: Evaluates left & right, returns `True` or `False`.

### 3. Tiny Example

```text
AST Expression: BinaryOpNode(LiteralNode(2), '+', BinaryOpNode(LiteralNode(3), '*', LiteralNode(4)))
Evaluated Output: 14
```

### 4. Interview Key Point
`Interpreter.evaluate()` recursively walks expression AST subtrees. Logical operators (`and`, `or`) implement short-circuiting to prevent unnecessary evaluation, while arithmetic operators enforce strict type checking and zero-division error handling.

---

# Phase 5.3: `interpreter.py` (Part 2 — Statements & Control Flow)

- **INPUT**: Statement AST nodes (`ProgramNode`, `VarDeclNode`, `VarAssignNode`, `ShowNode`, `WhenNode`) and an `Environment`.
- **OUTPUT**: Memory state changes in `Environment`, conditional branching execution, and output stored in `output_buffer`.

### 1. Flowchart & Statement Execution Trace

```text
Executing:
let age <- 21
when age >= 18:
    show "Adult"

Execution Trace:
1. ProgramNode ──> executes VarDeclNode("age", 21) ──> calls env.define("age", 21)
2. WhenNode ──> evaluates condition (age >= 18) ──> True
3. Creates child scope: child_env = Environment(parent=global_env)
4. Executes ShowNode("Adult") in child_env ──> prints "Adult" & appends to output_buffer
```

### 2. Functions & Statement Execution Rules

#### `Interpreter` (Class Statement Handlers)
- **WHAT**: Executes statements that perform side-effects (memory mutations, console output, conditional branching).
- **WHY**: Powers multi-statement script execution, state management, and scope-isolated branching.

##### Statement Node Rules:
- **`ProgramNode(statements)`**: Iterates over `statements` and executes each sequentially.
- **`VarDeclNode(name, value_expr)`**: Evaluates `value_expr` and calls `env.define(name, value)` to create variable in local scope. Supports variable shadowing.
- **`VarAssignNode(name, value_expr)`**: Evaluates `value_expr` and calls `env.set(name, value)` to reassign existing variable (raises `NameError` if variable was never declared).
- **`ShowNode(expr)`**: Evaluates `expr`, formats booleans (`true`/`false`), prints to standard output, and records string in `self.output_buffer`.
- **`WhenNode(condition, then_block, otherwise_block)`**: Evaluates `condition`.
  - If truthy: Creates a child scope `child_env = Environment(parent=env)` and executes `then_block`.
  - If falsy & `otherwise_block` exists: Creates a child scope and executes `otherwise_block`.
  - *Why child scopes?*: Prevents block-local variables from polluting outer scope memory.

### 3. Tiny Example

```text
Code:
let age <- 15
when age >= 18:
    show "Adult"
otherwise:
    show "Minor"

Output Buffer: ["Minor"]
```

### 4. Interview Key Point
Statements perform side-effects while expressions produce values. Flowlang statement execution creates dedicated child `Environment` instances for `when`/`otherwise` blocks to enforce lexical scope isolation, preventing block-local variables from leaking into outer scopes.

---

# Phase 5.4: `interpreter.py` (Part 3 — Functions & Pipeline Mechanics)

- **INPUT**: Function & Pipeline AST nodes (`FunctionDeclNode`, `FunctionCallNode`, `GiveNode`, `PipelineNode`, `KeepStageNode`, `TransformIntoStageNode`, `TransformUsingStageNode`, `ShowStageNode`) and an `Environment`.
- **OUTPUT**: Function return values, transformed list collections, and printed pipeline output.

### 1. Flowchart & Pipeline Data Flow

```text
Executing Pipeline:
numbers
  |> keep x where x > 2
  |> transform x into x * 10
  |> show

Pipeline Data Flow:
Initial Target: [1, 2, 3, 4, 5]
       ↓
Stage 1: keep x where x > 2 ──> [3, 4, 5]
       ↓
Stage 2: transform x into x * 10 ──> [30, 40, 50]
       ↓
Stage 3: show ──> prints "[30, 40, 50]" & appends to output_buffer
```

### 2. Functions, Return Unwinding & Pipeline Rules

#### Function Execution & Return Mechanics:
- **`FunctionValue(name, params, body_block, closure_env)`**: Runtime function object storing parameter names, body statements, and closure environment.
- **`ReturnException(value)`**: Special control-flow exception raised by `give` to unwind the Python call stack immediately back to the caller.
- **`FunctionDeclNode(name, params, body_block)`**: Instantiates a `FunctionValue` and binds it in `env.define(name, func)`.
- **`FunctionCallNode(callee_name, args)`**: Resolves `FunctionValue`, validates parameter counts, creates a new call-frame `Environment(parent=func.closure_env)`, binds arguments, and executes body statements until `ReturnException` is caught.
- **`GiveNode(value_expr)`**: Evaluates return expression and raises `ReturnException(value)`.

#### Pipeline Stage Rules:
- **`PipelineNode(target_expr, stages)`**: Evaluates initial target collection, then streams the array sequentially through each stage.
- **`KeepStageNode(element_var, condition_expr)`**: Evaluates condition for each item `element_var` in a stage scope and filters matching items.
- **`TransformIntoStageNode(element_var, transform_expr)`**: Evaluates `transform_expr` for each item `element_var` and produces mapped list.
- **`TransformUsingStageNode(element_var, function_name)`**: Invokes `function_name(element_var)` for each item in the collection.
- **`ShowStageNode()`**: Formats collection into string `[30, 40, 50]`, prints to stdout, and records in `output_buffer`.

### 3. Tiny Example

```text
Code:
define square(x):
    give x * x

let nums <- [1, 2, 3]

nums
  |> transform x using square
  |> show

Output Buffer: ["1", "4", "9"]
```

### 4. Interview Key Point
Flowlang function calls create isolated call-frames linked to the function's `closure_env`, while `give` raises a `ReturnException` to cleanly unwind execution. Pipeline stages (`|>`) process data transformation streams sequentially by binding current list items to temporary stage variables inside temporary local environments.

---

# Phase 6: `semantic.py` (Static Semantic Analyzer & Symbol Table)

- **INPUT**: Abstract Syntax Tree (`ProgramNode`) from `parser.py`.
- **OUTPUT**: Validated AST if clean, or raises descriptive `SemanticError` exceptions.

### 1. Flowchart & Static Validation Rules

```text
               AST (ProgramNode)
                      ↓
           SemanticAnalyzer.analyze()
                      │
   ┌──────────────────┼──────────────────┬──────────────────┐
   │                  │                  │                  │
[Variable Checks] [Function Checks]  [Scope Checks]    [Pipeline Checks]
   │                  │                  │                  │
   ├── Undefined var  ├── Undefined func ├── Variable        ├── Undefined func
   │   (not in table) │   (not in table) │   redeclaration  │   in transform using
   └── Undeclared     └── Parameter      └── Return 'give'  └── Param count != 1
       assign             mismatch           outside func       in transform using
                      │
                      ↓
         AST Validated / SemanticError
```

### 2. Classes & Safety Validation Rules

#### `Symbol` & `SymbolTable` (Classes)
- **WHAT**: Tracks compile-time symbol metadata (`name`, `kind`: `"var"`/`"func"`, `param_count`) and nested scope parent pointers (`parent`).
- **WHY**: Maintains compile-time scope hierarchies for static safety checks without storing runtime values.

##### `SymbolTable.define_var(name)`, `SymbolTable.define_func(name, param_count)`
- **WHAT**: Registers a variable or function symbol in the current compile-time scope.
- **WHY**: Records declared symbols to prevent duplicate declarations and track function parameter counts.

##### `SymbolTable.lookup(name)`, `SymbolTable.is_defined_locally(name)`
- **WHAT**: Searches current and parent symbol tables for a symbol.
- **WHY**: Validates variable access and function calls at compile-time.

#### `SemanticAnalyzer` (Class)
- **WHAT**: Recursively walks AST nodes before runtime to enforce 5 static safety rules.
- **WHY**: Catches structural meaning errors before execution, returning clear compile-time error messages.

##### Static Safety Checks Enforced:
1. **Undefined Variable Check**: Reading a variable before `let` declaration raises `SemanticError: Undefined variable 'x'`.
2. **Variable Re-declaration Check**: Re-declaring `let x` in the same scope raises `SemanticError: Variable 'x' is already declared in this scope`.
3. **Undefined Function Check**: Calling `func(a)` or using `transform x using func` when `func` is un-declared raises `SemanticError: Undefined function 'func'`.
4. **Function Argument Mismatch**: Calling `square(1, 2)` when `square` expects 1 parameter raises `SemanticError: Function 'square' expects 1 arguments, but got 2`.
5. **Return (`give`) Outside Function**: Using `give` at top-level outside a `define` block raises `SemanticError: 'give' statement cannot be used outside of a function`.

### 3. Tiny Example

```text
Invalid Code:
show total + 5

Semantic Analyzer Output:
SemanticError: Undefined variable 'total' (Caught BEFORE runtime execution!)
```

### 4. Interview Key Point
Flowlang's `SemanticAnalyzer` separates **Syntax Validation** (Parser) from **Semantic Validation** (Static Checker). It uses a compile-time `SymbolTable` hierarchy to catch undefined variables, duplicate declarations, parameter count mismatches, and stray `give` statements before executing the program.

---

# Phase 7 & 8: Bytecode Compiler & Virtual Machine (Architecture Overview)

### Phase 7 & 8 Master Execution Workflow

```text
             AST (ProgramNode)
                     ↓
       [Phase 7.2: Compiler.compile()]
                     │
    ┌────────────────┼────────────────┐
    │                │                │
[Expressions]   [Statements]    [Conditionals]
    │                │                │
(LOAD_CONST)    (STORE_FAST)    (JUMP_IF_FALSE &
(BINARY_ADD)    (SHOW_OUTPUT)    Backpatching)
    │                │                │
    └────────────────┼────────────────┘
                     ↓
     Flowlang Bytecode Instructions [Phase 7.1: bytecode.py]
                     ↓
       [Phase 8: VirtualMachine.run()]
                     │
    ┌────────────────┼────────────────┐
    │                │                │
[Evaluation Stack] [Local/Global Mem] [Call Frames]
(push / pop)      (STORE_FAST)        (ip tracking)
    │                │                │
    └────────────────┼────────────────┘
                     ↓
          Program Execution / Output
```

---

# Phase 7.1: `bytecode.py` (Bytecode & Instruction Specifications)

- **INPUT**: None (Opcode Enum & Instruction Class definition file).
- **OUTPUT**: `Opcode` enum values and immutable `Instruction(opcode, operand)` objects.

### 1. Flowchart

```text
Bytecode Specification (bytecode.py)
   ├── Opcode Enum       ──> Categorizes instruction types (LOAD, STORE, ADD, JUMP, CALL, etc.)
   └── Instruction Class ──> Holds (opcode, optional_operand, line)
```

### 2. Classes & Opcode Categories

#### `Opcode` (Enum)
- **WHAT**: Defines all valid low-level instruction opcodes for Flowlang VM.
- **WHY**: Provides an instruction set architecture (ISA) for compilation and stack VM execution.
- **Categories**:
  - **Memory & Stack**: `LOAD_CONST`, `LOAD_FAST`, `STORE_FAST`, `POP_TOP`
  - **Arithmetic**: `BINARY_ADD`, `BINARY_SUB`, `BINARY_MUL`, `BINARY_DIV`, `BINARY_MOD`, `UNARY_NEGATE`
  - **Logic & Comparison**: `COMPARE_OP`, `UNARY_NOT`
  - **Collections**: `BUILD_LIST`
  - **Control Flow**: `JUMP_IF_FALSE`, `JUMP`
  - **Functions**: `MAKE_FUNCTION`, `CALL_FUNCTION`, `RETURN_VALUE`
  - **Pipelines**: `PIPELINE_KEEP`, `PIPELINE_TRANSFORM_INTO`, `PIPELINE_TRANSFORM_USING`
  - **Output**: `SHOW_OUTPUT`

#### `Instruction` (Class)
- **WHAT**: Represents a single bytecode instruction tuple `(opcode, operand, line)`.
- **WHY**: Packages low-level opcodes with arguments (e.g. `LOAD_CONST 42`, `JUMP_IF_FALSE 7`).

### 3. Tiny Example

```text
Source: let x <- 10 + 20

Compiled Bytecode Stream:
00: Instruction(LOAD_CONST, 10)
01: Instruction(LOAD_CONST, 20)
02: Instruction(BINARY_ADD)
03: Instruction(STORE_FAST, 'x')
```

### 4. Interview Key Point
`bytecode.py` defines Flowlang's Instruction Set Architecture (ISA). It converts complex nested AST nodes into a flat linear sequence of `Instruction(opcode, operand)` objects designed for fast stack-based virtual machine execution.

---

# Phase 7.2: `compiler.py` (AST to Bytecode Compiler)

- **INPUT**: Abstract Syntax Tree (`ProgramNode`) from `parser.py`.
- **OUTPUT**: A flat, linear sequence of compiled instructions (`List[Instruction]`).

### 1. Flowchart & Compilation Process

```text
               AST Node (Tree Structure)
                          ↓
                  Compiler.compile()
                          │
   ┌──────────────────────┼──────────────────────┬──────────────────────┐
   │                      │                      │                      │
[Expressions]        [Statements]           [Conditionals]         [Functions]
   │                      │                      │                      │
   ├── Literal            ├── VarDecl            ├── WhenNode           ├── FunctionDecl
   │   (LOAD_CONST)       │   (STORE_FAST)       │   (JUMP_IF_FALSE)    │   (MAKE_FUNCTION)
   ├── BinaryOp           ├── ShowNode           └── Patch Target       └── FunctionCall
   │   (BINARY_ADD/MUL)   │   (SHOW_OUTPUT)          Index                (CALL_FUNCTION)
                          ↓
              Flat Instruction Stream
```

### 2. Functions & Classes

#### `FunctionCode` (Class)
- **WHAT**: Metadata holder for compiled function bytecode (`name`, `params`, `instructions`).
- **WHY**: Packages function bytecode blocks so the VM can instantiate function call objects at runtime.

##### `FunctionCode.__init__(name, params, instructions)`
- **WHAT**: Initializes a compiled function metadata object.
- **WHY**: Binds function parameters and instruction lists together.

#### `Compiler` (Class)
- **WHAT**: Recursive AST-to-Bytecode compiler.
- **WHY**: Flattens nested tree structures into linear bytecode arrays.

##### `Compiler.__init__()`
- **WHAT**: Initializes an empty `instructions` list.
- **WHY**: Prepares state for accumulating compiled bytecode instructions.

##### `Compiler.emit(opcode, operand=None, line=1)`
- **WHAT**: Appends a new `Instruction` object to `self.instructions` and returns its index in the array.
- **WHY**: Central helper for building bytecode streams and obtaining instruction indices needed for jump backpatching.

##### `Compiler.compile(node)`
- **WHAT**: Main recursive visitor method that flattens AST nodes into bytecode instructions.
- **WHY**: Dispatches compilation for expressions (`LOAD`, `BINARY_ADD`), statements (`STORE`, `SHOW`), conditionals (`JUMP_IF_FALSE` with backpatching), functions (`MAKE_FUNCTION`, `CALL_FUNCTION`), and pipelines (`PIPELINE_KEEP`, `PIPELINE_TRANSFORM_INTO`, `PIPELINE_TRANSFORM_USING`).

### 3. Tiny Example

```text
Code:
when age >= 18:
    show "Adult"

Compiled Bytecode Stream:
00: Instruction(LOAD_FAST, 'age')
01: Instruction(LOAD_CONST, 18)
02: Instruction(COMPARE_OP, '>=')
03: Instruction(JUMP_IF_FALSE, 06)  ──> Jump to 06 if false
04: Instruction(LOAD_CONST, 'Adult')
05: Instruction(SHOW_OUTPUT)
06: (Next Instruction...)
```

### 4. Interview Key Point
Flowlang's `Compiler` transforms hierarchical AST trees into flat bytecode instruction lists. It uses a **Two-Pass Backpatching** technique for conditionals and jumps: emitting placeholder jump instructions first, compiling branch bodies, and then retroactively patching jump target indices once block sizes are known.

---

# Phase 8: `vm.py` (Stack-Based Virtual Machine)

- **INPUT**: A flat sequence of compiled instructions (`List[Instruction]`) from `compiler.py`.
- **OUTPUT**: VM program execution, state changes in `globals`, and output recorded in `output_buffer`.

### 1. Flowchart & Stack Execution Trace

```text
Virtual Machine Execution Loop (vm.py)

            run(instructions)
                    │
            while self.frames:
                    ↓
        fetch instr = frame.instructions[ip]
        advance frame.ip += 1
                    ↓
          match instr.opcode:
   ┌───────────┬───────────┬───────────┬───────────┐
   │           │           │           │           │
[Stack Ops]  [Math Ops]  [Jumps]    [Calls]    [Output]
   │           │           │           │           │
LOAD_CONST   BINARY_ADD  JUMP_IF_   CALL_FUNC  SHOW_OUTPUT
LOAD_FAST    BINARY_SUB  FALSE      RETURN_VAL (print &
STORE_FAST   COMPARE_OP  JUMP       (CallFrame) buffer)
   │           │           │           │           │
   └───────────┴───────────┴───────────┴───────────┘
                    ↓
         Next Instruction Loop (ip)
```

```text
Stack Execution Trace Example:
Executing: LOAD_CONST 10 -> LOAD_CONST 20 -> BINARY_ADD -> STORE_FAST 'x'

Instruction Stream                Evaluation Stack State
──────────────────                ──────────────────────
00: LOAD_CONST 10            ──>  [10]
01: LOAD_CONST 20            ──>  [10, 20]
02: BINARY_ADD               ──>  Pops 20, Pops 10 ──> Computes 10 + 20 ──> [30]
03: STORE_FAST 'x'           ──>  Pops 30 ──> Stores globals['x'] = 30 ──> []
```

### 2. Functions & Classes

#### `VMFunction` (Class)
- **WHAT**: Represents a compiled function object in VM memory.
- **WHY**: Stores function parameter names and compiled instruction sequences for invocation.

#### `CallFrame` (Class)
- **WHAT**: Represents an active function call frame on the VM call stack (`instructions`, `ip`, `locals`).
- **WHY**: Isolates local memory and tracks instruction pointer `ip` during nested function calls.

#### `VirtualMachine` (Class)
- **WHAT**: Stack-based execution engine simulation for Flowlang bytecode.
- **WHY**: Executes low-level opcodes line-by-line using an evaluation stack instead of tree walking.

##### `VirtualMachine.__init__()`
- **WHAT**: Initializes `self.stack`, `self.globals`, `self.frames`, and `self.output_buffer`.
- **WHY**: Prepares VM execution state and memory structures.

##### `VirtualMachine.run(instructions)`
Main VM execution loop driving instruction fetching, opcode decoding, and execution:
- **Stack Operations**: `LOAD_CONST` (push constant), `LOAD_FAST` (push variable), `STORE_FAST` (pop to variable), `POP_TOP` (pop & discard).
- **Arithmetic & Logic**: `BINARY_ADD`, `BINARY_SUB`, `BINARY_MUL`, `BINARY_DIV`, `BINARY_MOD`, `UNARY_NEGATE`, `UNARY_NOT`, `COMPARE_OP`.
- **Collections**: `BUILD_LIST` (pops `n` items and pushes Python list).
- **Control Flow**: `JUMP_IF_FALSE` (pops boolean; if False, updates `frame.ip`), `JUMP` (updates `frame.ip`).
- **Functions**: `MAKE_FUNCTION`, `CALL_FUNCTION` (pushes `CallFrame`), `RETURN_VALUE` (pops `CallFrame` and pushes return value).
- **Pipelines**: `PIPELINE_KEEP`, `PIPELINE_TRANSFORM_INTO`, `PIPELINE_TRANSFORM_USING` (streams sub-VM executions over collection items).
- **Output**: `SHOW_OUTPUT` (pops value, formats string, prints to stdout, appends to `output_buffer`).

### 3. Tiny Example

```text
Bytecode Input:
00: LOAD_CONST 'Hello Flowlang'
01: SHOW_OUTPUT

VM Output Buffer: ["Hello Flowlang"]
```

### 4. Interview Key Point
Flowlang's `VirtualMachine` simulates hardware CPU execution using a **Stack-Based Architecture** (`self.stack`). Instructions operate on stack operands using an Instruction Pointer (`ip`), enabling high-performance linear execution without tree traversal.

---

# Phase 9: `cli.py`, `flowlang.cmd` & `setup.py` (CLI Executable Entry Point & Packaging)

- **INPUT**: Command line arguments (`sys.argv`), `.flow` source file path, and optional mode flags.
- **OUTPUT**: File execution dispatch, printed execution outputs, AST/Bytecode inspection dumps, exit code `0` (success) or `1` (error).

### 1. Flowchart & Architecture

```text
User Command Line Invocation
   ├── flowlang examples/01_hello_world.flow
   ├── flowlang file.flow --mode interp
   ├── flowlang file.flow --dump-bytecode
   └── flowlang file.flow --dump-ast
                     │
                     ▼
          Executable Wrapper Layer
    ┌─────────────────────────┬─────────────────────────┐
    │ Windows Batch Launcher  │ Python Package Entry    │
    │     flowlang.cmd        │   setup.py (pip -e .)   │
    └────────────┬────────────┴────────────┬────────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                       cli.py (main)
                              │
                     argparse Parser
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
    Lexer -> Parser -> Semantic        Lexer -> Parser -> Semantic
            │                                   │
            ▼                                   ▼
    Bytecode Compiler                   Tree-Walking Interpreter
            │                               (`--mode interp`)
            ▼                                   │
      Stack VM Engine                           ▼
    (Default `--mode vm`)                     Output
            │
            ▼
          Output
```

### 2. Components & Structure

#### `cli.py` (Main CLI Module)
- **WHAT**: The unified command-line entry point for Flowlang.
- **WHY**: Provides argument parsing, driver logic, AST/Bytecode inspection dumps, and handles proper process exit codes (`0` vs `1`).

##### `dump_ast(node, indent)`
- **WHAT**: Generates a clean human-readable text tree representation of any AST node.
- **WHY**: Used when `--dump-ast` is passed to visualize parsed AST structures without raw dict clutter.

##### `run_file(filepath, mode, dump_ast_flag, dump_bytecode_flag)`
- **WHAT**: Executes a `.flow` file through the complete compilation pipeline:
  1. Lexer tokenization
  2. Parser AST generation (optional `--dump-ast`)
  3. Semantic Analysis checks
  4. Engine execution:
     - **Default VM Mode** (`--mode vm` / `compiler`): Compiles AST to bytecode (optional `--dump-bytecode`), then runs in `VirtualMachine()`.
     - **Interpreter Mode** (`--mode interp`): Evaluates AST directly via `Interpreter()`.
- **WHY**: Centralized execution pipeline driver for file execution.

##### `main(args_list)`
- **WHAT**: CLI entry point accepting `sys.argv` arguments, building `argparse.ArgumentParser`, and delegating to `run_file`.
- **WHY**: Allows invocation from Python command line or unit test runner.

---

#### `setup.py` (Python Package Entry Point Configuration)
- **WHAT**: Standard Setuptools configuration file.
- **WHY**: Registers `flowlang=cli:main` under `console_scripts`. Running `pip install -e .` allows users to invoke `flowlang file.flow` from **any terminal directory** system-wide.

```python
setup(
    name="flowlang",
    version="0.1.0",
    py_modules=["cli", "lexer", "parser", "semantic", "interpreter", "compiler", "vm", "bytecode", "ast_nodes", "environment", "tokens"],
    entry_points={
        "console_scripts": [
            "flowlang=cli:main",
        ],
    },
)
```

---

#### `flowlang.cmd` (Windows Batch Executable Wrapper)
- **WHAT**: A 2-line Windows command script in the project root:
  ```cmd
  @echo off
  python "%~dp0cli.py" %*
  ```
- **WHY**: Allows instant local terminal execution (`.\flowlang file.flow` or `flowlang file.flow`) without needing `python cli.py` or active pip installation.
---


### 3. Interview Key Point
Flowlang's CLI layer (`cli.py`) encapsulates the entire language frontend and backend into a single cohesive tool. By using Setuptools `console_scripts` in `setup.py` and a batch launcher `flowlang.cmd`, Flowlang behaves like a native compiled language binary (`flowlang program.flow`), defaulting to Bytecode Compiler + Stack VM execution while offering flags for inspection and fallback tree-walking interpretation.

