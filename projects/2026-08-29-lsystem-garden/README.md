# L-system garden

Grows fractal plants and curves from tiny string-rewriting grammars
(L-systems) and renders them as SVG turtle drawings.

An L-system starts from an "axiom" string and repeatedly replaces symbols
using production rules (e.g. `X -> F+[[X]-X]-F[-FX]+X`). Interpreting the
final string as turtle-graphics commands — `F`/`G` draw forward, `+`/`-`
rotate, `[`/`]` push/pop position+heading onto a stack — turns a couple of
rewrite rules into a branching plant, a dragon curve, a Koch snowflake edge,
or a Sierpinski arrowhead, depending only on which grammar you feed it.

## Run it

```bash
python3 lsystem_garden.py                          # default: plant.svg
python3 lsystem_garden.py --preset dragon
python3 lsystem_garden.py --preset koch --iterations 4
python3 lsystem_garden.py --preset sierpinski
python3 lsystem_garden.py --preset plant --seed 7 --out my_plant.svg
```

No dependencies — just the Python standard library. Open the resulting
`.svg` in a browser to view it.

## Interesting detail

The plant preset injects a small random angle jitter (`--seed` controls it)
into every forward-move and turn, so no two runs of the same grammar produce
an identical plant even though the rewrite rules are fixed — small floating
errors accumulate through the branching stack into visibly different, organic
silhouettes. Branch color also blends from a dark trunk-green to a lighter leaf-green
based on stack depth at draw time, so deeper branches (twigs) read as
lighter/younger than the trunk without any extra state being tracked beyond
the push/pop depth counter.

`plant.svg` in this folder is a sample output (`--preset plant --seed 7`).
