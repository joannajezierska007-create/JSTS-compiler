import re
import sys
import os
from collections import namedtuple

# =========================
# TOKENS
# =========================
Token = namedtuple("Token", ["type", "value"])

TOKEN_SPEC = [
    ("NUMBER", r"\d+"),
    ("ID", r"[a-zA-Z_]\w*"),
    ("ASSIGN", r"="),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("COMMA", r","),
    ("OP", r"[\+\-\*/]"),
    ("SKIP", r"[ \t]+"),
    ("NEWLINE", r"\n"),
]

MASTER = re.compile("|".join(f"(?P<{t}>{p})" for t, p in TOKEN_SPEC))


# =========================
# LEXER
# =========================
def lex(code):
    tokens = []
    for m in MASTER.finditer(code):
        kind = m.lastgroup
        value = m.group()

        if kind in ("SKIP", "NEWLINE"):
            continue

        tokens.append(Token(kind, value))
    return tokens


# =========================
# AST
# =========================
class Num:
    def __init__(self, v): self.value = int(v)

class Var:
    def __init__(self, n): self.name = n

class BinOp:
    def __init__(self, l, o, r):
        self.left = l
        self.op = o
        self.right = r

class Assign:
    def __init__(self, n, e):
        self.name = n
        self.expr = e

class Print:
    def __init__(self, e):
        self.expr = e

class Call:
    def __init__(self, n, a):
        self.name = n
        self.args = a


# =========================
# PARSER
# =========================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, t=None):
        tok = self.peek()
        if not tok:
            return None
        if t and tok.type != t:
            raise Exception(f"Expected {t}, got {tok}")
        self.pos += 1
        return tok

    def parse_factor(self):
        tok = self.peek()

        if tok.type == "NUMBER":
            return Num(self.eat("NUMBER").value)

        if tok.type == "ID":
            name = self.eat("ID").value

            if self.peek() and self.peek().type == "LPAREN":
                self.eat("LPAREN")
                args = []

                while self.peek() and self.peek().type != "RPAREN":
                    args.append(self.parse_expr())
                    if self.peek() and self.peek().type == "COMMA":
                        self.eat("COMMA")

                self.eat("RPAREN")
                return Call(name, args)

            return Var(name)

    def parse_term(self):
        node = self.parse_factor()

        while self.peek() and self.peek().type == "OP" and self.peek().value in "*/":
            op = self.eat("OP").value
            node = BinOp(node, op, self.parse_factor())

        return node

    def parse_expr(self):
        node = self.parse_term()

        while self.peek() and self.peek().type == "OP" and self.peek().value in "+-":
            op = self.eat("OP").value
            node = BinOp(node, op, self.parse_term())

        return node

    def parse_statement(self):
        tok = self.peek()
        if not tok:
            return None

        # print
        if tok.type == "ID" and tok.value == "print":
            self.eat("ID")
            self.eat("LPAREN")
            expr = self.parse_expr()
            self.eat("RPAREN")
            return Print(expr)

        # assignment
        if tok.type == "ID":
            name = self.eat("ID").value

            if self.peek() and self.peek().type == "ASSIGN":
                self.eat("ASSIGN")
                return Assign(name, self.parse_expr())

        return None

    def parse(self):
        out = []
        while self.peek():
            stmt = self.parse_statement()
            if stmt:
                out.append(stmt)
        return out


# =========================
# VM
# =========================
class VM:
    def __init__(self):
        self.vars = {}
        self.stack = []

    def eval_expr(self, node):
        if isinstance(node, Num):
            return node.value

        if isinstance(node, Var):
            return self.vars.get(node.name, 0)

        if isinstance(node, BinOp):
            a = self.eval_expr(node.left)
            b = self.eval_expr(node.right)

            if node.op == "+": return a + b
            if node.op == "-": return a - b
            if node.op == "*": return a * b
            if node.op == "/": return a / b

        if isinstance(node, Call):
            args = [self.eval_expr(a) for a in node.args]

            if node.name == "add":
                return args[0] + args[1]

        return 0

    def run_ast(self, ast):
        for stmt in ast:
            if isinstance(stmt, Assign):
                self.vars[stmt.name] = self.eval_expr(stmt.expr)

            elif isinstance(stmt, Print):
                print(self.eval_expr(stmt.expr))


# =========================
# FILE SYSTEM
# =========================
def load_file(path):
    # normalize path so it works everywhere
    full_path = os.path.abspath(path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read(), full_path


def run_files(files):
    vm = VM()

    for f in files:
        code, full_path = load_file(f)

        print(f"\n--- RUNNING {full_path} ---")

        tokens = lex(code)
        ast = Parser(tokens).parse()

        vm.run_ast(ast)


# =========================
# CLI
# =========================
def cli():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python jsvm.py run file1.js file2.ts ...")
        return

    cmd = sys.argv[1]

    if cmd == "run":
        run_files(sys.argv[2:])
    else:
        print(f"Unknown command: {cmd}")
    
    if cmd == "run-folder":
        if len(sys.argv) < 3:
            print("Usage: python jsvm.py run-folder folder_path")
            return

        folder = sys.argv[2]
        if not os.path.isdir(folder):
            print(f"Not a directory: {folder}")
            return
    
    files = []

    for name in os.listdir(folder):
        if name.endswith((".js", ".ts")):
            files.append(os.path.join(folder, name))

    run_files(files)
    return


if __name__ == "__main__":
    cli()