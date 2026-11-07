"""🚀 次の一手：今後の人生戦略・戦術を立案する際のヒント集

出発点の問い「❓ 動物の肉を食べても、その動物にならないのはなぜだろうか」の答えを、
戦略（何を選び、何を捨てるか）と戦術（今週なにをするか）に持ち出す最終ページ。
入力はこの画面の中だけで使い、保存も送信もしない（シートは手元へのダウンロードだけ）。
"""
import plotly.graph_objects as go
import streamlit as st

import guard
import next_move as nm
import ui

ui.hero("出発点の問い ➡︎ 次の一手", "🚀 次の一手：今後の人生戦略・戦術を立案する際のヒント集",
        "教科書の問いから確かめた答えを、自分のこれからの選び方（戦略）と、今週の動き方（戦術）に持ち出そう。")

c1, c2, c3 = st.columns([5, 1, 5])
with c1.container(border=True):
    st.markdown("**❓ 出発点の問い**")
    st.markdown("動物の肉を食べても、その動物にならないのはなぜだろうか")
c2.markdown("<div style='font-size:2.2rem;text-align:center;padding-top:1.2rem'>➡︎</div>", unsafe_allow_html=True)
with c3.container(border=True):
    st.markdown("**💡 たどり着いた答え（原理）**")
    st.markdown(f"**{nm.PRINCIPLE}**。食べ物は『材料』、設計図は『自分の遺伝子』。")
ui.hint("この原理は、勉強や進路にもそのまま使える。人の話・本・SNS・体験記はすべて『材料』。"
        "そのまま着るのではなく、分解して、自分の設計図（目的・価値観）で組み直す。")

st.markdown("**戦略**＝何を選び、何を捨てるか（長い目で）　／　**戦術**＝今週、具体的に何をするか（手順）")

ui.reading_card(
    axis="生物で確かめた事実 × 自分の生活の場面", unit="─（数字ではなく『考え方の型』を持ち出す）",
    control="持ち出すのは『型』だけ。生物の細かい中身（どのアミノ酸か等）は持ち出さない",
    can="同じ考え方の型（分解して組み直す・不足を見つける・組み合わせる・予想とずれ）が、ほかの場面でも使える",
    cannot="生物の事実が、人生の正解を決めること（ヒントは比喩。決めるのは自分）",
    protocols=["P4", "P3"], material="このページのヒント集")

st.subheader("① いまの自分に合わせる")
s1, s2 = st.columns(2)
stage = s1.selectbox("いまの時期", list(nm.STAGES), index=1)
concern = s2.selectbox("いちばんの悩み", nm.CONCERNS)
w = nm.STAGES[stage]

fig = go.Figure()
fig.add_bar(y=["時間の配分"], x=[w * 100], orientation="h", name="探索（新しいことを試す）",
            marker_color="#7aa95c", text=[f"探索 {w:.0%}"], textposition="inside")
fig.add_bar(y=["時間の配分"], x=[(1 - w) * 100], orientation="h", name="活用（できることで得点する）",
            marker_color="#4a6a8a", text=[f"活用 {1 - w:.0%}"], textposition="inside")
fig.update_layout(barmode="stack", height=130, margin=dict(t=10, b=10, l=10, r=10), showlegend=False,
                  xaxis=dict(range=[0, 100], ticksuffix="%"), yaxis=dict(visible=False))
st.plotly_chart(fig, width="stretch")
st.caption("探索＝畑やパン工房のように、まだ知らない場面を経験する。活用＝共通テストのように、身につけた型で確実に点を取る。"
           "配分は時期ごとの目安（比喩）で、決まった正解ではない。")

st.subheader("② ヒント集（あなたの状況に合う順）")
ranked = nm.rank_hints(stage, concern)
for i, h in enumerate(ranked):
    head = f"{h['icon']} {h['title']}　｜ 出どころ：{h['page']}"
    with st.expander(("⭐ " if i < 3 else "") + head, expanded=i < 3):
        st.markdown(ui.badges([h["p"]]), unsafe_allow_html=True)
        st.markdown(f"**🔬 生物での事実**：{h['fact']}")
        st.markdown(f"**🧭 戦略**：{h['strategy']}")
        st.markdown(f"**🛠️ 戦術**：{h['tactics']}")

st.subheader("③ 次の一手シートを書く")
ui.hint("全部を書かなくてよい。1つでも書けたら、それが『次の一手』。来週、予想とのずれを確かめよう。")
top = ranked[0]
rows = {
    "戦略：これから選ぶこと／捨てること": st.text_area(max_chars=guard.MAX_TEXT, label="🧭 戦略：これから選ぶこと／捨てること", key="nm_strategy",
                                         placeholder=f"例：{top['strategy']}"),
    "必須アミノ酸：自分だけではつくれず、外から補うもの": st.text_input(max_chars=guard.MAX_TEXT, label=
        "🔤 自分の『必須アミノ酸』（自分だけでは身につかず、外から補うもの）", key="nm_essential",
        placeholder="例：英語の長文を読む速さ → 先生に添削してもらう"),
    "補足効果：組み合わせる相手・教科": st.text_input(max_chars=guard.MAX_TEXT, label="🫘 組み合わせる相手・教科（補足効果）", key="nm_partner",
                                          placeholder="例：情報Ⅰが得意な友だちと、理科基礎のグラフ問題を教え合う"),
    "戦術：今週やること（1つだけ）": st.text_input(max_chars=guard.MAX_TEXT, label="🛠️ 戦術：今週やること（1つだけ）", key="nm_tactics",
                                         placeholder=f"例：{top['tactics']}"),
    "予想：来週どうなっているはずか": st.text_input(max_chars=guard.MAX_TEXT, label="🎯 予想：来週どうなっているはず？（数字があればなおよい）", key="nm_predict",
                                         placeholder="例：模試の第2問が 6点 → 9点"),
}
if any(rows.values()):
    st.download_button("次の一手シートをテキストで保存", guard.clean_text(nm.plan_sheet(stage, concern, rows), 10000).encode("utf-8"),
                       "次の一手シート.txt", "text/plain")
else:
    st.caption("1つ書くと、シートを保存できます（保存は手元へのダウンロードだけ）。")

with st.container(border=True):
    st.markdown("**⚠️ 比喩としての限界**")
    st.markdown("- 体はアミノ酸を機械的に並べるが、人は**自分で設計図を書き直せる**。目的や価値観は変えてよい。\n"
                "- AIは何百万回も練習して上達するが、人は**数回の濃い経験**から学べる。だから1回の体験を大切に記録する。\n"
                "- 『面白い』という気持ちは、点数より強い原動力になる。ヒントに合わない自分の感覚も、大事な材料。")
