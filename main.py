import networkx as nx
import graphviz
from pycparser import c_generator

from core.cfg_builder import parse_code
from passes.constant_fold import apply_constant_optimizations
from passes.dead_code_elim import mark_unreachable_edges, mark_dead_nodes, eliminate_dead_code
from passes.live_vars import run_lva, print_lva
from passes.reaching_defs import run_rda, print_rda

def print_optimized_code(cfg):
    print("\n" + "="*80)
    print(f"{'OPTIMIZED BLOCK CODE (Shows effect of DCE & DSE)':^80}")
    print("="*80)
    generator = c_generator.CGenerator()
    
    for b in sorted(cfg.nodes):
        label = cfg.nodes[b].get('label', 'Block')
        status = "(DEAD BLOCK)" if cfg.nodes[b].get('dead', False) else "(LIVE)"
        print(f"Block {b}: {label} {status}")
        
        stmts = cfg.nodes[b].get('stmts', [])
        if not stmts:
            print("    <empty block>")
        else:
            for stmt in stmts:
                try:
                    print("    " + generator.visit(stmt).strip())
                except Exception:
                    print("    " + str(stmt.__class__.__name__))
        print("-" * 80)

def detect_loops(cfg, entry):
    doms = nx.immediate_dominators(cfg, entry)
    def dominates(v, u):
        while u != v and u != entry:
            u = doms.get(u, u)
            if u == doms.get(u): break
        return u == v
    loops = []
    for u, v in cfg.edges():
        if dominates(v, u) and not cfg.edges[u, v].get('dead', False):
            nodes = {v, u}
            q = [u]
            while q:
                c = q.pop()
                for p in cfg.predecessors(c):
                    if p not in nodes and not cfg.edges[p, c].get('dead', False):
                        nodes.add(p)
                        q.append(p)
            loops.append((v, nodes))
    return loops

def export_cfg(cfg, filename="optimized_cfg"):
    dot = graphviz.Digraph(format='pdf')
    for n in cfg.nodes: 
        label = cfg.nodes[n].get('label', 'Block')
        is_dead = cfg.nodes[n].get('dead', False)
        color = 'red' if is_dead else 'black'
        style = 'dashed' if is_dead else 'solid'
        dot.node(str(n), f"{n}: {label}", color=color, fontcolor=color, style=style)
        
    for u, v in cfg.edges: 
        is_dead = cfg.edges[u, v].get('dead', False)
        color = 'red' if is_dead else 'black'
        style = 'dashed' if is_dead else 'solid'
        dot.edge(str(u), str(v), color=color, style=style)
    
    dot.save(f"{filename}.dot")
    try: 
        dot.render(filename, view=False)
    except Exception: 
        print("Visual PDF rendering skipped (Graphviz binary not found). Dot file saved.")

if __name__ == "__main__":
    c_code = r"""
    #include <stdio.h>
    #include <stdbool.h>

    int main() {
        int x = 10;
        printf("Start\n");
        
        if (x!=10) { 
            int a = 5;
            int b = 10;
            printf("%d", a + b);
        }

        int a = 10; 
        x = a + 10; 

        while (0) {
            x = x + 1;
            printf("%d", x);
        }

        if (0) {
            printf("Alive block\n");
            x=11;
            int y=999;
        }
        else {
            x=x+10;
            int y = 50; 
            printf("%d", y);
        }
        x=x+1;
        printf("End\n");
        return x; 
    }
    """

    # Execution Flow
    cfg, entry = parse_code(c_code)

    apply_constant_optimizations(cfg, entry)
    mark_unreachable_edges(cfg)
    mark_dead_nodes(cfg, entry)

    live_in, live_out = run_lva(cfg)
    reach_in, reach_out = run_rda(cfg)

    eliminate_dead_code(cfg, live_out)

    # Output Outputs
    print_lva(cfg, live_in, live_out)
    print_rda(cfg, reach_in, reach_out)
    print_optimized_code(cfg)

    loops = detect_loops(cfg, entry)
    print("\nDetected loops (header, nodes):", loops)

    export_cfg(cfg, "visual_dce_cfg")
    print("\nCFG Export Pipeline Execution Completed.")