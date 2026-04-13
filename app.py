import streamlit as st

# ページ全体の設定
st.set_page_config(
    page_title="Billiard Simulator",
    page_icon="🎱",
    layout="centered"
)

# タイトル
st.title("🎱 Billiard Simulator")

# 説明
st.markdown("""
このアプリでは、ビリヤードの各種シミュレーションを確認できます。

左のサイドバーから、以下のシミュレーションを選択してください。

### シミュレーション一覧
- **Nineball (Surface)**
- **Nineball (iPhone)**
- **Rotation (Surface)**
- **Rotation (iPhone)**

各ページでは、対応するプログラムを実行・可視化できます。
""")

st.markdown("---")

# フッター（任意）
st.caption("Built with Python & Streamlit")