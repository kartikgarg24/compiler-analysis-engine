from pycparser import c_ast

def eval_const(node, consts):
    """Safely evaluates compile-time expressions given a tracking environment."""
    if isinstance(node, c_ast.Constant) and node.type == 'int':
        try: return int(node.value)
        except ValueError: return None
    if isinstance(node, c_ast.ID):
        return consts.get(node.name, None)
    if isinstance(node, c_ast.BinaryOp):
        l = eval_const(node.left, consts)
        r = eval_const(node.right, consts)
        if l is not None and r is not None:
            try:
                op = node.op
                if op == '+': return l + r
                if op == '-': return l - r
                if op == '*': return l * r
                if op == '/': return l // r if r != 0 else 0
                if op == '%': return l % r if r != 0 else 0
                if op == '==': return 1 if l == r else 0
                if op == '!=': return 1 if l != r else 0
                if op == '<': return 1 if l < r else 0
                if op == '>': return 1 if l > r else 0
                if op == '<=': return 1 if l <= r else 0
                if op == '>=': return 1 if l >= r else 0
                if op == '&&': return 1 if (l and r) else 0
                if op == '||': return 1 if (l or r) else 0
            except Exception: pass
    return None