"""ホーム：教科書の問いと、このダッシュボードの歩き方"""
import streamlit as st

import backbone as bb
import sister_sites as ss
import tanpaku_core as tc
import ui

ui.hero("科学と人間生活 ｜ 第1部 生命の科学 ｜ 1章A タンパク質と遺伝子",
        "❓ 動物の肉を食べても、その動物にならないのはなぜだろうか",
        "教科書 p.14〜15 の図と文章を、Python で動かして確かめます。"
        "「① 計算する → ② 見える化する → ③ 自分で判断する」の3段で進みます。")

c1, c2, c3 = st.columns(3)
c1.metric("細胞の水", "67 %", "教科書の値")
c2.metric("水を除いたタンパク質", f"{tc.ratio_without(tc.CELL)['タンパク質']:.0f} %", "主成分")
c3.metric("アミノ酸の種類", f"{len(tc.AMINO)} 種", f"うち必須 {sum(v[1] for v in tc.AMINO.values())} 種")

st.subheader("このダッシュボードの歩き方")
st.table({
    "ページ": ["🧪 体は何でできている？", "🔤 アミノ酸は20種類", "🍖 食べる→消化→吸収→合成",
             "🧬 遺伝子→タンパク質", "💻 情報Ⅰとつなげる", "✅ 確認クイズ", "🌾 畑とパン工房につなげる"],
    "教科書": ["図1 細胞の成分", "アミノ酸は20種類", "図4 タンパク質の分解", "p.18〜19 図9・図10", "─", "─",
             "フィールドワークの事前学習"],
    "やってみること": ["水を除くスイッチ", "必須アミノ酸を探す", "食べ物を変えて比べる（対照実験）",
                  "塩基を1文字書きかえる・全部試す", "並べ方の数とビット数", f"{len(tc.QUIZ)}問＋問題づくり",
                  "パンだけで足りる？（アミノ酸の補足効果）"],
})

with st.container(border=True):
    st.markdown("### 📝 先に答えを言うと")
    st.markdown("食べ物のタンパク質は、消化されて**順番のないバラバラのアミノ酸**（部品）として吸収される。"
                "体はその部品を、**自分の遺伝子**（ヒトの設計図）が指定する順番に並べ直してタンパク質をつくる。"
                "**食べ物は『材料』、設計図は『自分の遺伝子』。** ほんとうにそうなるか、各ページで確かめよう。")

with st.container(border=True):
    st.markdown("### 🦴 どのページでも同じ『考え方の型』を使う")
    st.markdown("各ページに **🔎 読解カード**（4項目）と **🎯 先に予想しよう** があります。"
                "理科基礎・情報Ⅰ第4問・フィールドワークの野帳でも、同じカードで読みます。")
    st.markdown("  \n".join(f"{i}. {q}" for i, (_, q) in enumerate(bb.READING_CARD, 1)))
    st.markdown(ui.badges(list(bb.PROTOCOLS)), unsafe_allow_html=True)
    st.caption("P1〜P5 は、問題を解くときに使う5つの考え方（手順を回す・資料を読む・比較を疑う・模型で考える・知識で答える）。")

ui.hint("左のメニューを上から順に開くと、授業1コマ分（約50分）の流れになります。"
        "最後の「🌾 畑とパン工房につなげる」が、姉妹サイトでのフィールドワークへの橋渡しです。")

st.subheader("🔗 教材ネットワーク：教室と現場を往復する")
n1, n2 = st.columns(2)
for col, key in ((n1, "tanpaku"), (n2, "bakery")):
    s = ss.SITES[key]
    with col.container(border=True):
        st.markdown(f"### {s['icon']} {s['name']}" + ("（このサイト）" if key == "tanpaku" else ""))
        st.markdown(s["role"])
st.markdown("教室で **① 計算する・② 見える化する** → 現場で **③ 自分で判断する** → "
            "現場で湧いた問いを、教室でもう一度計算する。この往復で、1つの単元が探究に育ちます。")
ss.render("tanpaku", "")
