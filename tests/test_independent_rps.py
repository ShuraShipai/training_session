import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "projects/rock-paper-scissors/game_logic.py"
spec = importlib.util.spec_from_file_location("independent_rps_game", MODULE)
logic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logic)


class IndependentGameTests(unittest.TestCase):
    def test_all_winners_and_draw(self):
        self.assertEqual(logic.winner("Rock", "Scissors"), "You Win")
        self.assertEqual(logic.winner("Paper", "Rock"), "You Win")
        self.assertEqual(logic.winner("Scissors", "Paper"), "You Win")
        self.assertEqual(logic.winner("Rock", "Paper"), "Computer Wins")
        self.assertEqual(logic.winner("Paper", "Scissors"), "Computer Wins")
        self.assertEqual(logic.winner("Scissors", "Rock"), "Computer Wins")
        self.assertEqual(logic.winner("Rock", "Rock"), "Draw")

    def test_confidence_and_one_scoring_action_per_round(self):
        game = logic.Game(computer="Scissors")
        self.assertIsNone(logic.valid_detection([("Rock", 0.24)]))
        self.assertIsNone(logic.valid_detection([("Rock", float("nan"))]))
        self.assertIsNone(logic.valid_detection([("Rock", 0.99), ("Paper", 0.99)]))
        self.assertTrue(game.confirm([("Rock", 0.9)], 0))
        self.assertFalse(game.confirm([("Rock", 0.9)], 0))
        self.assertEqual((game.player_score, game.computer_score, game.draws), (1, 0, 0))
        self.assertFalse(game.confirm([("Paper", 0.9)], 1))

    def test_replay_and_reset(self):
        game = logic.Game(computer="Rock")
        self.assertTrue(game.confirm([("Rock", 0.9)], 0))
        self.assertEqual(game.draws, 1)
        game.play_again()
        self.assertEqual(game.round_id, 1)
        self.assertFalse(game.completed)
        game.confirm([("Paper", 0.9)], 1)
        game.reset()
        self.assertEqual((game.player_score, game.computer_score, game.draws), (0, 0, 0))
        self.assertEqual(game.round_id, 2)
        self.assertFalse(game.completed)


if __name__ == "__main__":
    unittest.main()
