# -*- coding: utf-8 -*-
# surface.py
# -----------------------------------------------------------------------------
# 変更点：
#  - 操作ボタン色：ディープブルーで統一（#0B1E5B / hover #12307A）
#  - 操作ボタンの高さ拡大（min-height / padding / font-size）
#  - 操作ボタン領域＆ボール領域の上下余白を圧縮（CSS＋列 gap）
#  - st.columns の gap: "tiny" 未サポート → BALLS は "xxsmall" に修正
#  - 15番ボールのストライプ色は #8B4513 を維持
# -----------------------------------------------------------------------------

from __future__ import annotations

import base64
import html
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

# =========================
# 0) ページ設定
# =========================
st.set_page_config(
    page_title="Rotation Scoreboard (Surface Pro 8)",
    page_icon="🎱",
    layout="wide",
)

# =========================
# 画像 → data:URI
# =========================
APP_DIR = Path(__file__).parent.resolve()
TURN_IMG_FILE = APP_DIR / "image" / "1_turn.png"      # 手番
NOTURN_IMG_FILE = APP_DIR / "image" / "1_noturn.png"  # 待機

def data_uri_from_file(path: Path) -> str:
    """ローカル画像を data:URI にして返す（見つからなければ空文字）"""
    try:
        if not path.exists():
            return ""
        mime = "image/png" if path.suffix.lower() == ".png" else "image/svg+xml"
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{b64}"
    except Exception:
        return ""

TURN_IMG_URI = data_uri_from_file(TURN_IMG_FILE)
NOTURN_IMG_URI = data_uri_from_file(NOTURN_IMG_FILE)

# =========================
# CSS（ディープブルー統一 + 高さ拡大 + 余白圧縮）
# =========================
st.markdown("""
<style>

/* Streamlit標準ヘッダーとフッターを隠して全画面感を出す */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {
    padding-top: 2rem;
    padding-bottom: 0rem;
}
            
/* =========================================================
   Base / Theme / Layout
   ========================================================= */
:root {
  --bg:#0f1117; --panel:#171a1f; --panel-2:#1c2130; --text:#e8eaed; --accent:#f7c948;
  --gap:.8rem; 

  --ops-deepblue: #0B1E5B;
  --ops-deepblue-hover: #12307A;

  /* ボタンのイメージ（高さ・色）は維持 */
  --ops-btn-minh: clamp(64px, 7.2vh, 96px);
  --ops-btn-pad-v: 1.25rem;
  --ops-btn-pad-h: 1.30rem;
  --ops-btn-fsize: clamp(22px, 2.0vw, 30px); /* 文字崩れ防止のため最大値を少し抑制 */
  --ops-btn-radius: 16px;
}
            
html, body { background: var(--bg); }

.main .block-container, .block-container{
  padding-top: max(8px, env(safe-area-inset-top, 0px)) !important;
  padding-bottom: .8rem;
}

/* iOS / Edge button appearance reset */
.stButton>button{ -webkit-appearance:none; }

/* =========================================================
   Header Title
   ========================================================= */
.app-top-spacer{
  height: calc(env(safe-area-inset-top, 0px) + 8px);
}

.h-title{
  font-weight:900;
  letter-spacing:.6px;
  text-align:center;
  color:#fff;
  margin: 0 0 .20rem !important;
  font-size: clamp(20px, 1.8vw, 28px);
  scroll-margin-top: calc(env(safe-area-inset-top, 0px) + 12px);
}

/*   ***   */
hr.sep{
  border:none;
  height:1px;
  background:#2b3142;
  margin:.25rem 0 !important;
}

.section-title{
  margin:.4rem 0 .3rem !important;
}

/* =========================================================
   Settings: Expander Container / Spacing
   ========================================================= */
.settings-wrap{
  margin:.25rem 0 .4rem !important;
  padding:0 !important;
  border:none !important;
  background:transparent !important;
}

.settings-wrap [data-testid="stExpander"] > details{
  padding:0 !important;
  margin:0 !important;
  border:none !important;
  background:transparent !important;
}

.settings-wrap [data-testid="stExpander"] .block-container{
  padding-top:0 !important;
  margin-top:0 !important;
}

/* =========================================
   Player Name ラベル (Player 1 Nameなど)
   ========================================= */
.settings-label-player {
    font-size: 32px !important;
    font-weight: 900 !important;
    margin-bottom: 15px !important; /* ラベルと入力欄の隙間を少し作る */
}

/* =========================================
   勝利点・減点 などのラベル
   ========================================= */
.settings-label {
  font-size: 28px !important; /* 横並びのため少しだけ調整 */
  font-weight: 900 !important;
  color: #cfd3dc !important;
  line-height: 1.8 !important; /* 入力欄と高さを合わせる */
  white-space: nowrap !important;
}

/* =========================================
   チェックボックス (マイナス許可) の文字
   ========================================= */
[data-testid="stCheckbox"] p {
  font-size: 28px !important;
  font-weight: 800 !important;
  line-height: 1.2 !important;
}

/* チェックボックスの箱を大きく */
[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] span {
  transform: scale(1.5) !important;
  margin-right: 10px !important;
}

/* =========================================
   入力ボックス内の数字・文字サイズ
   ========================================= */
[data-testid="stTextInput"] div[data-baseweb="input"] {
    /* ボックス自体の高さを十分に確保 (文字サイズ32pxに対して) */
    height: 70px !important; 
    display: flex !important;
    align-items: center !important;
}

[data-testid="stTextInput"] input {
    /* 文字サイズ */
    font-size: 32px !important;
    font-weight: 900 !important;
    /* 内部の余白を調整して文字の「欠け」を防ぐ */
    padding-top: 0px !important;
    padding-bottom: 0px !important;
    height: 100% !important;
    line-height: 1 !important;
    color: #ffffff !important;
}

/* =========================================
   数値入力 (勝利点など) の高さも合わせて統一
   ========================================= */
[data-testid="stNumberInputField"] div[data-baseweb="input"] {
    height: 60px !important;
}

[data-testid="stNumberInputField"] input {
    font-size: 32px !important;
    font-weight: 900 !important;
}

[data-testid="stNumberInputField"] input {
    font-size: 32px !important;
    font-weight: 900 !important;
}

/* =========================================================
   Settings: Streamlit Widgets (Active)
   ========================================================= */

/* =========================================
   Expander title（Streamlit仕様）
   ========================================= */
[data-testid="stExpander"]
[data-testid="stMarkdownContainer"] > p {
  font-size: 22px !important;
  font-weight: 800 !important;
}

/* 数値表示（61） */
[data-testid="stNumberInputField"] {
  background-color: transparent;
  border: none;

  font-size: 28px;
  line-height: 1;
  height: 100%;
  
  
  display: flex;
  align-items: center;

  width: auto;
  min-width: 72px;
  padding: 0 6px;

  text-align: center;
}

/* − / ＋ ボタン */
[data-testid="stNumberInput"] button {
  height: 100%;
  min-width: 32px;


  display: flex;
  align-items: center;
  justify-content: center;

  background: transparent;
  border: none;
  color: #ffffff;
}


/* =========================================
   Checkbox ラベル（マイナス許可）
   ========================================= */
[data-testid="stWidgetLabel"]
[data-testid="stMarkdownContainer"] > p {
  font-size: 28px !important;
  font-weight: 800 !important;

  position: relative;
  top: -5px;
  line-height: 1;
}

/* =========================================================
   Scoreboard
   ========================================================= */
.score-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--gap);
  /* スコアボードのエリアを画面の55%まで拡大 */
  min-height: 55vh !important; 
  align-items: stretch;
  /* 操作ボタンを下に押し下げて、誤操作を防ぐ余白を作る */
  margin-bottom: 5px !important; 
}

.score-card {
  height: 100%;
  background: linear-gradient(180deg,#232736,#171a1f);
  border: 1px solid #2b3142;
  border-radius: 16px;
  padding: 2rem 1.2rem !important; /* 上下の余白を増やして広く見せる */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between; /* 名前・数字・バッジをバランスよく配置 */
}

.score-head{
  width:100%;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:.6rem;
  margin-bottom:.25rem;
}

.score-name{
  font-weight:900;
  font-size:clamp(26px,2.6vw,38px);
  color:#fff;
  padding:.35rem 1rem;
  border-radius:10px;
  background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.08);
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}

.score-val {
  /* フォントサイズをさらに大きく (最小200px / 最大450px) */
  font-size: clamp(200px, 35vw, 450px) !important; 
  /* 行高を極限まで小さくして余白を排除 */
  line-height: 0.75;
  margin: auto 0 !important;
  font-weight: 900;
  color: #fff;
  text-shadow: 0 15px 40px rgba(0,0,0,0.6);
  /* 数字が枠からはみ出さないよう微調整 */
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ボタン内の文字が2行にならないように強制 */
.stButton > button div p {
  white-space: nowrap !important;
  letter-spacing: -0.5px !important;
}
.turn-badge{
  margin:0;
  padding:0;
  background:transparent;
  border:none;
  line-height:0;
}

.turn-badge img{
  display:block;
  height:clamp(48px, 5.2vw, 96px);
  width:auto;
}

.turn-badge.off img{
  filter:grayscale(100%);
  opacity:.35;
}

.turn-badge-fallback{
  padding:.45rem 1rem;
  border-radius:999px;
  font-weight:950;
  white-space:nowrap;
  background:var(--accent);
  color:#111;
  box-shadow:0 4px 10px rgba(247,201,72,.22);
  font-size:clamp(22px, 1.9vw, 30px);
}

.turn-badge-fallback.off{
  background:#2b3142;
  color:#e0e0e0;
  box-shadow:none;
  opacity:.75;
}

/* =========================================================
   Operation Buttons
   ========================================================= */
#ops-scope{ margin-top:.25rem; margin-bottom:.25rem; }

.st-key-btn_turn_surface  div.stButton > button,
.st-key-btn_foul_surface  div.stButton > button,
.st-key-btn_scratch_surface div.stButton > button,
.st-key-btn_undo_surface  div.stButton > button,
.st-key-btn_reset_surface div.stButton > button,
.st-key-btn_match_reset_surface div.stButton > button,
.st-key-btn_turn_surface  button[data-testid="stBaseButton-secondary"],
.st-key-btn_foul_surface  button[data-testid="stBaseButton-secondary"],
.st-key-btn_scratch_surface button[data-testid="stBaseButton-secondary"],
.st-key-btn_undo_surface  button[data-testid="stBaseButton-secondary"],
.st-key-btn_reset_surface button[data-testid="stBaseButton-secondary"],
.st-key-btn_match_reset_surface button[data-testid="stBaseButton-secondary"]{
  background: var(--ops-deepblue) !important;
  color:#fff !important;
}

.st-key-btn_turn_surface  div.stButton > button:hover,
.st-key-btn_foul_surface  div.stButton > button:hover,
.st-key-btn_scratch_surface div.stButton > button:hover,
.st-key-btn_undo_surface  div.stButton > button:hover,
.st-key-btn_reset_surface div.stButton > button:hover,
.st-key-btn_match_reset_surface div.stButton > button:hover,
.st-key-btn_turn_surface  button[data-testid="stBaseButton-secondary"]:hover,
.st-key-btn_foul_surface  button[data-testid="stBaseButton-secondary"]:hover,
.st-key-btn_scratch_surface button[data-testid="stBaseButton-secondary"]:hover,
.st-key-btn_undo_surface  button[data-testid="stBaseButton-secondary"]:hover,
.st-key-btn_reset_surface button[data-testid="stBaseButton-secondary"]:hover,
.st-key-btn_match_reset_surface button[data-testid="stBaseButton-secondary"]:hover{
  background: var(--ops-deepblue-hover) !important;
  filter: brightness(1.02) saturate(1.02);
}

.st-key-btn_turn_surface  div.stButton > button,
.st-key-btn_foul_surface  div.stButton > button,
.st-key-btn_scratch_surface div.stButton > button,
.st-key-btn_undo_surface  div.stButton > button,
.st-key-btn_reset_surface div.stButton > button,
.st-key-btn_match_reset_surface div.stButton > button{
  width:100%;
  min-height: var(--ops-btn-minh);
  padding: var(--ops-btn-pad-v) var(--ops-btn-pad-h);
  font-size: var(--ops-btn-fsize) !important;
  font-weight:900;
  letter-spacing:.2px;
  line-height:1.25;
  white-space:normal;
  border-radius: var(--ops-btn-radius);
  border:none;
  cursor:pointer;
  box-shadow:0 3px 0 rgba(0,0,0,.35), 0 6px 16px rgba(0,0,0,.20);
  transition: filter .12s ease, transform .06s ease, box-shadow .12s ease, background-color .12s ease;
}

.st-key-btn_turn_surface  div.stButton > button:active,
.st-key-btn_foul_surface  div.stButton > button:active,
.st-key-btn_scratch_surface div.stButton > button:active,
.st-key-btn_undo_surface  div.stButton > button:active,
.st-key-btn_reset_surface div.stButton > button:active,
.st-key-btn_match_reset_surface div.stButton > button:active{
  transform:translateY(1px);
  box-shadow:0 1px 0 rgba(0,0,0,.35) !important;
}

.st-key-btn_turn_surface  div.stButton > button:focus-visible,
.st-key-btn_foul_surface  div.stButton > button:focus-visible,
.st-key-btn_scratch_surface div.stButton > button:focus-visible,
.st-key-btn_undo_surface  div.stButton > button:focus-visible,
.st-key-btn_reset_surface div.stButton > button:focus-visible,
.st-key-btn_match_reset_surface div.stButton > button:focus-visible{
  outline:3px solid rgba(255,255,255,.45);
  outline-offset:2px;
  box-shadow:0 0 0 3px rgba(255,255,255,.25), 0 6px 16px rgba(0,0,0,.25) !important;
}



/* =========================================================
   Balls
   ========================================================= */
#balls-scope{ margin-top:.2rem; margin-bottom:.4rem; }

#ops-scope [data-testid="stElementContainer"],
#balls-scope [data-testid="stElementContainer"]{
  margin:.1rem 0 !important;
  padding:0 !important;
}

#ops-scope [data-testid="stVerticalBlock"],
#balls-scope [data-testid="stVerticalBlock"]{
  gap:.2rem !important;
  row-gap:.2rem !important;
}

#ops-scope [data-testid="stHorizontalBlock"],
#balls-scope [data-testid="stHorizontalBlock"]{
  row-gap:.2rem !important;
  margin:0 !important;
  padding:0 !important;
}

#ops-scope div.stButton{ margin-bottom:.1rem !important; }
#balls-scope .stButton{ margin:.1rem 0 !important; }
#balls-scope + hr.sep{ margin-top:.2rem !important; }

.st-key-btn_turn_surface  div.stButton [data-testid="stMarkdownContainer"] > p,
.st-key-btn_foul_surface  div.stButton [data-testid="stMarkdownContainer"] > p,
.st-key-btn_scratch_surface div.stButton [data-testid="stMarkdownContainer"] > p,
.st-key-btn_undo_surface  div.stButton [data-testid="stMarkdownContainer"] > p,
.st-key-btn_reset_surface div.stButton [data-testid="stMarkdownContainer"] > p,
.st-key-btn_match_reset_surface div.stButton [data-testid="stMarkdownContainer"] > p{
  font-size: clamp(20px, 1.6vw, 26px) !important;
  line-height: 1.28 !important;
  font-weight: 950 !important;
  letter-spacing: .2px !important;
  margin: 0 !important;
  white-space: nowrap !important;
  overflow-wrap: normal !important;
}

.st-key-btn_turn_surface  button[data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"] > p,
.st-key-btn_foul_surface  button[data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"] > p,
.st-key-btn_scratch_surface button[data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"] > p,
.st-key-btn_undo_surface  button[data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"] > p,
.st-key-btn_reset_surface button[data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"] > p,
.st-key-btn_match_reset_surface button[data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"] > p{
  font-size: clamp(22px, 1.9vw, 30px) !important;
  line-height: 1.28 !important;
  font-weight: 950 !important;
  letter-spacing: .2px !important;
  margin: 0 !important;
}



/* Balls appearance */
[class*="st-key-ball_"][class*="_surface"] .stButton>button{
  width:100%;
  aspect-ratio:1/1;
  height:auto;
  border-radius:50% !important;
  padding:0 !important;
  box-sizing:border-box;
  overflow:hidden;
  border:2px solid rgba(255,255,255,.25);
  box-shadow: inset 0 8px 12px rgba(255,255,255,.18), 0 4px 12px rgba(0,0,0,.35);
  color:#111;
  font-weight:900;
  font-size:clamp(20px, 1.8vw, 30px) !important;
  -webkit-mask-image: radial-gradient(circle, #000 99%, transparent 100%);
  mask-image: radial-gradient(circle, #000 99%, transparent 100%);
}

[class*="st-key-ball_"][class*="_surface"] .stButton>button:disabled{
  filter:grayscale(100%);
  opacity:.35;
  box-shadow:none;
  cursor:not-allowed;
}

[class*="st-key-ball_"][class*="_surface"]
[data-testid="stMarkdownContainer"] > p{
  font-size: clamp(20px, 1.8vw, 30px) !important;
  line-height: 1 !important;
  font-weight: 950 !important;
  letter-spacing: .2px !important;
  margin: 0 !important;
}



/* =========================================================
   Ordered Balls Colors
   ========================================================= */
.st-key-ball_1_surface  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #F5C400; }
.st-key-ball_2_surface  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #2A61FF; }
.st-key-ball_3_surface  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #D93636; }
.st-key-ball_4_surface  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #7B2FFF; }
.st-key-ball_5_surface  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #FF7F23; }
.st-key-ball_6_surface  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #118C4F; }
.st-key-ball_7_surface  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #8B4513; }
.st-key-ball_8_surface  .stButton>button{ background:radial-gradient(circle at 50% 50%, #fff 0 27%, transparent 28%), #000000; color:#f5f5f5; }

.st-key-ball_9_surface   .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #F5C400 18% 82%, #fff 82%), #fff; }
.st-key-ball_10_surface  .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #2A61FF 18% 82%, #fff 82%), #fff; }
.st-key-ball_11_surface  .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #D93636 18% 82%, #fff 82%), #fff; }
.st-key-ball_12_surface  .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #7B2FFF 18% 82%, #fff 82%), #fff; }
.st-key-ball_13_surface  .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #FF7F23 18% 82%, #fff 82%), #fff; }
.st-key-ball_14_surface  .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #118C4F 18% 82%, #fff 82%), #fff; }
.st-key-ball_15_surface  .stButton>button{ background:radial-gradient(circle,#fff 0 27%,transparent 30%), linear-gradient(#fff 0 18%, #8B4513 18% 82%, #fff 82%), #fff; }



/* =========================================================
   Win Banner (高さ圧縮・スリム版)
   ========================================================= */
.win-banner {
  background: radial-gradient(100% 130% at 50% 0%, rgba(247,201,72,.24), rgba(0,0,0,.0));
  border: 1px solid rgba(247,201,72,.35);
  border-radius: 12px;
  
  /* 上下パディングを 0.4rem → 0.8rem に微増（少し広く） */
  padding: 0.8rem 1.2rem;
  
  /* 外側のマージンも少し広げて独立感を出す */
  margin: 0.6rem 0 0.8rem;
  
  text-align: center;
  color: #fff;
  box-shadow: 0 8px 20px rgba(0,0,0,.4);
}

.win-title {
  font-weight: 950;
  /* 文字サイズはスリム版を維持 */
  font-size: clamp(28px, 4.2vw, 52px);
  letter-spacing: .05em;
  /* 行高を少し広げて、タイトルとサブテキストの間隔を確保 */
  line-height: 1.2; 
  text-shadow: 0 4px 15px rgba(0,0,0,.6);
}

.win-sub {
  /* サブテキストの上の余白を調整 */
  margin-top: 0.2rem;
  font-size: clamp(14px, 1.8vw, 20px);
  color: #f7f7f7;
  opacity: .95;
  line-height: 1.3;
}
            
/* =========================================================
   Win Banner Buttons (微調整・サイズ適正化版)
   ========================================================= */
.st-key-win_close_btn div.stButton > button,
.st-key-win_reset_btn div.stButton > button {
    /* 最小24px→20px / 最大36px→28px へ一段階コンパクトに */
    font-size: clamp(20px, 2.2vw, 28px) !important;
    font-weight: 900 !important;
    
    /* 高さも 80px→64px に抑えてスッキリと */
    min-height: 64px !important;
    padding: 0.8rem 1rem !important;
    
    border-radius: 10px !important;
    white-space: nowrap !important;
}

/* ボタン内テキストの微調整 */
.st-key-win_close_btn [data-testid="stMarkdownContainer"] > p,
.st-key-win_reset_btn [data-testid="stMarkdownContainer"] > p {
    font-size: clamp(20px, 2.2vw, 28px) !important;
    line-height: 1.2 !important;
    margin: 0 !important;
}

.log-wrap{
  margin: 1.4rem 0 .8rem;
  margin-top: 4.2rem;
  padding: 1.0rem 0;
  border-radius: 10px;
  background: transparent;
  border: none;
}

.log-expander[data-testid="stExpander"]{
  margin-top: .2rem;
}

.log-panel{
  background: var(--panel-2);
  border: 1px solid #2b3142;
  border-radius: 10px;
  padding: .8rem 1.0rem;
  color: var(--text);
  min-height: 3rem;
  word-break: break-word;
  overflow-wrap: anywhere;
}

/* =========================================================
   st.columns 内で出る 上境界線を消す（設定エリア専用）
   ========================================================= */

/* number_input を含む column の上線を除去 */
[data-testid="stVerticalBlock"] > div {
  border-top: none !important;
  box-shadow: none !important;
}

/* =========================================================
   設定エリア：Column / Block 境界線の完全無効化
   （これが「上の線」の正体）
   ========================================================= */

#settings-scope [data-testid="stVerticalBlock"],
#settings-scope [data-testid="stHorizontalBlock"],
#settings-scope [data-testid="stElementContainer"] {
  border: none !important;
  box-shadow: none !important;
}

/* expander 内部の不要な separator も除去 */
#settings-scope hr,
/* #settings-scope [role="separator"] {
  display: none !important;
}
*/
</style>
""", unsafe_allow_html=True)

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
if "show_win" not in st.session_state:
  st.session_state.show_win = False
if "win_winner" not in st.session_state:
  st.session_state.win_winner = ""
if "show_settings" not in st.session_state:
  st.session_state.show_settings = False

settings: Settings = st.session_state.settings
state: MatchState = st.session_state.rotation_state

# =========================
# 3) ユーティリティ
# =========================
def current_player() -> PlayerState:
  return state.players[state.current_player_index]

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
      st.session_state.show_win = True
      st.session_state.win_winner = p.name
      try: st.balloons()
      except: pass
      try: st.toast(f"{p.name} - WIN!", icon="🎉")
      except: pass
      break

def snapshot() -> Dict[str, Any]:
  return {
      "players": [{"name": p.name, "score": p.score} for p in state.players],
      "current_player_index": state.current_player_index,
      "pocketed": dict(state.pocketed),
      "finished": state.finished,
  }

def push_snapshot():
  state.history.append({"type": "snapshot", "state": snapshot()})

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
  state.current_player_index = 1 - state.current_player_index
  add_log("ターン交代")
  st.session_state.state = state
  st.rerun()

def apply_penalty(kind: str):
  if state.finished:
    return
  push_snapshot()
  penalty = settings.foul_penalty if kind == "foul" else settings.scratch_penalty
  player = current_player()
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
  p1 = (state.players[0].name or "Player 1").strip() or "Player 1"
  p2 = (state.players[1].name or "Player 2").strip() or "Player 2"
  state.players = [PlayerState(p1), PlayerState(p2)]
  state.current_player_index = 0
  state.pocketed = {i: False for i in range(1, 16)}
  state.history = []
  state.finished = False
  st.session_state.log = []
  st.session_state.show_win = False
  st.session_state.win_winner = ""
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
    global settings, state

    s = data.get("settings", {})
    st.session_state.settings = Settings(
        target_points=int(s.get("target_points", 61)),
        foul_penalty=int(s.get("foul_penalty", -1)),
        scratch_penalty=int(s.get("scratch_penalty", -1)),
        allow_negative=bool(s.get("allow_negative", True)),
    )

    raw_players = data.get("state", {}).get(
        "players",
        [{"name": "Player 1", "score": 0}, {"name": "Player 2", "score": 0}]
    )

    players = [
        PlayerState(
            clean_name(p.get("name", f"Player {i+1}")),
            int(p.get("score", 0))
        )
        for i, p in enumerate(raw_players)
    ]

    st.session_state.state = MatchState(
        players=players,
        current_player_index=int(data.get("state", {}).get("current_player_index", 0)),
        pocketed={
            int(k): bool(v)
            for k, v in data.get("state", {}).get(
                "pocketed",
                {i: False for i in range(1, 16)}
            ).items()
        },
        history=[],
        finished=bool(data.get("state", {}).get("finished", False)),
    )

    settings = st.session_state.settings
    state = st.session_state.state
    add_log("JSON から試合を読み込み")

def clean_name(s: str) -> str:
  s = (s or "").strip()
  return "".join(ch for ch in s if ch.isprintable())

# =========================
# 4) タイトル表示（15番ボールアイコン付き）
# 【アイコン最小化・微調整版】
# =========================

# 15番ボールの色（マルーン/ブラウン系）
BALL_15_COLOR = "#8B4513" 

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

    /* 3. 15番ボール（さらにコンパクトに） */
    .ball-15-mini {{
        /* サイズを前回の 30-42px から 24-34px へ縮小 */
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
        
        /* 数字の「15」をボールサイズに合わせて縮小 */
        color: #111;
        font-weight: 950;
        font-size: clamp(7px, 0.8vw, 10px);
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
        <div class="ball-15-mini">15</div>
        <div class="title-text-mini-ver">Rotation Scoreboard — Surface</div>
    </div>
    """,
    unsafe_allow_html=True
)

# 設定
with st.expander("設定を開く／閉じる", expanded=st.session_state.show_settings):
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="settings-label-player">Player 1 Name</div>',
            unsafe_allow_html=True
        )
        st.text_input(
            "プレイヤー1",
            value=state.players[0].name,
            key="p1_name",
            label_visibility="collapsed"
        )

    with col2:
        st.markdown(
            '<div class="settings-label-player">Player 2 Name</div>',
            unsafe_allow_html=True
        )
        st.text_input(
            "プレイヤー2",
            value=state.players[1].name,
            key="p2_name",
            label_visibility="collapsed"
        )

    # カラム比率を微調整して、大きな文字でも入り切るようにしました
    col1, col2, col3, col4 = st.columns([1.1, 1.2, 1.3, 1.0])

    with col1:
        # ラベルとフィールドの比率を調整
        lab, field = st.columns([0.8, 1.2])
        with lab:
            st.markdown('<div class="settings-label">勝利点</div>', unsafe_allow_html=True)
        with field:
            st.number_input("勝利点", value=settings.target_points, min_value=0, max_value=1000, key="target_points", label_visibility="collapsed")

    with col2:
        lab, field = st.columns([1.1, 0.9])
        with lab:
            st.markdown('<div class="settings-label">ファウル減点</div>', unsafe_allow_html=True)
        with field:
            st.number_input("ファウル減点", value=settings.foul_penalty, key="foul_penalty", label_visibility="collapsed")

    with col3:
        lab, field = st.columns([1.1, 0.9])
        with lab:
            st.markdown('<div class="settings-label">スクラッチ減点</div>', unsafe_allow_html=True)
        with field:
            st.number_input("スクラッチ減点", value=settings.scratch_penalty, key="scratch_penalty", label_visibility="collapsed")

    with col4:
        # マイナス許可のチェックボックス自体を垂直中央に寄せるため、ラベルは無しに
        st.checkbox("マイナス許可", value=settings.allow_negative, key="allow_negative")

    if st.button("設定を適用", use_container_width=True, key="apply_settings_btn"):
        state.players[0].name = st.session_state.p1_name or "Player 1"
        state.players[1].name = st.session_state.p2_name or "Player 2"
        apply_settings(
            st.session_state.target_points,
            st.session_state.foul_penalty,
            st.session_state.scratch_penalty,
            st.session_state.allow_negative
        )

# 勝利バナー
if st.session_state.get("show_win"):
  winner = st.session_state.get("win_winner", "WINNER")
  st.markdown(
    f"""
    <div class="win-banner">
      <div class="win-title">🏆 WIN</div>
      <div class="win-sub">{html.escape(winner)} が勝利しました！</div>
    </div>
    """,
    unsafe_allow_html=True,
  )
  c_win1, c_win2 = st.columns([1,1])
  with c_win1:
    if st.button("閉じる", key="win_close_btn", use_container_width=True):
      st.session_state.show_win = False
      st.rerun()
  with c_win2:
    if st.button("試合リセット", key="win_reset_btn", use_container_width=True):
      st.session_state.show_win = False
      reset_match()

# バッジ
def render_turn_badge_img(is_turn: bool) -> str:
    """
    手番バッジ（TURN/WAITING）を <img> で描画。
    画像が無い場合はテキストでフォールバック。
    ※ < や > が &lt; / &gt; に変換されても、最後に unescape して正しく復元します。
    """
    src_on  = TURN_IMG_URI or ""
    src_off = NOTURN_IMG_URI or ""

    # 画像が両方ない → テキストバッジ
    if src_on == "" and src_off == "":
        label = "YOUR TURN" if is_turn else "WAITING"
        cls = "turn-badge-fallback" + ("" if is_turn else " off")
        # 実体参照のまま書いてもOK。最後に unescape します。
        tmpl = f"""
        &lt;div class="{cls}"&gt;{html.escape(label)}&lt;/div&gt;
        """
        return html.unescape(tmpl.strip())

    # 片方欠け → ある方で補完
    if src_on == "":
        src_on = src_off
    if src_off == "":
        src_off = src_on

    src = src_on if is_turn else src_off
    cls = "turn-badge on" if is_turn else "turn-badge off"
    alt = "YOUR TURN" if is_turn else "WAITING"

    # 実体参照で安全に記述 → 実行時に HTML に戻す
    tmpl = f"""
    &lt;div class="{cls}"&gt;
      &lt;img src="{html.escape(src)}" alt="{html.escape(alt)}" /&gt;
    &lt;/div&gt;
    """
    return html.unescape(tmpl.strip())


# スコアボード
p1, p2 = state.players[0], state.players[1]
p1_name_esc = html.escape(p1.name or "")
p2_name_esc = html.escape(p2.name or "")

st.markdown(
  f"""
  <div class='score-grid'>
    <div class="score-card">
      <div class="score-head">
        <div class="score-name">{p1_name_esc}</div>
        {render_turn_badge_img(state.current_player_index == 0)}
      </div>
      <div class="score-val">{p1.score}</div>
    </div>

    <div class="score-card">
      <div class="score-head">
        <div class="score-name">{p2_name_esc}</div>
        {render_turn_badge_img(state.current_player_index==1)}
      </div>
      <div class="score-val">{p2.score}</div>
    </div>
  </div>
  """,
  unsafe_allow_html=True,
)

st.markdown("<hr class='sep'/>", unsafe_allow_html=True)
            
# =========================
# 9) 操作ボタン (6列)
# =========================
st.markdown("<div id='ops-scope'>", unsafe_allow_html=True)

# gapをsmallにして、ボタン同士がくっつきすぎないように調整
ctrl = st.columns(6, gap="small")

# イメージを崩さず、1行に収まりやすいラベル名に変更
labels = ["🔄 交代", "⚠️ ﾌｧｳﾙ", "🚫 ｽｸﾗｯﾁ", "↩ 戻る", "📋 ﾗｯｸ", "🧹 終了"]
keys   = ["btn_turn_surface", "btn_foul_surface", "btn_scratch_surface",
          "btn_undo_surface", "btn_reset_surface", "btn_match_reset_surface"]

for col, label, key in zip(ctrl, labels, keys):
  with col:
    if st.button(label, key=key, use_container_width=True):
      if key == "btn_turn_surface":           end_turn()
      elif key == "btn_foul_surface":         apply_penalty("foul")
      elif key == "btn_scratch_surface":      apply_penalty("scratch")
      elif key == "btn_undo_surface":         undo_last()
      elif key == "btn_reset_surface":        reset_rack()
      elif key == "btn_match_reset_surface":  reset_match()

st.markdown("</div>", unsafe_allow_html=True)

# ===== ボール（横15）— スコープで囲んで余白圧縮 =====
st.markdown("<div id='balls-scope'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>BALLS</div>", unsafe_allow_html=True)

# small -> xxsmall（"none" で完全ゼロも可）
cols = st.columns(15, gap="xxsmall")
# cols = st.columns(15, gap="none")  # ← 横完全ゼロにしたい場合

for n, col in enumerate(cols, start=1):
  with col:
    disabled = state.finished or state.pocketed.get(n, False)
    if st.button(str(n), key=f"ball_{n}_surface", use_container_width=True, disabled=disabled):
      pocket_ball(n)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr class='sep'/>", unsafe_allow_html=True)

# ログ
st.markdown("<div class='log-wrap'>", unsafe_allow_html=True)
with st.expander("ゲームログ（必要な時だけ開く）", expanded=False):
  st.markdown(
    f"<div class='log-panel'>{'<br>'.join(st.session_state.log) or '（ログはまだありません）'}</div>",
    unsafe_allow_html=True,
  )

# 保存 & 読み込み
c_save, c_load = st.columns(2)
with c_save:
  download_json = json.dumps(to_dict(), ensure_ascii=False, indent=2)
  st.download_button(
    "試合を保存（JSONダウンロード）",
    data=download_json,
    file_name="rotation_match.json",
    mime="application/json",
    use_container_width=True,
    key="download_surface"
  )
with c_load:
  uploaded = st.file_uploader("試合を読み込み（JSONアップロード）", type=["json"], key="uploader_surface")
  if uploaded is not None:
    try:
      raw = uploaded.getvalue() if hasattr(uploaded, "getvalue") else uploaded.getValue()
      data = json.loads(raw.decode("utf-8"))
      load_from_dict(data)
      st.success("試合を読み込みました")
    except Exception as e:
      st.error(f"読み込みに失敗しました: {e}")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<hr class='sep'/>", unsafe_allow_html=True)
st.caption("© Rotation Scoreboard for Surface Pro 8 (Streamlit)")