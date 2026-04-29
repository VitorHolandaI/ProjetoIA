from collections.abc import Callable
from random import Random

from .config import SimulationConfig
from .dna import HumanDNA, MinotaurDNA
from .fitness import score_human, score_minotaurs
from .genetic import make_next_generation
from .knowledge import KnowledgeBase
from .maze import Maze, Position, manhattan
from .models import GenerationStats, HumanAgent, HumanRunEvent, MinotaurAgent, TrialResult
from .perception import ScentMap
from .trial_helpers import add_scores, best_escaped_path, or_flags

class LabyrinthEvolution:
    def __init__(
        self,
        config: SimulationConfig,
        maze: Maze | None = None,
    ) -> None:
        self.config = config
        self.maze = maze or Maze.default()
        self.rng = Random(config.random_seed)
        self.knowledge = KnowledgeBase()
        self.best_path: list[Position] | None = None
        self.best_human_score = 0.0
        self.best_human_score_path: list[Position] | None = None
        self.best_minotaur_path: list[Position] | None = None
        self.human_population = self._create_human_population()
        self.minotaur_population = self._create_minotaur_population()

    def run(
        self,
        on_generation: Callable[[GenerationStats], None] | None = None,
    ) -> list[GenerationStats]:
        history: list[GenerationStats] = []
        for generation in range(1, self.config.generations + 1):
            stats = self.run_generation(generation)
            history.append(stats)
            if on_generation is not None:
                on_generation(stats)
        return history

    def run_generation(self, generation: int) -> GenerationStats:
        human_totals = [0.0 for _ in self.human_population]
        human_parent_flags = [False for _ in self.human_population]
        minotaur_scores: list[float] = []
        events: list[HumanRunEvent] = []
        escaped = caught = timed_out = 0
        for minotaur_dna in self.minotaur_population:
            result = self._run_trial(minotaur_dna)
            human_totals = add_scores(human_totals, result.human_scores)
            human_parent_flags = or_flags(human_parent_flags, result.human_escaped_flags)
            minotaur_scores.append(result.minotaur_score)
            events.extend(result.human_events)
            escaped += result.escaped_count
            caught += result.caught_count
            timed_out += result.timed_out_count
            self._record_best_path(result.best_path)
        self._record_generation_knowledge(events)
        human_scores = [score / len(self.minotaur_population) for score in human_totals]
        stats = self._build_stats(generation, human_scores, minotaur_scores, escaped, caught, timed_out)
        self._breed_next_generation(human_scores, human_parent_flags, minotaur_scores)
        return stats

    def _run_trial(self, minotaur_dna: MinotaurDNA) -> TrialResult:
        humans = self._spawn_humans()
        minotaurs = self._spawn_minotaurs(minotaur_dna)
        scent = self._create_scent_map()
        self._deposit_human_scent(humans, scent)
        for step in range(1, self.config.max_steps + 1):
            self._advance_trial_step(humans, minotaurs, scent, step)
            if all(not human.is_alive for human in humans):
                break
        self._mark_timeouts(humans)
        human_scores = [score_human(self.config, self.maze, human) for human in humans]
        self._record_best_human_score_path(humans, human_scores)
        events = [self._make_human_event(human) for human in humans]
        best_path = best_escaped_path(humans)
        self._record_best_minotaur_path(minotaurs)
        return TrialResult(
            human_scores=human_scores,
            human_escaped_flags=[human.escaped for human in humans],
            human_events=events,
            minotaur_score=score_minotaurs(self.config, self.maze, self.knowledge, minotaurs, humans),
            escaped_count=sum(1 for human in humans if human.escaped),
            caught_count=sum(1 for human in humans if human.caught),
            timed_out_count=sum(1 for human in humans if human.timed_out),
            best_path=best_path,
        )

    def _create_scent_map(self) -> ScentMap:
        return ScentMap(
            self.config.scent_drop_strength,
            self.config.scent_decay_rate,
            self.config.scent_minimum_strength,
        )

    def _advance_trial_step(
        self,
        humans: list[HumanAgent],
        minotaurs: list[MinotaurAgent],
        scent: ScentMap,
        step: int,
    ) -> None:
        self._move_humans(humans, minotaurs, step)
        self._deposit_human_scent(humans, scent)
        self._move_minotaurs(minotaurs, humans, scent, step)
        scent.decay()

    def _deposit_human_scent(self, humans: list[HumanAgent], scent: ScentMap) -> None:
        for human in humans:
            if human.is_alive:
                scent.deposit(human.position)

    def _move_humans(
        self,
        humans: list[HumanAgent],
        minotaurs: list[MinotaurAgent],
        step: int,
    ) -> None:
        for human in humans:
            if not human.is_alive:
                continue
            minotaur_positions = [minotaur.position for minotaur in minotaurs]
            self._move_human(human, minotaur_positions)
            human.steps_alive = step
            catching_minotaur = self._minotaur_at_position(minotaurs, human.position)
            if catching_minotaur is not None:
                self._catch_human(human, catching_minotaur, step)

    def _move_human(self, human: HumanAgent, minotaur_positions: list[Position]) -> None:
        neighbors = self.maze.neighbors(human.position)
        if self.rng.random() < human.dna.exploration_rate:
            next_position = self.rng.choice(neighbors)
        else:
            next_position = self._best_human_move(human, neighbors, minotaur_positions)
        self._update_human_position(human, next_position)

    def _best_human_move(
        self,
        human: HumanAgent,
        neighbors: list[Position],
        minotaur_positions: list[Position],
    ) -> Position:
        scored = [
            (self._score_human_move(human, position, minotaur_positions), position)
            for position in neighbors
        ]
        best_score = max(score for score, _ in scored)
        best_positions = [position for score, position in scored if score == best_score]
        return self.rng.choice(best_positions)

    def _score_human_move(
        self,
        human: HumanAgent,
        position: Position,
        minotaur_positions: list[Position],
    ) -> float:
        if position == self.maze.exit_position:
            return 10_000.0
        score = self._exit_progress_score(human, position)
        score += self._landmark_score(human, position)
        score += self._minotaur_fear_score(human, position, minotaur_positions)
        score -= human.dna.loop_penalty_weight * human.visited_counts.get(position, 0) * 10.0
        return score + self.rng.uniform(-0.05, 0.05)

    def _exit_progress_score(self, human: HumanAgent, position: Position) -> float:
        current_distance = self.maze.shortest_distance(human.position, self.maze.exit_position)
        next_distance = self.maze.shortest_distance(position, self.maze.exit_position)
        return human.dna.exit_bias * (current_distance - next_distance) * 20.0

    def _landmark_score(self, human: HumanAgent, position: Position) -> float:
        score = 0.0
        for landmark_id in self.maze.visible_landmarks(position, radius=2):
            previous_visits = human.landmark_memory.get(landmark_id, 0)
            score += human.dna.landmark_memory_weight * self.knowledge.landmark_safety(landmark_id) * 8.0
            score -= human.dna.danger_avoidance_weight * self.knowledge.landmark_danger(landmark_id) * 12.0
            score -= human.dna.loop_penalty_weight * previous_visits * 1.5
        return score

    def _minotaur_fear_score(
        self,
        human: HumanAgent,
        position: Position,
        minotaur_positions: list[Position],
    ) -> float:
        current_distance = min(self.maze.shortest_distance(human.position, minotaur) for minotaur in minotaur_positions)
        next_distance = min(self.maze.shortest_distance(position, minotaur) for minotaur in minotaur_positions)
        if next_distance == 0:
            return -10_000.0
        if self._human_sees_minotaur(human.position, minotaur_positions):
            return human.dna.minotaur_fear_weight * (next_distance - current_distance) * 32.0
        if current_distance > self.config.human_hearing:
            return 0.0
        return human.dna.minotaur_fear_weight * (next_distance - current_distance) * 12.0

    def _human_sees_minotaur(
        self,
        human_position: Position,
        minotaur_positions: list[Position],
    ) -> bool:
        return any(
            manhattan(human_position, minotaur) <= self.config.human_sight
            and self.maze.line_of_sight(human_position, minotaur)
            for minotaur in minotaur_positions
        )

    def _update_human_position(self, human: HumanAgent, position: Position) -> None:
        human.position = position
        human.path.append(position)
        human.visited_counts[position] = human.visited_counts.get(position, 0) + 1
        self._record_human_landmarks(human, position)
        if position == self.maze.exit_position:
            human.escaped = True

    def _record_human_landmarks(self, human: HumanAgent, position: Position) -> None:
        for landmark_id in self.maze.visible_landmarks(position, radius=1):
            human.seen_landmarks.add(landmark_id)
            human.landmark_memory[landmark_id] = human.landmark_memory.get(landmark_id, 0) + 1

    def _move_minotaurs(
        self,
        minotaurs: list[MinotaurAgent],
        humans: list[HumanAgent],
        scent: ScentMap,
        step: int,
    ) -> None:
        for _ in range(self.config.minotaur_moves_per_turn):
            for minotaur in minotaurs:
                if not any(human.is_alive for human in humans):
                    return
                self._move_minotaur_once(minotaur, humans, scent, step)

    def _move_minotaur_once(
        self,
        minotaur: MinotaurAgent,
        humans: list[HumanAgent],
        scent: ScentMap,
        step: int,
    ) -> None:
        neighbors = self.maze.neighbors(minotaur.position)
        if self.rng.random() < minotaur.dna.random_patrol_rate:
            next_position = self.rng.choice(neighbors)
        else:
            next_position = self._best_minotaur_move(minotaur, humans, scent, neighbors)
        self._update_minotaur_position(minotaur, next_position)
        self._catch_humans_at_position(humans, minotaur, step)

    def _best_minotaur_move(
        self,
        minotaur: MinotaurAgent,
        humans: list[HumanAgent],
        scent: ScentMap,
        neighbors: list[Position],
    ) -> Position:
        scored = [(self._score_minotaur_move(minotaur, humans, scent, position), position) for position in neighbors]
        best_score = max(score for score, _ in scored)
        best_positions = [position for score, position in scored if score == best_score]
        return self.rng.choice(best_positions)

    def _score_minotaur_move(
        self,
        minotaur: MinotaurAgent,
        humans: list[HumanAgent],
        scent: ScentMap,
        position: Position,
    ) -> float:
        score = self._chase_score(minotaur, humans, position)
        score += minotaur.dna.traffic_weight * scent.strength_at(position) * 18.0
        score += minotaur.dna.traffic_weight * self.knowledge.traffic_score(position) * 15.0
        score += self._minotaur_landmark_score(minotaur.dna, position)
        score += self._entrance_prediction_score(minotaur.dna, position)
        score += self._minotaur_exploration_move_score(minotaur, position)
        score -= minotaur.visited_counts.get(position, 0) * 1.5
        return score + self.rng.uniform(-0.05, 0.05)

    def _chase_score(
        self,
        minotaur: MinotaurAgent,
        humans: list[HumanAgent],
        position: Position,
    ) -> float:
        alive_positions = [human.position for human in humans if human.is_alive]
        current_distance = min(self.maze.shortest_distance(minotaur.position, human) for human in alive_positions)
        next_distance = min(self.maze.shortest_distance(position, human) for human in alive_positions)
        if self._minotaur_sees_human(minotaur.position, alive_positions):
            return minotaur.dna.chase_weight * (current_distance - next_distance) * 35.0
        if current_distance > self.config.minotaur_hearing:
            return 0.0
        return minotaur.dna.chase_weight * (current_distance - next_distance) * 14.0

    def _minotaur_sees_human(
        self,
        minotaur_position: Position,
        human_positions: list[Position],
    ) -> bool:
        return any(
            manhattan(minotaur_position, human) <= self.config.minotaur_sight
            and self.maze.line_of_sight(minotaur_position, human)
            for human in human_positions
        )

    def _minotaur_landmark_score(self, dna: MinotaurDNA, position: Position) -> float:
        score = 0.0
        for landmark_id in self.maze.visible_landmarks(position, radius=2):
            score += dna.landmark_patrol_weight * self.knowledge.landmark_traffic(landmark_id) * 10.0
        return score

    def _entrance_prediction_score(self, dna: MinotaurDNA, position: Position) -> float:
        score = 0.0
        for entrance in self.maze.entrances:
            distance = max(1, self.maze.shortest_distance(position, entrance))
            score += dna.entrance_prediction_weight * self.knowledge.entrance_activity(entrance) / distance
        return score * 20.0

    def _minotaur_exploration_move_score(
        self,
        minotaur: MinotaurAgent,
        position: Position,
    ) -> float:
        score = 0.0
        if position not in minotaur.visited_counts:
            score += 8.0
        current_distance = self.maze.shortest_distance(minotaur.position, self.maze.minotaur_start)
        next_distance = self.maze.shortest_distance(position, self.maze.minotaur_start)
        score += (next_distance - current_distance) * 3.0
        return score

    def _update_minotaur_position(self, minotaur: MinotaurAgent, position: Position) -> None:
        minotaur.position = position
        minotaur.path.append(position)
        minotaur.visited_counts[position] = minotaur.visited_counts.get(position, 0) + 1

    def _catch_humans_at_position(
        self,
        humans: list[HumanAgent],
        minotaur: MinotaurAgent,
        step: int,
    ) -> None:
        for human in humans:
            if human.is_alive and human.position == minotaur.position:
                self._catch_human(human, minotaur, step)

    def _catch_human(
        self,
        human: HumanAgent,
        minotaur: MinotaurAgent,
        step: int,
    ) -> None:
        human.caught = True
        human.steps_alive = step
        minotaur.capture_steps.append(step)

    def _minotaur_at_position(
        self,
        minotaurs: list[MinotaurAgent],
        position: Position,
    ) -> MinotaurAgent | None:
        for minotaur in minotaurs:
            if minotaur.position == position:
                return minotaur
        return None

    def _mark_timeouts(self, humans: list[HumanAgent]) -> None:
        for human in humans:
            if human.is_alive:
                human.timed_out = True
                human.steps_alive = self.config.max_steps

    def _make_human_event(self, human: HumanAgent) -> HumanRunEvent:
        if human.escaped:
            outcome = "escaped"
        elif human.caught:
            outcome = "caught"
        else:
            outcome = "timed_out"
        return HumanRunEvent(human.entrance, human.path, human.seen_landmarks, outcome)

    def _spawn_humans(self) -> list[HumanAgent]:
        humans: list[HumanAgent] = []
        for dna in self.human_population:
            entrance = self.rng.choice(self.maze.entrances)
            human = HumanAgent.spawn(dna, entrance)
            human.visited_counts[entrance] = 1
            self._record_human_landmarks(human, entrance)
            humans.append(human)
        return humans

    def _spawn_minotaurs(self, dna: MinotaurDNA) -> list[MinotaurAgent]:
        return [
            MinotaurAgent.spawn(dna, self.maze.minotaur_start)
            for _ in range(self.config.active_minotaurs)
        ]

    def _create_human_population(self) -> list[HumanDNA]:
        return [HumanDNA.random(self.rng) for _ in range(self.config.human_population)]

    def _create_minotaur_population(self) -> list[MinotaurDNA]:
        return [MinotaurDNA.random(self.rng) for _ in range(self.config.minotaur_population)]

    def _record_best_path(self, path: list[Position] | None) -> None:
        if path is None:
            return
        if self.best_path is None or len(path) < len(self.best_path):
            self.best_path = path

    def _record_best_human_score_path(
        self,
        humans: list[HumanAgent],
        human_scores: list[float],
    ) -> None:
        for human, score in zip(humans, human_scores, strict=True):
            if human.escaped and score > self.best_human_score:
                self.best_human_score = score
                self.best_human_score_path = list(human.path)

    def _record_best_minotaur_path(self, minotaurs: list[MinotaurAgent]) -> None:
        for minotaur in minotaurs:
            if self._is_better_minotaur_path(minotaur.path):
                self.best_minotaur_path = list(minotaur.path)

    def _is_better_minotaur_path(self, path: list[Position]) -> bool:
        if self.best_minotaur_path is None:
            return True
        current_unique = len(set(path))
        best_unique = len(set(self.best_minotaur_path))
        return current_unique > best_unique or (
            current_unique == best_unique and len(path) > len(self.best_minotaur_path)
        )

    def _record_generation_knowledge(self, events: list[HumanRunEvent]) -> None:
        for event in events:
            self.knowledge.record_human_run(
                event.entrance,
                event.path,
                event.seen_landmarks,
                event.outcome,
            )

    def _build_stats(
        self,
        generation: int,
        human_scores: list[float],
        minotaur_scores: list[float],
        escaped: int,
        caught: int,
        timed_out: int,
    ) -> GenerationStats:
        trial_count = len(self.minotaur_population)
        return GenerationStats(
            generation=generation,
            best_human_fitness=max(human_scores),
            average_human_fitness=sum(human_scores) / len(human_scores),
            best_minotaur_fitness=max(minotaur_scores),
            average_minotaur_fitness=sum(minotaur_scores) / len(minotaur_scores),
            average_escaped=escaped / trial_count,
            average_caught=caught / trial_count,
            average_timed_out=timed_out / trial_count,
            best_path_length=len(self.best_path) if self.best_path is not None else None,
            best_minotaur_path_length=len(self.best_minotaur_path) if self.best_minotaur_path else None,
            best_minotaur_unique_cells=len(set(self.best_minotaur_path)) if self.best_minotaur_path else None,
        )

    def _breed_next_generation(
        self,
        human_scores: list[float],
        human_parent_flags: list[bool],
        minotaur_scores: list[float],
    ) -> None:
        eligible_humans = [
            (dna, score)
            for dna, score, can_parent in zip(
                self.human_population,
                human_scores,
                human_parent_flags,
                strict=True,
            )
            if can_parent
        ]
        if eligible_humans:
            self.human_population = make_next_generation(
                eligible_humans,
                self.config.human_population,
                self.config.elite_count,
                self.config.mutation_rate,
                self.rng,
                lambda left, right, rng: left.crossover(right, rng),
                lambda dna, mutation_rate, rng: dna.mutate(mutation_rate, rng),
            )
        else:
            self.human_population = self._create_human_population()
        self.minotaur_population = make_next_generation(
            list(zip(self.minotaur_population, minotaur_scores, strict=True)),
            self.config.minotaur_population,
            self.config.elite_count,
            self.config.mutation_rate,
            self.rng,
            lambda left, right, rng: left.crossover(right, rng),
            lambda dna, mutation_rate, rng: dna.mutate(mutation_rate, rng),
        )
