# 🌊 Flowlang Programming Language (v0.1.0)

[![PyPI version](https://img.shields.io/pypi/v/flowlang-lang.svg)](https://pypi.org/project/flowlang-lang/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **A modern, pipeline-oriented programming language designed for expressive data transformation workflows, readable syntax, and dual-engine execution (Tree-Walking Interpreter & Stack-Based Bytecode VM).**

---

## 🌟 Key Highlights

- **Pipeline Operator (`|>`)**: Clean left-to-right data stream transformations without nested function calls.
- **Declarative Data Operations**: High-level data filtering (`keep`) and mapping (`transform into`, `transform using`).
- **Pythonic Block Syntax**: Indentation-based scope blocks (`INDENT`/`DEDENT`) with trailing colons (`:`).
- **Dual Execution Engine**:
  - 🌳 **Tree-Walking Interpreter**: Direct AST evaluation for fast inspection.
  - ⚡ **Stack-Based Virtual Machine**: Two-pass backpatching compiler & stack bytecode VM execution.
- **Static Semantic Analysis**: Scope and variable declaration verification before execution.
- **CLI & Packaging Support**: Native `flowlang <file.flow>` command with bytecode disassembly and AST visualization tools.

---

## 🏗️ System Architecture & Compiler Pipeline

```text
                               ┌───────────────────────────────┐
                               │  Flowlang Source Code (.flow) │
                               └───────────────┬───────────────┘
                                               │
                                     Lexer (Maximal Munch)
                                               │
                                     Parser (Formal EBNF)
                                               │
                                   Abstract Syntax Tree (AST)
                                               │
                                    Static Semantic Analyzer
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
          Tree-Walking Interpreter                         Bytecode Compiler
             (`--mode interp`)                             (Two-Pass Backpatch)
                       │                                               │
                       │                                    Instruction Set (ISA)
                       │                                               │
                       │                                    Stack Virtual Machine
                       │                                       (`--mode vm`)
                       ▼                                               ▼
              Program Output                                  Program Output
```

---

## 🚀 Installation & Usage

There are two primary ways to install and use Flowlang:

### 1. CLI Way (Recommended for running `.flow` files from terminal)

For executing `.flow` source files directly from your terminal, installing via **`pipx`** is recommended because it manages the command-line executable and path reliably in an isolated environment:

```bash
pipx install flowlang-lang
```

Alternative: `pip install flowlang-lang`

Once installed, use the **`flowlang`** CLI executable:

```bash
# Display version
flowlang --version

# Display help and usage options
flowlang --help

# Run a Flowlang program (Default: Bytecode Compiler & Virtual Machine)
flowlang program.flow
flowlang examples/01_hello_world.flow

# Explicitly choose execution engine
flowlang program.flow --mode vm       # Stack Virtual Machine
flowlang program.flow --mode interp   # Tree-Walking Interpreter
```

---

### 2. Python Package Way (Using Flowlang from Python)

To import and use Flowlang programmatically inside Python applications:

```bash
pip install flowlang-lang
```

You can import **`flowlang`** in Python to tokenize, parse, analyze, evaluate, or compile Flowlang source code using the exported API:

```python
import flowlang

source_code = """
let x <- 10
let y <- 20
show x + y
"""

# 1. Lexical Analysis & Parsing
lexer = flowlang.Lexer(source_code)
tokens = lexer.tokenize()

parser = flowlang.Parser(tokens)
ast = parser.parse()

# 2. Option A: Execute via Stack Virtual Machine
compiler = flowlang.Compiler()
instructions = compiler.compile(ast)

vm = flowlang.VirtualMachine()
vm.run(instructions)
print(vm.output_buffer)  # ['30']

# 3. Option B: Evaluate via Tree-Walking Interpreter
interpreter = flowlang.Interpreter()
interpreter.evaluate(ast)
print(interpreter.output_buffer)  # ['30']
```

---

### 3. Install from GitHub Source (Development)

Source code and development tools are available on GitHub:

```bash
git clone https://github.com/Nilkamal21/Flowlang.git
cd Flowlang
pip install -e .
```

---

## 🛠️ CLI Inspection Tools

```bash
# Disassemble Compiled Bytecode Instructions
flowlang examples/05_simple_pipeline.flow --dump-bytecode

# Print Abstract Syntax Tree (AST)
flowlang examples/05_simple_pipeline.flow --dump-ast
```

---

## 💡 Syntax Showcase & Language Features

### 1. Variables & Expressions
```flowlang
let greeting <- "Hello, Flowlang!"
let a <- 10
let b <- 3
let result <- (a + b) * (a - b)

show greeting
show result
```

### 2. Conditional Logic (`when` / `otherwise`)
```flowlang
let score <- 85
let passing_grade <- 70

when score >= passing_grade:
    show "Status: Passed"
otherwise:
    show "Status: Failed"
```

### 3. User-Defined Functions (`define` / `give`)
```flowlang
define square(n):
    give n * n

define calculate_tax(amount):
    when amount > 100:
        give amount * 0.15
    otherwise:
        give amount * 0.05

show square(7)
show calculate_tax(120)
```

### 4. Declarative Pipeline Transformations (`|>`)
```flowlang
define double_val(val):
    give val * 2

let raw_data <- [-5, 10, -3, 8, 0, 15]

# Filter positive numbers, double them via function, and output result
raw_data
  |> keep item where item > 0
  |> transform item using double_val
  |> show
```

---

## 📁 Sample Programs Gallery (`examples/`)

Flowlang includes 10 sample programs demonstrating language constructs:

| File | Description | Highlights |
| :--- | :--- | :--- |
| **[01_hello_world.flow](file:///C:/Users/adhik/OneDrive/Desktop/Flowlang/examples/01_hello_world.flow)** | Minimal starter program | Variable declarations, string output |
| **[02_arithmetic.flow](file:///C:/Users/adhik/OneDrive/Desktop/Flowlang/examples/02_arithmetic.flow)** | Math operations | Precedence, modulo, negative numbers |
| **[03_conditionals.flow](file:///C:/Users/adhik/OneDrive/Desktop/Flowlang/examples/03_conditionals.flow)** | Control flow | `when` / `otherwise`, logical `and`/`or` |
| **[04_functions.flow](file:///C:/Users/adhik/OneDrive/Desktop/Flowlang/examples/04_functions.flow)** | Subroutines | `define`, `give`, argument passing |
| **[05_simple_pipeline.flow](file:///C:/Users/adhik/OneDrive/Desktop/Flowlang/examples/05_simple_pipeline.flow)** | Pipelines | Inline list filtering and mapping |
| **[06_function_pipeline.flow](file:///C:/Users/adhik/OneDrive/Desktop/Flowlang/examples/06_function_pipeline.flow)** | Pipelines | Using custom functions in pipeline stages |
| **[07_nested_conditionals.flow](file:///C:/Users/adhik/OneDrive/Desktop/Flowlang/examples/07_nested_conditionals.flow)** | Branching | Multi-level decision trees |
| **[08_complex_pipeline.flow](file:///C:/Users/adhik/OneDrive/Desktop/Flowlang/examples/08_complex_pipeline.flow)** | Data streams | Multi-stage pipeline processing |
| **[09_math_library.flow](file:///C:/Users/adhik/OneDrive/Desktop/Flowlang/examples/09_math_library.flow)** | Standard math | Custom `abs`, `max`, `min`, `clamp` |
| **[10_data_processing_program.flow](file:///C:/Users/adhik/OneDrive/Desktop/Flowlang/examples/10_data_processing_program.flow)** | Full application | E-commerce order processing pipeline |

---

## 🧪 Testing & Quality Assurance

Flowlang maintains 100% test coverage across all compiler components:

```bash
# Run complete unit & integration test suite (74 tests)
python -m pytest
```

---

## 📂 Project Directory Sitemap

```text
Flowlang/
├── flowlang/                   # Core Package Directory
│   ├── __init__.py             # Package exports & version (__version__)
│   ├── tokens.py               # Lexical token definitions & TokenType enum
│   ├── lexer.py                # Scanner & Pythonic indentation logic (INDENT/DEDENT)
│   ├── parser.py               # EBNF grammar recursive descent parser
│   ├── ast_nodes.py            # AST node class hierarchy
│   ├── environment.py          # Scope environment memory manager
│   ├── interpreter.py          # Tree-Walking AST Interpreter
│   ├── semantic.py             # Static semantic analyzer & scope checker
│   ├── bytecode.py             # ISA Opcode enums & Instruction definitions
│   ├── compiler.py             # AST to Bytecode compiler with jump backpatching
│   ├── vm.py                   # Stack Virtual Machine execution engine
│   └── cli.py                  # Main CLI entry point & argument parser
├── docs/
│   └── spec_v0.1.md            # Formal Language Specification
├── examples/                   # 10 test & demonstration programs (.flow)
├── tests/                      # Pytest unit & integration test suite (74 tests)
├── .gitignore                  # Git ignore rules
├── EXPLANATION.md              # Comprehensive Architecture & Interview Guide
├── flowlang.cmd                # Windows executable launcher (`python -m flowlang.cli`)
├── pyproject.toml              # Modern PEP 517/518 build configuration
└── README.md                   # Project documentation homepage
```

---

## 📖 Documentation & References

- **[PyPI Official Package Page](https://pypi.org/project/flowlang-lang/)**: Official release metadata and wheel downloads.
- **[Flowlang v0.1 Formal Language Specification](docs/spec_v0.1.md)**: Formal EBNF grammar, lexical rules, operator precedence table, AST schema, and ISA opcodes.
- **[Comprehensive Architecture & Interview Guide](EXPLANATION.md)**: Detailed phase-by-phase walkthrough with flowcharts, call stack trace diagrams, and component breakdowns.
