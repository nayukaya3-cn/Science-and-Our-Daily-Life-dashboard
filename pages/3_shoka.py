"""🍖 食べる → 消化 → 吸収 → 合成（教科書 図4）"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import tanpaku_core as tc
import ui

ui.hero("教科書 p.15 図4", "🍖 食べる → 消化 → 吸収 → 合成",
        "食べ物を選んで、体の中でタンパク質がどう作り直されるかを確かめよう。")
ui.hint("食べたタンパク質は、消化酵素によって鎖が切られ、バラバラのアミノ酸になってから小腸で吸収される。"
        "このとき『並び順』の情報は消える。体は自分の遺伝子にしたがって並べ直す。")

c1, c2, c3 = st.columns([2, 1, 2])
menu = c1.multiselect("① 食べるもの（複数可）", list(tc.FOODS), default=[list(tc.FOODS)[0]])
times = c2.slider("食べる回数", 1, 10, 3)
target_name = c3.selectbox("③ 体でつくるヒトのタンパク質", list(tc.HUMAN_PROTEINS))

st.session_state.setdefault("digest_seed", 0)
if st.button("🔄 もう一度消化する（バラバラの順番が変わる）"):
    st.session_state.digest_seed += 1
seed = st.session_state.digest_seed

if not menu:
    st.warning("食べるものを1つ以上選んでください。")
    st.stop()

food0 = tc.FOODS[menu[0]]
st.markdown(f"**消化前：{menu[0]} のタンパク質（先頭24個）** ― 並び順に意味がある")
ui.chain(food0[:24])
st.markdown("⬇️ **消化**（消化酵素が鎖を切る）")
ui.chain(tc.digest(food0[:24], seed), scatter=True, seed=seed)
st.caption("並び順はバラバラ。残るのは『どのアミノ酸が何個あるか』だけ。")

pool = tc.absorb(menu, times)
target = tc.HUMAN_PROTEINS[target_name]
need = pd.Series({a: target.count(a) for a in tc.AMINO})

st.markdown("⬇️ **吸収** → 体の中の『アミノ酸のたくわえ（プール）』")
labels = [f"{a} {tc.AMINO[a][0]}" for a in tc.AMINO]
fig = go.Figure()
fig.add_bar(x=labels, y=[pool[a] for a in tc.AMINO], name="たくわえ",
            marker_color=[tc.COLOR[a] for a in tc.AMINO])
fig.add_scatter(x=labels, y=need.values, name="合成に必要な数", mode="markers",
                marker=dict(symbol="line-ew-open", size=26, color="black", line=dict(width=3)))
fig.update_layout(height=360, margin=dict(t=20, b=10), legend=dict(orientation="h"),
                  yaxis_title="個数")
st.plotly_chart(fig, width="stretch")

st.markdown("⬇️ **合成**（ヒトの遺伝子が決めた順番に並べる）")
protein, short = tc.synthesize(tc.make_gene(target), pool)
if short:
    names = "、".join(f"{tc.AMINO[a][0]}（あと{n}個）" for a, n in short.items())
    st.error(f"材料不足で合成できません：{names}")
    if any(tc.AMINO[a][1] for a in short):
        st.warning("足りないのは**必須アミノ酸**。体内でつくれないので、食べ物を変える必要がある。"
                   "→ ほかの食品を追加してみよう。")
else:
    ui.chain(protein)
    st.success(f"合成成功：{target_name}")

st.subheader("🔬 比べてみよう：食べ物を1種類ずつ変えたら？（対照実験）")
ui.hint("変えるのは『食べ物』だけ。食べる回数とつくるタンパク質はそろえてある（条件の統制）。")
rows = []
for f in tc.FOODS:
    p, s = tc.synthesize(tc.make_gene(target), tc.absorb([f], times))
    rows.append({"食べたもの（1種類だけ）": f, "できたタンパク質": p or "（材料不足）",
                 "ヒトの配列と一致": "✅" if p == target else "—"})
st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

with st.container(border=True):
    st.markdown("### 📝 答え")
    st.markdown("材料が足りれば、**何を食べても、できるのは同じ『ヒトの』タンパク質**。"
                "食べ物の配列（牛らしさ・魚らしさ）は消化の時点で消え、体に残らない。"
                "**食べ物は『材料』、設計図は『自分の遺伝子』。** だから牛肉を食べても牛にはならない。")
