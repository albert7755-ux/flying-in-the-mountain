"""
峽谷鬼影計時賽 — Streamlit 外殼

這支程式只做三件事：
  1. 讀取同資料夾的 game.html
  2. 把 Supabase 的網址和金鑰填進去
  3. 把整個遊戲畫面顯示出來（撐滿整個螢幕）

遊戲本體、鬼影和排行榜邏輯都在 game.html 裡面，要改遊戲內容改那一支就好。
"""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------- 基本設定
PAGE_TITLE = "峽谷鬼影計時賽"

# 遊戲畫面預設高度（像素）。下面的 CSS 會把它撐成整個螢幕高，
# 這個數字只是瀏覽器不支援時的備用值。
FRAME_HEIGHT = 820

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🛩️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 把 Streamlit 預設的上下留白和頁首頁尾收掉，讓遊戲撐滿整個畫面
st.markdown(
    """
    <style>
      .block-container { padding: 0 !important; max-width: 100% !important; }
      header[data-testid="stHeader"] { display: none; }
      #MainMenu, footer { visibility: hidden; }
      iframe { border: 0; width: 100% !important;
               height: 100vh !important; height: 100dvh !important; display: block; }
      [data-testid="stAppViewContainer"], .main { overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- 讀設定
def get_secret(key: str) -> str:
    """從 secrets.toml 讀一個值，沒設定就回空字串（遊戲仍可單機玩）。"""
    try:
        return str(st.secrets[key]).strip()
    except Exception:
        return ""


SUPABASE_URL = get_secret("SUPABASE_URL").rstrip("/")
SUPABASE_ANON_KEY = get_secret("SUPABASE_ANON_KEY")


# ---------------------------------------------------------------- 讀遊戲
@st.cache_data(show_spinner=False)
def load_template() -> str:
    path = Path(__file__).parent / "game.html"
    return path.read_text(encoding="utf-8")


try:
    html = load_template()
except FileNotFoundError:
    st.error("找不到 game.html，請確認它和 app.py 放在同一個資料夾。")
    st.stop()

html = html.replace("__SUPABASE_URL__", SUPABASE_URL)
html = html.replace("__SUPABASE_ANON_KEY__", SUPABASE_ANON_KEY)

if not (SUPABASE_URL and SUPABASE_ANON_KEY):
    st.warning(
        "尚未設定 Supabase，排行榜和「追第一名鬼影」不會共用（成績只留在自己的裝置）。"
        "請在 App settings → Secrets 填入 SUPABASE_URL 和 SUPABASE_ANON_KEY。",
        icon="⚠️",
    )

components.html(html, height=FRAME_HEIGHT, scrolling=False)
