from pycparser import c_ast
from utils.ast_extractor import ext

def mark_unreachable_edges(cfg):
    for u in cfg.nodes:
        label = cfg.nodes[u].get('label', '')
        if label not in ("If_Condition", "While_Condition", "For_Condition"):
            continue
            
        stmts = cfg.nodes[u].get('stmts', [])
        if not stmts: continue
        
        cond = stmts[-1] 
        if isinstance(cond, c_ast.Constant) and cond.type == 'int':
            val = int(cond.value)
            
            for v in cfg.successors(u):
                v_label = cfg.nodes[v].get('label', '')
                
                if val == 0 and v_label in ("If_True", "While_Body", "For_Body"):
                    cfg.edges[u, v]['dead'] = True
                elif val != 0 and v_label == "If_False":
                    cfg.edges[u, v]['dead'] = True
                elif val != 0 and label == "If_Condition" and v_label == "If_Merge":
                    cfg.edges[u, v]['dead'] = True
                elif val != 0 and label in ("While_Condition", "For_Condition") and v_label in ("While_Exit", "For_Exit"):
                    cfg.edges[u, v]['dead'] = True

def mark_dead_nodes(cfg, entry):
    reach = set()
    q = [entry]
    
    while q:
        curr = q.pop(0)
        if curr not in reach:
            reach.add(curr)
            for succ in cfg.successors(curr):
                if not cfg.edges[curr, succ].get('dead', False):
                    q.append(succ)
                    
    for n in cfg.nodes:
        if n not in reach:
            cfg.nodes[n]['dead'] = True
            for succ in cfg.successors(n):
                cfg.edges[n, succ]['dead'] = True

def has_side_effects(node):
    if isinstance(node, c_ast.FuncCall): return True
    for attr in getattr(node, '__slots__', []):
        child = getattr(node, attr)
        if isinstance(child, c_ast.Node) and has_side_effects(child): return True
        elif isinstance(child, list):
            if any(isinstance(c, c_ast.Node) and has_side_effects(c) for c in child): 
                return True
    return False

def eliminate_dead_code(cfg, lout):
    for i in cfg.nodes:
        if cfg.nodes[i].get('dead', False): continue
        
        live = set(lout[i])
        kept = []
        for s in reversed(cfg.nodes[i]['stmts']):
            if isinstance(s, c_ast.Assignment) and isinstance(s.lvalue, c_ast.ID):
                if s.lvalue.name not in live and not has_side_effects(s.rvalue): 
                    continue 
                live.discard(s.lvalue.name)
                ext(s.rvalue, live, 'use')
                if s.op != '=': ext(s.lvalue, live, 'use')
            
            elif isinstance(s, c_ast.Decl) and s.name and s.init:
                if s.name not in live and not has_side_effects(s.init):
                    s.init = None 
                else:
                    live.discard(s.name)
                    ext(s.init, live, 'use')
            else:
                ext(s, live, 'use')
            kept.append(s)
        cfg.nodes[i]['stmts'] = kept[::-1]