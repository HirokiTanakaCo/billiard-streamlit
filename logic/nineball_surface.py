# logic/nineball_surface.py
from logic.core import Player, MatchState

def create_initial_state():
    """初期状態を生成して返す (iPhone版と関数名を統一)"""
    return MatchState(players=[
        Player("Player 1"),
        Player("Player 2"),
    ])