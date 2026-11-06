"""🧬 遺伝子 → タンパク質（教科書 p.18〜19 ③ タンパク質の合成：図9・図10）"""
import html

import pandas as pd
import plotly.express as px
import streamlit as st

import sister_sites as ss
import tanpaku_core as tc
import ui

ui.hero("教科書 p.15・p.18〜19（③ タンパク質の合成 図9・図10）", "🧬 遺伝子がアミノ酸配列を決める",
        "DNAの文字を3つずつ読むと、アミノ酸の並び順が決まる。1文字書きかえるとどうなる？")
ui.hint("DNAの文字（A・T・G・C）を3つずつ区切ると、1つのアミノ酸に対応する（この3文字を『コドン』という）。")

ui.reading_card(
    axis="DNAの塩基の位置 × できたアミノ酸の並び", unit="塩基は『文字』、コドンは『3文字ひと組』",
    control="書きかえるのは1か所の1文字だけ。ほかの塩基はそろえたまま",
    can="1文字の書きかえで、アミノ酸が変わらないことも、1個変わることも、途中で止まることもある",
    cannot="実際の遺伝子でも同じ割合になる（このアプリの遺伝子は、説明用に代表コドンで組み立てたもの）",
    protocols=["P1", "P4"], material="DNA の文字列とコドン表")

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

if st.toggle("相手の鎖（鋳型鎖）も表示する：教科書 図10 の相補性", value=False):
    tmpl = tc.template_strand(dna)
    st.markdown(f"<code style='font-size:15px'>{' '.join(tmpl[i:i + 3] for i in range(0, len(tmpl), 3))}</code>"
                "　← 鋳型鎖（A↔T、G↔C で向かい合う）", unsafe_allow_html=True)
    st.caption("転写では、鋳型鎖の塩基に RNA の塩基が相補的に結合する（A→U、T→A、G→C、C→G）。"
               "だからできる mRNA は、上の遺伝子の T を U に置きかえた並びと同じになる。")
    assert tc.transcribe_from_template(tmpl) == tc.transcribe(dna)

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

st.subheader("🧮 1文字の書きかえを『全部』試すと？（総当たり）")
spec = tc.mutation_spectrum(tc.HUMAN_PROTEINS[pname])
total = sum(spec.values())
rec = ui.predict(f"syn_{list(tc.HUMAN_PROTEINS).index(pname)}",
                 f"**{pname.split('（')[0]}の遺伝子で、1文字の書きかえ（全{total}通り）のうち、"
                 "アミノ酸が変わらない『同義』は何％？**", spec["同義"] / total * 100, "％", protocol="P4", value=50.0)
if rec is None:
    st.caption("予想を確定すると、総当たりの結果（同義・置換・短縮の割合）が表示されます。")
else:
    sdf = pd.DataFrame({"結果": list(spec), "件数": list(spec.values())})
    sdf["割合"] = (sdf["件数"] / total * 100).round(1).astype(str) + "%"
    fig = px.bar(sdf, x="結果", y="件数", text="割合", color="結果",
                 color_discrete_map={"同義": "#4c9a5e", "置換": "#d9a400", "短縮": "#d62728"})
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=320, margin=dict(t=30, b=10), showlegend=False)
    st.plotly_chart(fig, width="stretch")
    ui.hint("プログラムなら、1か所ずつ・3通りずつ全部試せる（情報Ⅰの『総当たり』）。"
            "『同義』の多くは3文字目の書きかえ。同じアミノ酸を表すコドンが複数あるため。")

with st.expander("📖 遺伝暗号表（64コドン）を見る"):
    rows = [{f"2文字目={b}": f"{a}{b}{c} {tc.CODON[a + b + c]}" for b in tc.BASES}
            for a in tc.BASES for c in tc.BASES]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.caption("*は終止コドン。AUG（メチオニン）は開始の合図にもなる。"
               "※このアプリの遺伝子は、説明用に各アミノ酸の代表コドンで組み立てたもの。")

ss.render("tanpaku", "idenshi")
