# 🔧 Compiler Analysis Engine

A Python-based tool that analyzes and optimizes C code using **compiler techniques** — the same ideas used in real compilers like GCC and Clang.

---

## 📌 What Does It Do?

You give it a C program, and it:

1. **Parses** the C code and builds a **Control Flow Graph (CFG)** — a map of all possible execution paths
2. **Folds constants** — replaces expressions like `x = 5 + 3` with `x = 8` at compile time
3. **Detects dead code** — finds code that can never run (e.g., inside `if (0) { ... }`)
4. **Eliminates dead assignments** — removes variables assigned but never used
5. **Runs dataflow analysis** — tracks which variables are live and which definitions reach each point
6. **Detects loops** — identifies back edges in the CFG
7. **Exports a visual graph** — generates a `.dot` / `.pdf` diagram of the CFG

---

## 🧠 Key Concepts (Simply Explained)

| Term | What It Means |
|---|---|
| **CFG (Control Flow Graph)** | A graph where each node is a block of code and edges show what runs next |
| **Constant Folding** | Evaluating constant expressions at analysis time, not runtime |
| **Dead Code** | Code that can never be reached or executed |
| **Live Variable Analysis (LVA)** | Figuring out which variables are still needed at each point |
| **Reaching Definitions (RDA)** | Tracking where each variable was last assigned |
| **Dead Store Elimination (DSE)** | Removing assignments to variables that are never read |

---

## 📁 Project Structure

```
compiler-analysis-engine/
│
├── config/         # Configuration settings
├── core/           # Core CFG builder and AST logic
├── passes/         # Optimization passes (constant folding, DCE, etc.)
├── utils/          # Helper utilities
└── main.py         # Entry point — run this to analyze C code
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install pycparser networkx graphviz
```

> Make sure [Graphviz](https://graphviz.org/download/) is also installed on your system for PDF export.

### 2. Run the Analyzer

```bash
python main.py
```

By default, it analyzes the example C code defined inside the script. You'll see printed output for:
- Live Variable Analysis table
- Reaching Definitions table  
- Optimized block-by-block code
- Detected loops
- An exported CFG diagram (`optimized_cfg.pdf`)

---

## 📊 Example Output

Given this C code:
```c
int x = 10;
if (x != 10) {   // This is always false!
    int a = 5;
    printf("%d", a + 10);
}
while (0) {       // Never executes
    x = x + 1;
}
```

The engine will:
- Mark the `if (x != 10)` branch as **dead** (since `x` is always 10)
- Mark the `while (0)` body as **dead** (condition is always false)
- Remove unused variable assignments
- Show you exactly what code survives optimization

---

## 🗺️ CFG Visualization

After running, open `optimized_cfg.pdf` to see the full control flow graph:

- **Black nodes/edges** = Live (reachable) code
- **Red dashed nodes/edges** = Dead (unreachable) code

---

## 🔬 Optimization Passes (In Order)

```
1. Constant Folding     → Simplify constant expressions
2. Mark Dead Edges      → Flag branches that can't be taken
3. Mark Dead Nodes      → Flag blocks that can't be reached
4. Live Variable Analysis  → Compute live-in / live-out sets
5. Reaching Definitions    → Compute reaching def sets
6. Dead Code Elimination   → Remove dead assignments safely
```

---

## 📄 License

This project is for educational and research purposes. Feel free to explore, fork, and extend it!

---

## 👤 Author

**Kartik Garg** — [github.com/kartikgarg24](https://github.com/kartikgarg24)
