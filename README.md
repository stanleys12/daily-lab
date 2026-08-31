# daily-lab 🧪

An **autonomous daily AI experiment lab**. Every day, [Claude Code](https://claude.com/claude-code) runs on a schedule on my machine, invents one small self-contained project, builds it, tests it, and commits it here.

This repo is automation — disclosed and on purpose. Commits are co-authored by Claude, and each project is generated end-to-end without manual intervention. The fun is in seeing what a fresh AI session comes up with each day, one tiny runnable program at a time.

## How it works

1. A `launchd` agent fires once a day (at login or on the hour, whichever comes first).
2. It launches a headless Claude Code session with a prompt asking for a *new* small project that doesn't repeat anything in the index below.
3. Claude writes the project into `projects/YYYY-MM-DD-<slug>/`, runs it to verify it works, and updates the index.
4. The runner script commits and pushes the result.

Each project lives in its own folder with a README and is runnable with plain `python3` or `node` — no dependencies.

## Project index

| Date | Project | What it is |
|------|---------|------------|
| 2026-08-29 | [lsystem-garden](projects/2026-08-29-lsystem-garden) | Grammar-driven fractal plants/curves (L-systems) rendered to SVG via a hand-rolled turtle interpreter |
| 2026-08-30 | [phantom-traffic-jam](projects/2026-08-30-phantom-traffic-jam) | Nagel-Schreckenberg traffic cellular automaton showing backward-propagating "phantom" jams, animated in-terminal and rendered as a PPM space-time diagram |
| 2026-08-31 | [thompson-regex](projects/2026-08-31-thompson-regex) | Regex engine built from scratch: recursive-descent parser + Thompson NFA construction, matched via parallel-thread simulation (no backtracking, no `re` module) |
