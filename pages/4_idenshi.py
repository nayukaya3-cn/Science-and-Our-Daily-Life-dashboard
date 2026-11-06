"""🧬 遺伝子 → タンパク質（教科書 図3・タンパク質の合成）"""
import html

import pandas as pd
import streamlit as st

import sister_sites as ss
import tanpaku_core as tc
import ui

ui.hero("教科書 p.15 図3", "🧬 遺伝子がアミノ酸配列を決める",
        "DNAの文字を3つずつ読むと、アミノ酸の並び順が決まる。1文字書きかえるとどうなる？")
ui.hint("DNAの文字（A・T・G・C）を3つずつ区切ると、1つのアミノ酸に対応する（この3文字を『コドン』という）。")

pname = st.selectbox("遺伝子を選ぶ", list(tc.HUMAN_PROTEINS))
original_dna = tc.make_gene(tc.HUMAN_PROTEINS[pname])
original_protein, _ = tc.translate(original_dna)

c1, c2, c3 = st.columns([2, 1, 1])
pos = c1.slider("書きかえる位置（何番目の塩基？）", 4, len(original_dna) - 3, 10)
new_base = c2.selectbox("書きかえる塩基", list("ATGC"), index=1)
do_mutate = c3.toggle("書きかえる（突然変異）", value=False)

dna = tc.mutate(original_dna, pos, new_base) if do_mutate else original_dna
protein, codons = tc.translate(dna)

st.markdown("**DNA（遺伝子）**")
groups = []
for i in range(len(dna) // 3):
    chars = []
    for j, ch in enumerate(dna[3 * i:3 * i + 3]):
        hit = do_mutate and 3 * i + j + 1 == pos
        chars.append(f"<b style='color:#d62728'>{ch}</b>" if hit else html.escape(ch))
    groups.append("".join(chars))
st.markdown(f"<code style='font-size:15px'>{' '.join(groups)}</code>", unsafe_allow_html=True)

st.markdown("⬇️ **転写**（T → U に置きかえて mRNA に） ⬇️ **翻訳**（3文字ずつアミノ酸へ）")
cdf = pd.DataFrame([{"番号": i + 1, "コドン": c, "アミノ酸": a,
                     "名前": "終止" if a == "*" else tc.AMINO.get(a, ("?",))[0]}
                    for i, (c, a) in enumerate(codons)])
st.dataframe(cdf.set_index("番号").astype(str).T, width="stretch")
st.markdown("**できたタンパク質**")
ui.chain(protein)

if do_mutate:
    kind, diff = tc.classify_mutation(original_protein, protein)
    if kind == "同義":
        st.success("アミノ酸は変わらなかった！（同じアミノ酸を表すコドンが複数あるため）")
    elif kind == "短縮":
        st.error(f"途中で終止コドンになり、タンパク質が短くなった"
                 f"（{len(original_protein)}個 → {len(protein)}個）。")
    else:
        st.warning(f"{'・'.join(map(str, diff))}番目のアミノ酸が変わった。"
                   "並び順が変わると、はたらきが変わることがある。")

with st.expander("📖 遺伝暗号表（64コドン）を見る"):
    rows = [{f"2文字目={b}": f"{a}{b}{c} {tc.CODON[a + b + c]}" for b in tc.BASES}
            for a in tc.BASES for c in tc.BASES]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.caption("*は終止コドン。AUG（メチオニン）は開始の合図にもなる。"
               "※このアプリの遺伝子は、説明用に各アミノ酸の代表コドンで組み立てたもの。")

ss.render("tanpaku", "idenshi")
