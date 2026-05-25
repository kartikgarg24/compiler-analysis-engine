from utils.ast_extractor import ext

def run_lva(cfg):
    lin, lout = {i: set() for i in cfg.nodes}, {i: set() for i in cfg.nodes}
    for _ in range(1000):
        ch = False
        for i in cfg.nodes:
            if cfg.nodes[i].get('dead', False): continue
            
            nout = set()
            for s in cfg.successors(i):
                if not cfg.edges[i, s].get('dead', False):
                    nout |= lin.get(s, set())
                    
            if nout != lout[i]: lout[i], ch = nout, True
            use, df = set(), set()
            for s in cfg.nodes[i]['stmts']:
                ext(s, use, 'use')
                ext(s, df, 'def')
            nin = use | (lout[i] - df)
            if nin != lin[i]: lin[i], ch = nin, True
        if not ch: break
    return lin, lout

def print_lva(cfg, lin, lout):
    print("\n" + "="*80)
    print(f"{'LIVE VARIABLE ANALYSIS':^80}")
    print("="*80)
    print(f"{'Block':<22} | {'Live In (IN)':<26} | {'Live Out (OUT)':<26}")
    print("-" * 80)
    
    for b in sorted(cfg.nodes):
        label = cfg.nodes[b].get('label', 'Block')
        block_name = f"B{b} ({label})"
        lin_str = "{" + ", ".join(sorted(lin[b])) + "}" if lin[b] else "∅"
        lout_str = "{" + ", ".join(sorted(lout[b])) + "}" if lout[b] else "∅"
        print(f"{block_name:<22} | {lin_str:<26} | {lout_str:<26}")
    print("="*80)