import unittest
from app.components.game import Game, winner, valid_detection


class GameTests(unittest.TestCase):
    def test_all_nine_results(self):
        expected = {
            ("Rock", "Rock"): "Draw", ("Rock", "Paper"): "Computer Wins",
            ("Rock", "Scissors"): "You Win", ("Paper", "Rock"): "You Win",
            ("Paper", "Paper"): "Draw", ("Paper", "Scissors"): "Computer Wins",
            ("Scissors", "Rock"): "Computer Wins", ("Scissors", "Paper"): "You Win",
            ("Scissors", "Scissors"): "Draw",
        }
        for (player, computer), result in expected.items():
            with self.subTest(player=player, computer=computer):
                game = Game(computer=computer)
                self.assertEqual(winner(player, computer), result)
                self.assertTrue(game.confirm([(player, .9)], game.round_id))
                self.assertEqual(game.result, result)
                self.assertEqual((game.player_score, game.computer_score, game.draws),
                                 (int(result == "You Win"), int(result == "Computer Wins"), int(result == "Draw")))

    def test_duplicate_confirmation_and_stale_round(self):
        game = Game(computer="Rock")
        self.assertTrue(game.confirm([("Paper", .9)], 0))
        for _ in range(30):
            self.assertFalse(game.confirm([("Paper", .9)], 0))
        self.assertEqual(game.player_score, 1)
        game.play_again()
        self.assertFalse(game.confirm([("Paper", .9)], 0))
        self.assertEqual(game.player_score, 1)
        self.assertFalse(game.completed)

    def test_invalid_detections_do_not_score(self):
        for detections in ([], [("Rock", .59)], [("hand", .99)], [("Rock", float("nan"))],
                           [("Rock", float("inf"))], [("Rock", 1.1)], [("Rock", -.1)],
                           [("Rock", .99), ("Paper", .99)]):
            with self.subTest(detections=detections):
                game = Game()
                self.assertIsNone(valid_detection(detections))
                self.assertFalse(game.confirm(detections, 0))
                self.assertEqual((game.player_score, game.computer_score, game.draws), (0, 0, 0))

    def test_threshold_reset_and_session_isolation(self):
        game, other = Game(computer="Rock"), Game()
        self.assertTrue(game.confirm([("Rock", .60)], 0))
        self.assertEqual(game.draws, 1)
        game.reset()
        self.assertEqual((game.player_score, game.computer_score, game.draws), (0, 0, 0))
        self.assertEqual(game.round_id, 1)
        self.assertFalse(game.completed)
        self.assertEqual(other.round_id, 0)

    def test_invalid_move(self):
        with self.assertRaises(ValueError):
            winner("Lizard", "Rock")
