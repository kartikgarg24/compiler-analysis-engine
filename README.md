# Compiler Analysis Engine

A Python-based static analysis and optimization tool for C programs. It applies classic compiler techniques — the same foundational ideas behind production compilers like GCC and Clang — to parse, analyze, and optimize C code at a structural level.

---

## Overview

The engine takes a C source file, builds an internal representation of its control flow, and runs a series of analysis and optimization passes over it. The goal is to identify redundant computations, unreachable code, and unnecessary variable assignments — and either report or eliminate them.

Specifically, the tool:

1. Parses the C code and constructs a **Control Flow Graph (CFG)**, representing all possible execution paths through the program.
2. Performs **constant folding** — evaluating constant expressions such as `x = 5 + 3` at analysis time rather than runtime.
3. Detects **dead code** — blocks that can never be reached, for example the body of `if (0) { ... }` or `while (0) { ... }`.
4. Eliminates **dead assignments** — variables that are assigned a value but never subsequently read.
5. Runs **live variable analysis** and **reaching definitions analysis** across all live blocks.
6. Detects **loops** by identifying back edges in the CFG.
7. Exports a **visual diagram** of the full CFG, with dead nodes and edges clearly marked.

---

## Key Concepts

| Term | Description |
|---|---|
| Control Flow Graph (CFG) | A directed graph where each node represents a basic block of statements and each edge represents a possible transfer of control |
| Constant Folding | Replacing constant expressions with their computed values before execution |
| Dead Code | Code that is syntactically present but can never be executed at runtime |
| Live Variable Analysis | Determining which variables may be read after each program point |
| Reaching Definitions | Tracking which assignment to a variable might reach a given point in the program |
| Dead Store Elimination | Removing assignments to variables whose values are never used |

---

## Project Structure

```
compiler-analysis-engine/
│
├── config/         # Configuration settings
├── core/           # CFG builder and AST traversal logic
├── passes/         # Optimization and analysis passes
├── utils/          # Shared helper utilities
└── main.py         # Entry point
```

---

## Getting Started

### Prerequisites

Install the required Python packages:

```bash
pip install pycparser networkx graphviz
```

Also install the [Graphviz system package](https://graphviz.org/download/) on your machine, which is required for rendering the CFG to PDF.

### Running the Analyzer

```bash
python main.py
```

By default, the tool analyzes the example C program defined in the script. The output includes:

- A live variable analysis table (live-in and live-out sets per block)
- A reaching definitions table
- Optimized code printed block by block
- A list of detected loops
- An exported CFG diagram saved as `optimized_cfg.pdf`

---

## Example

Given the following C code:

```c
int x = 10;

if (x != 10) {   // condition is always false
    int a = 5;
    printf("%d", a + 10);
}

while (0) {       // loop body never executes
    x = x + 1;
}
```

The engine will determine that `x` is always `10` at the `if` condition, mark the true branch as dead, and mark the entire `while (0)` body as unreachable. Dead assignments inside those blocks are then eliminated.

---

## CFG Visualization

After running, open `optimized_cfg.pdf` to inspect the control flow graph. Live nodes and edges are drawn in black. Dead (unreachable) nodes and edges are drawn in red with dashed lines.

---

## Optimization Pipeline

The passes run in the following order:

```
1. Constant Folding          Evaluate and substitute constant expressions
2. Dead Edge Marking         Flag branches whose conditions are statically false
3. Dead Node Marking         Flag blocks unreachable from the entry point
4. Live Variable Analysis    Compute live-in and live-out sets over live blocks
5. Reaching Definitions      Compute reaching definition sets over live blocks
6. Dead Code Elimination     Remove dead assignments from live blocks
```

---

