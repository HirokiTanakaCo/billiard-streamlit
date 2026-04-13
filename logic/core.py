# logic/core.py
from dataclasses import dataclass, field
from typing import List


@dataclass
class Player:
    name: str
    wins: int = 0       # 共通で wins に統一
    target: int = 3     # 勝利条件（ハンデ）


@dataclass
class MatchState:
    players: List[Player] = field(default_factory=list)
    turn: int = 0                   # 現在の手番 index
    history: list = field(default_factory=list)
    winner: str = ""
    finished: bool = False

    # ---- 共通ユーティリティ ----
    def current_player(self) -> Player:
        return self.players[self.turn]

    def next_turn(self):
        self.turn = (self.turn + 1) % len(self.players)

    def prev_turn(self):
        self.turn = (self.turn - 1) % len(self.players)

    def snapshot(self):
        self.history.append({
            "players": [(p.name, p.wins, p.target) for p in self.players],
            "turn": self.turn,
            "finished": self.finished,
            "winner": self.winner,
        })

    def undo(self):
        if not self.history:
            return
        snap = self.history.pop()
        for i, p in enumerate(self.players):
            p.name, p.wins, p.target = snap["players"][i]
        self.turn = snap["turn"]
        self.finished = snap["finished"]
        self.winner = snap["winner"]