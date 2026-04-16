# logic/nineball_surface.py

from dataclasses import dataclass, field
from typing import List

@dataclass
class Player:
    name: str
    wins: int = 0       # 共通で wins に統一
    target: int = 3     # 勝利条件（ハンデ）

@dataclass
class MatchState:
    players: List[Player] = field(default_factory=lambda: [
        Player("Player 1"),
        Player("Player 2"),
    ])
    turn: int = 0                   # 現在の手番 index
    history: list = field(default_factory=list)
    winner: str = ""
    finished: bool = False

    # ---- iPhone版と同様の共通ユーティリティ・メソッド ----

    def current_player(self) -> Player:
        """現在の手番のプレイヤーを返す"""
        return self.players[self.turn]

    def next_turn(self):
        """手番を次のプレイヤーに進める"""
        self.turn = (self.turn + 1) % len(self.players)

    def snapshot(self):
        """現在の状態を履歴に保存する（UNDO用）"""
        self.history.append({
            "players": [(p.name, p.wins, p.target) for p in self.players],
            "turn": self.turn,
            "finished": self.finished,
            "winner": self.winner,
        })

    def undo(self):
        """一回前の状態に戻す"""
        if not self.history:
            return
        snap = self.history.pop()
        for i, (name, wins, target) in enumerate(snap["players"]):
            if i < len(self.players):
                self.players[i].name = name
                self.players[i].wins = wins
                self.players[i].target = target
        
        self.turn = snap["turn"]
        self.finished = snap["finished"]
        self.winner = snap["winner"]

def create_initial_state():
    """初期状態を生成して返す (iPhone版と関数名を統一)"""
    return MatchState()