# thompson-regex

A regex engine built from scratch: parser, NFA compiler, and simulator — no
`re` module, no backtracking.

## Run it

```
python3 regex_engine.py
```

## What it does

Implements a subset of regex syntax (literals, `.`, `|`, `*`, `+`, `?`,
`(...)`, `\` escapes) via a hand-written recursive-descent parser, compiles
the resulting AST into an NFA using **Thompson's construction**, and matches
strings by simulating the NFA the way Ken Thompson's original `grep` and
Russ Cox's "Pike VM" articles describe it: instead of trying one alternative
at a time and backtracking on failure, every reachable NFA state ("thread")
is advanced in lockstep for each input character. The demo prints the full
match/no-match table for ten test cases, then dumps the live thread set at
each step of one match so you can see the parallel-threads idea directly,
and finally times the classic pathological pattern `(a*)*b` against inputs
of length 20, 5,000, and 50,000 — this engine stays linear (milliseconds),
while a naive backtracking matcher would blow up exponentially on the same
input.

## One interesting detail

The compiler never allocates a state it can't immediately wire up: instead
of building the NFA top-down, `compile_node` returns a *fragment* — an entry
state plus a list of still-dangling `(state, attribute)` pointers — and the
caller patches those pointers once it knows what comes next. This "patch
list" technique (same one used in Cox's regexp articles) is what lets `*`,
`+`, `?`, concatenation, and alternation all compose recursively without
ever needing a second pass over the graph.
