# logic/rotation_iphone.py

from dataclasses import dataclass, field

@dataclass
class Player:
    name: str
    wins: int = 0
    target: int = 3

@dataclass
class MatchState:
    players: list[Player] = field(default_factory=lambda: [
        Player("Player 1"),
        Player("Player 2"),
    ])
    turn: int = 0
    history: list = field(default_factory=list)
    winner: str = ""
    finished: bool = False


def simulate():
    """
    Streamlit pages から呼ばれる場合の入口。
    今は『初期状態を返すだけ』でOK。
    """
    return MatchState()