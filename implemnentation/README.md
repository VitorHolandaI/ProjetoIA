# Minotaur Labyrinth GA Implementation

This folder contains a first complete implementation of the project idea from `MINOTAUR_GA_ROADMAP.md`.

It has a console mode, a terminal animation mode, and a Pygame window mode.

## Run

From the repo root:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --generations 40 --replay
```

Small quick run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --generations 5 --humans 12 --minotaurs 3 --time-limit 80 --replay
```

Watch it move in the terminal:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --visual --generations 10 --humans 12 --minotaurs 3 --time-limit 80
```

Watch it in a Pygame window:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --pygame --generations 10 --humans 12 --minotaurs 3 --time-limit 80
```

The Pygame command shows 5 labyrinths before the experiment starts. Click one map or press `1`-`5`.

Train first, then show only the best human result:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --train-then-show --generations 50 --humans 20 --minotaurs 3 --time-limit 100
```

Skip the selection screen:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --pygame --maze 2 --generations 10 --humans 12 --minotaurs 3 --time-limit 80
```

Slow down the animation:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --pygame --step-delay 0.35 --generations 10 --humans 12 --minotaurs 3 --time-limit 80
```

`--time-limit` is measured in simulation ticks. Any human that has not escaped or been caught when the limit ends is counted as `timed_out`. The old `--steps` option still works as an alias.

You can also use frames per second directly:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --pygame --fps 2
```

Make the Minotaur faster or slower:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --pygame --generations 20 --minotaur-speed 1
```

Save stats:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m implemnentation.main --generations 40 --csv implemnentation/results.csv
```

Run tests:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m unittest implemnentation.test_simulation
```

## What Is Implemented

- Human DNA with exploration, exit bias, landmark memory, danger avoidance, loop avoidance, and Minotaur fear.
- Minotaur DNA with chase, traffic memory, landmark patrol, entrance prediction, and random patrol.
- Fitness functions for humans and Minotaur.
- Parent selection, crossover, mutation, and elitism.
- Twenty landmarks per labyrinth that become safer or more dangerous based on previous generations.
- Traffic memory so the Minotaur can learn where humans usually walk.
- Human scent trails with decay, used by the Minotaur while hunting.
- Hearing by path distance, so walls affect how close agents feel.
- Vision in straight corridors, blocked by walls.
- Individual human landmark memory during each life.
- Five selectable labyrinths in the Pygame GUI.
- All walkable cells in every labyrinth are connected, so the Minotaur cannot spawn inside a closed pocket.
- Multiple active Minotaurs in the same maze.
- Stacked humans and stacked Minotaurs are allowed on the same cell.
- Human parents are selected only from humans that escaped.
- Minotaur fitness now rewards captures and map exploration.
- Console metrics per generation.
- Terminal animation mode with `--visual`.
- Pygame window mode with `--pygame`.
- Training mode with `--train-then-show`, which runs generations without live animation and opens the GUI only for the best human result.
- ASCII replay of the best escaped path.

## Agent Behavior

Humans:

- Move randomly sometimes, based on `exploration_rate`.
- Prefer moves that reduce path distance to the exit.
- Avoid cells already visited by the same human.
- Remember landmarks seen during their own life.
- Use global landmark history to prefer safer landmarks and avoid dangerous ones.
- Fear Minotaurs they can see in a straight corridor.
- Also react to nearby Minotaurs by hearing, using path distance through the maze.

Minotaurs:

- Move randomly sometimes, based on `random_patrol_rate`.
- Chase humans they can see in a straight corridor.
- Hear nearby humans by path distance, even when walls block vision.
- Follow human scent trails; scent fades every simulation tick.
- Prefer paths with previous human traffic.
- Patrol landmarks that humans often pass.
- Explore new cells and longer paths, so they can learn the map.

There is no diagonal movement. Capture happens when a human and a Minotaur occupy the same cell.

## Reading The Output

- `human best`: best human fitness in the generation.
- `human avg`: average human fitness in the generation.
- `minotaur best`: best Minotaur fitness in the generation.
- `minotaur avg`: average Minotaur fitness in the generation.
- `esc`: average escaped humans per Minotaur trial.
- `caught`: average caught humans per Minotaur trial.
- `timeout`: average humans that neither escaped nor got caught.
- `best path`: shortest escaped path found so far.
- `mino unique`: best count of unique cells explored by a Minotaur path.

## Next Useful Improvements

- Add random maze generation.
- Add multiple entrances.
- Plot the CSV data.
- Compare runs with landmarks disabled.
