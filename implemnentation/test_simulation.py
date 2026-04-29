import unittest
from random import Random

from .config import SimulationConfig
from .dna import HumanDNA, MinotaurDNA
from .fitness import minotaur_exploration_score
from .maze import MAZE_GRIDS, Maze
from .models import HumanAgent, MinotaurAgent
from .perception import ScentMap
from .simulation import LabyrinthEvolution


class MazeTests(unittest.TestCase):
    def test_default_maze_has_reachable_exit(self) -> None:
        maze = Maze.default()
        distance = maze.shortest_distance(maze.entrances[0], maze.exit_position)

        self.assertLess(distance, maze.width * maze.height)

    def test_all_maze_choices_are_valid_and_reachable(self) -> None:
        for maze_id in MAZE_GRIDS:
            with self.subTest(maze_id=maze_id):
                maze = Maze.by_id(maze_id)
                distance = maze.shortest_distance(maze.entrances[0], maze.exit_position)

                self.assertTrue(maze.is_walkable(maze.minotaur_start))
                self.assertEqual(len(maze.landmarks), 20)
                self.assertEqual(
                    maze.reachable_positions(maze.minotaur_start),
                    maze.walkable_positions(),
                )
                self.assertLess(distance, maze.width * maze.height)


class DNATests(unittest.TestCase):
    def test_mutation_keeps_values_in_range(self) -> None:
        rng = Random(1)
        human = HumanDNA.random(rng).mutate(1.0, rng)
        minotaur = MinotaurDNA.random(rng).mutate(1.0, rng)

        for value in human.__dict__.values():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
        for value in minotaur.__dict__.values():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)


class SimulationTests(unittest.TestCase):
    def test_one_generation_runs(self) -> None:
        config = SimulationConfig(
            generations=1,
            human_population=6,
            minotaur_population=2,
            active_minotaurs=2,
            max_steps=40,
            random_seed=3,
        )
        evolution = LabyrinthEvolution(config)
        history = evolution.run()

        self.assertEqual(len(history), 1)
        self.assertEqual(len(evolution.human_population), 6)
        self.assertEqual(len(evolution.minotaur_population), 2)

    def test_agents_can_stack_on_same_cell(self) -> None:
        config = SimulationConfig(
            generations=1,
            human_population=4,
            minotaur_population=1,
            active_minotaurs=3,
            max_steps=10,
            random_seed=5,
        )
        evolution = LabyrinthEvolution(config)

        humans = evolution._spawn_humans()
        minotaurs = evolution._spawn_minotaurs(evolution.minotaur_population[0])

        self.assertEqual(len({human.position for human in humans}), 1)
        self.assertEqual(len(minotaurs), 3)
        self.assertEqual(len({minotaur.position for minotaur in minotaurs}), 1)

    def test_only_escaped_humans_are_used_as_parents(self) -> None:
        config = SimulationConfig(
            human_population=4,
            minotaur_population=1,
            mutation_rate=0.0,
            elite_count=1,
            random_seed=8,
        )
        evolution = LabyrinthEvolution(config)
        escaped_dna = HumanDNA(0.10, 0.20, 0.30, 0.40, 0.50, 0.60)
        evolution.human_population = [
            escaped_dna,
            HumanDNA(0.90, 0.90, 0.90, 0.90, 0.90, 0.90),
            HumanDNA(0.80, 0.80, 0.80, 0.80, 0.80, 0.80),
            HumanDNA(0.70, 0.70, 0.70, 0.70, 0.70, 0.70),
        ]

        evolution._breed_next_generation(
            human_scores=[100.0, 900.0, 800.0, 700.0],
            human_parent_flags=[True, False, False, False],
            minotaur_scores=[1.0],
        )

        self.assertEqual(evolution.human_population, [escaped_dna] * 4)

    def test_minotaur_exploration_rewards_longer_unique_paths(self) -> None:
        config = SimulationConfig(human_population=1, minotaur_population=1, random_seed=2)
        evolution = LabyrinthEvolution(config)
        dna = evolution.minotaur_population[0]
        short_minotaur = MinotaurAgent.spawn(dna, evolution.maze.minotaur_start)
        long_minotaur = MinotaurAgent.spawn(dna, evolution.maze.minotaur_start)
        long_minotaur.path = [
            (7, 7),
            (7, 8),
            (7, 9),
            (8, 9),
            (9, 9),
            (9, 10),
            (9, 11),
        ]

        self.assertGreater(
            minotaur_exploration_score(evolution.maze, [long_minotaur]),
            minotaur_exploration_score(evolution.maze, [short_minotaur]),
        )

    def test_best_human_score_path_is_recorded(self) -> None:
        config = SimulationConfig(human_population=1, minotaur_population=1, random_seed=4)
        evolution = LabyrinthEvolution(config)
        human = HumanAgent.spawn(evolution.human_population[0], evolution.maze.entrances[0])
        human.escaped = True
        human.path = [evolution.maze.entrances[0], evolution.maze.exit_position]

        evolution._record_best_human_score_path([human], [500.0])

        self.assertEqual(evolution.best_human_score, 500.0)
        self.assertEqual(evolution.best_human_score_path, human.path)

    def test_scent_map_decays_old_human_trails(self) -> None:
        scent = ScentMap(drop_strength=1.0, decay_rate=0.5, minimum_strength=0.2)

        scent.deposit((1, 1))
        scent.decay()
        scent.decay()
        scent.decay()

        self.assertEqual(scent.strength_at((1, 1)), 0.0)

    def test_line_of_sight_is_blocked_by_walls(self) -> None:
        maze = Maze.default()

        self.assertTrue(maze.line_of_sight((1, 1), (5, 1)))
        self.assertFalse(maze.line_of_sight((1, 1), (7, 1)))


if __name__ == "__main__":
    unittest.main()
