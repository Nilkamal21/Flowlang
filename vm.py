from typing import Any, Dict, List, Optional
from bytecode import Opcode, Instruction

class VMFunction:
    """
    Represents a compiled function object in VM memory.
    """
    def __init__(self, name: str, params: List[str], instructions: List[Instruction]):
        self.name = name
        self.params = params
        self.instructions = instructions

    def __repr__(self) -> str:
        return f"<vm function {self.name}>"

class CallFrame:
    """
    Represents a single active function call frame on the VM call stack.
    """
    def __init__(self, instructions: List[Instruction], locals: Dict[str, Any]):
        self.instructions = instructions
        self.ip: int = 0
        self.locals = locals

class VirtualMachine:
    """
    Stack-Based Virtual Machine for Flowlang Bytecode execution.
    """
    def __init__(self):
        self.stack: List[Any] = []
        self.globals: Dict[str, Any] = {}
        self.frames: List[CallFrame] = []
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

    def run(self, instructions: List[Instruction]) -> Any:
        """
        Executes a sequence of bytecode instructions on the stack VM.
        """
        main_frame = CallFrame(instructions, {})
        self.frames = [main_frame]

        last_value: Any = None

        while self.frames:
            frame = self.frames[-1]

            if frame.ip >= len(frame.instructions):
                self.frames.pop()
                continue

            instr = frame.instructions[frame.ip]
            frame.ip += 1

            # --- STACK & MEMORY OPCODES ---

            if instr.opcode == Opcode.LOAD_CONST:
                self.stack.append(instr.operand)

            elif instr.opcode == Opcode.LOAD_FAST:
                var_name = instr.operand
                if var_name in frame.locals:
                    self.stack.append(frame.locals[var_name])
                elif var_name in self.globals:
                    self.stack.append(self.globals[var_name])
                else:
                    raise NameError(f"VM Runtime Error: Undefined variable '{var_name}'")

            elif instr.opcode == Opcode.STORE_FAST:
                val = self.stack.pop()
                var_name = instr.operand
                if len(self.frames) > 1:
                    frame.locals[var_name] = val
                else:
                    self.globals[var_name] = val

            elif instr.opcode == Opcode.POP_TOP:
                if self.stack:
                    self.stack.pop()

            # --- ARITHMETIC OPCODES ---

            elif instr.opcode == Opcode.BINARY_ADD:
                b = self.stack.pop()
                a = self.stack.pop()
                if isinstance(a, str) or isinstance(b, str):
                    self.stack.append(self._stringify(a) + self._stringify(b))
                elif isinstance(a, list) and isinstance(b, list):
                    self.stack.append(a + b)
                else:
                    self.stack.append(a + b)

            elif instr.opcode == Opcode.BINARY_SUB:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)

            elif instr.opcode == Opcode.BINARY_MUL:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)

            elif instr.opcode == Opcode.BINARY_DIV:
                b = self.stack.pop()
                a = self.stack.pop()
                if b == 0:
                    raise ZeroDivisionError("VM Runtime Error: Division by zero")
                self.stack.append(a / b)

            elif instr.opcode == Opcode.BINARY_MOD:
                b = self.stack.pop()
                a = self.stack.pop()
                if b == 0:
                    raise ZeroDivisionError("VM Runtime Error: Modulo by zero")
                self.stack.append(a % b)

            elif instr.opcode == Opcode.UNARY_NEGATE:
                a = self.stack.pop()
                if not isinstance(a, (int, float)):
                    raise TypeError(f"VM Runtime Error: Cannot apply unary '-' to non-numeric type '{type(a).__name__}'")
                self.stack.append(-a)

            elif instr.opcode == Opcode.UNARY_NOT:
                a = self.stack.pop()
                self.stack.append(not bool(a))

            # --- COMPARISON OPCODES ---

            elif instr.opcode == Opcode.COMPARE_OP:
                b = self.stack.pop()
                a = self.stack.pop()
                op = instr.operand
                if op == "==":
                    self.stack.append(a == b)
                elif op == "!=":
                    self.stack.append(a != b)
                elif op == "<":
                    self.stack.append(a < b)
                elif op == "<=":
                    self.stack.append(a <= b)
                elif op == ">":
                    self.stack.append(a > b)
                elif op == ">=":
                    self.stack.append(a >= b)

            # --- COLLECTION OPCODES ---

            elif instr.opcode == Opcode.BUILD_LIST:
                count = instr.operand
                elems = [self.stack.pop() for _ in range(count)][::-1]
                self.stack.append(elems)

            # --- CONTROL FLOW OPCODES ---

            elif instr.opcode == Opcode.JUMP_IF_FALSE:
                val = self.stack.pop()
                if not bool(val):
                    frame.ip = instr.operand

            elif instr.opcode == Opcode.JUMP:
                frame.ip = instr.operand

            # --- FUNCTION OPCODES ---

            elif instr.opcode == Opcode.MAKE_FUNCTION:
                func_code = instr.operand
                vm_func = VMFunction(func_code.name, func_code.params, func_code.instructions)
                self.stack.append(vm_func)

            elif instr.opcode == Opcode.CALL_FUNCTION:
                arg_count = instr.operand
                func = self.stack.pop()
                if not isinstance(func, VMFunction):
                    raise TypeError(f"VM Runtime Error: Target is not a callable function")

                args = [self.stack.pop() for _ in range(arg_count)][::-1]
                call_locals = {p: a for p, a in zip(func.params, args)}
                new_frame = CallFrame(func.instructions, call_locals)
                self.frames.append(new_frame)

            elif instr.opcode == Opcode.RETURN_VALUE:
                val = self.stack.pop()
                self.frames.pop()
                if self.frames:
                    self.stack.append(val)
                else:
                    return val

            # --- PIPELINE OPCODES ---

            elif instr.opcode == Opcode.PIPELINE_KEEP:
                element_var, cond_instrs = instr.operand
                current_list = self.stack.pop()
                if not isinstance(current_list, list):
                    raise TypeError("VM Runtime Error: Pipeline 'keep' expects a list target")

                filtered = []
                for item in current_list:
                    sub_vm = VirtualMachine()
                    sub_vm.globals = dict(self.globals)
                    sub_vm.globals[element_var] = item
                    res = sub_vm.run(cond_instrs)
                    if bool(res):
                        filtered.append(item)
                self.stack.append(filtered)

            elif instr.opcode == Opcode.PIPELINE_TRANSFORM_INTO:
                element_var, transform_instrs = instr.operand
                current_list = self.stack.pop()
                if not isinstance(current_list, list):
                    raise TypeError("VM Runtime Error: Pipeline 'transform into' expects a list target")

                mapped = []
                for item in current_list:
                    sub_vm = VirtualMachine()
                    sub_vm.globals = dict(self.globals)
                    sub_vm.globals[element_var] = item
                    res = sub_vm.run(transform_instrs)
                    mapped.append(res)
                self.stack.append(mapped)

            elif instr.opcode == Opcode.PIPELINE_TRANSFORM_USING:
                func_name = instr.operand
                current_list = self.stack.pop()
                if not isinstance(current_list, list):
                    raise TypeError("VM Runtime Error: Pipeline 'transform using' expects a list target")

                func = self.globals.get(func_name)
                if not isinstance(func, VMFunction):
                    raise TypeError(f"VM Runtime Error: Pipeline 'transform using' expected function '{func_name}'")

                mapped = []
                for item in current_list:
                    call_instrs = [
                        Instruction(Opcode.LOAD_CONST, item),
                        Instruction(Opcode.LOAD_FAST, func_name),
                        Instruction(Opcode.CALL_FUNCTION, 1)
                    ]
                    sub_vm = VirtualMachine()
                    sub_vm.globals = dict(self.globals)
                    res = sub_vm.run(call_instrs)
                    mapped.append(res)
                self.stack.append(mapped)

            # --- OUTPUT OPCODES ---

            elif instr.opcode == Opcode.SHOW_OUTPUT:
                val = self.stack.pop()
                text = self._stringify(val)
                print(text)
                self.output_buffer.append(text)
                last_value = val

        if self.stack:
            return self.stack[-1]
        return last_value
