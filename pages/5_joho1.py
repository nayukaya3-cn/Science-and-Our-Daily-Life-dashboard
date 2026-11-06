"""💻 情報Ⅰとつなげる：タンパク質は『20種類の文字で書かれた文章』"""
import math

import pandas as pd
import plotly.express as px
import streamlit as st

import tanpaku_core as tc
import ui

ui.hero("教科×情報Ⅰ", "💻 タンパク質は『20種類の文字で書かれた文章』",
        "場合の数・情報量（ビット）・文字列・辞書。情報Ⅰの道具で、生物のしくみを読み直そう。")
ui.hint("アミノ酸が20種類あると、並べ方の数は爆発的に増える。"
        "これで、約10万種類のタンパク質を区別できる理由がわかる。")

n = st.slider("アミノ酸の個数 n", 1, 100, 30)
c1, c2, c3 = st.columns(3)
c1.metric("並べ方の数 20ⁿ", f"約 10^{tc.combos_log10(n):.0f} 通り")
c2.metric("情報量", f"約 {tc.bits(n):.0f} ビット", f"1個あたり {math.log2(20):.2f} ビット")
c3.metric("ヒトのタンパク質の種類", "約 10万 ≒ 10^5")

ns = list(range(1, 101))
fig = px.line(x=ns, y=[tc.combos_log10(k) for k in ns],
              labels={"x": "アミノ酸の個数 n", "y": "並べ方の数（10の何乗か）"})
fig.add_hline(y=5, line_dash="dash", annotation_text="ヒトのタンパク質 約10万種類（10^5）")
fig.add_vline(x=n, line_color="red")
fig.update_layout(height=340, margin=dict(t=20))
st.plotly_chart(fig, width="stretch")
st.caption("アミノ酸が4個並ぶだけで 20⁴＝16万通り。10万種類を区別するには十分。")

st.subheader("生物と情報の対応表")
st.table(pd.DataFrame({
    "生物（科学と人間生活）": ["アミノ酸20種類", "タンパク質（アミノ酸の鎖）", "消化（鎖を切る）",
                        "吸収（アミノ酸のたくわえ）", "遺伝子（DNA）", "遺伝暗号表（コドン→アミノ酸）",
                        "食べ物を1種類ずつ変えて比べる"],
    "情報Ⅰ・プログラミング": ["文字の種類（文字コード）", "文字列（配列）", "文字列を1文字ずつ分解",
                        "種類ごとの個数を数える（辞書・Counter）", "設計図となるデータ",
                        "対応表（辞書）による変換", "条件をそろえた比較（対照実験・交絡の統制）"],
}))

st.subheader("実際のコード（tanpaku_core.py より）")
st.code('''from collections import Counter
beef = "AKELMWNEGG"                      # 牛肉のタンパク質（文字列）
pool = Counter(beef)                     # 消化・吸収：並び順を捨て、個数だけ数える
CODON = {"UUU": "F", "GUU": "V", ...}    # 遺伝暗号表（辞書）
gene = "AUGUUUGUU..."                    # ヒトの遺伝子
protein = "".join(CODON[gene[i:i+3]] for i in range(3, len(gene), 3))''', language="python")

with st.expander("✍️ DNCL（共通テスト用プログラム表記）で書くと"):
    st.code('''タンパク質 = ""
i を 4 から 要素数(遺伝子) - 2 まで 3 ずつ増やしながら繰り返す:
    コドン = 部分文字列(遺伝子, i, 3)
    もし 暗号表[コドン] == "終止" ならば:
        繰り返しを抜ける
    タンパク質 = タンパク質 + 暗号表[コドン]
表示する(タンパク質)''', language="text")
    st.caption("先頭の3文字（開始コドン AUG）の次から、3文字ずつ読み進める。")
