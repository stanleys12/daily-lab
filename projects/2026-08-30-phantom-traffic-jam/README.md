# Phantom Traffic Jam

A cellular-automaton traffic simulation (the Nagel-Schreckenberg model) on a
circular one-lane road. There are no traffic lights, no crashes, no lane
changes, no bottleneck of any kind — every car just follows four local
rules each tick (accelerate, brake for the car ahead, randomly "dawdle",
move). Despite that, dense traffic spontaneously clumps into jams that
persist and crawl *backwards* against the direction of travel. This is a
real, measured phenomenon in highway traffic, not just a simulation
artifact — it's why you sometimes stop on a highway for no visible reason.

## Run it

```
python3 traffic_sim.py
```

This prints ~60 animated frames of the road to the terminal (`·` = empty
cell, denser glyphs = faster cars), then finishes the remaining ticks
silently and writes `spacetime.ppm`, a space-time diagram (x = position on
the road, y = time flowing downward, color = speed: red/dark = jammed,
green = free-flowing). Open the PPM with any image viewer that supports the
format (e.g. `open spacetime.ppm` on macOS, or convert it with
`sips -s format png spacetime.ppm --out spacetime.png`).

Pass `--no-animate` to skip the terminal animation and just get the summary
+ image.

## The interesting bit

The only source of randomness is the "dawdle" rule: a moving car has some
probability each tick of losing one unit of speed for no reason (modeling
a driver's imperfect reaction). That's enough to occasionally force the
car behind it to brake harder than necessary. The extra braking propagates
backward through the line of cars, and because each following car reacts
slightly overcautiously, the disturbance doesn't dissipate — it grows into
a jam that moves upstream (backward) even while every individual car is
trying to move forward. In the space-time diagram this shows up as dark
diagonal streaks slanting against the direction of traffic flow — the
signature of a phantom jam.

`spacetime.ppm` in this folder is a sample run (fixed random seed `7`,
100-cell road, 28 cars, `V_MAX=5`, 30% dawdle probability).
