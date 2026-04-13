# -----------------------------------------------------------------------------
# ローテーション（1〜15）スコアボード Web アプリ（Streamlit）
#
# ・縦向き（Portrait）：
#     1行目：ターン交代 / ファウル / スクラッチ（横3）
#     2行目：アンドゥ / ラックﾘｾｯﾄ / 試合ﾘｾｯﾄ（横2）
# ・横向き（Landscape）：5つ横並び
#   → .st-key-btn_* を含む行にCSS適用 + 行マーカー（併用で堅牢）
#
# ・スコアカードは常に横2固定（:has + 行マーカー 併用）
# ・縦向きの操作ボタン縦余白を圧縮（行間/上下マージン/ボタン内パディング）
# ・スコア直下～操作ボタン、操作ボタン～ボール見出しの余白も圧縮
# ・ボールは 5×3 固定、右余白あり、9〜15 は中央対称の超太ストライプ（18–82%）
# -----------------------------------------------------------------------------

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List

import streamlit as st
import html

# =========================
# 0) ページ設定
# =========================
st.set_page_config(
    page_title="ローテーション スコアボード",
    page_icon="🎱",
    layout="wide",
)

# =========================
# CSS（※ 必ず <style> タグはエスケープ無し）
# =========================
STYLES = """
<style>
:root{
  --bg:#0f1117; --panel:#1b1e27; --text:#e8eaed; --accent:#f7c948;
}
.block-container{padding-top:1rem; padding-bottom:2rem;}
/* iOS Safari 既定外観オフ（角丸・幅指定を通す） */
.stButton>button{-webkit-appearance:none}

/* ===== タイトル ===== */
.h-title{
  font-weight:900; letter-spacing:.6px; text-align:center;
  margin:.2rem 0 1rem; color:#fff;
  margin-top: .6rem !important;   /* 既定: .2rem → 少し下げる */
  font-size: clamp(1.2rem, 2.3vw, 1.75rem) !important;
  /* 最小=1.4rem（約22.px）、通常=2.3vw、最大=1.75rem（約28px） */
}

/* ===== スコアカード ===== */
.score-card{
  background:linear-gradient(180deg,#232736,#171a25);
  border:1px solid #2b3142; border-radius:12px; padding:5px 12px;
  box-shadow:0 4px 12px rgba(0,0,0,.25);
}
.score-name{
  font-weight:900; font-size:14px; color:#fff;
  padding:4px 10px; border-radius:8px; display:inline-block;
}
.score-val{
  font-size:52px; font-weight:900; color:#fff; line-height:1; margin:.25rem 0 .2rem;
  text-shadow:0 2px 0 rgba(0,0,0,.35);
}
.turn-badge{
  display:inline-block; margin-top:4px; padding:4px 10px; border-radius:999px;
  background:var(--accent); color:#111; font-weight:800; letter-spacing:.4px;
}

/* ★ WINバナー (Surface版の豪華演出を移植) ★ */
.win-banner {
    width: 100%;
    background: linear-gradient(90deg, rgba(23,26,37,0.4) 0%, rgba(247,201,72,0.2) 15%, rgba(247,201,72,0.2) 85%, rgba(23,26,37,0.4) 100%), #171a25;
    border-top: 3px solid #f7c948;
    border-bottom: 3px solid #f7c948;
    padding: 12px 0;
    margin: 10px 0 20px 0;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
.win-title { color: #f7c948; font-weight: 900; font-size: 32px; letter-spacing: 6px; margin: 0; text-shadow: 0 0 15px rgba(247,201,72,0.5); }
.win-player { color: #ffffff; font-weight: 800; font-size: 24px; margin: 5px 0 0 0; }

/* 勝利したカードの強調 */
.score-card.winner-card {
    border-color: #f7c948 !important;
    animation: win-pulse 1.8s infinite;
}
@keyframes win-pulse {
    0% { box-shadow: 0 0 5px rgba(247,201,72,0.3); transform: scale(1); }
    50% { box-shadow: 0 0 25px rgba(247,201,72,0.6); transform: scale(1.02); }
    100% { box-shadow: 0 0 5px rgba(247,201,72,0.3); transform: scale(1); }
}

/* WIN画面専用ボタンのスタイル調整 */
div:has(> button[key="win_close"]) button { background-color: #4e5569 !important; color: white !important; font-size: 18px !important; height: 50px !important; }
div:has(> button[key="win_reset"]) button { background-color: #f7c948 !important; color: #111 !important; font-size: 18px !important; font-weight: 800 !important; height: 50px !important; }


/* 区切り線：上下マージンを控えめに（スコア下を詰める） */
hr.sep{border:none; height:1px; background:#2b3142; margin:.25rem 0 !important;}

/* ===== 操作ボタン：折り返し禁止（基本） ===== */
[class*="st-key-btn"] button{
  white-space: nowrap !important;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 内部の span / div も強制 */
[class*="st-key-btn"] button *{
  white-space: nowrap !important;
}

/* ===== 縦向き：全体の文字を少し縮小 ===== */
@media (orientation: portrait){
  [class*="st-key-btn"] button{
    font-size: clamp(0.72rem, 2.6vw, 0.9rem);
  }
}

/* ===== 長い日本語ラベル専用（最終調整） ===== */
.st-key-btn_reset button{
  font-size: clamp(0.56rem, 2.2vw, 0.74rem) !important;
  padding-left: 0.4rem !important;
  padding-right: 0.4rem !important;
}

.st-key-btn_match_reset button{
  font-size: clamp(0.62rem, 2.4vw, 0.78rem) !important;
}

.st-key-btn_match_reset button{
  background-color: #c62828;
}


/* ====== 空のMarkdownラッパの余白ゼロ化（余白源の解消） ====== */
[data-testid="stElementContainer"]:has(.ctrl-scope){
  margin:0 !important; padding:0 !important; line-height:0 !important;
}

/* ==========================================================
   スコア行：常に横2固定（:has + 行マーカー の両対応）
   ========================================================== */

/* :has でスコア行を横2固定 */
[data-testid="stHorizontalBlock"]:has(.score-card){
  display:flex !important; flex-wrap:nowrap !important;
  gap:.75rem !important; justify-content:flex-start !important;
  margin-top: -1.5rem !important;
}
[data-testid="stHorizontalBlock"]:has(.score-card) > [data-testid="stColumn"]{
  flex:0 0 50% !important; max-width:50% !important; min-width:0 !important;
}

/* 行マーカー（score-row-marker）直後の行も横2固定（:has 非対応端末の保険） */
.score-row-marker + [data-testid="stHorizontalBlock"]{
  display:flex !important; flex-wrap:nowrap !important;
  gap:.75rem !important; justify-content:flex-start !important;
}
.score-row-marker + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
  flex:0 0 50% !important; max-width:50% !important; min-width:0 !important;
}

/* ==========================================================
   操作ボタン行（.st-key-btn_* を含む行）：横向き=5横／縦向き=3+2
   + 行マーカー（controls-row-marker）対応も併用
   ========================================================== */

/* 共通：該当行は横並び行（横向き相当） */
[data-testid="stHorizontalBlock"]:has(.st-key-btn_turn, .st-key-btn_foul, .st-key-btn_scratch, .st-key-btn_undo, .st-key-btn_reset),
.controls-row-marker + [data-testid="stHorizontalBlock"],
.controls-row-marker ~ [data-testid="stHorizontalBlock"]{
  display:flex !important; flex-wrap:nowrap !important;
  gap:.6rem !important; justify-content:flex-start !important;
  margin-top: 0rem !important; margin-bottom: 0rem !important;
}
/* 共通：5等分 */
[data-testid="stHorizontalBlock"]:has(.st-key-btn_turn, .st-key-btn_foul, .st-key-btn_scratch, .st-key-btn_undo, .st-key-btn_reset) > [data-testid="stColumn"],
.controls-row-marker + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.controls-row-marker ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
  flex:0 0 20% !important; max-width:20% !important; min-width:0 !important;
}

/* 縦向き時：3 + 改行 + 2、かつ縦余白を強めに圧縮 */
@media (orientation: portrait){
  [data-testid="stHorizontalBlock"]:has(.st-key-btn_turn, .st-key-btn_foul, .st-key-btn_scratch, .st-key-btn_undo, .st-key-btn_reset),
  .controls-row-marker + [data-testid="stHorizontalBlock"],
  .controls-row-marker ~ [data-testid="stHorizontalBlock"]{
    flex-wrap:wrap !important;
    gap:.35rem !important; row-gap: 0rem !important;
    margin-top: -2rem !important; margin-bottom: 0rem !important;
  }
  /* 上3（1/3幅） */
  [data-testid="stHorizontalBlock"]:has(.st-key-btn_turn, .st-key-btn_foul, .st-key-btn_scratch, .st-key-btn_undo, .st-key-btn_reset) > [data-testid="stColumn"]:nth-child(-n+3),
  .controls-row-marker + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(-n+3),
  .controls-row-marker ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(-n+3){
    flex:0 0 calc((100% - 2*.35rem)/3) !important;
    max-width:calc((100% - 2*.35rem)/3) !important;
  }
  /* 下2（1/2幅） */
  [data-testid="stHorizontalBlock"]:has(.st-key-btn_turn, .st-key-btn_foul, .st-key-btn_scratch, .st-key-btn_undo, .st-key-btn_reset) > [data-testid="stColumn"]:nth-child(n+4),
  .controls-row-marker + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(n+4),
  .controls-row-marker ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(n+4){
    flex:0 0 calc((100% - .35rem)/2) !important;
    max-width:calc((100% - .35rem)/2) !important;
  }

  /* 列内の空ラッパ余白ゼロ（縦詰め） */
  [data-testid="stHorizontalBlock"]:has(.st-key-btn_turn, .st-key-btn_foul, .st-key-btn_scratch, .st-key-btn_undo, .st-key-btn_reset) [data-testid="stElementContainer"],
  .controls-row-marker + [data-testid="stHorizontalBlock"] [data-testid="stElementContainer"],
  .controls-row-marker ~ [data-testid="stHorizontalBlock"] [data-testid="stElementContainer"]{
    margin:0 !important; padding:0 !important; line-height:0 !important;
  }

  /* ボタン自体の高さを詰める */
  .ctrl-scope .stButton > button{
    padding:.5rem .75rem !important;   /* 既定 0.75rem → 0.5rem */
    line-height:1.0 !important;
  }

  /* スコア下の区切り線・見出しの余白もさらに圧縮 */
  hr.sep{ margin:.25rem 0 !important; }
  .section-title{ margin:.3rem 0 .2rem !important; }
  /* ボタン行直後に来る見出しの上余白を抑制 */
  [data-testid="stHorizontalBlock"]:has(.st-key-btn_turn, .st-key-btn_foul, .st-key-btn_scratch, .st-key-btn_undo, .st-key-btn_reset) + * .section-title,
  .controls-row-marker + [data-testid="stHorizontalBlock"] + * .section-title{
    margin-top:.1rem !important;
  }
}

/* ===== ボール行（5×3 固定・右余白） ===== */
/* 横向き：19%×5=95% → 右端に余白 */
[data-testid="stHorizontalBlock"]:has(.st-key-ball_1, .st-key-ball_2, .st-key-ball_3, .st-key-ball_4, .st-key-ball_5) > [data-testid="stColumn"],
[data-testid="stHorizontalBlock"]:has(.st-key-ball_6, .st-key-ball_7, .st-key-ball_8, .st-key-ball_9, .st-key-ball_10) > [data-testid="stColumn"],
[data-testid="stHorizontalBlock"]:has(.st-key-ball_11, .st-key-ball_12, .st-key-ball_13, .st-key-ball_14, .st-key-ball_15) > [data-testid="stColumn"]{
  flex:0 0 19% !important; max-width:19% !important; min-width:0 !important;
}
[data-testid="stHorizontalBlock"]:has(.st-key-ball_1, .st-key-ball_2, .st-key-ball_3, .st-key-ball_4, .st-key-ball_5),
[data-testid="stHorizontalBlock"]:has(.st-key-ball_6, .st-key-ball_7, .st-key-ball_8, .st-key-ball_9, .st-key-ball_10),
[data-testid="stHorizontalBlock"]:has(.st-key-ball_11, .st-key-ball_12, .st-key-ball_13, .st-key-ball_14, .st-key-ball_15){
  display:flex !important; gap:.4rem !important; justify-content:flex-start !important;
}

/* 縦向き：左右パディング + 列幅を自動再計算 */
@media (orientation: portrait){
  :root{ --balls-pad-inline:.5rem; --balls-gap:.35rem; }
  [data-testid="stHorizontalBlock"]:has(.st-key-ball_1, .st-key-ball_2, .st-key-ball_3, .st-key-ball_4, .st-key-ball_5),
  [data-testid="stHorizontalBlock"]:has(.st-key-ball_6, .st-key-ball_7, .st-key-ball_8, .st-key-ball_9, .st-key-ball_10),
  [data-testid="stHorizontalBlock"]:has(.st-key-ball_11, .st-key-ball_12, .st-key-ball_13, .st-key-ball_14, .st-key-ball_15){
    padding-left:var(--balls-pad-inline); padding-right:var(--balls-pad-inline);
    gap:var(--balls-gap) !important; margin-bottom:.1rem !important;
  }
  [data-testid="stHorizontalBlock"]:has(.st-key-ball_1, .st-key-ball_2, .st-key-ball_3, .st-key-ball_4, .st-key-ball_5) > [data-testid="stColumn"],
  [data-testid="stHorizontalBlock"]:has(.st-key-ball_6, .st-key-ball_7, .st-key-ball_8, .st-key-ball_9, .st-key-ball_10) > [data-testid="stColumn"],
  [data-testid="stHorizontalBlock"]:has(.st-key-ball_11, .st-key-ball_12, .st-key-ball_13, .st-key-ball_14, .st-key-ball_15) > [data-testid="stColumn"]{
    flex-basis: calc((100% - (var(--balls-pad-inline)*2) - (4*var(--balls-gap)))/5) !important;
    max-width:  calc((100% - (var(--balls-pad-inline)*2) - (4*var(--balls-gap)))/5) !important;
  }

  /* 縦向きは丸の枠・文字を少し控えめに */
  [class*="st-key-ball_"] .stButton>button{ border-width:1px; font-size:clamp(14px, 2.4vw, 18px); }
}

/* ===== ボール（丸・色） ===== */
[class*="st-key-ball_"] .stButton>button{
  width:100%; aspect-ratio:1/1; height:auto; padding:0; box-sizing:border-box;
  border-radius:50%; display:block; color:#111;
  border:2px solid rgba(255,255,255,.25);
  box-shadow: inset 0 8px 12px rgba(255,255,255,.18), 0 4px 12px rgba(0,0,0,.35);
}
/* 単色（1〜8） */
.st-key-ball_1  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #F5C400; }
.st-key-ball_2  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #2A61FF; }
.st-key-ball_3  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #D93636; }
.st-key-ball_4  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #7B2FFF; }
.st-key-ball_5  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #FF7F23; }
.st-key-ball_6  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #118C4F; }
.st-key-ball_7  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #8B4513; }
.st-key-ball_8  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #000000; }
/* ストライプ（9〜15）：白ベース + 色帯（中央対称・超太め 18〜82%） */
.st-key-ball_9  .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #F5C400 18% 82%, #fff 82%), #fff; }
.st-key-ball_10 .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #2A61FF 18% 82%, #fff 82%), #fff; }
.st-key-ball_11 .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #D93636 18% 82%, #fff 82%), #fff; }
.st-key-ball_12 .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #7B2FFF 18% 82%, #fff 82%), #fff; }
.st-key-ball_13 .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #FF7F23 18% 82%, #fff 82%), #fff; }
.st-key-ball_14 .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #118C4F 18% 82%, #fff 82%), #fff; }
.st-key-ball_15 .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #8B4513 18% 82%, #fff 82%), #fff; }

/* ===== ボール：ポケット後（disabled）表示 ===== */
[class*="st-key-ball_"] .stButton > button:disabled{
  filter: grayscale(100%);
  opacity: 0.35;
  box-shadow: none;
  cursor: not-allowed;
}

/* iOS Safari 対策（opacity が効かない場合の保険） */
[class*="st-key-ball_"] .stButton > button:disabled{
  background-blend-mode: luminosity;
}

</style>
"""
st.markdown(STYLES, unsafe_allow_html=True)

# =========================
# 1) データモデル
# =========================
@dataclass
class Settings:
    target_points: int = 61
    foul_penalty: int = -1
    scratch_penalty: int = -1
    allow_negative: bool = True

@dataclass
class PlayerState:
    name: str
    score: int = 0

@dataclass
class MatchState:
    players: List[PlayerState] = field(
        default_factory=lambda: [PlayerState("Player 1"), PlayerState("Player 2")]
    )
    current_player_index: int = 0
    pocketed: Dict[int, bool] = field(default_factory=lambda: {i: False for i in range(1, 16)})
    history: List[Dict[str, Any]] = field(default_factory=list)
    finished: bool = False

# =========================
# 2) セッション初期化
# =========================
if "settings" not in st.session_state:
    st.session_state.settings = Settings()
if "rotation_state" not in st.session_state:
    st.session_state.rotation_state = MatchState()
if "log" not in st.session_state:
    st.session_state.log: List[str] = []

settings: Settings = st.session_state.settings
state: MatchState = st.session_state.rotation_state

# =========================
# 3) ユーティリティ
# =========================
def current_player() -> PlayerState:
    return state.players[state.current_player_index]

def push_history(action: Dict[str, Any]):
    state.history.append(action)

def add_log(text: str):
    st.session_state.log.append(text)

def clamp_score(value: int) -> int:
    return value if settings.allow_negative else max(0, value)

def check_win():
    if state.finished:
        return
    target = settings.target_points
    for p in state.players:
        if p.score >= target:
            state.finished = True
            add_log(f"🏆 {p.name} が勝利（{p.score} 点）")
            st.success(f"{p.name} が {target} 点に到達しました！")
            break

def snapshot() -> Dict[str, Any]:
    return {
        "players": [{"name": p.name, "score": p.score} for p in state.players],
        "current_player_index": state.current_player_index,
        "pocketed": dict(state.pocketed),
        "finished": state.finished,
        "log": list(st.session_state.log),
    }

def push_snapshot():
    state.history.append({
        "type": "snapshot",
        "state": snapshot()
    })

# =========================
# 4) アクション
# =========================
def apply_settings(new_target: int, new_foul: int, new_scratch: int, new_allow_negative: bool):
    settings.target_points = int(new_target)
    settings.foul_penalty = int(new_foul)
    settings.scratch_penalty = int(new_scratch)
    settings.allow_negative = bool(new_allow_negative)
    add_log("設定を適用しました")

def pocket_ball(value: int):
    if state.finished or state.pocketed.get(value, False):
        return

    push_snapshot()

    player = current_player()
    before = player.score
    player.score = clamp_score(player.score + value)
    state.pocketed[value] = True

    add_log(f"{player.name} が {value} 番をポケット（+{value}） → {player.score} 点")
    check_win()

    st.session_state.state = state
    st.rerun()

def end_turn():
    if state.finished:
        return

    push_snapshot()

    prev = state.current_player_index
    state.current_player_index = 1 - prev

    add_log("ターン交代")

    st.session_state.state = state
    st.rerun()

def apply_penalty(kind: str):
    if state.finished:
        return

    push_snapshot()

    penalty = settings.foul_penalty if kind == "foul" else settings.scratch_penalty
    player = current_player()
    before = player.score
    player.score = clamp_score(player.score + penalty)

    label = "ファウル" if kind == "foul" else "スクラッチ"
    add_log(f"{player.name}：{label}（{penalty}） → {player.score} 点")

    st.session_state.state = state
    st.rerun()

def reset_rack():
    push_snapshot()

    state.pocketed = {i: False for i in range(1, 16)}
    add_log("ラックをリセット")

    st.session_state.state = state
    st.rerun()

def reset_match():
    """既存オブジェクトを破壊的に更新（global を使わない）"""
    p1 = (state.players[0].name or "Player 1").strip() or "Player 1"
    p2 = (state.players[1].name or "Player 2").strip() or "Player 2"
    state.players = [PlayerState(p1), PlayerState(p2)]
    state.current_player_index = 0
    state.pocketed = {i: False for i in range(1, 16)}
    state.history = []
    state.finished = False
    st.session_state.log = []
    add_log("=== 試合リセット ===")

    st.session_state.state = state
    st.rerun()

def undo_last():
    if not state.history:
        return

    snap = state.history.pop()["state"]

    for i, p in enumerate(snap["players"]):
        state.players[i].score = p["score"]

    state.current_player_index = snap["current_player_index"]
    state.pocketed = snap["pocketed"]
    state.finished = snap["finished"]
    st.session_state.log = snap.get("log", [])

    add_log("アンドゥ：直前の状態に戻しました")

    st.session_state.state = state
    st.rerun()

# =========================
# 5) JSON 保存 / 読み込み
# =========================
def to_dict() -> Dict[str, Any]:
    return {
        "settings": {
            "target_points": settings.target_points,
            "foul_penalty": settings.foul_penalty,
            "scratch_penalty": settings.scratch_penalty,
            "allow_negative": settings.allow_negative,
        },
        "state": {
            "players": [{"name": p.name, "score": p.score} for p in state.players],
            "current_player_index": state.current_player_index,
            "pocketed": state.pocketed,
            "finished": state.finished,
        },
    }

def load_from_dict(data: Dict[str, Any]):
    s = data.get("settings", {})

    st.session_state.settings = Settings(
        target_points=int(s.get("target_points", 61)),
        foul_penalty=int(s.get("foul_penalty", -1)),
        scratch_penalty=int(s.get("scratch_penalty", -1)),
        allow_negative=bool(s.get("allow_negative", True)),
    )

    players = [
        PlayerState(p.get("name", f"Player {i+1}"), int(p.get("score", 0)))
        for i, p in enumerate(
            data.get("state", {}).get("players", [
                {"name": "Player 1", "score": 0},
                {"name": "Player 2", "score": 0},
            ])
        )
    ]

    st.session_state.state = MatchState(
        players=players,
        current_player_index=int(
            data.get("state", {}).get("current_player_index", 0)
        ),
        pocketed={int(k): bool(v) for k, v in data.get("state", {}).get(
            "pocketed", {i: False for i in range(1, 16)}
        ).items()},
        history=[],
        finished=bool(data.get("state", {}).get("finished", False)),
    )

    add_log("JSON から試合を読み込み")

# =========================
# タイトル表示（15番ボールアイコン付き）
# =========================
BALL_15_COLOR = "#8B4513"  # マルーン/ブラウン系

st.markdown(
    f"""
    <style>
    /* ヘッダー全体のコンテナ */
    .header-safe-wrapper {{
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center; 
        gap: 12px;
        margin-top: 20px;
        padding: 10px 0 20px 0 !important; 
        background: transparent;
    }}

    /* 15番ボール（ミニアイコン） */
    .ball-15-mini {{
        width: clamp(24px, 2.8vw, 34px);
        height: clamp(24px, 2.8vw, 34px);
        aspect-ratio: 1/1;
        border-radius: 50%;
        flex-shrink: 0;
        
        /* ストライプのデザイン */
        background: 
            radial-gradient(circle at 50% 50%, #fff 0 35%, transparent 38%),
            linear-gradient(#fff 0 18%, {BALL_15_COLOR} 18% 82%, #fff 82%);
        
        border: 1.2px solid rgba(255,255,255,0.4);
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        
        display: flex;
        justify-content: center;
        align-items: center;
        
        color: #111;
        font-weight: 950;
        font-size: clamp(8px, 1.0vw, 11px);
        font-family: 'Arial Black', sans-serif;
        line-height: 1;
    }}

    /* タイトルテキスト */
    .title-text-mini-ver {{
        font-weight: 950;
        letter-spacing: 0.6px;
        color: #fff;
        margin: 0 !important;
        font-size: clamp(20px, 2.6vw, 32px);
        line-height: 1.0;
    }}
    </style>

    <div class="header-safe-wrapper">
        <div class="ball-15-mini">15</div>
        <div class="title-text-mini-ver">Rotation Scoreboard</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# 6) UI
# =========================
# --- 設定（プレイヤー名はここ：横2） ---
with st.expander("設定", expanded=False):
    n1, n2 = st.columns(2)
    with n1:
        name1 = st.text_input("プレイヤー1", value=state.players[0].name, key="player1_name")
    with n2:
        name2 = st.text_input("プレイヤー2", value=state.players[1].name, key="player2_name")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        target_points = st.number_input("勝利点", min_value=1, max_value=200, value=int(settings.target_points), step=1)
    with c2:
        foul_penalty = st.number_input("ファウル減点", min_value=-10, max_value=0, value=int(settings.foul_penalty), step=1)
    with c3:
        scratch_penalty = st.number_input("スクラッチ減点", min_value=-10, max_value=0, value=int(settings.scratch_penalty), step=1)
    with c4:
        allow_negative = st.checkbox("マイナススコアを許可", value=bool(settings.allow_negative))

    if st.button("設定を適用", use_container_width=True):
        state.players[0].name = (name1 or "").strip() or "Player 1"
        state.players[1].name = (name2 or "").strip() or "Player 2"
        apply_settings(target_points, foul_penalty, scratch_penalty, allow_negative)

# --- スコアカード（常に横2固定：行マーカーも併用） ---
st.markdown("<div class='score-row-marker'></div>", unsafe_allow_html=True)
s1, s2 = st.columns(2)
p1, p2 = state.players[0], state.players[1]

# 勝利判定のクラス付与
win_p1 = "winner-card" if state.finished and p1.score >= settings.target_points else ""
win_p2 = "winner-card" if state.finished and p2.score >= settings.target_points else ""

with s1:
    st.markdown(f"""
        <div class="score-card {win_p1}">
          <div class="score-name">{html.escape(p1.name)}</div>
          <div class="score-val">{p1.score}</div>
          {('<div class="turn-badge">YOUR TURN</div>' if state.current_player_index==0 and not state.finished else '')}
          {('<div class="turn-badge" style="background:#fff">🏆 WINNER</div>' if win_p1 else '')}
        </div>
        """, unsafe_allow_html=True)
with s2:
    st.markdown(f"""
        <div class="score-card {win_p2}">
          <div class="score-name">{html.escape(p2.name)}</div>
          <div class="score-val">{p2.score}</div>
          {('<div class="turn-badge">YOUR TURN</div>' if state.current_player_index==1 and not state.finished else '')}
          {('<div class="turn-badge" style="background:#fff">🏆 WINNER</div>' if win_p2 else '')}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='sep'/>", unsafe_allow_html=True)

if state.finished:
    # 勝利者名の取得
    winner_name = p1.name if p1.score >= settings.target_points else p2.name
    
    st.markdown(f"""
        <div class="win-banner">
            <p class="win-title">🏆 VICTORY</p>
            <p class="win-player">{html.escape(winner_name)}</p>
        </div>
    """, unsafe_allow_html=True)
    
    wc1, wc2 = st.columns(2)
    with wc1:
        if st.button("記録を継続（閉じる）", key="win_close", use_container_width=True):
            # 内部的な finished はそのままに、リ rerun して表示を更新（またはフラグ管理）
            # 今回は簡易的にfinishedを一時オフにするなどの処理はせず、ボタンで操作
            st.rerun()
    with wc2:
        if st.button("次の試合を開始", key="win_reset", use_container_width=True):
            reset_match()
            st.rerun()

st.markdown("<hr class='sep'/>", unsafe_allow_html=True)

# --- 操作ボタン（横向き=6横 / 縦向き=3+3：行マーカーも併用） ---
st.markdown("<div class='controls-row-marker'></div>", unsafe_allow_html=True)  # ★行マーカー（保険）

row1 = st.columns(3)

actions_row1 = [
    ("ターン交代", "#f4b400", "btn_turn"),
    ("ファウル", "#e53935", "btn_foul"),
    ("スクラッチ", "#8e24aa", "btn_scratch"),
]

for col, (label, color, key) in zip(row1, actions_row1):
    with col:
        st.markdown(
            f"<div class='ctrl-scope' style='--btn-bg:{color}'></div>",
            unsafe_allow_html=True
        )
        if st.button(label, key=key, use_container_width=True):
            if key == "btn_turn":
                end_turn()
            elif key == "btn_foul":
                apply_penalty("foul")
            elif key == "btn_scratch":
                apply_penalty("scratch")

row2 = st.columns(3)

actions_row2 = [
    ("アンドゥ", "#1e88e5", "btn_undo"),
    ("ラックﾘｾｯﾄ", "#43a047", "btn_reset"),
    ("試合ﾘｾｯﾄ", "#616161", "btn_match_reset"),
]

for col, (label, color, key) in zip(row2, actions_row2):
    with col:
        st.markdown(
            f"<div class='ctrl-scope' style='--btn-bg:{color}'></div>",
            unsafe_allow_html=True
        )
        if st.button(label, key=key, use_container_width=True):
            if key == "btn_undo":
                undo_last()
            elif key == "btn_reset":
                reset_rack()
            elif key == "btn_match_reset":
                reset_match()

# --- ボール（5×3 固定） ---
st.markdown("<div class='section-title'>BALL SELECTION</div>", unsafe_allow_html=True)
for row_start in (1, 6, 11):  # 1-5, 6-10, 11-15
    cols = st.columns(5)
    for i, n in enumerate(range(row_start, row_start + 5)):
        with cols[i]:
            disabled = state.finished or state.pocketed.get(n, False)
            if st.button(str(n), key=f"ball_{n}", use_container_width=True, disabled=disabled):
                pocket_ball(n)

# --- ログ & 保存/読み込み ---
st.markdown("<div class='section-title'>GAME LOG</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='log-panel'>{'<br>'.join(st.session_state.log) or '（ログはまだありません）'}</div>",
    unsafe_allow_html=True
)

c_save, c_load = st.columns(2)
with c_save:
    download_json = json.dumps(to_dict(), ensure_ascii=False, indent=2)
    st.download_button(
        "試合を保存（JSONダウンロード）",
        data=download_json,
        file_name="rotation_match.json",
        mime="application/json",
        use_container_width=True,
    )
with c_load:
    uploaded = st.file_uploader("試合を読み込み（JSONアップロード）", type=["json"])
    if uploaded is not None:
        # Streamlit のバージョン差異（getvalue / getValue）を吸収
        try:
            raw = uploaded.getvalue()
        except AttributeError:
            raw = uploaded.getValue()
        try:
            data = json.loads(raw.decode("utf-8"))
            load_from_dict(data)
            st.success("試合を読み込みました")
        except Exception as e:
            st.error(f"読み込みに失敗しました: {e}")

st.caption("© Rotation Scoreboard (Streamlit)")