import streamlit as st

# 0. ページ全体のレイアウト設定
# layout="centered" を指定することで、コンテンツを中央に寄せます。
# st.set_page_config は、他のすべての Streamlit コマンドよりも先に呼び出す必要があります。
st.set_page_config(
    page_title="Billiard Scoreboard",
    page_icon="🎱",
    initial_sidebar_state="auto"
)

# 全ページ共通のスタイル（Streamlitのブランディング・赤いボタンを完全に消去）
st.markdown("""
    <style>
    /* フッターを物理的に消去 */
    footer {display: none !important;}

    /* ヘッダー全体を消すとサイドバーが使えなくなるため、背景を透明にしてボタンは白く強調 */
    [data-testid="stHeader"] {background: rgba(0,0,0,0) !important;}
    [data-testid="stHeader"] svg {
        fill: white !important;
    }

    /* 赤い「Deploy」ボタンを消去 */
    .stAppDeployButton {display: none !important;}
    .stDeployButton {display: none !important;}
    /* 右下の「Hosted with Streamlit」バッジを消去 */
    div[class^="viewerBadge"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    #stConnectionStatus {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# 1. デバイス検知 (Streamlit 1.36.0+)
# ヘッダーから User-Agent を取得し、iPhone かどうかを判定します
ua = st.context.headers.get("User-Agent", "")
is_iphone = "iPhone" in ua

# 2. 各ページの定義
# st.Page を使用すると、pages/ ディレクトリの自動生成ルールを上書きできます
def show_home():
    # ホーム画面のみに適用するスタイル定義
    # これにより、Surface版のスコア画面などのwideレイアウトを邪魔しません
    st.markdown("""
        <style>
        .block-container {
            max-width: 800px;
            padding-top: 2rem;
            margin: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🎱 Billiard Scoreboard Simulator")
    st.markdown("""
    このアプリでは、ビリヤードの各種スコアボードのシミュレーションを確認できます。  
    左のサイドバーから、シミュレーションしたいスコアのゲームを選択してください。
    """)
    
    if is_iphone:
        st.markdown("※縦画面で利用してください（横画面非対応）。")
        st.info("📱 iPhoneからアクセスしています。モバイル専用ページを表示します。")

    st.markdown("---")
    st.caption("Built with Python & Streamlit")

home_pg = st.Page(show_home, title="Home", icon="🏠", default=True, layout="centered")
n_surface = st.Page("pages/1_nineball_surface.py", title="Nineball (Surface)", icon="🎱", layout="wide")
n_iphone  = st.Page("pages/2_nineball_iphone.py", title="Nineball (iPhone)", icon="📱", layout="centered")
r_surface = st.Page("pages/3_rotation_surface.py", title="Rotation (Surface)", icon="🎱", layout="wide")
r_iphone  = st.Page("pages/4_rotation_iphone.py", title="Rotation (iPhone)", icon="📱", layout="centered")

# 3. ナビゲーションの動的生成
# iPhone の場合は Surface 用のページをリストから除外します
if is_iphone:
    # iPhone の場合は iPhone 版のみ表示
    nav_dict = {
        "Main": [home_pg],
        "iPhone View": [n_iphone, r_iphone]
    }
else:
    # それ以外（Surface等）の場合は Surface 版のみ表示
    nav_dict = {
        "Main": [home_pg],
        "Surface View": [n_surface, r_surface]
    }

# ナビゲーションの実行
# これによりサイドバーが自動的に設定されます
pg = st.navigation(nav_dict)

# 選択されたページを実行
pg.run()