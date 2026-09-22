from enum import Enum, auto
from typing import Any, Optional

class Opcode(Enum):
    """
    Bytecode Instruction Opcodes for Flowlang Virtual Machine.
    """
    # Stack & Memory Operations
    LOAD_CONST = auto()       # Push constant operand onto stack
    LOAD_FAST = auto()        # Push variable operand from local memory onto stack
    STORE_FAST = auto()       # Pop top stack value and store in variable operand
    POP_TOP = auto()          # Pop and discard top value from stack

    # Arithmetic Operations
    BINARY_ADD = auto()       # Pop b, Pop a -> Push (a + b)
    BINARY_SUB = auto()       # Pop b, Pop a -> Push (a - b)
    BINARY_MUL = auto()       # Pop b, Pop a -> Push (a * b)
    BINARY_DIV = auto()       # Pop b, Pop a -> Push (a / b)
    BINARY_MOD = auto()       # Pop b, Pop a -> Push (a % b)
    UNARY_NEGATE = auto()     # Pop a -> Push (-a)

    # Comparison & Logical Operations
    COMPARE_OP = auto()       # Pop b, Pop a -> Push (a op b) [op passed in operand]
    UNARY_NOT = auto()        # Pop a -> Push (not a)

    # List & Collection Operations
    BUILD_LIST = auto()       # Pop 'arg' items from stack -> Push Python list

    # Control Flow & Jumps
    JUMP_IF_FALSE = auto()    # Pop top value. If False, jump to target_ip operand
    JUMP = auto()             # Unconditionally jump to target_ip operand

    # Function Operations
    MAKE_FUNCTION = auto()    # Push a FunctionCode object onto stack
    CALL_FUNCTION = auto()    # Pop 'arg' arguments and function object -> Execute call
    RETURN_VALUE = auto()     # Return top stack value from function

    # Pipeline Operations
    PIPELINE_KEEP = auto()            # Filter list on stack using predicate
    PIPELINE_TRANSFORM_INTO = auto()  # Map list on stack using transform expression
    PIPELINE_TRANSFORM_USING = auto() # Map list on stack using named function

    # Output Operations
    SHOW_OUTPUT = auto()      # Pop top value, format, print, and record in output buffer

class Instruction:
    """
    Represents a single Bytecode Instruction in Flowlang.
    """
    def __init__(self, opcode: Opcode, operand: Optional[Any] = None, line: int = 1):
        self.opcode = opcode
        self.operand = operand
        self.line = line

    def __repr__(self) -> str:
        if self.operand is not None:
            return f"Instruction({self.opcode.name}, {repr(self.operand)})"
        return f"Instruction({self.opcode.name})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Instruction):
            return False
        return self.opcode == other.opcode and self.operand == other.operand
