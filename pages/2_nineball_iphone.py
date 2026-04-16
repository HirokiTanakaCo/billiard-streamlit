import streamlit as st
import base64
from pathlib import Path
import html

from logic.core import MatchState, Player
from logic.nineball_surface import create_initial_state

# --- 1. Page Config ---
st.set_page_config(page_title="9-Ball ScoreBoard", page_icon="🎱", layout="centered")

# --- 2. Base64 Image Loader ---
def get_base64_img(file_name):
    path = Path(__file__).parent / "image" / file_name
    if path.exists():
        return f"data:image/png;base64,{base64.b64encode(path.read_bytes()).decode()}"
    return ""

IMG_TURN_B64 = get_base64_img("1_turn.png")
IMG_NOTURN_B64 = get_base64_img("1_noturn.png")

# --- 3. Session State（dict → MatchState）---
if "nineball_state" not in st.session_state:
    st.session_state.nineball_state = create_initial_state()

state: MatchState = st.session_state.nineball_state

if "show_win" not in st.session_state:
    st.session_state.show_win = False

# --- 4. Logic Functions（core API に移行）---
def snapshot():
    state.snapshot()

def add_score():
    if state.finished:
        return
    snapshot()
    p = state.current_player()
    p.wins += 1
    if p.wins >= p.target:
        state.finished = True
        state.winner = p.name
        st.session_state.show_win = True

def minus_score():
    if state.finished:
        return
    snapshot()
    p = state.current_player()
    p.wins = max(0, p.wins - 1)

def change_turn():
    snapshot()
    state.next_turn()

def undo():
    state.undo()
    st.session_state.show_win = state.finished

def reset_match():
    snapshot()
    for p in state.players:
        p.wins = 0
    state.turn = 0
    state.finished = False
    state.winner = ""
    state.history.clear()
    st.session_state.show_win = False

# --- 5. CSS（元 iPhone 版そのまま）---
BALL_9_COLOR = "#F7C948"

st.markdown(f"""
<style>
.stApp {{ background-color: #000000 !important; }}
.block-container {{ padding: 15px 5px 0 5px !important; max-width: 100% !important; }}

.header-box {{
    display: flex; justify-content: center; align-items: center;
    gap: 12px; margin-bottom: 15px;
}}
.ball-9-icon {{
    width: 35px; height: 35px; border-radius: 50%;
    background: radial-gradient(circle at 50% 50%, #fff 0 35%, transparent 38%),
                linear-gradient(#fff 0 25%, {BALL_9_COLOR} 25% 75%, #fff 75%);
    border: 2px solid white; display: flex; justify-content: center; align-items: center;
    color: #111; font-weight: 950; font-size: 13px;
}}
.title-text {{ font-weight: 950; color: #fff; font-size: 22px; }}

.win-banner {{
    width: 100%;
    background: linear-gradient(90deg, rgba(23,26,37,0.4) 0%, rgba(247,201,72,0.2) 15%, rgba(247,201,72,0.2) 85%, rgba(23,26,37,0.4) 100%), #171a25;
    border-top: 2px solid {BALL_9_COLOR};
    border-bottom: 2px solid {BALL_9_COLOR};
    padding: 10px 0;
    margin-bottom: 15px;
    text-align: center;
}}
.win-title {{ color: {BALL_9_COLOR}; font-weight: 900; font-size: 28px; letter-spacing: 4px; margin: 0; }}
.win-player {{ color: #ffffff; font-weight: 800; font-size: 20px; margin: 0; }}

.player-row {{
    background: #171a25; border: 2px solid #2b3142; border-radius: 15px;
    display: flex; align-items: center; padding: 0 20px;
    justify-content: space-between;
}}
.active-card {{ border-color: {BALL_9_COLOR} !important; }}
.win-card {{ border-color: {BALL_9_COLOR} !important; }}

div[data-testid="stHorizontalBlock"] {{
    display: flex !important; flex-direction: row !important;
    flex-wrap: nowrap !important; width: 100% !important; gap: 5px !important;
}}
div[data-testid="stHorizontalBlock"] > div {{
    width: 48% !important;
    flex: 1 1 48% !important;
    min-width: 48% !important;
}}

div.stButton > button {{
    width: 100% !important; height: 46px !important;
    font-size: 11px !important;
}}

div[data-testid="stVerticalBlock"] > div:has(button[key="main_plus_btn"]) button {{
    background-color: #f7c948 !important; color: #111 !important;
    font-size: 18px !important; font-weight: 900 !important; height: 60px !important;
}}

</style>

<div class="header-box">
  <div class="ball-9-icon">9</div>
  <div class="title-text">9-Ball Scoreboard</div>
</div>
""", unsafe_allow_html=True)

# --- 6. WIN 表示 ---
if state.finished and st.session_state.show_win:
    st.markdown(f"""
        <div class="win-banner">
            <p class="win-title">🏆 WIN</p>
            <p class="win-player">{html.escape(state.winner)}</p>
        </div>
    """, unsafe_allow_html=True)

# --- 7. スコアボード表示（元と同じ構造）---
num_p = len(state.players)
if num_p <= 2:
    row_height, score_size, name_size, icon_h = "180px", "100px", "24px", "32px"
elif num_p == 3:
    row_height, score_size, name_size, icon_h = "130px", "75px", "20px", "26px"
else:
    row_height, score_size, name_size, icon_h = "95px", "50px", "16px", "18px"

for i, p in enumerate(state.players):
    is_turn = (i == state.turn)
    is_winner = (p.name == state.winner)
    card_cls = "win-card" if is_winner else ("active-card" if is_turn else "")
    icon_b64 = IMG_TURN_B64 if is_turn else IMG_NOTURN_B64

    st.markdown(f"""
      <div class="player-row {card_cls}" style="height:{row_height}; margin-bottom:10px;">
        <div class="player-info">
          <div class="player-name" style="font-size:{name_size};">{p.name}</div>
          <div style="color:#aaa; font-size:12px;">GOAL: {p.target}</div>
          <img src="{icon_b64}" style="height:{icon_h}; margin-top:10px;">
        </div>
        <div class="score-display" style="font-size:{score_size};">{p.wins}</div>
      </div>
    """, unsafe_allow_html=True)

# --- 8. 操作ボタン群（元 iPhone UX 完全維持）---
current_p = state.current_player()

if st.button(f"【 {current_p.name} 】に +1 点", key="main_plus_btn", use_container_width=True):
    add_score()
    st.rerun()

c1, c2 = st.columns(2)
with c1:
    if st.button("手番交代 ⇄", use_container_width=True):
        change_turn()
        st.rerun()
with c2:
    if st.button("修正 −1", use_container_width=True):
        minus_score()
        st.rerun()

c3, c4 = st.columns(2)
with c3:
    if st.button("UNDO (戻す)", use_container_width=True):
        undo()
        st.rerun()
with c4:
    if st.button("RESET", use_container_width=True):
        reset_match()
        st.rerun()

# --- 9. Settings（元コードそのまま）---
st.markdown("---")
with st.expander("⚙ プレイヤー設定"):
    c1, c2 = st.columns(2)
    with c1:
        if st.button("＋ プレイヤー追加", use_container_width=True):
            snapshot()
            state.players.append(Player(f"Player {len(state.players)+1}"))
            st.rerun()
    with c2:
        if st.button("ー プレイヤー削除", use_container_width=True) and len(state.players) > 1:
            snapshot()
            state.players.pop()
            state.turn = min(state.turn, len(state.players)-1)
            st.rerun()

    with st.form("settings_form"):
        for i, p in enumerate(state.players):
            st.markdown(f"**Player {i+1} 設定**")
            p.name = st.text_input("名前", p.name, key=f"name_{i}")
            p.target = st.number_input("目標得点", 1, 99, p.target, key=f"target_{i}")
        if st.form_submit_button("設定を保存して反映", use_container_width=True):
            st.rerun()