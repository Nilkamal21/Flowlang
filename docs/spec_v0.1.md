# Flowlang v0.1 Formal Language Specification

**Version:** 0.1.0  
**Status:** Formal Specification & Standard Reference  
**Target Architectures:** Tree-Walking Interpreter & Stack-Based Bytecode Virtual Machine  

---

## 1. Executive Summary & Design Philosophy

Flowlang is a statically-analyzed, pipeline-oriented programming language engineered for functional data-transformation workflows, syntactic clarity, and pedagogical transparent compiler design. 

### 1.1 Core Principles
- **Pipeline-First Syntax**: Data operations flow left-to-right via the pipeline operator (`|>`), eliminating deeply nested function calls.
- **Declarative Iteration**: Flowlang excludes traditional `for` and `while` loop constructs. Data manipulation over collections is expressed declaratively using pipeline stages (`keep`, `transform`).
- **Pythonic Indentation**: Control structures and function bodies utilize whitespace indentation (`INDENT`/`DEDENT` tokens) with trailing colons (`:`).
- **Dual Execution Engines**: Source code can be executed directly via a Tree-Walking Interpreter or compiled to a compact Bytecode Instruction Set executed on a Stack Virtual Machine (VM).

---

## 2. Type System & Data Semantics

Flowlang is dynamically typed at runtime with static variable resolution and scoping rules.

### 2.1 Primitive & Composite Types
1. **Integer (`INT`)**: 64-bit signed numeric literals (e.g., `42`, `0`). Negative numbers are represented via unary negation (`-42`).
2. **Float (`FLOAT`)**: IEEE 754 double-precision floating-point literals (e.g., `3.14`, `0.001`).
3. **String (`STRING`)**: Immutable UTF-8 character sequences enclosed in double quotes (e.g., `"Hello Flowlang"`). Escape sequences supported: `\n`, `\t`, `\"`, `\\`.
4. **Boolean (`BOOLEAN`)**: Distinct boolean values `true` and `false`.
5. **List (`LIST`)**: Heterogeneous ordered collections enclosed in square brackets (e.g., `[1, "two", 3.0, true]`).

### 2.2 Truthiness Semantics
In conditional contexts (`when` expressions, `keep` pipeline clauses):
- `false` evaluates to `False`.
- `0` and `0.0` evaluate to `False`.
- Empty strings `""` evaluate to `False`.
- Empty lists `[]` evaluate to `False`.
- All other values evaluate to `True`.

---

## 3. Lexical Structure & Tokenization

### 3.1 Maximal Munch Scanning
The Lexer processes raw source code left-to-right, applying the **Maximal Munch Rule** (matching the longest possible valid token):
- `<-` is scanned as `ASSIGN`, not `<` followed by `-`.
- `|>` is scanned as `PIPE`, not `|` followed by `>`.
- `<=` and `>=` are scanned as comparison operators, not single punctuation symbols.

### 3.2 Reserved Keywords
```text
let        define     give       show       when       otherwise
keep       where      transform  into       using      and
or         not        true       false
```

### 3.3 Operators & Delimiters
```text
<-  |>  +   -   *   /   %   ==  !=  <   <=  >   >=  :   ,   (   )   [   ]
```

### 3.4 Indentation Tracking (`INDENT` / `DEDENT`)
The Lexer maintains an indentation stack initialized to `[0]`.
- At line beginnings (outside parentheses/brackets), if the current indentation level > top of stack: emit `INDENT` and push level.
- If current indentation level < top of stack: pop stack levels and emit `DEDENT` for each level until a matching level is found.
- Mismatched indentation levels trigger a lexical `IndentationError`.

---

## 4. Operator Precedence & Associativity

Operators are evaluated according to the following precedence hierarchy (lowest to highest):

| Level | Operator(s) | Category | Associativity | Description |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `\|>` | Pipeline | Left-to-Right | Data stream forwarding |
| **2** | `or` | Logical | Left-to-Right | Short-circuiting logical OR |
| **3** | `and` | Logical | Left-to-Right | Short-circuiting logical AND |
| **4** | `not` | Unary Logical | Right-to-Left | Logical negation |
| **5** | `==`, `!=`, `<`, `<=`, `>`, `>=` | Relational | Left-to-Right | Equality & ordering comparisons |
| **6** | `+`, `-` | Additive | Left-to-Right | Addition & subtraction |
| **7** | `*`, `/`, `%` | Multiplicative | Left-to-Right | Multiplication, division, modulo |
| **8** | `-` (unary) | Unary Negation | Right-to-Left | Arithmetic sign inversion |
| **9** | `()`, `[]` | Primary | Left-to-Right | Function call & list literal |

---

## 5. Formal EBNF Grammar

```ebnf
program          ::= statement* EOF ;

statement        ::= var_decl
                   | var_assign
                   | show_stmt
                   | when_stmt
                   | func_decl
                   | return_stmt
                   | expr_stmt ;

var_decl         ::= "let" IDENTIFIER "<-" expression NEWLINE ;
var_assign       ::= IDENTIFIER "<-" expression NEWLINE ;
show_stmt        ::= "show" expression NEWLINE ;

when_stmt        ::= "when" expression ":" NEWLINE block
                     ( "otherwise" ":" NEWLINE block )? ;

func_decl        ::= "define" IDENTIFIER "(" parameters? ")" ":" NEWLINE block ;
parameters       ::= IDENTIFIER ( "," IDENTIFIER )* ;
return_stmt      ::= "give" expression NEWLINE ;

block            ::= INDENT statement+ DEDENT ;

expression       ::= pipeline_expr ;
pipeline_expr    ::= logic_or ( "|>" pipeline_stage )* ;

pipeline_stage   ::= "keep" IDENTIFIER "where" expression
                   | "transform" IDENTIFIER "into" expression
                   | "transform" IDENTIFIER "using" IDENTIFIER
                   | "show" ;

logic_or         ::= logic_and ( "or" logic_and )* ;
logic_and        ::= logic_not ( "and" logic_not )* ;
logic_not        ::= "not" logic_not | comparison ;
comparison       ::= term ( ( "==" | "!=" | "<" | "<=" | ">" | ">=" ) term )* ;
term             ::= factor ( ( "+" | "-" ) factor )* ;
factor           ::= unary ( ( "*" | "/" | "%" ) unary )* ;
unary            ::= "-" unary | primary ;

primary          ::= INT | FLOAT | STRING | "true" | "false"
                   | IDENTIFIER
                   | IDENTIFIER "(" arguments? ")"
                   | "[" arguments? "]"
                   | "(" expression ")" ;

arguments        ::= expression ( "," expression )* ;
```

---

## 6. Abstract Syntax Tree (AST) Node Specification

| AST Node Class | Constructor Attributes | Description |
| :--- | :--- | :--- |
| `ProgramNode` | `statements: List[ASTNode]` | Root node representing full script |
| `VarDeclNode` | `name: str, value_expr: ASTNode` | Initial variable binding (`let x <- ...`) |
| `VarAssignNode` | `name: str, value_expr: ASTNode` | Reassignment to existing variable (`x <- ...`) |
| `ShowNode` | `expr: ASTNode` | Console print statement (`show ...`) |
| `WhenNode` | `condition: ASTNode, then_block: List[ASTNode], otherwise_block: Optional[List[ASTNode]]` | Conditional statement |
| `FunctionDeclNode` | `name: str, params: List[str], body_block: List[ASTNode]` | Function definition (`define ...`) |
| `GiveNode` | `value_expr: ASTNode` | Function return statement (`give ...`) |
| `PipelineNode` | `target_expr: ASTNode, stages: List[ASTNode]` | Pipeline expression target and stages |
| `KeepStageNode` | `var_name: str, condition_expr: ASTNode` | Pipeline filter stage (`keep x where cond`) |
| `TransformIntoStageNode`| `var_name: str, transform_expr: ASTNode` | Inline transform stage (`transform x into expr`) |
| `TransformUsingStageNode`| `var_name: str, func_name: str` | Function transform stage (`transform x using func`) |
| `ShowStageNode` | *(None)* | Pipeline output stage (`\|> show`) |
| `BinaryOpNode` | `left: ASTNode, op: str, right: ASTNode` | Binary operator evaluation |
| `UnaryOpNode` | `op: str, operand: ASTNode` | Unary operator evaluation (`-`, `not`) |
| `LiteralNode` | `value: Any` | Literal value (int, float, str, bool) |
| `VarAccessNode` | `name: str` | Variable lookup by identifier name |
| `FunctionCallNode` | `callee_name: str, args: List[ASTNode]` | Function invocation expression |
| `ListNode` | `elements: List[ASTNode]` | Array/list literal evaluation |

---

## 7. Bytecode Instruction Set Architecture (ISA)

Flowlang compiles AST nodes into linear bytecodes for execution on the Virtual Machine:

| Opcode Enum | Operand | Stack Delta | Description |
| :--- | :--- | :--- | :--- |
| `LOAD_CONST` | `value` | +1 | Push constant value onto stack |
| `LOAD_FAST` | `name` | +1 | Push value of variable `name` onto stack |
| `STORE_FAST` | `name` | -1 | Pop stack top into variable `name` |
| `POP_TOP` | None | -1 | Pop and discard stack top |
| `BINARY_ADD` | None | -1 | Pop `b`, pop `a`, push `a + b` |
| `BINARY_SUB` | None | -1 | Pop `b`, pop `a`, push `a - b` |
| `BINARY_MUL` | None | -1 | Pop `b`, pop `a`, push `a * b` |
| `BINARY_DIV` | None | -1 | Pop `b`, pop `a`, push `a / b` |
| `BINARY_MOD` | None | -1 | Pop `b`, pop `a`, push `a % b` |
| `UNARY_NEGATE` | None | 0 | Pop `a`, push `-a` |
| `UNARY_NOT` | None | 0 | Pop `a`, push `not a` |
| `COMPARE_OP` | `op` | -1 | Pop `b`, pop `a`, push `a (op) b` |
| `BUILD_LIST` | `count` | `1 - count` | Pop `count` items, push array list |
| `JUMP_IF_FALSE` | `target_idx`| -1 | Pop `cond`; if false, jump to `target_idx` |
| `JUMP` | `target_idx`| 0 | Unconditional jump to `target_idx` |
| `MAKE_FUNCTION` | `func_obj` | +1 | Push compiled function metadata object |
| `CALL_FUNCTION` | `arg_count` | `-arg_count`| Call function with `arg_count` popped args |
| `RETURN_VALUE` | None | 0 | Return stack top from call frame |
| `PIPELINE_KEEP` | `var_name, body`| 0 | Filter list on stack using sub-bytecode |
| `PIPELINE_TRANSFORM_INTO`| `var_name, body`| 0 | Transform list on stack using sub-bytecode |
| `PIPELINE_TRANSFORM_USING`| `var_name, func`| 0 | Transform list on stack using custom function |
| `SHOW_OUTPUT` | None | -1 | Pop top, print formatted output to console |

---

## 8. Compiler Backpatching & Jump Resolution

In `compiler.py`, control flow constructs (`when`/`otherwise`) utilize **Two-Pass Jump Backpatching**:
1. When compiling `when cond:`, emit `JUMP_IF_FALSE` with temporary target index `0`.
2. Save the index of the placeholder instruction.
3. Compile the `then_block` body statements.
4. Calculate the offset to the start of the `otherwise_block` (or next instruction).
5. Retroactively update (`backpatch`) the target instruction pointer in the placeholder instruction.

---

## 9. Virtual Machine Architecture & Call Stack Dynamics

The Virtual Machine (`VirtualMachine` in `vm.py`) executes compiled instructions using a call frame stack (`self.frames`):

```text
+-------------------------------------------------------+
|                     VirtualMachine                    |
|                                                       |
|  self.stack: [ item1, item2, item3 ... ]              |
|  self.globals: { "x": 10, "add": <VMFunction> }       |
|  self.output_buffer: [ "Hello Flowlang" ]             |
|                                                       |
|  self.frames: [ CallFrame_0 (main), CallFrame_1 ... ] |
+-------------------------------------------------------+
```

Each `CallFrame` isolates function local variables:
- `instructions`: Bytecode instruction sequence.
- `ip`: Instruction Pointer tracking current opcode.
- `locals`: Local variable binding environment.

---

## 10. Error Handling & Diagnostics Taxonomy

Flowlang classifies error handling into four explicit stages:

1. **Lexical Errors (`SyntaxError`)**: Invalid characters, unclosed string literals, invalid indentation depth.
2. **Parsing Errors (`SyntaxError`)**: Unexpected tokens, missing colons `:`, unmatched parentheses/brackets.
3. **Semantic Errors (`SemanticError`)**: Re-declaration of variables via `let`, access to undefined variables/functions.
4. **Runtime Errors (`RuntimeError` / `ZeroDivisionError`)**: Division by zero, incorrect function call argument count.
