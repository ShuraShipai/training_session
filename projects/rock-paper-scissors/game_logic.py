"""Round and scoring rules for the independent RPS application."""
from dataclasses import dataclass, field
import math
import secrets

MOVES = ("Rock", "Paper", "Scissors")
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
    if len(detections) != 1:
        return None
    label, confidence = detections[0]
    if label not in MOVES or not math.isfinite(confidence) or not MIN_CONFIDENCE <= confidence <= 1:
        return None
    return label, confidence


@dataclass
class Game:
    player_score: int = 0
    computer_score: int = 0
    draws: int = 0
    round_id: int = 0
    completed: bool = False
    player: str = ""
    result: str = ""
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
        self.player = self.result = ""
        self.computer = secrets.choice(MOVES)

    def reset(self):
        self.player_score = self.computer_score = self.draws = 0
        self.play_again()
