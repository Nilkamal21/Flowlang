# 🌊 Flowlang Programming Language (v0.1.0)

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

## 🚀 Installation & Quickstart

### 1. Global Command Installation (Recommended)
Clone the repository and install locally using `pip`:
```bash
git clone https://github.com/Nilkamal21/Flowlang.git
cd Flowlang
pip install -e .
```
Now run any Flowlang script directly from your terminal:
```bash
flowlang examples/01_hello_world.flow
```

### 2. Local Windows Script Execution
You can also run scripts directly via the included `flowlang.cmd` script without installing `pip`:
```powershell
.\flowlang examples/01_hello_world.flow
```

---

## 🛠️ CLI Usage & Inspection Tools

The `flowlang` command defaults to high-performance **Bytecode Virtual Machine** execution (`--mode vm`), while allowing engine switching and compiler disassembly inspection flags:

```bash
# 1. Run using Bytecode Compiler & Virtual Machine (DEFAULT)
flowlang examples/10_data_processing_program.flow

# 2. Run using Tree-Walking Interpreter
flowlang examples/10_data_processing_program.flow --mode interp

# 3. Disassemble Compiled Bytecode Instructions
flowlang examples/05_simple_pipeline.flow --dump-bytecode

# 4. Print Abstract Syntax Tree (AST)
flowlang examples/05_simple_pipeline.flow --dump-ast

# 5. Display Version Information
flowlang --version
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

- **[Flowlang v0.1 Formal Language Specification](docs/spec_v0.1.md)**: Formal EBNF grammar, lexical rules, operator precedence table, AST schema, and ISA opcodes.
- **[Comprehensive Architecture & Interview Guide](EXPLANATION.md)**: Detailed phase-by-phase walkthrough with flowcharts, call stack trace diagrams, and component breakdowns.
