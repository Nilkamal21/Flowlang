from typing import Any, List, Optional
from bytecode import Opcode, Instruction
from ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, VarAssignNode, ShowNode,
    WhenNode, FunctionDeclNode, GiveNode, PipelineNode, KeepStageNode,
    TransformIntoStageNode, TransformUsingStageNode, ShowStageNode,
    LiteralNode, VarAccessNode, FunctionCallNode, ListNode,
    UnaryOpNode, BinaryOpNode
)

class FunctionCode:
    """
    Metadata container for compiled function bytecode.
    """
    def __init__(self, name: str, params: List[str], instructions: List[Instruction]):
        self.name = name
        self.params = params
        self.instructions = instructions

    def __repr__(self) -> str:
        return f"<code object {self.name}, params={self.params}, instructions={len(self.instructions)}>"

class Compiler:
    """
    AST to Flowlang Bytecode Compiler.
    Flattens AST trees into sequential bytecode instructions.
    """
    def __init__(self):
        self.instructions: List[Instruction] = []

    def emit(self, opcode: Opcode, operand: Optional[Any] = None, line: int = 1) -> int:
        """Emits an instruction and returns its index in the bytecode stream."""
        instr = Instruction(opcode, operand, line)
        self.instructions.append(instr)
        return len(self.instructions) - 1

    def compile(self, node: ASTNode) -> List[Instruction]:
        """
        Recursively compiles an AST node into bytecode instructions.
        """
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.compile(stmt)
            return self.instructions

        # --- STATEMENTS ---

        if isinstance(node, VarDeclNode):
            self.compile(node.value_expr)
            self.emit(Opcode.STORE_FAST, node.name)
            return self.instructions

        if isinstance(node, VarAssignNode):
            self.compile(node.value_expr)
            self.emit(Opcode.STORE_FAST, node.name)
            return self.instructions

        if isinstance(node, ShowNode):
            self.compile(node.expr)
            self.emit(Opcode.SHOW_OUTPUT)
            return self.instructions

        if isinstance(node, WhenNode):
            self.compile(node.condition)
            # Emit JUMP_IF_FALSE with placeholder index 0
            jump_false_idx = self.emit(Opcode.JUMP_IF_FALSE, 0)

            for stmt in node.then_block:
                self.compile(stmt)

            if node.otherwise_block is not None:
                # Emit JUMP to skip otherwise block after then block runs
                jump_end_idx = self.emit(Opcode.JUMP, 0)
                # Patch jump_false_idx to point to start of otherwise block
                self.instructions[jump_false_idx].operand = len(self.instructions)

                for stmt in node.otherwise_block:
                    self.compile(stmt)

                # Patch jump_end_idx to point past otherwise block
                self.instructions[jump_end_idx].operand = len(self.instructions)
            else:
                # Patch jump_false_idx to point past then block
                self.instructions[jump_false_idx].operand = len(self.instructions)

            return self.instructions

        if isinstance(node, FunctionDeclNode):
            sub_compiler = Compiler()
            for stmt in node.body_block:
                sub_compiler.compile(stmt)

            # Ensure implicit return None if body didn't execute give
            sub_compiler.emit(Opcode.LOAD_CONST, None)
            sub_compiler.emit(Opcode.RETURN_VALUE)

            func_code = FunctionCode(node.name, node.params, sub_compiler.instructions)
            self.emit(Opcode.MAKE_FUNCTION, func_code)
            self.emit(Opcode.STORE_FAST, node.name)
            return self.instructions

        if isinstance(node, GiveNode):
            self.compile(node.value_expr)
            self.emit(Opcode.RETURN_VALUE)
            return self.instructions

        # --- PIPELINES ---

        if isinstance(node, PipelineNode):
            self.compile(node.target_expr)

            for stage in node.stages:
                if isinstance(stage, KeepStageNode):
                    sub_compiler = Compiler()
                    sub_compiler.compile(stage.condition_expr)
                    self.emit(Opcode.PIPELINE_KEEP, (stage.element_var, sub_compiler.instructions))

                elif isinstance(stage, TransformIntoStageNode):
                    sub_compiler = Compiler()
                    sub_compiler.compile(stage.transform_expr)
                    self.emit(Opcode.PIPELINE_TRANSFORM_INTO, (stage.element_var, sub_compiler.instructions))

                elif isinstance(stage, TransformUsingStageNode):
                    self.emit(Opcode.PIPELINE_TRANSFORM_USING, stage.function_name)

                elif isinstance(stage, ShowStageNode):
                    self.emit(Opcode.SHOW_OUTPUT)

                else:
                    raise RuntimeError(f"Compile Error: Unknown pipeline stage type '{type(stage).__name__}'")

            return self.instructions

        # --- EXPRESSIONS ---

        if isinstance(node, LiteralNode):
            self.emit(Opcode.LOAD_CONST, node.value)
            return self.instructions

        if isinstance(node, VarAccessNode):
            self.emit(Opcode.LOAD_FAST, node.name)
            return self.instructions

        if isinstance(node, ListNode):
            for elem in node.elements:
                self.compile(elem)
            self.emit(Opcode.BUILD_LIST, len(node.elements))
            return self.instructions

        if isinstance(node, FunctionCallNode):
            for arg in node.args:
                self.compile(arg)
            self.emit(Opcode.LOAD_FAST, node.callee_name)
            self.emit(Opcode.CALL_FUNCTION, len(node.args))
            return self.instructions

        if isinstance(node, UnaryOpNode):
            self.compile(node.operand)
            if node.op == "-":
                self.emit(Opcode.UNARY_NEGATE)
            elif node.op == "not":
                self.emit(Opcode.UNARY_NOT)
            else:
                raise RuntimeError(f"Compile Error: Unknown unary operator '{node.op}'")
            return self.instructions

        if isinstance(node, BinaryOpNode):
            if node.op == "and":
                self.compile(node.left)
                jump_false_idx = self.emit(Opcode.JUMP_IF_FALSE, 0)
                self.emit(Opcode.POP_TOP)
                self.compile(node.right)
                self.instructions[jump_false_idx].operand = len(self.instructions)
                return self.instructions

            if node.op == "or":
                self.compile(node.left)
                jump_false_idx = self.emit(Opcode.JUMP_IF_FALSE, 0)
                jump_end_idx = self.emit(Opcode.JUMP, 0)
                self.instructions[jump_false_idx].operand = len(self.instructions)
                self.emit(Opcode.POP_TOP)
                self.compile(node.right)
                self.instructions[jump_end_idx].operand = len(self.instructions)
                return self.instructions

            self.compile(node.left)
            self.compile(node.right)

            if node.op == "+":
                self.emit(Opcode.BINARY_ADD)
            elif node.op == "-":
                self.emit(Opcode.BINARY_SUB)
            elif node.op == "*":
                self.emit(Opcode.BINARY_MUL)
            elif node.op == "/":
                self.emit(Opcode.BINARY_DIV)
            elif node.op == "%":
                self.emit(Opcode.BINARY_MOD)
            elif node.op in ("==", "!=", "<", "<=", ">", ">="):
                self.emit(Opcode.COMPARE_OP, node.op)
            else:
                raise RuntimeError(f"Compile Error: Unknown binary operator '{node.op}'")

            return self.instructions

        raise RuntimeError(f"Compile Error: Cannot compile unknown AST node type '{type(node).__name__}'")
