import sys
import os
import argparse
from typing import List, Optional

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from compiler import Compiler
from vm import VirtualMachine
from interpreter import Interpreter
import ast_nodes

VERSION = "Flowlang v0.1.0 (Bytecode Compiler & Stack VM Engine)"

def dump_ast(node: ast_nodes.ASTNode, indent: int = 0) -> str:
    """Helper to generate a clean text representation of the AST."""
    prefix = "  " * indent
    node_name = node.__class__.__name__
    lines = [f"{prefix}{node_name}"]
    
    for attr, val in node.__dict__.items():
        if isinstance(val, ast_nodes.ASTNode):
            lines.append(f"{prefix}  {attr}:")
            lines.append(dump_ast(val, indent + 2))
        elif isinstance(val, list):
            lines.append(f"{prefix}  {attr}: [")
            for item in val:
                if isinstance(item, ast_nodes.ASTNode):
                    lines.append(dump_ast(item, indent + 2))
                else:
                    lines.append(f"{prefix}    {repr(item)}")
            lines.append(f"{prefix}  ]")
        else:
            lines.append(f"{prefix}  {attr}: {repr(val)}")
    return "\n".join(lines)

def run_file(filepath: str, mode: str = "vm", dump_ast_flag: bool = False, dump_bytecode_flag: bool = False) -> int:
    """
    Executes a Flowlang source file (.flow).
    Returns exit code: 0 for success, 1 for error.
    """
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        return 1

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()

        # Phase 1: Lexing
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        # Phase 2: Parsing
        parser = Parser(tokens)
        ast = parser.parse()

        if dump_ast_flag:
            print("=== ABSTRACT SYNTAX TREE (AST) ===")
            print(dump_ast(ast))
            print("=================================")

        # Phase 3: Static Analysis
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)

        # Phase 4: Execution Engine
        if mode == "interp":
            interp = Interpreter()
            interp.evaluate(ast)
            return 0
        elif mode in ("vm", "compiler"):
            compiler = Compiler()
            instructions = compiler.compile(ast)
            
            if dump_bytecode_flag:
                print("=== BYTECODE DISASSEMBLY ===")
                for i, inst in enumerate(instructions):
                    print(f"{i:04d} | {inst}")
                print("============================")
                
            vm = VirtualMachine()
            vm.run(instructions)
            return 0
        else:
            print(f"Error: Unknown execution mode '{mode}'. Choose 'vm' or 'interp'.", file=sys.stderr)
            return 1

    except Exception as e:
        print(f"Flowlang Error: {e}", file=sys.stderr)
        return 1

def main(args_list: Optional[List[str]] = None) -> int:
    arg_parser = argparse.ArgumentParser(
        prog="flowlang",
        description="Flowlang v0.1 - Pipeline-Oriented Language Compiler & VM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  flowlang examples/01_hello_world.flow
  flowlang examples/01_hello_world.flow --mode interp
  flowlang examples/05_simple_pipeline.flow --dump-bytecode
  flowlang examples/05_simple_pipeline.flow --dump-ast
"""
    )

    arg_parser.add_argument(
        "file",
        nargs="?",
        help="Path to Flowlang source file (.flow)"
    )
    arg_parser.add_argument(
        "--mode",
        choices=["vm", "interp", "compiler"],
        default="vm",
        help="Execution engine: 'vm' for Bytecode Virtual Machine (default), 'interp' for Tree-Walking Interpreter"
    )
    arg_parser.add_argument(
        "--dump-ast",
        action="store_true",
        help="Print Abstract Syntax Tree (AST)"
    )
    arg_parser.add_argument(
        "--dump-bytecode",
        action="store_true",
        help="Disassemble compiled bytecode instructions"
    )
    arg_parser.add_argument(
        "-v", "--version",
        action="version",
        version=VERSION,
        help="Show Flowlang version info"
    )

    parsed_args = arg_parser.parse_args(args_list)

    if not parsed_args.file:
        arg_parser.print_help()
        return 0

    return run_file(
        filepath=parsed_args.file,
        mode=parsed_args.mode,
        dump_ast_flag=parsed_args.dump_ast,
        dump_bytecode_flag=parsed_args.dump_bytecode
    )

if __name__ == "__main__":
    sys.exit(main())
