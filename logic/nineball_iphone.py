# logic/nineball_iphone.py

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

    def current_player(self):
        return self.players[self.turn]

    # 👇 メイン側で snapshot() なども呼んでいるので、空の関数を作っておくとエラーを防げます
    def snapshot(self):
        pass

    def next_turn(self):
        self.turn = (self.turn + 1) % len(self.players)

    def undo(self):
        pass

def create_initial_state():
    """
    Streamlit pages から呼ばれる場合の入口。
    今は『初期状態を返すだけ』でOK。
    """
    return MatchState()