import unittest
from app.components.game import (
    MIN_CONFIDENCE, Game, LiveRoundTracker, LocalGame, winner, valid_detection, valid_pair,
)


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
        for detections in ([], [("Rock", .24)], [("hand", .99)], [("Rock", float("nan"))],
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

    def test_live_pair_left_to_right_and_all_outcomes(self):
        cases = {
            ("Rock", "Scissors"): "Player 1 Wins",
            ("Scissors", "Paper"): "Player 1 Wins",
            ("Paper", "Rock"): "Player 1 Wins",
            ("Scissors", "Rock"): "Player 2 Wins",
            ("Paper", "Scissors"): "Player 2 Wins",
            ("Rock", "Paper"): "Player 2 Wins",
            ("Rock", "Rock"): "Draw",
            ("Paper", "Paper"): "Draw",
            ("Scissors", "Scissors"): "Draw",
        }
        for (left_move, right_move), result in cases.items():
            with self.subTest(left=left_move, right=right_move):
                game = LocalGame()
                # Supply in reverse order to verify positional sorting.
                detections = [(right_move, .91, .8), (left_move, .95, .2)]
                self.assertEqual(valid_pair(detections)[0][0], left_move)
                self.assertTrue(game.confirm(detections, game.round_id))
                self.assertEqual(game.result, result)
                self.assertEqual(
                    (game.player1_score, game.player2_score, game.draws),
                    (int(result == "Player 1 Wins"), int(result == "Player 2 Wins"), int(result == "Draw")),
                )

    def test_live_pair_rejects_uncertain_invalid_or_ambiguous_frames(self):
        invalid_frames = (
            [],
            [("Rock", .95, .2)],
            [("Rock", .95, .2), ("Paper", .24, .8)],
            [("Rock", .95, .2), ("Lizard", .99, .8)],
            [("Rock", .95, .4), ("Paper", .9, .42)],
        )
        for detections in invalid_frames:
            with self.subTest(detections=detections):
                game = LocalGame()
                self.assertIsNone(valid_pair(detections))
                self.assertFalse(game.confirm(detections, game.round_id))
                self.assertEqual((game.player1_score, game.player2_score, game.draws), (0, 0, 0))

    def test_live_pair_requires_both_gestures_to_meet_existing_threshold(self):
        # The strong Rock is valid, but the Scissors detection is below 60%,
        # so the two-player round is incomplete and must not score.
        detections = [("Rock", .8489, .829), ("Scissors", .3677, .230)]
        game = LocalGame()
        self.assertEqual(MIN_CONFIDENCE, .60)
        self.assertIsNone(valid_pair(detections))
        self.assertFalse(game.confirm(detections, game.round_id))
        self.assertEqual((game.player1_score, game.player2_score, game.draws), (0, 0, 0))

    def test_live_pair_uses_strongest_confident_box_in_each_lane(self):
        # Same-label duplicates are safe; conflicting gestures in one zone fail closed.
        detections = [
            ("Paper", .91, .27),
            ("Rock", .86, .78),
            ("Rock", .42, .80),
        ]
        self.assertEqual(valid_pair(detections), (("Paper", .91), ("Rock", .86)))
        self.assertIsNone(valid_pair(detections + [("Scissors", .68, .24)]))

    def test_live_round_scores_once_replay_and_reset(self):
        game = LocalGame()
        frame_detections = [("Paper", .9, .2), ("Rock", .9, .8)]
        self.assertTrue(game.confirm(frame_detections, 0))
        for _ in range(50):
            self.assertFalse(game.confirm(frame_detections, 0))
        self.assertEqual(game.player1_score, 1)
        game.play_again()
        self.assertFalse(game.completed)
        self.assertFalse(game.confirm(frame_detections, 0))
        self.assertTrue(game.confirm(frame_detections, game.round_id))
        game.reset()
        self.assertEqual((game.player1_score, game.player2_score, game.draws), (0, 0, 0))

    def test_live_tracker_scores_stable_pair_and_rearms_after_hands_lower(self):
        game = LocalGame()
        tracker = LiveRoundTracker()
        pair = [("Paper", .91, .2), ("Rock", .86, .8)]
        self.assertEqual(tracker.update(game, pair, 0.0), "detected")
        self.assertEqual(tracker.update(game, pair, 0.4), "countdown")
        self.assertEqual(tracker.update(game, pair, 0.8), "scored")
        self.assertEqual((game.player1_score, game.player2_score, game.draws), (1, 0, 0))
        for index in range(3):
            self.assertEqual(tracker.update(game, pair, 1.2 + index * .4), "round-complete")
        self.assertEqual(game.player1_score, 1)
        status = tracker.update(game, [], 3.0)
        self.assertEqual(status, "round-complete")
        status = tracker.update(game, [], 3.8)
        self.assertEqual(status, "ready")
        self.assertFalse(game.completed)
        self.assertEqual(game.round_id, 1)
        self.assertEqual(tracker.update(game, pair, 5.1), "detected")
        self.assertEqual(tracker.update(game, pair, 6.0), "scored")
        self.assertEqual(game.player1_score, 2)

    def test_single_dropout_does_not_rearm_or_score_incomplete_pair(self):
        game = LocalGame()
        tracker = LiveRoundTracker()
        pair = [("Rock", .9, .2), ("Scissors", .9, .8)]
        self.assertEqual(tracker.update(game, pair, 0), "detected")
        self.assertEqual(tracker.update(game, pair, .8), "scored")
        self.assertEqual(tracker.update(game, [], 1.0), "round-complete")
        self.assertEqual(tracker.update(game, pair[:1], 2.0), "round-complete")
        self.assertEqual(tracker.update(game, pair, 2.4), "round-complete")
        self.assertEqual(game.player1_score, 1)

    def test_one_lowered_hand_blocks_rearm_until_both_zones_clear(self):
        game = LocalGame()
        tracker = LiveRoundTracker()
        pair = [("Rock", .9, .2), ("Scissors", .9, .8)]
        self.assertEqual(tracker.update(game, pair, 0.0), "detected")
        self.assertEqual(tracker.update(game, pair, .8), "scored")
        self.assertEqual(tracker.update(game, [], 1.0), "round-complete")
        self.assertEqual(tracker.update(game, pair[:1], 1.8), "round-complete")
        self.assertEqual(tracker.update(game, [], 2.0), "round-complete")
        self.assertEqual(tracker.update(game, [], 2.8), "ready")
        self.assertEqual(game.round_id, 1)

    def test_one_player_only_never_scores_and_reset_waits_for_clear(self):
        game = LocalGame()
        tracker = LiveRoundTracker()
        only_left = [("Rock", .9, .2)]
        only_right = [("Paper", .9, .8)]
        for sample_time in (0.0, .9, 1.8):
            self.assertEqual(tracker.update(game, only_left, sample_time), "waiting")
        for sample_time in (2.7, 3.6, 4.5):
            self.assertEqual(tracker.update(game, only_right, sample_time), "waiting")
        self.assertEqual((game.player1_score, game.player2_score, game.draws), (0, 0, 0))

        pair = [("Rock", .9, .2), ("Rock", .9, .8)]
        tracker.update(game, pair, 5.0)
        self.assertEqual(tracker.update(game, pair, 5.9), "scored")
        tracker.reset(game)
        self.assertEqual((game.player1_score, game.player2_score, game.draws), (0, 0, 0))
        self.assertEqual(tracker.update(game, pair, 6.0), "hands-down")
        for sample_time in (7.0, 7.8):
            result = tracker.update(game, [], sample_time)
        self.assertEqual(result, "ready")
