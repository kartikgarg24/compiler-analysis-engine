from pycparser import c_ast
from utils.ast_evaluator import eval_const

class ASTConstantOptimizer:
    def __init__(self, constants):
        self.constants = constants
        self.changed = False

    def optimize(self, node):
        if node is None: return None
        if isinstance(node, c_ast.ID):
            if node.name in self.constants:
                self.changed = True
                return c_ast.Constant(type='int', value=str(self.constants[node.name]))
            return node

        for attr in getattr(node, '__slots__', []):
            child = getattr(node, attr)
            if isinstance(node, c_ast.Assignment) and attr == 'lvalue':
                continue
            if isinstance(child, c_ast.Node):
                setattr(node, attr, self.optimize(child))
            elif isinstance(child, list):
                for i in range(len(child)):
                    if isinstance(child[i], c_ast.Node):
                        child[i] = self.optimize(child[i])

        if isinstance(node, c_ast.BinaryOp):
            if isinstance(node.left, c_ast.Constant) and isinstance(node.right, c_ast.Constant):
                res = eval_const(node, {})
                if res is not None:
                    self.changed = True
                    return c_ast.Constant(type='int', value=str(res))
        return node

def compute_constants(cfg, entry):
    out_consts = {n: None for n in cfg.nodes}
    out_consts[entry] = {} 
    
    global_changed = True
    iters = 0
    while global_changed and iters < 1000:
        global_changed = False
        iters += 1
        
        for b in cfg.nodes:
            preds = list(cfg.predecessors(b))
            valid_preds = [p for p in preds if out_consts[p] is not None]
            if not valid_preds and b != entry:
                continue 
            
            current_consts = {}
            if valid_preds:
                first_pred = out_consts[valid_preds[0]]
                for var, val in first_pred.items():
                    if all(out_consts[p].get(var) == val for p in valid_preds[1:]):
                        current_consts[var] = val
            
            simulated_consts = current_consts.copy()
            for stmt in cfg.nodes[b]['stmts']:
                if isinstance(stmt, c_ast.Assignment) and stmt.op == '=' and isinstance(stmt.lvalue, c_ast.ID):
                    val = eval_const(stmt.rvalue, simulated_consts)
                    if val is not None:
                        simulated_consts[stmt.lvalue.name] = val
                    else:
                        simulated_consts.pop(stmt.lvalue.name, None)
                elif isinstance(stmt, c_ast.Decl) and stmt.name:
                    if stmt.init:
                        val = eval_const(stmt.init, simulated_consts)
                        if val is not None:
                            simulated_consts[stmt.name] = val
                        else:
                            simulated_consts.pop(stmt.name, None)
                    else:
                        simulated_consts.pop(stmt.name, None)

            if out_consts[b] is None or out_consts[b] != simulated_consts:
                out_consts[b] = simulated_consts
                global_changed = True
                
    return out_consts

def apply_constant_optimizations(cfg, entry):
    out_consts = compute_constants(cfg, entry)
    
    for b in cfg.nodes:
        preds = list(cfg.predecessors(b))
        valid_preds = [p for p in preds if out_consts[p] is not None]
        if not valid_preds and b != entry:
            continue
            
        current_consts = {}
        if valid_preds:
            first_pred = out_consts[valid_preds[0]]
            for var, val in first_pred.items():
                if all(out_consts[p].get(var) == val for p in valid_preds[1:]):
                    current_consts[var] = val
                    
        new_stmts = []
        for stmt in cfg.nodes[b]['stmts']:
            optimizer = ASTConstantOptimizer(current_consts)
            opt_stmt = optimizer.optimize(stmt)
            
            if isinstance(opt_stmt, c_ast.Assignment) and opt_stmt.op == '=' and isinstance(opt_stmt.lvalue, c_ast.ID):
                if isinstance(opt_stmt.rvalue, c_ast.Constant):
                    current_consts[opt_stmt.lvalue.name] = int(opt_stmt.rvalue.value)
                else:
                    current_consts.pop(opt_stmt.lvalue.name, None)
            elif isinstance(opt_stmt, c_ast.Decl) and opt_stmt.name:
                if opt_stmt.init and isinstance(opt_stmt.init, c_ast.Constant):
                    current_consts[opt_stmt.name] = int(opt_stmt.init.value)
                else:
                    current_consts.pop(opt_stmt.name, None)
                    
            new_stmts.append(opt_stmt)
        cfg.nodes[b]['stmts'] = new_stmts