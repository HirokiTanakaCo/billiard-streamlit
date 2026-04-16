# =========================================================
# Nine Ball - Surface Giant UI（最終確定・安定版）
# 操作ボタン安定 / key指定CSS / デグレなし
# =========================================================

import streamlit as st
import html

from logic.core import MatchState, Player
from logic.nineball_surface import create_initial_state

from pathlib import Path
import base64

def get_base64_img(file_name):
    path = Path(__file__).parent / "image" / file_name
    try:
        if path.exists():
            return f"data:image/png;base64,{base64.b64encode(path.read_bytes()).decode()}"
    except:
        pass
    return ""

IMG_TURN_B64 = get_base64_img("1_turn.png")
IMG_NOTURN_B64 = get_base64_img("1_noturn.png")

# ---------------------------------------------------------
# Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Nine Ball Game - Surface",
    page_icon="🎱",
    layout="wide",
)

# ---------------------------------------------------------
# Session Init
# ---------------------------------------------------------
if "nineball_state" not in st.session_state:
    st.session_state.nineball_state = create_initial_state()

if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

if "show_win" not in st.session_state:
    st.session_state.show_win = False

if "win_winner" not in st.session_state:
    st.session_state.win_winner = ""

state: MatchState = st.session_state.nineball_state


# ---------------------------------------------------------
# CSS（操作ボタン key 指定・Surface サイズ）
# ---------------------------------------------------------
# ---------------------------------------------------------
# CSS（操作ボタン key 指定・Surface サイズ / 画像表示対応版）
# ---------------------------------------------------------
# 冒頭に f をつけ、中身の CSS 波括弧をすべて {{ }} に置換済みです
st.markdown(f"""
<style>
/* =========================================================
   Nine Ball - Surface Giant UI
   最終確定 CSS（画像表示対応・二重波括弧適用済）
   ========================================================= */

/* Streamlit標準ヘッダーとフッターを隠して全画面感を出す */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
.block-container {{
    padding-top: 2rem;
    padding-bottom: 0rem;
}}

/* ===============================
   Expander（設定エリア）の文字サイズ拡大
   =============================== */
[data-testid="stExpander"]
[data-testid="stMarkdownContainer"] > p {{
  font-size: 22px !important;
  font-weight: 800 !important;
}}

/* =========================================================
   入力ウィジェット全体のデザイン統一 (Text & Number)
   ========================================================= */
/* 大きくできないのでデフォルトにしている */

            
/* ===============================
   スコアボード（カード）
   =============================== */
.card{{
  height:70vh;
  background:linear-gradient(180deg,#232736,#171a25);
  border:3px solid #2b3142;
  border-radius:20px;
  text-align:center;
  overflow:hidden;
  box-shadow:0 10px 24px rgba(0,0,0,.45);

  /* 4 行構造 */
  display:grid;
  grid-template-rows:
    auto        /* Player 名 */
    auto        /* ハンデ */
    1fr         /* スコア */
    100px;       /* TURN */
}}

/* 手番・勝利枠 */
.card.turn{{
  border-color:#f7c948;
}}

.card.win{{
  border-color:#f7c948;
  animation: win-pulse 1.8s infinite;
}}

@keyframes win-pulse{{
  0%   {{ box-shadow:0 0 18px rgba(247,201,72,.4);}}
  50% {{ box-shadow:0 0 55px rgba(247,201,72,1);}}
  100%{{ box-shadow:0 0 18px rgba(247,201,72,.4);}}
}}

/* ===============================
   上段：Player 名
   =============================== */
.card .name{{
  grid-row: 1;
  margin-top: 0px;
  justify-self: center;
  font-size: clamp(30px, 3.6vw, 64px);
  font-weight: 900;
  color: #ffffff;
}}

.card.players-2 .name{{
  font-size: clamp(46px, 5.8vw, 96px);
}}

/* ===============================
   ハンデ
   =============================== */
.card .target{{
  grid-row: 2;
  margin-top: 0px;
  justify-self: center;
  font-size: clamp(22px,2.6vw,44px);
  color: #cccccc;
}}

/* ===============================
   中央：スコア
   =============================== */
.card .score{{
  grid-row: 3;
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight:900;
  color:#ffffff;
  line-height:1;
  margin-top: 0;
}}

/* 人数別スコアサイズ */
.card.players-2 .score{{
  font-size: clamp(180px, 28vw, 38vh);
}}

.card.players-many .score{{
  font-size: clamp(160px,22vw,32vh);
}}

/* ===============================
   下段：画像表示用（YOUR TURN / WAITING）
   =============================== */
.card .turnlabel {{
    grid-row: 4;
    align-self:center;
    justify-self:center;
    margin-bottom: 16px;
    
    /* 画像の表示領域を設定 */
    width: 280px;
    height: 80px;
    
    /* 変数から画像データを読み込み（ここだけ単一の波括弧） */
    background-image: url('{IMG_NOTURN_B64}'); 
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    
    /* 元のテキスト（YOUR TURN等）を隠す */
    text-indent: -9999px;
    overflow: hidden;
    white-space: nowrap;
    
    position: relative;
    z-index: 2;
}}

.card.turn .turnlabel {{
    /* 手番時の画像に差し替え（ここだけ単一の波括弧） */
    background-image: url('{IMG_TURN_B64}');
    background-color: transparent;
}}

/* ===============================
   WIN バナー（サイズ調整版）
   =============================== */
.win-banner{{
  width: 100vw;               /* 画面の横幅いっぱい（View Width） */
  max-width: 100vw;           /* 制限なし */
  height: 64px;               /* 縦幅はスリムに固定 */
  
  /* 画面中央に強制配置（左右の余白を無視） */
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
  margin-bottom: 20px;
  
  display: flex;
  align-items: center;
  justify-content: center;    /* 中央寄せ */
  gap: 80px;                  /* WINと名前の間隔をさらに広く */
  
  /* 背景：中央が濃く、端に向かって少し透過するグラデーション */
  background: linear-gradient(
    90deg, 
    rgba(23,26,37,0.4) 0%, 
    rgba(247,201,72,0.2) 15%, 
    rgba(247,201,72,0.2) 85%, 
    rgba(23,26,37,0.4) 100%
  ), #171a25;
  
  /* 上下のゴールドラインを画面端まで貫通させる */
  border-top: 3px solid rgba(247,201,72,0.8);
  border-bottom: 3px solid rgba(247,201,72,0.8);
  border-left: none;
  border-right: none;
  
  color: #ffffff;
  box-shadow: 0 15px 50px rgba(0,0,0,0.7);
  z-index: 99;                /* 最前面に */
}}

.win-banner h1{{
  margin: 0;
  font-size: 42px;            /* 少し大きくして視認性アップ */
  font-weight: 900;
  color: #f7c948;
  letter-spacing: .4em;       /* ワイド画面に合わせて文字間隔を最大化 */
  white-space: nowrap;
  text-shadow: 0 0 20px rgba(247,201,72,0.6);
}}

.win-banner p{{
  margin: 0;
  font-size: 32px;            /* プレイヤー名 */
  font-weight: 800;
  color: #ffffff;
  white-space: nowrap;
  letter-spacing: .1em;
}}

/* WIN表示エリアのボタンを特定してスタイル適用 */
[data-testid="stVerticalBlock"] .stButton button {{
    /* WINバナーが表示されている時のみ、
       通常の操作ボタン(op_plus等)以外のボタンも大きくする設定 
    */
    font-size: 24px !important; 
    font-weight: 800 !important;
    height: 64px !important;
    border-radius: 12px !important;
}}

/* 「閉じる」ボタン（標準色またはグレー系） */
div:has(> button[kind="secondary"]) button {{
    background-color: #4e5569 !important;
    color: white !important;
}}

/* 「試合リセット」ボタン（赤・警告色で目立たせる場合） */
/* ※Streamlitのボタンテキストで判定 */
div:has(> button) p:contains("試合リセット") {{
    font-size: 24px !important;
}}

/* ===============================
   操作ボタン（Surface サイズ限定）
   =============================== */
.st-key-op_plus  div.stButton > button,
.st-key-op_minus div.stButton > button,
.st-key-op_prev  div.stButton > button,
.st-key-op_next  div.stButton > button,
.st-key-op_undo  div.stButton > button,
.st-key-op_reset div.stButton > button{{
  width:100%;
  min-height:80px;
  padding:1.2rem 1.4rem;
  font-size:clamp(26px,3vw,36px);
  font-weight:800;
  border-radius:16px;
  background: linear-gradient(180deg,#3f5ea8,#2a3f74);
  color:#ffffff;
  box-shadow:
    0 3px 0 rgba(0,0,0,.45),
    0 8px 20px rgba(0,0,0,.45);
  transition:
    transform .06s ease,
    box-shadow .12s ease;
}}

.st-key-op_plus  div.stButton > button:hover,
.st-key-op_minus div.stButton > button:hover,
.st-key-op_prev  div.stButton > button:hover,
.st-key-op_next  div.stButton > button:hover,
.st-key-op_undo  div.stButton > button:hover,
.st-key-op_reset div.stButton > button:hover{{
  background: linear-gradient(180deg,#324472,#223155);
}}

.st-key-op_plus  button:active,
.st-key-op_minus button:active,
.st-key-op_prev  button:active,
.st-key-op_next  button:active,
.st-key-op_undo  button:active,
.st-key-op_reset button:active{{
  transform: translateY(2px);
  box-shadow:
    0 1px 0 rgba(0,0,0,.55),
    0 4px 10px rgba(0,0,0,.45);
  background: linear-gradient(180deg,#25345c,#182448);
}}

/* 操作ボタン文字（Streamlit DOM 対応） */
.st-key-op_plus  p,
.st-key-op_minus p,
.st-key-op_prev  p,
.st-key-op_next  p,
.st-key-op_undo  p,
.st-key-op_reset p{{
  font-size:32px !important;
  font-weight:900 !important;
  margin:0 !important;
  line-height:1 !important;
  white-space:nowrap !important;
}}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Logic（安定コールバック）
# ---------------------------------------------------------
def add_player():
    if len(state.players) >= 4:
        return
    state.snapshot()
    state.players.append(Player(f"Player {len(state.players)+1}"))
    state.turn = min(state.turn, len(state.players) - 1)

def remove_player():
    if len(state.players) <= 1:
        return
    state.snapshot()
    state.players.pop()
    state.turn = min(state.turn, len(state.players) - 1)

def op_plus():
    if state.finished:
        return
    state.snapshot()
    p = state.current_player()
    p.wins += 1
    if p.wins >= p.target:
        state.finished = True
        state.winner = p.name
        st.session_state.show_win = True
        st.session_state.win_winner = p.name


def op_minus():
    if state.finished:
        return
    state.snapshot()
    p = state.current_player()
    p.wins = max(0, p.wins - 1)


def op_prev():
    state.snapshot()
    state.prev_turn()


def op_next():
    state.snapshot()
    state.next_turn()


def undo():
    state.undo()
    st.session_state.show_win = state.finished
    st.session_state.win_winner = state.winner


def reset_match():
    for p in state.players:
        p.wins = 0
    state.turn = 0
    state.finished = False
    state.winner = ""
    state.history.clear()   # ✅ 履歴を触るのはここだけOK
    st.session_state.show_win = False
    st.session_state.win_winner = ""

# ---------------------------------------------------------
# Title
# ---------------------------------------------------------
# 9番ボールの色（イエロー）
BALL_9_COLOR = "#F5C400" 

st.markdown(
    f"""
    <style>
    /* 1. アプリ最上部の余白（微調整） */
    .stApp {{
        margin-top: 10px !important;
    }}
    
    /* 2. ヘッダー全体のコンテナ */
    .header-safe-wrapper {{
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center; 
        gap: 12px; /* ボールとテキストの距離をわずかに広げてスッキリと */
        padding: 20px 0 !important; 
        margin-top: -10px !important;
        background: transparent;
    }}

    /* 3. 9番ボール（ストライプデザインに修正） */
    .ball-9-mini-striped {{
        /* サイズは前回のコンパクトな設定を維持 */
        width: clamp(24px, 2.8vw, 34px);
        height: clamp(24px, 2.8vw, 34px);
        aspect-ratio: 1/1;
        border-radius: 50%;
        flex-shrink: 0;
        
        /* ストライプのデザインを適用 */
        background: 
            radial-gradient(circle at 50% 50%, #fff 0 35%, transparent 38%), /* 中央の白い円 */
            linear-gradient(#fff 0 18%, {BALL_9_COLOR} 18% 82%, #fff 82%); /* イエローとホワイトの縞模様 */
        
        border: 1.2px solid rgba(255,255,255,0.4);
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        
        display: flex;
        justify-content: center;
        align-items: center;
        
        /* 数字の「9」のデザイン */
        color: #111;
        font-weight: 950;
        /* 数字が見やすいよう、 clampの下限を少し上げました（7px -> 8px） */
        font-size: clamp(8px, 0.9vw, 11px); 
        font-family: 'Arial Black', sans-serif;
        line-height: 1;
    }}

    /* 4. タイトルテキスト */
    .title-text-mini-ver {{
        font-weight: 950;
        letter-spacing: 0.6px;
        color: #fff;
        margin: 0 !important;
        font-size: clamp(24px, 2.6vw, 36px);
        line-height: 1.0;
        display: flex;
        align-items: center;
    }}

    /* ヘッダー干渉対策 */
    /*
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0) !important;
        height: 0px !important;
    }}
    */
    </style>

    <div class="header-safe-wrapper">
        <div class="ball-9-mini-striped">9</div>
        <div class="title-text-mini-ver">9Ball Scoreboard — Surface</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Settings Toggle
# ---------------------------------------------------------
with st.expander("⚙ 設定 (人数・名前・ハンデ)", expanded=st.session_state.show_settings):
    # --- プレイヤー人数（即時反映・on_click） ---
    spL, c0, c1, spM1, c2, spM2, c3, spR = st.columns([0.2, 4, 1, 1, 1, 1, 1, 10])
    
    with c0:
        st.markdown("#### プレイヤー人数")
    with c1:
        st.button("ー", on_click=remove_player, use_container_width=True, key="p_minus_btn")
    with c2:
        st.markdown(f'<div style="height:56px; display:flex; align-items:baseline; justify-content:center; gap:6px;"><span style="font-size:32px; font-weight:600;">{len(state.players)}</span><span style="font-size:20px;">人</span></div>', unsafe_allow_html=True)
    with c3:
        st.button("＋", on_click=add_player, use_container_width=True, key="p_plus_btn")

    # --- 名前・ハンデ（form） ---
    with st.form("settings_form", clear_on_submit=False):
        colL, colR = st.columns(2)
        for i, p in enumerate(state.players):
            with colL:
                st.text_input(f"プレイヤー {i+1}", value=p.name, key=f"name_{i}")
            with colR:
                st.number_input("ハンデ", min_value=1, max_value=20, value=p.target, key=f"target_{i}")
        
        # 「設定を適用」ボタン
        if st.form_submit_button("設定を適用", use_container_width=True):
            for i, p in enumerate(state.players):
                p.name   = st.session_state[f"name_{i}"]
                p.target = st.session_state[f"target_{i}"]
            st.session_state.show_settings = False # 適用後に閉じる
            st.rerun()

# ---------------------------------------------------------
# WIN
# ---------------------------------------------------------
if st.session_state.show_win:
    st.markdown(
        f"<div class='win-banner'><h1>🏆 WIN</h1><p>{html.escape(st.session_state.win_winner)}</p></div>",
        unsafe_allow_html=True
    )
    c1,c2 = st.columns(2)
    with c1:
        if st.button("閉じる", use_container_width=True):
            st.session_state.show_win = False
            st.rerun()
    with c2:
        if st.button("試合リセット", use_container_width=True, on_click=reset_match):
            st.rerun()

# ---------------------------------------------------------
# プレイヤー人数クラス（CSS制御用）
# ---------------------------------------------------------
player_count = len(state.players)

if player_count == 2:
    st.markdown("<div class='players-2'>", unsafe_allow_html=True)
else:
    st.markdown("<div class='players-many'>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Scoreboard
# ---------------------------------------------------------
player_count = len(state.players)
size_class = "players-2" if player_count == 2 else "players-many"

cols = st.columns(player_count)
for i, col in enumerate(cols):
    p = state.players[i]
    is_turn = i == state.turn
    is_win = state.finished and p.name == state.winner
    with col:
        st.markdown(
            f"""
            <div class="card {size_class} {'turn' if is_turn else ''} {'win' if is_win else ''}">
              <div class="name">{html.escape(p.name)}</div>
              <div class="target">ハンデ：{p.target}</div>
              <div class="score">{p.wins}</div>
              <div class="turnlabel">{'YOUR TURN' if is_turn else 'WAITING'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div class='ops-spacer'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Operation Buttons（6個・on_click）
# ---------------------------------------------------------
cols_ops = st.columns(6)

cols_ops[0].button("手番（+1）",   key="op_plus",  use_container_width=True, on_click=op_plus)
cols_ops[1].button("手番（−1）",   key="op_minus", use_container_width=True, on_click=op_minus)
cols_ops[2].button("前ターン",   key="op_prev",  use_container_width=True, on_click=op_prev)
cols_ops[3].button("次ターン",   key="op_next",  use_container_width=True, on_click=op_next)
cols_ops[4].button("アンドゥ", key="op_undo",  use_container_width=True, on_click=undo)
cols_ops[5].button("リセット",key="op_reset", use_container_width=True, on_click=reset_match)

