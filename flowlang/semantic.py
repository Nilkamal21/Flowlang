from typing import Any, Dict, List, Optional
from .ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, VarAssignNode, ShowNode,
    WhenNode, FunctionDeclNode, GiveNode, PipelineNode, KeepStageNode,
    TransformIntoStageNode, TransformUsingStageNode, ShowStageNode,
    LiteralNode, VarAccessNode, FunctionCallNode, ListNode,
    UnaryOpNode, BinaryOpNode
)

class SemanticError(Exception):
    """Exception raised for compile-time semantic errors."""
    pass

class Symbol:
    """Represents a symbol (variable or function) in the symbol table."""
    def __init__(self, name: str, kind: str, param_count: int = 0):
        self.name = name
        self.kind = kind  # "var" or "func"
        self.param_count = param_count

class SymbolTable:
    """
    Tracks compile-time scope symbols and nesting for static validation.
    """
    def __init__(self, parent: Optional["SymbolTable"] = None, in_function: bool = False):
        self.symbols: Dict[str, Symbol] = {}
        self.parent: Optional[SymbolTable] = parent
        self.in_function: bool = in_function or (parent.in_function if parent else False)

    def define_var(self, name: str) -> None:
        self.symbols[name] = Symbol(name, "var")

    def define_func(self, name: str, param_count: int) -> None:
        self.symbols[name] = Symbol(name, "func", param_count)

    def lookup(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def is_defined_locally(self, name: str) -> bool:
        return name in self.symbols

class SemanticAnalyzer:
    """
    Static analyzer that walks the AST to enforce semantic safety rules.
    """
    def __init__(self):
        self.global_table: SymbolTable = SymbolTable()

    def analyze(self, node: ASTNode, table: Optional[SymbolTable] = None) -> None:
        if table is None:
            table = self.global_table

        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.analyze(stmt, table)
            return

        if isinstance(node, VarDeclNode):
            if table.is_defined_locally(node.name):
                raise SemanticError(f"Semantic Error: Variable '{node.name}' is already declared in this scope")
            self.analyze(node.value_expr, table)
            table.define_var(node.name)
            return

        if isinstance(node, VarAssignNode):
            sym = table.lookup(node.name)
            if sym is None:
                raise SemanticError(f"Semantic Error: Cannot assign to undefined variable '{node.name}'")
            if sym.kind != "var":
                raise SemanticError(f"Semantic Error: Cannot assign to function '{node.name}'")
            self.analyze(node.value_expr, table)
            return

        if isinstance(node, ShowNode):
            self.analyze(node.expr, table)
            return

        if isinstance(node, WhenNode):
            self.analyze(node.condition, table)
            then_table = SymbolTable(parent=table)
            for stmt in node.then_block:
                self.analyze(stmt, then_table)

            if node.otherwise_block is not None:
                otherwise_table = SymbolTable(parent=table)
                for stmt in node.otherwise_block:
                    self.analyze(stmt, otherwise_table)
            return

        if isinstance(node, FunctionDeclNode):
            if table.is_defined_locally(node.name):
                raise SemanticError(f"Semantic Error: Function or variable '{node.name}' is already declared in this scope")

            table.define_func(node.name, len(node.params))
            func_table = SymbolTable(parent=table, in_function=True)

            # Register parameters as local variables inside function scope
            for param in node.params:
                if func_table.is_defined_locally(param):
                    raise SemanticError(f"Semantic Error: Duplicate parameter '{param}' in function '{node.name}'")
                func_table.define_var(param)

            for stmt in node.body_block:
                self.analyze(stmt, func_table)
            return

        if isinstance(node, GiveNode):
            if not table.in_function:
                raise SemanticError("Semantic Error: 'give' statement cannot be used outside of a function")
            self.analyze(node.value_expr, table)
            return

        if isinstance(node, PipelineNode):
            self.analyze(node.target_expr, table)
            for stage in node.stages:
                if isinstance(stage, KeepStageNode):
                    stage_table = SymbolTable(parent=table)
                    stage_table.define_var(stage.element_var)
                    self.analyze(stage.condition_expr, stage_table)

                elif isinstance(stage, TransformIntoStageNode):
                    stage_table = SymbolTable(parent=table)
                    stage_table.define_var(stage.element_var)
                    self.analyze(stage.transform_expr, stage_table)

                elif isinstance(stage, TransformUsingStageNode):
                    sym = table.lookup(stage.function_name)
                    if sym is None or sym.kind != "func":
                        raise SemanticError(f"Semantic Error: Pipeline 'transform using' refers to undefined function '{stage.function_name}'")
                    if sym.param_count != 1:
                        raise SemanticError(f"Semantic Error: Function '{stage.function_name}' used in pipeline must take exactly 1 parameter, but takes {sym.param_count}")

                elif isinstance(stage, ShowStageNode):
                    pass

                else:
                    raise SemanticError(f"Semantic Error: Unknown pipeline stage type '{type(stage).__name__}'")
            return

        if isinstance(node, LiteralNode):
            return

        if isinstance(node, VarAccessNode):
            sym = table.lookup(node.name)
            if sym is None:
                raise SemanticError(f"Semantic Error: Undefined variable '{node.name}'")
            return

        if isinstance(node, FunctionCallNode):
            sym = table.lookup(node.callee_name)
            if sym is None:
                raise SemanticError(f"Semantic Error: Undefined function '{node.callee_name}'")
            if sym.kind != "func":
                raise SemanticError(f"Semantic Error: '{node.callee_name}' is a variable, not a function")
            if len(node.args) != sym.param_count:
                raise SemanticError(
                    f"Semantic Error: Function '{node.callee_name}' expects {sym.param_count} arguments, but got {len(node.args)}"
                )
            for arg in node.args:
                self.analyze(arg, table)
            return

        if isinstance(node, ListNode):
            for elem in node.elements:
                self.analyze(elem, table)
            return

        if isinstance(node, UnaryOpNode):
            self.analyze(node.operand, table)
            return

        if isinstance(node, BinaryOpNode):
            self.analyze(node.left, table)
            self.analyze(node.right, table)
            return

        raise SemanticError(f"Semantic Error: Unknown AST node type '{type(node).__name__}'")
