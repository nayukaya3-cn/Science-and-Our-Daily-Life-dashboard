"""
画面の共通部品（どのページでも同じ見た目にする）
  - hero(): ページ上部の見出しカード
  - hint(): 「やさしい解説」スイッチがONのときだけ出す説明
  - chain_html(): アミノ酸を色つきの丸で並べる（教科書の図3・図4のイメージ）
"""
from __future__ import annotations

import html
import random

import streamlit as st

import tanpaku_core as tc

EASY_KEY = "easy_mode"  # app.py のサイドバーのスイッチと共有

_CSS = """
<style>
.hero {padding: 1.4rem 1.6rem 1.2rem; border-radius: 16px;
       background: linear-gradient(120deg, #e3efd6 0%, #e4ecf5 100%);
       color: #22313f; margin-bottom: 1rem;}
.hero .eyebrow {font-size: .85rem; letter-spacing: .08em; color: #4a6a8a; margin: 0 0 .3rem 0;}
.hero h1 {margin: 0 0 .5rem 0; font-size: 1.7rem; line-height: 1.35; color: #22313f;}
.hero .lead {margin: 0; font-size: 1.02rem; line-height: 1.8;}
.aa {display:inline-block; border-radius:50%; color:#111; text-align:center;
     font-size:12px; font-weight:600; border:1px solid #555; position:relative;}
</style>
"""


def hero(eyebrow: str, title: str, lead: str) -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(
        f"<div class='hero'><p class='eyebrow'>{html.escape(eyebrow)}</p>"
        f"<h1>{html.escape(title)}</h1><p class='lead'>{html.escape(lead)}</p></div>",
        unsafe_allow_html=True,
    )


def easy() -> bool:
    return st.session_state.get(EASY_KEY, True)


def hint(text: str) -> None:
    if easy():
        st.info(text, icon="💡")


def chain_html(seq: str, size: int = 26, gap: int = 2, scatter: bool = False, seed: int = 0) -> str:
    rng = random.Random(seed)
    cells = []
    for a in seq:
        dy = rng.randint(-14, 14) if scatter else 0
        mx = rng.randint(2, 10) if scatter else gap
        name = tc.AMINO.get(a, ("?",))[0]
        cells.append(
            f"<span class='aa' title='{html.escape(name)}' style='width:{size}px;height:{size}px;"
            f"line-height:{size}px;background:{tc.COLOR.get(a, '#ccc')};margin:0 {mx}px;top:{dy}px'>"
            f"{html.escape(a)}</span>")
    return "<div style='line-height:46px;padding:6px 0'>" + "".join(cells) + "</div>"


def chain(seq: str, **kw) -> None:
    st.markdown(_CSS + chain_html(seq, **kw), unsafe_allow_html=True)
