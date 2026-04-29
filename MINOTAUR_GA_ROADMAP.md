# Minotaur Labyrinth Genetic Algorithm Roadmap

This document is a practical checklist for turning the current maze experiments into a learning project about genetic algorithms.

The project idea: people enter a labyrinth, use landmarks to remember paths, try to survive the Minotaur, and pass successful behavior to the next generation. The Minotaur also learns over generations by discovering where people usually enter, which landmarks they use, and which paths are easiest to intercept.

## Project Goal

Build a simulation where two populations improve over time:

- Human agents evolve strategies for finding the exit and avoiding the Minotaur.
- The Minotaur evolves strategies for predicting, chasing, and catching humans.
- Landmarks become useful memory points that both sides can learn from.

The learning objective is not just to finish a game. The goal is to understand the genetic algorithm loop:

1. Represent behavior as DNA.
2. Run a simulation.
3. Score every agent with a fitness function.
4. Select the better agents.
5. Create the next generation with crossover and mutation.
6. Repeat and observe whether behavior improves.

## Current Code Notes

Current useful files:

- `a.py`: smallest Pygame maze drawing prototype.
- `labyrinth.py`: fixed maze, random agents, best path replay.
- `labyrinth2.py`: generated maze, `Path` objects that can become landmarks, simple movement memory.
- `genetic/src/main/java/org/example`: Java string-evolution genetic algorithm example.

Important current gaps:

- [ ] `labyrinth2.py` marks the entrance as `2` and the exit as `3`, but `find_exit()` and movement currently look for `2`.
- [ ] `reset_generation()` in `labyrinth2.py` starts agents at `(1, 1)` instead of the generated `entrada`.
- [ ] The agents do not yet inherit behavior from previous generations.
- [ ] `best_path` records the best successful route, but it is not used as DNA.
- [ ] `Path.pista` creates a landmark id, but agents do not yet use the id to make decisions.
- [ ] `time_limit` exists but is not used to end a generation.
- [ ] There is no Minotaur agent yet.
- [ ] There is no fitness score for humans or Minotaur.

## Recommended Direction

Use Python first for the labyrinth simulation because the Pygame prototype already exists. Use the Java genetic algorithm as a reference for the GA concepts: population, DNA, fitness, selection, crossover, and mutation.

After the Python version works, optionally port the clean model to Java.

## Core Concepts

### Maze

The maze should contain:

- Walls.
- Walkable paths.
- One or more entrances.
- One exit.
- Landmarks.
- Agent positions.
- Minotaur position.

Checklist:

- [ ] Define constants for wall, path, entrance, exit, and landmark cells.
- [ ] Keep coordinates consistent as `(x, y)` everywhere.
- [ ] Add a helper like `is_walkable(position)`.
- [ ] Add a helper like `neighbors(position)`.
- [ ] Add a helper like `distance_to_exit(position)`.
- [ ] Add a helper like `visible_landmarks(position, radius)`.

### Landmarks

Landmarks are the memory system. They should help agents learn where they are and which decisions are useful.

Examples:

- Statue.
- Torch.
- Fountain.
- Broken wall.
- Blood mark.
- Door symbol.

Checklist:

- [ ] Give each landmark a stable id.
- [ ] Give each landmark a position.
- [ ] Give each landmark a type or name.
- [ ] Let humans remember landmarks they passed.
- [ ] Track how often each landmark appears in successful escape paths.
- [ ] Track how often each landmark appears before a Minotaur capture.
- [ ] Use landmark scores when agents choose where to move.

## Human Agent Design

The human DNA should describe behavior, not a fixed exact path at first.

Possible human genes:

- `exploration_rate`: chance to try a random direction.
- `exit_bias`: how strongly the agent prefers moves closer to the exit.
- `landmark_memory_weight`: how strongly the agent follows known useful landmarks.
- `danger_avoidance_weight`: how strongly the agent avoids landmarks linked to captures.
- `loop_penalty_weight`: how strongly the agent avoids revisiting cells.
- `minotaur_fear_radius`: how far away the agent reacts to the Minotaur.

Checklist:

- [ ] Create a `HumanDNA` structure.
- [ ] Create random DNA for generation 0.
- [ ] Give every human a DNA instance.
- [ ] Use DNA values during movement decisions.
- [ ] Store each human path.
- [ ] Store landmarks seen by each human.
- [ ] Store whether the human escaped, died, or timed out.

## Human Fitness

Fitness decides which humans reproduce.

Suggested score:

- Large bonus for reaching the exit.
- Bonus for reaching the exit quickly.
- Bonus for ending closer to the exit.
- Bonus for using landmarks seen in successful paths.
- Penalty for being caught.
- Penalty for wasting steps.
- Penalty for loops.

Example formula:

```text
fitness =
  escape_bonus
  + distance_progress
  + landmark_success_score
  - caught_penalty
  - step_penalty
  - loop_penalty
```

Checklist:

- [ ] Implement `calculate_human_fitness(human, maze, minotaur)`.
- [ ] Print best human fitness each generation.
- [ ] Print average human fitness each generation.
- [ ] Track the best human path ever found.
- [ ] Save useful landmark statistics after every generation.

## Minotaur Agent Design

The Minotaur should also have DNA. Its behavior should improve by catching more humans.

Possible Minotaur genes:

- `spawn_prediction_weight`: preference for paths near common entrances.
- `landmark_patrol_weight`: preference for landmarks humans often use.
- `chase_weight`: how strongly it follows visible humans.
- `ambush_weight`: how strongly it waits near high-traffic landmarks.
- `random_patrol_rate`: chance to explore randomly.
- `memory_decay`: how fast old human traffic data becomes less important.

Checklist:

- [ ] Create a `MinotaurDNA` structure.
- [ ] Create one Minotaur per simulation.
- [ ] Decide if each generation has one Minotaur or a population of Minotaurs.
- [ ] Let the Minotaur move after or before humans each turn.
- [ ] Let the Minotaur catch a human when they occupy the same cell.
- [ ] Track which landmarks are near captures.
- [ ] Track which entrances produce the most humans.

## Minotaur Fitness

Fitness decides which Minotaur strategies survive.

Suggested score:

- Bonus for each captured human.
- Bonus for early captures.
- Bonus for correctly patrolling high-traffic landmarks.
- Penalty for walking in useless loops.
- Penalty when many humans escape.

Checklist:

- [ ] Implement `calculate_minotaur_fitness(minotaur, humans)`.
- [ ] Print best Minotaur fitness each generation.
- [ ] Print capture count per generation.
- [ ] Print escape count per generation.
- [ ] Track which landmarks were most dangerous.

## Genetic Algorithm Loop

This is the main learning cycle.

Checklist:

- [ ] Create an initial population of random humans.
- [ ] Create an initial population of random Minotaurs or one Minotaur strategy.
- [ ] Run the simulation for a fixed number of steps.
- [ ] Calculate human fitness.
- [ ] Calculate Minotaur fitness.
- [ ] Select parents based on fitness.
- [ ] Use crossover to create children.
- [ ] Use mutation to keep variation.
- [ ] Keep the best few agents unchanged with elitism.
- [ ] Repeat for many generations.

Basic pseudocode:

```text
create population

for generation in generations:
    reset maze
    run simulation
    score humans
    score minotaur
    save metrics
    select parents
    create children with crossover
    mutate children
    replace old population
```

## Milestone Checklist

### Milestone 1: Fix The Current Maze Prototype

- [ ] Fix entrance and exit constants in `labyrinth2.py`.
- [ ] Make `find_exit()` return the exit cell, not the entrance.
- [ ] Start every generation from `entrada`.
- [ ] Stop a generation when all humans escape, die, or time out.
- [ ] Remove unused code or mark it as TODO.
- [ ] Print generation number, escaped count, and best path length.

Done when:

- [ ] Agents can reliably move from the entrance.
- [ ] The simulation correctly detects the exit.
- [ ] Generations reset without breaking the maze.

### Milestone 2: Add A Real Human DNA

- [ ] Add `HumanDNA`.
- [ ] Add random DNA creation.
- [ ] Add DNA-based movement decisions.
- [ ] Add mutation.
- [ ] Add crossover.
- [ ] Add a fitness score.

Done when:

- [ ] Better humans are more likely to become parents.
- [ ] Children inherit mixed behavior from parents.
- [ ] Some mutation creates new behavior.

### Milestone 3: Use Landmarks For Learning

- [ ] Place named landmarks in the maze.
- [ ] Record landmarks seen by each human.
- [ ] Score landmarks based on escapes and deaths.
- [ ] Let human DNA decide how much to trust landmark memory.
- [ ] Show landmark scores in the console.

Done when:

- [ ] Successful paths make nearby landmarks more attractive.
- [ ] Dangerous landmarks become less attractive.

### Milestone 4: Add The Minotaur

- [ ] Add a Minotaur position.
- [ ] Draw the Minotaur in Pygame.
- [ ] Move the Minotaur each turn.
- [ ] Detect captures.
- [ ] End a human run when captured.
- [ ] Add simple chase behavior.

Done when:

- [ ] Humans can escape, be caught, or time out.
- [ ] Capture count is printed each generation.

### Milestone 5: Evolve The Minotaur

- [ ] Add `MinotaurDNA`.
- [ ] Add Minotaur fitness.
- [ ] Add Minotaur mutation.
- [ ] Add Minotaur crossover.
- [ ] Let Minotaur behavior depend on learned human traffic.

Done when:

- [ ] Minotaur strategies improve over generations.
- [ ] Common human routes become more dangerous.

### Milestone 6: Coevolution Experiment

- [ ] Evolve humans and Minotaur at the same time.
- [ ] Save stats per generation.
- [ ] Plot escape rate over time.
- [ ] Plot capture rate over time.
- [ ] Plot average fitness over time.
- [ ] Compare runs with and without landmarks.

Done when:

- [ ] You can explain whether landmarks helped humans survive.
- [ ] You can explain whether the Minotaur learned high-traffic zones.

### Milestone 7: Make It Easy To Study

- [ ] Add a headless mode that runs without Pygame.
- [ ] Add a visual mode that replays the best run.
- [ ] Add a config section for population size, mutation rate, and generation count.
- [ ] Save results to a CSV file.
- [ ] Add a README with run commands.

Done when:

- [ ] You can run experiments quickly.
- [ ] You can replay interesting generations visually.

## Experiment Ideas

Use these to learn how genetic algorithms behave.

- [ ] Run with mutation rate `0.01`.
- [ ] Run with mutation rate `0.05`.
- [ ] Run with mutation rate `0.10`.
- [ ] Compare small population size against large population size.
- [ ] Compare one entrance against many entrances.
- [ ] Compare fixed maze against random maze every generation.
- [ ] Compare humans with landmark memory against humans without landmark memory.
- [ ] Compare Minotaur with memory against Minotaur without memory.
- [ ] Check whether too much mutation prevents learning.
- [ ] Check whether too little mutation gets stuck.

## Terms To Learn While Building

- [ ] Population.
- [ ] Individual.
- [ ] DNA or genome.
- [ ] Gene.
- [ ] Fitness function.
- [ ] Selection.
- [ ] Mating pool.
- [ ] Crossover.
- [ ] Mutation.
- [ ] Elitism.
- [ ] Exploration vs exploitation.
- [ ] Coevolution.
- [ ] Local optimum.
- [ ] Convergence.

## Suggested First Implementation Order

1. Fix `labyrinth2.py` entrance and exit detection.
2. Add a simple fitness score for humans.
3. Add `HumanDNA` with only three genes: exploration, exit bias, and loop avoidance.
4. Add selection, crossover, and mutation for humans.
5. Add named landmarks and landmark memory.
6. Add a simple Minotaur that chases the nearest human.
7. Add Minotaur DNA.
8. Run experiments and write down what changed.

## Definition Of A Finished Learning Version

- [ ] The maze has entrance, exit, landmarks, humans, and Minotaur.
- [ ] Humans have DNA.
- [ ] Minotaur has DNA.
- [ ] Humans and Minotaur receive fitness scores.
- [ ] New generations inherit from better previous agents.
- [ ] Mutation sometimes creates new behavior.
- [ ] The program prints useful generation statistics.
- [ ] The best human path can be replayed.
- [ ] The project has at least one experiment comparing different settings.

