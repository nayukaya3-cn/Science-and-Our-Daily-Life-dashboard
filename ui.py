"""
画面の共通部品（どのページでも同じ見た目にする）
  - hero(): ページ上部の見出しカード
  - hint(): 「やさしい解説」スイッチがONのときだけ出す説明
  - chain_html(): アミノ酸を色つきの丸で並べる（教科書の図3・図4のイメージ）
  - reading_card(): 読解カード（4項目）。全ページで同じ見た目・同じ言葉（背骨①＝共有エンコーダ）
  - predict(): 先に予想 → 答え → ずれ δ（背骨の「TD誤差が出る場面」。ログはセッションの中だけ）
"""
from __future__ import annotations

import html
import random

import streamlit as st

import backbone as bb
import tanpaku_core as tc

API_VERSION = 2          # 画面部品の版。app.py が古いモジュールの読み込みを検出するのに使う
EASY_KEY = "easy_mode"  # app.py のサイドバーのスイッチと共有
TD_LOG_KEY = "td_log"   # 予想と実測のずれ（誤差ログ）。このセッションの中だけ

_CSS = """
<style>
.hero {padding: 1.4rem 1.6rem 1.2rem; border-radius: 16px;
       background: linear-gradient(120deg, #e3efd6 0%, #e4ecf5 100%);
       color: #22313f; margin-bottom: 1rem;}
.hero .eyebrow {font-size: .85rem; letter-spacing: .08em; color: #4a6a8a; margin: 0 0 .3rem 0;}
.hero h1 {margin: 0 0 .5rem 0; font-size: 1.7rem; line-height: 1.35; color: #22313f;}
.hero .lead {margin: 0; font-size: 1.02rem; line-height: 1.8;}
.pbadge {display:inline-block; padding:1px 8px; margin-right:4px; border-radius:10px;
          background:#e4ecf5; color:#22313f; font-size:.8rem; font-weight:600;}
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


def badges(codes: list[str]) -> str:
    return "".join(f"<span class='pbadge'>{html.escape(bb.p_label(c))}</span>" for c in codes)


def reading_card(axis: str, unit: str, control: str, can: str, cannot: str,
                 protocols: list[str], material: str = "このページの図・表") -> None:
    """読解カード（4項目）。問いは先に見せ、答えは自分で考えてから開く。
    理科基礎・情報Ⅰ第4問・フィールドワークの野帳で同じカードを使う（方策を途中で取り替えない）"""
    st.markdown(_CSS, unsafe_allow_html=True)
    answers = (axis, unit, control, f"**言える**：{can}  \n**言えない**：{cannot}")
    with st.container(border=True):
        st.markdown(f"**🔎 読解カード**　{badges(protocols)}", unsafe_allow_html=True)
        st.caption(f"読むもの：{material}。理科基礎・情報Ⅰ第4問・フィールドワークの野帳でも、同じ4項目で読む。")
        st.markdown("  \n".join(f"{i}. {q}" for i, (_, q) in enumerate(bb.READING_CARD, 1)))
        with st.expander("答え合わせ（自分で考えてから開く）"):
            for (name, _), a in zip(bb.READING_CARD, answers):
                st.markdown(f"**{name}**　{a}")


def predict(key: str, question: str, actual: float, unit: str, *, protocol: str = "P4",
            min_value: float = 0.0, max_value: float = 100.0, step: float = 1.0,
            value: float | None = None, fmt: str = "%.0f", field: str = "生命の科学") -> dict | None:
    """先に予想させ、答えとのずれ δ（相対誤差）を見せる。結果はこのセッションの誤差ログに入る（保存・送信しない）"""
    log = st.session_state.setdefault(TD_LOG_KEY, {})
    with st.container(border=True):
        st.markdown(f"**🎯 先に予想しよう**　{badges([protocol])}", unsafe_allow_html=True)
        st.markdown(question)
        with st.form(f"pred_{key}"):
            guess = st.number_input(f"あなたの予想（{unit}）", min_value=min_value, max_value=max_value,
                                    value=min_value if value is None else value, step=step, format=fmt)
            done = st.form_submit_button("予想を確定して答えを見る")
        if done:
            log[key] = bb.log_record("科学と人間生活", field, "-", "予想", protocol, float(guess), float(actual), unit)
            log[key]["question"] = question
        rec = log.get(key)
        if rec is None:
            st.caption("予想を書いてから答えを見ると、ずれ（δ）が学びの入口になる。")
            return None
        d = rec["td_error"]
        c1, c2, c3 = st.columns(3)
        c1.metric("あなたの予想", f"{rec['predicted']:g} {unit}")
        c2.metric("答え", f"{actual:.3g} {unit}")
        c3.metric("ずれ δ", f"{d:.2f}", help="δ＝|答え−予想|÷|予想|。単位がちがう問題どうしでも比べられる")
        if d < 0.1:
            st.success("ほぼ予想どおり。なぜ当てられたのか、根拠を1行で言えるかな？")
        elif d < 0.5:
            st.warning("少しずれた。どこで見込みがちがったか考えよう。")
        else:
            st.error("大きくずれた！ ここがいちばんの学びどころ。")
        st.text_input("ずれの理由（1行：考え方／測り方／自然のばらつき）", key=f"why_{key}")
        return rec
