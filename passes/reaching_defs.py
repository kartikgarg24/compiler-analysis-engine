from utils.ast_extractor import ext

def run_rda(cfg):
    rin, rout, g, k = {i: set() for i in cfg.nodes}, {i: set() for i in cfg.nodes}, {}, {}
    for i in cfg.nodes:
        gs, ks = set(), set()
        for s in cfg.nodes[i]['stmts']:
            d = set()
            ext(s, d, 'def')
            for v in d:
                gs.add((v, i))
                ks |= {(x, y) for x, y in gs if x == v and y != i}
        g[i], k[i] = gs, ks
    for _ in range(1000):
        ch = False
        for i in cfg.nodes:
            if cfg.nodes[i].get('dead', False): continue
            
            nin = set()
            for p in cfg.predecessors(i):
                if not cfg.edges[p, i].get('dead', False):
                    nin |= rout.get(p, set())
                    
            if nin != rin[i]: rin[i], ch = nin, True
            nout = g[i] | (rin[i] - k[i])
            if nout != rout[i]: rout[i], ch = nout, True
        if not ch: break
    return rin, rout

def print_rda(cfg, rin, rout):
    print("\n" + "="*120)
    print(f"{'REACHING DEFINITIONS ANALYSIS':^120}")
    print("="*120)
    print(f"{'Block':<22} | {'Reach In (IN)':<46} | {'Reach Out (OUT)':<46}")
    print("-" * 120)
    
    def format_defs(def_set):
        if not def_set: return "∅"
        grouped = {}
        for var_name, block_id in def_set:
            if var_name not in grouped: grouped[var_name] = []
            grouped[var_name].append(block_id)
        parts = []
        for var_name in sorted(grouped.keys()):
            blocks = ", ".join([f"B{bid}" for bid in sorted(grouped[var_name])])
            parts.append(f"{var_name} {{{blocks}}}")
        return ", ".join(parts)

    for b in sorted(cfg.nodes):
        label = cfg.nodes[b].get('label', 'Block')
        block_name = f"B{b} ({label})"
        print(f"{block_name:<22} | {format_defs(rin[b]):<46} | {format_defs(rout[b]):<46}")
    print("="*120)