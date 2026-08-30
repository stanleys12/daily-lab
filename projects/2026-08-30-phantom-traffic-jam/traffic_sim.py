#!/usr/bin/env python3
"""
Phantom traffic jam simulator.

Implements the Nagel-Schreckenberg cellular-automaton traffic model on a
circular one-lane road. No obstacles, no traffic lights, no accidents -
just cars following four simple local rules each tick. Watch jams appear,
thicken, and crawl backwards through the traffic even though nothing ever
blocks the road. That backward-moving clot is a real, measured phenomenon
called a "phantom" or "phantom-shockwave" traffic jam.

Run with: python3 traffic_sim.py
"""
import random
import sys
import time

ROAD_LENGTH = 100
NUM_CARS = 28
V_MAX = 5
DAWDLE_PROB = 0.3
STEPS = 220
ANIMATE_STEPS = 60
FRAME_DELAY = 0.05
RECORD_LAST = 150  # rows kept for the space-time diagram
PPM_PATH = "spacetime.ppm"

SPEED_GLYPHS = " .:-=+*#%@"  # slow -> fast, index scaled by v/V_MAX


def init_road(rng):
    positions = sorted(rng.sample(range(ROAD_LENGTH), NUM_CARS))
    speeds = [0] * NUM_CARS
    return positions, speeds


def gap_ahead(i, positions):
    n = len(positions)
    nxt = positions[(i + 1) % n]
    here = positions[i]
    d = nxt - here
    if d <= 0:
        d += ROAD_LENGTH
    return d - 1


def step(positions, speeds, rng):
    n = len(positions)
    # 1: acceleration, 2: braking, 3: randomization
    for i in range(n):
        if speeds[i] < V_MAX:
            speeds[i] += 1
        g = gap_ahead(i, positions)
        if speeds[i] > g:
            speeds[i] = g
        if speeds[i] > 0 and rng.random() < DAWDLE_PROB:
            speeds[i] -= 1
    # 4: movement
    for i in range(n):
        positions[i] = (positions[i] + speeds[i]) % ROAD_LENGTH
    # re-sort by position (order can change as cars wrap around)
    order = sorted(range(n), key=lambda i: positions[i])
    positions[:] = [positions[i] for i in order]
    speeds[:] = [speeds[i] for i in order]


def render_frame(positions, speeds, t):
    road = ["·"] * ROAD_LENGTH
    for p, v in zip(positions, speeds):
        road[p] = SPEED_GLYPHS[min(v, V_MAX) * (len(SPEED_GLYPHS) - 1) // V_MAX]
    print(f"\x1b[H\x1b[2Jt={t:4d}  " + "".join(road))


def speed_to_rgb(v):
    if v < 0:
        return (10, 10, 10)  # empty road cell
    # red (jammed) -> yellow -> green (free flow)
    frac = v / V_MAX
    r = int(220 * (1 - frac) + 40 * frac)
    g = int(60 * (1 - frac) + 200 * frac)
    b = 40
    return (r, g, b)


def write_ppm(history, path):
    height = len(history)
    width = ROAD_LENGTH
    with open(path, "w") as f:
        f.write(f"P3\n{width} {height}\n255\n")
        for row in history:
            grid = [-1] * width
            for p, v in row:
                grid[p] = v
            for v in grid:
                r, g, b = speed_to_rgb(v)
                f.write(f"{r} {g} {b} ")
            f.write("\n")


def main():
    rng = random.Random(7)
    positions, speeds = init_road(rng)
    history = []

    animate = "--no-animate" not in sys.argv
    for t in range(STEPS):
        step(positions, speeds, rng)
        if t >= STEPS - RECORD_LAST:
            history.append(list(zip(positions, speeds)))
        if animate and t < ANIMATE_STEPS:
            render_frame(positions, speeds, t)
            time.sleep(FRAME_DELAY)

    write_ppm(history, PPM_PATH)

    avg_speed = sum(speeds) / len(speeds)
    jammed = sum(1 for v in speeds if v <= 1)
    print(f"\nFinal tick {STEPS}: avg speed {avg_speed:.2f}/{V_MAX}, "
          f"{jammed}/{NUM_CARS} cars nearly stopped.")
    print(f"Space-time diagram written to {PPM_PATH} "
          f"({ROAD_LENGTH}x{len(history)} px, time flows downward).")
    print("Diagonal dark streaks in that image = phantom jams drifting "
          "backward against traffic flow.")


if __name__ == "__main__":
    main()
