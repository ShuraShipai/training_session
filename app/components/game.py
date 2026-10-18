"""Round state independent of the UI and detection engine."""
from dataclasses import dataclass, field
import math
import secrets
from typing import Optional

MOVES = ("Rock", "Paper", "Scissors")
# Keep the deployed game's existing confidence requirement unchanged.
MIN_CONFIDENCE = 0.60


def winner(player, computer):
    if player not in MOVES or computer not in MOVES:
        raise ValueError("Choose Rock, Paper, or Scissors.")
    if player == computer:
        return "Draw"
    return "You Win" if (player, computer) in {
        ("Rock", "Scissors"), ("Paper", "Rock"), ("Scissors", "Paper")
    } else "Computer Wins"


def valid_detection(detections):
    """Reject ambiguous frames rather than arbitrarily selecting a hand."""
    if len(detections) != 1:
        return None
    label, confidence = detections[0]
    if (label not in MOVES or not math.isfinite(confidence)
            or not MIN_CONFIDENCE <= confidence <= 1):
        return None
    return label, confidence


def valid_pair(detections):
    """Return an unambiguous confident gesture in each lane, or reject the frame."""
    lanes = {"left": [], "right": []}
    for detection in detections:
        if len(detection) != 3:
            continue
        label, confidence, center_x = detection
        if (label not in MOVES or not math.isfinite(confidence)
                or not MIN_CONFIDENCE <= confidence <= 1
                or not math.isfinite(center_x) or not 0 <= center_x <= 1):
            continue
        lane = "left" if center_x < 0.5 else "right"
        lanes[lane].append((label, confidence, center_x))
    if not lanes["left"] or not lanes["right"]:
        return None
    # Duplicate boxes for one class are harmless; conflicting classes in one
    # player's zone are ambiguous and must never be scored.
    if any(len({item[0] for item in lane}) != 1 for lane in lanes.values()):
        return None
    left = max(lanes["left"], key=lambda item: item[1])
    right = max(lanes["right"], key=lambda item: item[1])
    return (left[0], left[1]), (right[0], right[1])


@dataclass
class LocalGame:
    """Two-person, same-camera game; confirmation can score only once per round."""
    player1_score: int = 0
    player2_score: int = 0
    draws: int = 0
    round_id: int = 0
    completed: bool = False
    player1: Optional[str] = None
    player2: Optional[str] = None
    player1_confidence: Optional[float] = None
    player2_confidence: Optional[float] = None
    result: Optional[str] = None

    def confirm(self, detections, round_id):
        pair = valid_pair(detections)
        if self.completed or round_id != self.round_id or pair is None:
            return False
        self.player1, self.player1_confidence = pair[0]
        self.player2, self.player2_confidence = pair[1]
        outcome = winner(self.player1, self.player2)
        self.result = {
            "You Win": "Player 1 Wins",
            "Computer Wins": "Player 2 Wins",
            "Draw": "Draw",
        }[outcome]
        self.player1_score += self.result == "Player 1 Wins"
        self.player2_score += self.result == "Player 2 Wins"
        self.draws += self.result == "Draw"
        self.completed = True
        return True

    def play_again(self):
        self.round_id += 1
        self.completed = False
        self.player1 = self.player2 = self.result = None
        self.player1_confidence = self.player2_confidence = None

    def reset(self):
        self.player1_score = self.player2_score = self.draws = 0
        self.play_again()


@dataclass
class LiveRoundTracker:
    """Automatic round state machine; one inference observation per input frame."""
    stable_moves: Optional[tuple] = None
    stable_since: Optional[float] = None
    completed_at: Optional[float] = None
    clear_since: Optional[float] = None
    clear_observations: int = 0
    waiting_for_clear: bool = False
    last_round: Optional[tuple] = None
    state: str = "WAITING_FOR_HANDS"

    def reset_candidate(self):
        self.stable_moves = None
        self.stable_since = None

    def reset(self, game):
        """Reset scores while requiring a fresh, confirmed hands-down interval."""
        game.reset()
        self.reset_candidate()
        self.completed_at = None
        self.clear_since = None
        self.clear_observations = 0
        self.waiting_for_clear = True
        self.state = "WAITING_FOR_HANDS_DOWN"
        self.last_round = None

    def update(self, game, detections, now, *, stable_seconds=0.8,
               clear_seconds=0.8, min_clear_observations=2):
        """Consume one sampled frame, debouncing gestures and physical zone release.

        Empty YOLO results are only a proxy for hands-down: this checkpoint has
        no hand-presence class. Require both zones to remain free of every model
        box for a timed interval and multiple samples. A single miss cannot rearm.
        """
        pair = valid_pair(detections)
        any_box_in_zones = any(
            len(d) == 3 and d[0] in MOVES and math.isfinite(d[1])
            and math.isfinite(d[2]) and 0 <= d[2] <= 1
            for d in detections
        )

        if game.completed:
            self.state = "WAITING_FOR_HANDS_DOWN"
            if any_box_in_zones:
                self.clear_since = None
                self.clear_observations = 0
            else:
                if self.clear_since is None:
                    self.clear_since = now
                    self.clear_observations = 1
                else:
                    self.clear_observations += 1
            if (self.clear_since is not None
                    and self.clear_observations >= min_clear_observations
                    and now - self.clear_since + 1e-9 >= clear_seconds):
                game.play_again()
                self.completed_at = None
                self.clear_since = None
                self.clear_observations = 0
                self.reset_candidate()
                self.state = "BOTH_HANDS_CLEARED"
                return "ready"
            return "round-complete"

        if self.waiting_for_clear:
            self.state = "WAITING_FOR_HANDS_DOWN"
            if any_box_in_zones:
                self.clear_since = None
                self.clear_observations = 0
                return "hands-down"
            if self.clear_since is None:
                self.clear_since = now
                self.clear_observations = 1
            else:
                self.clear_observations += 1
            if (self.clear_observations >= min_clear_observations
                    and now - self.clear_since + 1e-9 >= clear_seconds):
                self.waiting_for_clear = False
                self.clear_since = None
                self.clear_observations = 0
                self.state = "BOTH_HANDS_CLEARED"
                return "ready"
            return "clearing"

        self.state = "WAITING_FOR_HANDS"
        if pair is None:
            self.reset_candidate()
            return "waiting"

        moves = (pair[0][0], pair[1][0])
        if moves != self.stable_moves:
            self.stable_moves = moves
            self.stable_since = now
            self.state = "BOTH_HANDS_DETECTED"
            return "detected"
        self.state = "VALIDATE_GESTURES"

        if (self.stable_since is not None
                and now - self.stable_since >= stable_seconds
                and game.confirm(detections, game.round_id)):
            self.completed_at = now
            self.last_round = (game.result, game.player1, game.player2)
            self.state = "ROUND_COMPLETE"
            return "scored"
        return "countdown"


@dataclass
class Game:
    player_score: int = 0
    computer_score: int = 0
    draws: int = 0
    round_id: int = 0
    completed: bool = False
    player: Optional[str] = None
    result: Optional[str] = None
    # Commit the computer move before seeing a player detection.
    computer: str = field(default_factory=lambda: secrets.choice(MOVES))

    def confirm(self, detections, round_id):
        detection = valid_detection(detections)
        if self.completed or round_id != self.round_id or detection is None:
            return False
        self.player = detection[0]
        self.result = winner(self.player, self.computer)
        self.player_score += self.result == "You Win"
        self.computer_score += self.result == "Computer Wins"
        self.draws += self.result == "Draw"
        self.completed = True
        return True

    def play_again(self):
        self.round_id += 1
        self.completed = False
        self.player = self.result = None
        self.computer = secrets.choice(MOVES)

    def reset(self):
        self.player_score = self.computer_score = self.draws = 0
        self.play_again()
