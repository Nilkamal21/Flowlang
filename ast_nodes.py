from typing import Any, List, Optional

class ASTNode:
    """Base class for all Abstract Syntax Tree nodes in Flowlang."""
    pass

class ProgramNode(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

    def __repr__(self) -> str:
        return f"ProgramNode({self.statements})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ProgramNode) and self.statements == other.statements

class VarDeclNode(ASTNode):
    def __init__(self, name: str, value_expr: ASTNode):
        self.name = name
        self.value_expr = value_expr

    def __repr__(self) -> str:
        return f"VarDeclNode('{self.name}', {self.value_expr})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, VarDeclNode) and self.name == other.name and self.value_expr == other.value_expr

class VarAssignNode(ASTNode):
    def __init__(self, name: str, value_expr: ASTNode):
        self.name = name
        self.value_expr = value_expr

    def __repr__(self) -> str:
        return f"VarAssignNode('{self.name}', {self.value_expr})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, VarAssignNode) and self.name == other.name and self.value_expr == other.value_expr

class ShowNode(ASTNode):
    def __init__(self, expr: ASTNode):
        self.expr = expr

    def __repr__(self) -> str:
        return f"ShowNode({self.expr})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ShowNode) and self.expr == other.expr

class WhenNode(ASTNode):
    def __init__(self, condition: ASTNode, then_block: List[ASTNode], otherwise_block: Optional[List[ASTNode]] = None):
        self.condition = condition
        self.then_block = then_block
        self.otherwise_block = otherwise_block

    def __repr__(self) -> str:
        return f"WhenNode({self.condition}, then={self.then_block}, otherwise={self.otherwise_block})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, WhenNode)
            and self.condition == other.condition
            and self.then_block == other.then_block
            and self.otherwise_block == other.otherwise_block
        )

class FunctionDeclNode(ASTNode):
    def __init__(self, name: str, params: List[str], body_block: List[ASTNode]):
        self.name = name
        self.params = params
        self.body_block = body_block

    def __repr__(self) -> str:
        return f"FunctionDeclNode('{self.name}', params={self.params}, body={self.body_block})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, FunctionDeclNode)
            and self.name == other.name
            and self.params == other.params
            and self.body_block == other.body_block
        )

class GiveNode(ASTNode):
    def __init__(self, value_expr: ASTNode):
        self.value_expr = value_expr

    def __repr__(self) -> str:
        return f"GiveNode({self.value_expr})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, GiveNode) and self.value_expr == other.value_expr

class PipelineNode(ASTNode):
    def __init__(self, target_expr: ASTNode, stages: List[ASTNode]):
        self.target_expr = target_expr
        self.stages = stages

    def __repr__(self) -> str:
        return f"PipelineNode({self.target_expr}, stages={self.stages})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PipelineNode) and self.target_expr == other.target_expr and self.stages == other.stages

class KeepStageNode(ASTNode):
    def __init__(self, element_var: str, condition_expr: ASTNode):
        self.element_var = element_var
        self.condition_expr = condition_expr

    def __repr__(self) -> str:
        return f"KeepStageNode('{self.element_var}', {self.condition_expr})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, KeepStageNode)
            and self.element_var == other.element_var
            and self.condition_expr == other.condition_expr
        )

class TransformIntoStageNode(ASTNode):
    def __init__(self, element_var: str, transform_expr: ASTNode):
        self.element_var = element_var
        self.transform_expr = transform_expr

    def __repr__(self) -> str:
        return f"TransformIntoStageNode('{self.element_var}', {self.transform_expr})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, TransformIntoStageNode)
            and self.element_var == other.element_var
            and self.transform_expr == other.transform_expr
        )

class TransformUsingStageNode(ASTNode):
    def __init__(self, element_var: str, function_name: str):
        self.element_var = element_var
        self.function_name = function_name

    def __repr__(self) -> str:
        return f"TransformUsingStageNode('{self.element_var}', '{self.function_name}')"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, TransformUsingStageNode)
            and self.element_var == other.element_var
            and self.function_name == other.function_name
        )

class ShowStageNode(ASTNode):
    def __repr__(self) -> str:
        return "ShowStageNode()"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ShowStageNode)

class BinaryOpNode(ASTNode):
    def __init__(self, left: ASTNode, op: str, right: ASTNode):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self) -> str:
        return f"BinaryOpNode({self.left}, '{self.op}', {self.right})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, BinaryOpNode)
            and self.left == other.left
            and self.op == other.op
            and self.right == other.right
        )

class UnaryOpNode(ASTNode):
    def __init__(self, op: str, operand: ASTNode):
        self.op = op
        self.operand = operand

    def __repr__(self) -> str:
        return f"UnaryOpNode('{self.op}', {self.operand})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, UnaryOpNode) and self.op == other.op and self.operand == other.operand

class LiteralNode(ASTNode):
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self) -> str:
        return f"LiteralNode({repr(self.value)})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LiteralNode) and self.value == other.value

class VarAccessNode(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"VarAccessNode('{self.name}')"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, VarAccessNode) and self.name == other.name

class FunctionCallNode(ASTNode):
    def __init__(self, callee_name: str, args: List[ASTNode]):
        self.callee_name = callee_name
        self.args = args

    def __repr__(self) -> str:
        return f"FunctionCallNode('{self.callee_name}', args={self.args})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, FunctionCallNode)
            and self.callee_name == other.callee_name
            and self.args == other.args
        )

class ListNode(ASTNode):
    def __init__(self, elements: List[ASTNode]):
        self.elements = elements

    def __repr__(self) -> str:
        return f"ListNode({self.elements})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ListNode) and self.elements == other.elements
