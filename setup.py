from setuptools import setup

setup(
    name="flowlang",
    version="0.1.0",
    description="A small, pipeline-oriented programming language with Compiler and Virtual Machine.",
    author="Flowlang Team",
    py_modules=[
        "cli",
        "lexer",
        "parser",
        "semantic",
        "interpreter",
        "compiler",
        "vm",
        "bytecode",
        "ast_nodes",
        "environment",
        "tokens",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "flowlang=cli:main",
        ],
    },
)
