# Flowlang VS Code Extension

Visual Studio Code language support for **Flowlang** — a modern, pipeline-oriented programming language with Compiler and Virtual Machine.

---

## ✨ Features

- 🎨 **Syntax Highlighting**: Full color highlighting for Flowlang v0.1 keywords (`let`, `define`, `give`, `show`, `when`, `otherwise`, `keep`, `where`, `transform`, `into`, `using`, `and`, `or`, `not`), operators (`<-`, `|>`), numbers, strings, comments, and functions.
- 💬 **Comments**: Single-line `#` comment support (`Toggle Line Comment`).
- 🔒 **Bracket Matching & Autoclosing**: Autocloses parentheses `()`, brackets `[]`, and double quotes `""`.
- 📐 **Indentation Rules**: Python-style indentation for blocks ending in `:` and automatic dedent for `otherwise:`.
- ⚡ **Code Snippets**: Fast autocomplete snippets for `let`, `define`, `when`, `pipeline`, and `show`.

---

## 🚀 Quickstart & Testing

1. Open a `.flow` file (e.g. `examples/01_hello_world.flow`).
2. VS Code will automatically detect the file language as **Flowlang**.

---

## 🛠️ Building & Packaging

Package into a `.vsix` installer file using `vsce`:

```bash
npm install -g @vscode/vsce
cd flowlang-vscode
vsce package
```

Install into VS Code:
```bash
code --install-extension flowlang-vscode-0.1.0.vsix
```
