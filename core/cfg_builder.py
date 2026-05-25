import re
import networkx as nx
from pycparser import c_parser, c_ast
from config.fake_headers import FAKE_HEADERS

class CFGBuilder(c_ast.NodeVisitor):
    def __init__(self):
        self.cfg = nx.DiGraph()
        self.next_id = 0
        self.curr = None
        self.entry = None
        self.exit = None
        self.brk = []
        self.cnt = []
        
    def create(self, label="Block"):
        bid = self.next_id
        self.cfg.add_node(bid, stmts=[], label=label, dead=False)
        self.next_id += 1
        return bid
        
    def build(self, ast):
        self.entry = self.create("Entry")
        self.exit = self.create("Exit")
        self.curr = self.entry
        self.visit(ast)
        # Link lingering blocks to structural Exit node if left dangling
        if self.curr is not None and not self.cfg.has_edge(self.curr, self.exit):
            self.cfg.add_edge(self.curr, self.exit)
        return self.cfg, self.entry
        
    def visit_Compound(self, n):
        for s in (n.block_items or []): 
            self.visit(s)
        
    def visit_If(self, n):
        cb = self.curr
        self.cfg.nodes[cb]['label'] = "If_Condition"
        if n.cond: 
            self.cfg.nodes[cb]['stmts'].append(n.cond)
        
        tb = self.create("If_True")
        mb = self.create("If_Merge")
        fb = self.create("If_False") if n.iffalse else None
        
        self.cfg.add_edge(cb, tb)
        self.cfg.add_edge(cb, fb if fb else mb)
        
        self.curr = tb
        self.visit(n.iftrue)
        if self.curr is not None:
            self.cfg.add_edge(self.curr, mb)
        
        if fb:
            self.curr = fb
            self.visit(n.iffalse)
            if self.curr is not None:
                self.cfg.add_edge(self.curr, mb)
        self.curr = mb
        
    def visit_While(self, n):
        hb = self.curr
        self.cfg.nodes[hb]['label'] = "While_Condition"
        if n.cond: 
            self.cfg.nodes[hb]['stmts'].append(n.cond)
        
        bb = self.create("While_Body")
        eb = self.create("While_Exit")
        
        self.cfg.add_edge(hb, bb)
        self.cfg.add_edge(hb, eb)
        
        self.brk.append(eb)
        self.cnt.append(hb)
        
        self.curr = bb
        self.visit(n.stmt)
        if self.curr is not None:
            self.cfg.add_edge(self.curr, hb)
        
        self.brk.pop()
        self.cnt.pop()
        self.curr = eb
        
    def visit_For(self, n):
        ib = self.curr
        self.cfg.nodes[ib]['label'] = "For_Init"
        if n.init: 
            self.visit(n.init)
        
        hb = self.create("For_Condition")
        bb = self.create("For_Body")
        eb = self.create("For_Exit")
        
        self.cfg.add_edge(ib, hb)
        if n.cond: 
            self.cfg.nodes[hb]['stmts'].append(n.cond)
        self.cfg.add_edge(hb, bb)
        self.cfg.add_edge(hb, eb)
        
        self.brk.append(eb)
        self.cnt.append(hb)
        
        self.curr = bb
        self.visit(n.stmt)
        if n.next: 
            self.visit(n.next)
        if self.curr is not None:
            self.cfg.add_edge(self.curr, hb)
        
        self.brk.pop()
        self.cnt.pop()
        self.curr = eb
        
    def visit_Assignment(self, n): self.cfg.nodes[self.curr]['stmts'].append(n)
    def visit_Decl(self, n):       self.cfg.nodes[self.curr]['stmts'].append(n)
    def visit_FuncCall(self, n):   self.cfg.nodes[self.curr]['stmts'].append(n)
    def visit_Return(self, n):     self.cfg.nodes[self.curr]['stmts'].append(n)
    def visit_UnaryOp(self, n):    self.cfg.nodes[self.curr]['stmts'].append(n)
        
    def visit_FuncDef(self, n):
        if n.body: 
            self.visit_Compound(n.body)

def parse_code(code):
    code = code.replace('\xa0', ' ')
    code = re.sub(r'//[^\n]*|/\*.*?\*/', '', code, flags=re.DOTALL)
    defines = {'NULL': '0', 'false': '0', 'true': '1', 'FALSE': '0', 'TRUE': '1'} 
    lines = []
    
    for l in code.split('\n'):
        s = l.strip()
        if s.startswith('#define'):
            p = s[7:].split(None, 1)
            if p: 
                defines[p[0]] = p[1] if len(p) > 1 else '1'
        elif not s.startswith('#'):
            for k, v in defines.items(): 
                l = re.sub(rf'\b{k}\b', str(v), l)
            lines.append(l)
            
    clean_code = '\n'.join(lines)
    parser = c_parser.CParser()
    ast = parser.parse(FAKE_HEADERS + clean_code)
    return CFGBuilder().build(ast)