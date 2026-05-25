from pycparser import c_ast

def ext(node, target_set, mode='use'):
    """Extract def/use variables from AST nodes recursively."""
    if node is None: 
        return
        
    if isinstance(node, c_ast.ID):
        if node.name not in ('printf', 'scanf', 'puts', 'false', 'true', 'NULL'): 
            target_set.add(node.name)
            
    elif isinstance(node, c_ast.Assignment):
        if mode == 'def' and isinstance(node.lvalue, c_ast.ID):
            target_set.add(node.lvalue.name)
        if mode == 'use':
            ext(node.rvalue, target_set, mode)
            if node.op != '=': 
                ext(node.lvalue, target_set, mode)
                
    elif isinstance(node, c_ast.Decl):
        if mode == 'def' and node.name:
            target_set.add(node.name)
        if mode == 'use' and node.init:
            ext(node.init, target_set, mode)
            
    elif isinstance(node, c_ast.FuncCall):
        if mode == 'use' and node.args:
            ext(node.args, target_set, mode)
            
    else:
        for _, child in node.children():
            ext(child, target_set, mode)