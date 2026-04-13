# logic/nineball_surface.py
from logic.core import Player, MatchState


def create_initial_state() -> MatchState:
    return MatchState(players=[
        Player("Player 1"),
        Player("Player 2"),
    ])
