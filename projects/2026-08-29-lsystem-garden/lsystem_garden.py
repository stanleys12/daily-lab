#!/usr/bin/env python3
"""
L-system garden: grows fractal plants/curves from string-rewriting rules
and renders them as an SVG "turtle" drawing.

An L-system starts from an axiom string and repeatedly replaces symbols
according to production rules. Interpreting the resulting string as turtle
commands (F = draw forward, +/- = rotate, [ / ] = push/pop state) turns a
handful of grammar rules into branching plants, snowflakes, and curves.

Usage:
    python3 lsystem_garden.py                # default: plant
    python3 lsystem_garden.py --preset dragon
    python3 lsystem_garden.py --preset koch --iterations 4
    python3 lsystem_garden.py --preset plant --seed 7 --out my_plant.svg
"""

import argparse
import math
import random

PRESETS = {
    "plant": {
        "axiom": "X",
        "rules": {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"},
        "angle": 25,
        "iterations": 5,
        "start_heading": -90,
        "jitter": 4.0,
        "stroke": "#2e7d32",
        "leaf_color": "#66bb6a",
    },
    "koch": {
        "axiom": "F--F--F",
        "rules": {"F": "F+F--F+F"},
        "angle": 60,
        "iterations": 4,
        "start_heading": 0,
        "jitter": 0.0,
        "stroke": "#1565c0",
        "leaf_color": "#1565c0",
    },
    "dragon": {
        "axiom": "FX",
        "rules": {"X": "X+YF+", "Y": "-FX-Y"},
        "angle": 90,
        "iterations": 11,
        "start_heading": 0,
        "jitter": 0.0,
        "stroke": "#ad1457",
        "leaf_color": "#ad1457",
    },
    "sierpinski": {
        "axiom": "F-G-G",
        "rules": {"F": "F-G+F+G-F", "G": "GG"},
        "angle": 120,
        "iterations": 6,
        "start_heading": 0,
        "jitter": 0.0,
        "stroke": "#ef6c00",
        "leaf_color": "#ef6c00",
    },
}


def expand(axiom, rules, iterations):
    s = axiom
    for _ in range(iterations):
        s = "".join(rules.get(ch, ch) for ch in s)
    return s


def interpret(instructions, angle_deg, start_heading, step, jitter, rand):
    """Walk the instruction string with a turtle, returning a list of
    (x1, y1, x2, y2, depth) line segments plus their bounding box."""
    x, y = 0.0, 0.0
    heading = start_heading
    stack = []
    depth = 0
    segments = []
    min_x = max_x = x
    min_y = max_y = y

    for ch in instructions:
        if ch in "FG":
            a = angle_deg + (rand.uniform(-jitter, jitter) if jitter else 0.0)
            rad = math.radians(heading)
            nx = x + step * math.cos(rad)
            ny = y + step * math.sin(rad)
            segments.append((x, y, nx, ny, depth))
            x, y = nx, ny
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
        elif ch == "+":
            heading += angle_deg + (rand.uniform(-jitter, jitter) if jitter else 0.0)
        elif ch == "-":
            heading -= angle_deg + (rand.uniform(-jitter, jitter) if jitter else 0.0)
        elif ch == "[":
            stack.append((x, y, heading, depth))
            depth += 1
        elif ch == "]":
            x, y, heading, depth = stack.pop()

    return segments, (min_x, min_y, max_x, max_y)


def lerp_color(c1, c2, t):
    def hex_to_rgb(c):
        c = c.lstrip("#")
        return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))

    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def render_svg(segments, bbox, stroke, leaf_color, padding=20, canvas=800):
    min_x, min_y, max_x, max_y = bbox
    width = max(max_x - min_x, 1e-6)
    height = max(max_y - min_y, 1e-6)
    scale = (canvas - 2 * padding) / max(width, height)

    def tx(px):
        return (px - min_x) * scale + padding

    def ty(py):
        return canvas - ((py - min_y) * scale + padding)

    max_depth = max((seg[4] for seg in segments), default=1) or 1

    lines = []
    for x1, y1, x2, y2, depth in segments:
        t = depth / max_depth
        color = lerp_color(stroke, leaf_color, t)
        stroke_width = max(0.6, 3.2 - t * 2.6)
        lines.append(
            f'<line x1="{tx(x1):.2f}" y1="{ty(y1):.2f}" '
            f'x2="{tx(x2):.2f}" y2="{ty(y2):.2f}" '
            f'stroke="{color}" stroke-width="{stroke_width:.2f}" '
            f'stroke-linecap="round"/>'
        )

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas}" height="{canvas}" '
        f'viewBox="0 0 {canvas} {canvas}">',
        f'<rect width="100%" height="100%" fill="#0b0f0a"/>',
        *lines,
        "</svg>",
    ]
    return "\n".join(svg)


def main():
    parser = argparse.ArgumentParser(description="Grow an L-system and render it to SVG.")
    parser.add_argument("--preset", choices=PRESETS.keys(), default="plant")
    parser.add_argument("--iterations", type=int, default=None)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    cfg = PRESETS[args.preset]
    iterations = args.iterations if args.iterations is not None else cfg["iterations"]
    rand = random.Random(args.seed)

    instructions = expand(cfg["axiom"], cfg["rules"], iterations)
    step = 1000 / (1.6 ** iterations)
    segments, bbox = interpret(
        instructions,
        cfg["angle"],
        cfg["start_heading"],
        step,
        cfg["jitter"],
        rand,
    )
    svg = render_svg(segments, bbox, cfg["stroke"], cfg["leaf_color"])

    out_path = args.out or f"{args.preset}.svg"
    with open(out_path, "w") as f:
        f.write(svg)

    print(f"preset:       {args.preset}")
    print(f"iterations:   {iterations}")
    print(f"string len:   {len(instructions)}")
    print(f"segments:     {len(segments)}")
    print(f"written to:   {out_path}")


if __name__ == "__main__":
    main()
