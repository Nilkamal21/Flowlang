from typing import Any, List, Optional
from environment import Environment
from ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, VarAssignNode, ShowNode,
    WhenNode, FunctionDeclNode, GiveNode, PipelineNode, KeepStageNode,
    TransformIntoStageNode, TransformUsingStageNode, ShowStageNode,
    LiteralNode, VarAccessNode, FunctionCallNode, ListNode,
    UnaryOpNode, BinaryOpNode
)

class FunctionValue:
    """
    Represents a user-defined function in Flowlang runtime memory.
    """
    def __init__(self, name: str, params: List[str], body_block: List[ASTNode], closure_env: Environment):
        self.name = name
        self.params = params
        self.body_block = body_block
        self.closure_env = closure_env

    def __repr__(self) -> str:
        return f"<function {self.name}>"

class ReturnException(Exception):
    """
    Control-flow exception raised by 'give' to unwind execution back to the caller.
    """
    def __init__(self, value: Any):
        self.value = value

class Interpreter:
    """
    Tree-Walking Interpreter for Flowlang.
    Walks AST nodes and evaluates expressions / executes statements.
    """
    def __init__(self):
        self.global_env: Environment = Environment()
        self.output_buffer: List[str] = []

    def _stringify(self, val: Any) -> str:
        """Helper to format runtime values to Flowlang output format."""
        if isinstance(val, bool):
            return "true" if val else "false"
        if val is None:
            return "nil"
        if isinstance(val, list):
            return "[" + ", ".join(self._stringify(x) for x in val) + "]"
        return str(val)

    def evaluate(self, node: ASTNode, env: Optional[Environment] = None) -> Any:
        """
        Recursively evaluates an AST node in the given environment.
        """
        if env is None:
            env = self.global_env

        # --- STATEMENTS ---

        if isinstance(node, ProgramNode):
            result = None
            for stmt in node.statements:
                result = self.evaluate(stmt, env)
            return result

        if isinstance(node, VarDeclNode):
            val = self.evaluate(node.value_expr, env)
            env.define(node.name, val)
            return val

        if isinstance(node, VarAssignNode):
            val = self.evaluate(node.value_expr, env)
            env.set(node.name, val)
            return val

        if isinstance(node, ShowNode):
            val = self.evaluate(node.expr, env)
            text = self._stringify(val)
            print(text)
            self.output_buffer.append(text)
            return val

        if isinstance(node, WhenNode):
            cond_val = self.evaluate(node.condition, env)
            if bool(cond_val):
                child_env = Environment(parent=env)
                res = None
                for stmt in node.then_block:
                    res = self.evaluate(stmt, child_env)
                return res
            elif node.otherwise_block is not None:
                child_env = Environment(parent=env)
                res = None
                for stmt in node.otherwise_block:
                    res = self.evaluate(stmt, child_env)
                return res
            return None

        if isinstance(node, FunctionDeclNode):
            func_val = FunctionValue(node.name, node.params, node.body_block, env)
            env.define(node.name, func_val)
            return func_val

        if isinstance(node, GiveNode):
            val = self.evaluate(node.value_expr, env)
            raise ReturnException(val)

        # --- PIPELINES ---

        if isinstance(node, PipelineNode):
            current_val = self.evaluate(node.target_expr, env)

            for stage in node.stages:
                if isinstance(stage, KeepStageNode):
                    if not isinstance(current_val, list):
                        raise TypeError(f"Runtime Error: Pipeline 'keep' stage expects a list target, got '{type(current_val).__name__}'")
                    filtered = []
                    for item in current_val:
                        stage_env = Environment(parent=env)
                        stage_env.define(stage.element_var, item)
                        cond_res = self.evaluate(stage.condition_expr, stage_env)
                        if bool(cond_res):
                            filtered.append(item)
                    current_val = filtered

                elif isinstance(stage, TransformIntoStageNode):
                    if not isinstance(current_val, list):
                        raise TypeError(f"Runtime Error: Pipeline 'transform into' stage expects a list target, got '{type(current_val).__name__}'")
                    mapped = []
                    for item in current_val:
                        stage_env = Environment(parent=env)
                        stage_env.define(stage.element_var, item)
                        map_res = self.evaluate(stage.transform_expr, stage_env)
                        mapped.append(map_res)
                    current_val = mapped

                elif isinstance(stage, TransformUsingStageNode):
                    if not isinstance(current_val, list):
                        raise TypeError(f"Runtime Error: Pipeline 'transform using' stage expects a list target, got '{type(current_val).__name__}'")
                    func = env.get(stage.function_name)
                    if not isinstance(func, FunctionValue):
                        raise TypeError(f"Runtime Error: Pipeline 'transform using' expected function name, got '{type(func).__name__}'")
                    mapped = []
                    for item in current_val:
                        call_node = FunctionCallNode(stage.function_name, [LiteralNode(item)])
                        mapped.append(self.evaluate(call_node, env))
                    current_val = mapped

                elif isinstance(stage, ShowStageNode):
                    text = self._stringify(current_val)
                    print(text)
                    self.output_buffer.append(text)

                else:
                    raise RuntimeError(f"Runtime Error: Unknown pipeline stage type '{type(stage).__name__}'")

            return current_val

        # --- EXPRESSIONS ---

        if isinstance(node, LiteralNode):
            return node.value

        if isinstance(node, VarAccessNode):
            return env.get(node.name)

        if isinstance(node, ListNode):
            return [self.evaluate(elem, env) for elem in node.elements]

        if isinstance(node, FunctionCallNode):
            func = env.get(node.callee_name)
            if not isinstance(func, FunctionValue):
                raise TypeError(f"Runtime Error: '{node.callee_name}' is not a function")

            if len(node.args) != len(func.params):
                raise RuntimeError(
                    f"Runtime Error: Function '{func.name}' expects {len(func.params)} arguments, but got {len(node.args)}"
                )

            arg_vals = [self.evaluate(arg, env) for arg in node.args]
            call_env = Environment(parent=func.closure_env)
            for param, arg_val in zip(func.params, arg_vals):
                call_env.define(param, arg_val)

            try:
                res = None
                for stmt in func.body_block:
                    res = self.evaluate(stmt, call_env)
                return None
            except ReturnException as ret_ex:
                return ret_ex.value

        if isinstance(node, UnaryOpNode):
            val = self.evaluate(node.operand, env)
            if node.op == "-":
                if not isinstance(val, (int, float)):
                    raise TypeError(f"Runtime Error: Cannot apply unary '-' to non-numeric type '{type(val).__name__}'")
                return -val
            if node.op == "not":
                return not bool(val)
            raise RuntimeError(f"Runtime Error: Unknown unary operator '{node.op}'")

        if isinstance(node, BinaryOpNode):
            # Short-circuit logic operators
            if node.op == "and":
                left_val = self.evaluate(node.left, env)
                if not bool(left_val):
                    return left_val
                return self.evaluate(node.right, env)

            if node.op == "or":
                left_val = self.evaluate(node.left, env)
                if bool(left_val):
                    return left_val
                return self.evaluate(node.right, env)

            # Evaluate left and right operands
            left = self.evaluate(node.left, env)
            right = self.evaluate(node.right, env)

            if node.op == "+":
                if isinstance(left, str) or isinstance(right, str):
                    return self._stringify(left) + self._stringify(right)
                if isinstance(left, list) and isinstance(right, list):
                    return left + right
                return left + right

            if node.op == "-":
                return left - right

            if node.op == "*":
                return left * right

            if node.op == "/":
                if right == 0:
                    raise ZeroDivisionError("Runtime Error: Division by zero")
                return left / right

            if node.op == "%":
                if right == 0:
                    raise ZeroDivisionError("Runtime Error: Modulo by zero")
                return left % right

            if node.op == "==":
                return left == right

            if node.op == "!=":
                return left != right

            if node.op == "<":
                return left < right

            if node.op == "<=":
                return left <= right

            if node.op == ">":
                return left > right

            if node.op == ">=":
                return left >= right

            raise RuntimeError(f"Runtime Error: Unknown binary operator '{node.op}'")

        raise RuntimeError(f"Runtime Error: Cannot evaluate unknown AST node type '{type(node).__name__}'")
