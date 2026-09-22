from typing import Any, Dict, Optional

class Environment:
    """
    Manages variable bindings and lexical scoping for Flowlang.
    """
    def __init__(self, parent: Optional["Environment"] = None):
        self.values: Dict[str, Any] = {}
        self.parent: Optional[Environment] = parent

    def define(self, name: str, value: Any) -> None:
        """
        Defines a new variable in the CURRENT local scope.
        """
        self.values[name] = value

    def set(self, name: str, value: Any) -> None:
        """
        Reassigns an existing variable.
        Searches current scope first, then recursively searches parent scopes.
        Raises NameError if variable is not defined anywhere.
        """
        if name in self.values:
            self.values[name] = value
            return
        if self.parent is not None:
            self.parent.set(name, value)
            return
        raise NameError(f"Runtime Error: Cannot assign to undefined variable '{name}'")

    def get(self, name: str) -> Any:
        """
        Retrieves the value of a variable.
        Searches current scope first, then recursively searches parent scopes.
        Raises NameError if variable is not defined anywhere.
        """
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise NameError(f"Runtime Error: Undefined variable '{name}'")
