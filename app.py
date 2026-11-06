"""
体をつくるタンパク質 ─ 入口（左メニューの組み立て）

起動: streamlit run app.py
  ホームの中身は home.py、各ページは pages/、計算部品は tanpaku_core.py にあります。

左メニューは「授業の流れ」の順に4つに束ねています（1つのまとまりは最大6ページ）。
ページを足すときは NAV に1行足すだけです（ファイルが無い行は自動で飛ばします）。
"""
from pathlib import Path

import streamlit as st

import sister_sites as ss
import ui

ROOT = Path(__file__).parent
MAX_PER_SECTION = 6

st.set_page_config(page_title="体をつくるタンパク質", page_icon="🧬", layout="wide")

# まとまり → [(ファイル, 表示名, アイコン)]
NAV = {
    "🧬 はじめに": [
        ("home.py", "ホーム（教科書の問い）", "🏠"),
    ],
    "📗 教科書 p.14〜15 を動かす": [
        ("pages/1_seibun.py", "体は何でできている？（図1）", "🧪"),
        ("pages/2_amino.py", "アミノ酸は20種類", "🔤"),
        ("pages/3_shoka.py", "消化→吸収→合成（図4）", "🍖"),
        ("pages/4_idenshi.py", "遺伝子→タンパク質（図3）", "🧬"),
    ],
    "📝 教科×情報Ⅰ": [
        ("pages/5_joho1.py", "情報Ⅰとつなげる", "💻"),
        ("pages/6_quiz.py", "確認クイズ", "✅"),
    ],
    "🌾 フィールドワークへ": [
        ("pages/7_field.py", "畑とパン工房につなげる", "🌾"),
    ],
}


def build_nav() -> dict[str, list]:
    nav = {}
    for section, items in NAV.items():
        assert len(items) <= MAX_PER_SECTION, f"「{section}」のページが多すぎます"
        pages = [st.Page(path, title=title, icon=icon, default=(path == "home.py"))
                 for path, title, icon in items if (ROOT / path).exists()]
        if pages:
            nav[section] = pages
    return nav


with st.sidebar:
    st.toggle("やさしい解説を表示（文系向け）", value=True, key=ui.EASY_KEY)
    st.caption("科学と人間生活 第1部 生命の科学 1章A ① 体をつくるタンパク質")
    st.caption("食品（牛肉・魚・大豆・卵・ゼラチン・小麦）の配列は説明用の架空データ。"
               "ヒトのインスリン・ヘモグロビンは実在の配列です。")
    st.divider()
    st.markdown("**🔗 姉妹サイト**")
    _b = ss.SITES["bakery"]
    st.link_button(f"{_b['icon']} {_b['name']} ↗", ss.url("bakery") or _b["repo"], width="stretch")
    st.caption(_b["role"])

st.navigation(build_nav()).run()
