"""
thompson-regex: a regex engine built from scratch using Thompson's
NFA construction, simulated the way Ken Thompson / Russ Cox / Rob Pike
describe it (a "Pike VM"): instead of backtracking through the string
trying alternatives one at a time, we advance ALL live parse threads
one input character at a time. That guarantees O(n * m) matching time
(n = text length, m = pattern size) with NO catastrophic blow-up on
patterns like (a*)*b that make naive backtracking engines hang.

Supported syntax: literals, '.', '|', '*', '+', '?', '(...)', '\\' escapes.

Run: python3 regex_engine.py
"""

import itertools
import time

_ids = itertools.count()


class State:
    """One node of the NFA. kind is 'char', 'any', 'split', or 'match'."""

    __slots__ = ("kind", "ch", "out", "out2", "id")

    def __init__(self, kind, ch=None):
        self.kind = kind
        self.ch = ch
        self.out = None
        self.out2 = None
        self.id = next(_ids)


class Frag:
    """A partially-built NFA fragment: an entry state plus a list of
    dangling (state, attr) pointers still waiting to be wired to
    whatever comes next."""

    def __init__(self, start, dangling):
        self.start = start
        self.dangling = dangling


def patch(dangling, target):
    for state, attr in dangling:
        setattr(state, attr, target)


# ---------------------------------------------------------------- parser --
# expr   := term ('|' term)*
# term   := factor*
# factor := base ('*' | '+' | '?')?
# base   := '.' | literal | '\' any | '(' expr ')'

class Parser:
    def __init__(self, pattern):
        self.p = pattern
        self.i = 0

    def peek(self):
        return self.p[self.i] if self.i < len(self.p) else None

    def advance(self):
        c = self.p[self.i]
        self.i += 1
        return c

    def parse(self):
        node = self.parse_expr()
        if self.i != len(self.p):
            raise ValueError(f"unexpected '{self.peek()}' at {self.i}")
        return node

    def parse_expr(self):
        term = self.parse_term()
        while self.peek() == "|":
            self.advance()
            term = ("alt", term, self.parse_term())
        return term

    def parse_term(self):
        factors = []
        while self.peek() is not None and self.peek() not in "|)":
            factors.append(self.parse_factor())
        result = None
        for f in factors:
            result = f if result is None else ("concat", result, f)
        return result if result is not None else ("empty",)

    def parse_factor(self):
        base = self.parse_base()
        c = self.peek()
        if c == "*":
            self.advance()
            return ("star", base)
        if c == "+":
            self.advance()
            return ("plus", base)
        if c == "?":
            self.advance()
            return ("opt", base)
        return base

    def parse_base(self):
        c = self.advance()
        if c == "(":
            node = self.parse_expr()
            if self.peek() != ")":
                raise ValueError("unbalanced '('")
            self.advance()
            return node
        if c == ".":
            return ("any",)
        if c == "\\":
            return ("char", self.advance())
        return ("char", c)


# -------------------------------------------------------------- compile --

def compile_node(node):
    kind = node[0]
    if kind == "char":
        s = State("char", node[1])
        return Frag(s, [(s, "out")])
    if kind == "any":
        s = State("any")
        return Frag(s, [(s, "out")])
    if kind == "empty":
        s = State("split")  # pure epsilon relay, out2 stays None
        return Frag(s, [(s, "out")])
    if kind == "concat":
        a, b = compile_node(node[1]), compile_node(node[2])
        patch(a.dangling, b.start)
        return Frag(a.start, b.dangling)
    if kind == "alt":
        s = State("split")
        a, b = compile_node(node[1]), compile_node(node[2])
        s.out, s.out2 = a.start, b.start
        return Frag(s, a.dangling + b.dangling)
    if kind == "star":
        s = State("split")
        a = compile_node(node[1])
        s.out = a.start
        patch(a.dangling, s)
        return Frag(s, [(s, "out2")])
    if kind == "plus":
        a = compile_node(node[1])
        s = State("split")
        s.out = a.start
        patch(a.dangling, s)
        return Frag(a.start, [(s, "out2")])
    if kind == "opt":
        s = State("split")
        a = compile_node(node[1])
        s.out = a.start
        return Frag(s, a.dangling + [(s, "out2")])
    raise ValueError(f"unknown node {node}")


def compile_regex(pattern):
    ast = Parser(pattern).parse()
    frag = compile_node(ast)
    accept = State("match")
    patch(frag.dangling, accept)
    return frag.start


# ------------------------------------------------------------- simulate --

def add_state(state, thread_list, seen):
    if state is None or state.id in seen:
        return
    seen.add(state.id)
    if state.kind == "split":
        add_state(state.out, thread_list, seen)
        add_state(state.out2, thread_list, seen)
    else:
        thread_list.append(state)


def run_nfa(start, text, trace=False):
    seen = set()
    current = []
    add_state(start, current, seen)
    history = []
    for ch in text:
        if trace:
            history.append((ch, sorted(s.id for s in current)))
        nxt, seen = [], set()
        for s in current:
            if s.kind == "match":
                continue
            if s.kind == "any" or (s.kind == "char" and s.ch == ch):
                add_state(s.out, nxt, seen)
        current = nxt
        if not current:
            break
    matched = any(s.kind == "match" for s in current)
    return matched, history


def fullmatch(pattern, text, trace=False):
    start = compile_regex(pattern)
    return run_nfa(start, text, trace=trace)


# ------------------------------------------------------------------ demo --

def demo():
    print("=== thompson-regex: NFA-simulation regex engine ===\n")

    cases = [
        (r"a(b|c)*d", "abccbd"),
        (r"a(b|c)*d", "abce"),
        (r"colou?r", "color"),
        (r"colou?r", "colour"),
        (r"colou?r", "colouur"),
        (r"(ab)+", "ababab"),
        (r"(ab)+", "aba"),
        (r".at", "cat"),
        (r".at", "9at"),
        (r".at", "cta"),
    ]
    for pattern, text in cases:
        matched, _ = fullmatch(pattern, text)
        mark = "MATCH  " if matched else "no match"
        print(f"  /{pattern}/  vs  {text!r:12s} -> {mark}")

    print("\n--- thread trace for /a(b|c)*d/ vs 'abccbd' ---")
    print("(each step shows every NFA state alive at once -- these are")
    print(" the 'parallel threads' Thompson's construction runs instead")
    print(" of backtracking)")
    _, history = fullmatch(r"a(b|c)*d", "abccbd", trace=True)
    for ch, ids in history:
        print(f"  read {ch!r:4s} while live states = {ids}")

    print("\n--- catastrophic-backtracking torture test ---")
    print("naive backtracking engines take exponential time on patterns")
    print("like (a*)*b matched against many a's with no trailing 'b'.")
    print("this NFA simulation stays linear:\n")
    for n in (20, 5000, 50000):
        text = "a" * n
        t0 = time.perf_counter()
        matched, _ = fullmatch(r"(a*)*b", text)
        dt = time.perf_counter() - t0
        print(f"  n={n:6d}  matched={matched!s:5s}  time={dt * 1000:8.3f} ms")


if __name__ == "__main__":
    demo()
