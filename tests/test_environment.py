import pytest
from environment import Environment

def test_define_and_get_global():
    env = Environment()
    env.define("age", 21)
    env.define("name", "Nilkamal")

    assert env.get("age") == 21
    assert env.get("name") == "Nilkamal"

def test_reassign_variable():
    env = Environment()
    env.define("count", 1)
    env.set("count", 2)

    assert env.get("count") == 2

def test_nested_scope_lookup():
    global_env = Environment()
    global_env.define("x", 100)

    local_env = Environment(parent=global_env)
    assert local_env.get("x") == 100

def test_variable_shadowing():
    global_env = Environment()
    global_env.define("x", 10)

    local_env = Environment(parent=global_env)
    local_env.define("x", 20)  # Shadow outer x

    assert local_env.get("x") == 20
    assert global_env.get("x") == 10  # Outer x remains 10

def test_nested_reassignment():
    global_env = Environment()
    global_env.define("counter", 5)

    local_env = Environment(parent=global_env)
    local_env.set("counter", 10)  # Reassigns outer counter

    assert global_env.get("counter") == 10
    assert local_env.get("counter") == 10

def test_undefined_variable_get_error():
    env = Environment()
    with pytest.raises(NameError, match="Undefined variable 'unknown'"):
        env.get("unknown")

def test_undefined_variable_set_error():
    env = Environment()
    with pytest.raises(NameError, match="Cannot assign to undefined variable 'unknown'"):
        env.set("unknown", 42)
