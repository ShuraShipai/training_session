"""Round state independent of the UI and detection engine."""
from dataclasses import dataclass, field
import math
import secrets
from typing import Optional

MOVES = ("Rock", "Paper", "Scissors")
# The preserved checkpoint returns the second hand at ~0.27–0.50 confidence
# on the user's actual camera view. A 0.60 gate discarded valid gestures.
MIN_CONFIDENCE = 0.25


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
    """Pick the strongest confident gesture in each player lane.

    A YOLO frame may contain extra low-confidence or overlapping class boxes for
    the same hand. Requiring exactly two raw boxes made otherwise usable frames
    fail. Filter candidates, then choose the strongest detection independently
    on each side of the visible center line.
    """
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
    result: Optional[str] = None

    def confirm(self, detections, round_id):
        pair = valid_pair(detections)
        if self.completed or round_id != self.round_id or pair is None:
            return False
        self.player1, self.player2 = pair[0][0], pair[1][0]
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

    def reset(self):
        self.player1_score = self.player2_score = self.draws = 0
        self.play_again()


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
