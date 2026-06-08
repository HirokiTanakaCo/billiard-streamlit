# logic/nineball_iphone.py
from logic.core import Player, MatchState

def create_initial_state():
    """
    Streamlit pages から呼ばれる場合の入口。
    今は『初期状態を返すだけ』でOK。
    """
    return MatchState(players=[
        Player("Player 1"),
        Player("Player 2"),
    ])