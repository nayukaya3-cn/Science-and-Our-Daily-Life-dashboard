"""ホーム：教科書の問いと、このダッシュボードの歩き方"""
import streamlit as st

import backbone as bb
import sister_sites as ss
import tanpaku_core as tc
import ui

ui.hero("科学と人間生活 ｜ 1章A タンパク質 → 2章B 微生物と食生活 → 終章 課題研究",
        "❓ 動物の肉を食べても、その動物にならないのはなぜだろうか",
        "教科書 p.14〜19・p.44〜49・p.182〜 の図と文章を、Python で動かして確かめます。"
        "「① 計算する → ② 見える化する → ③ 自分で判断する」の3段で進み、"
        "最後は「🚀 次の一手」で、答えをこれからの人生戦略・戦術に持ち出します。")

c1, c2, c3 = st.columns(3)
c1.metric("細胞の水", "67 %", "教科書の値")
c2.metric("水を除いたタンパク質", f"{tc.ratio_without(tc.CELL)['タンパク質']:.0f} %", "主成分")
c3.metric("アミノ酸の種類", f"{len(tc.AMINO)} 種", f"うち必須 {sum(v[1] for v in tc.AMINO.values())} 種")

st.subheader("🗺️ 高いところから見る：3つの単元は、2本の背骨でつながっている")
st.graphviz_chart("""
digraph G {
  rankdir=LR; node [shape=box, style="rounded,filled", fontname="sans-serif", fontsize=11, color="#4a6a8a", margin="0.35,0.12"];
  edge [color="#4a6a8a", fontsize=10];
  a [label="1章A タンパク質\n肉を食べても牛にならない", fillcolor="#e3efd6"];
  b [label="2章B 微生物と食生活\nヨーグルトと牛乳の味の違い", fillcolor="#e3efd6"];
  c [label="終章 課題研究\nどうして○○は△△なのか", fillcolor="#fdecc8"];
  f [label="❷ フィールドワーク\n播いた麦で、パンを焼くまで", fillcolor="#e4ecf5"];
  j [label="情報Ⅰ・共通テスト\n図表の読解・傾き・場合の数", fillcolor="#e4ecf5"];
  a -> b [label="分解→部品→組み直し\n（タンパク質→アミノ酸）"];
  b -> c [label="対照実験・予想→ずれ\n（パスツール・実験2）"];
  c -> f [label="自分の問いで1周"];
  f -> c [style=dashed, label="ふり返る"];
  a -> j; b -> j; c -> j [label="読解カード・P1〜P5"];
}
""", width="stretch")
st.markdown("**背骨1（内容）**：取り込んだものは部品に分解され、だれかの設計図で組み直される"
            "（ヒトの消化も、しょう油のうま味も、パンのふくらみも）。  \n"
            "**背骨2（方法）**：先に予想 → 条件を1つだけ変えて比べる → ずれを見る → ふり返って直す"
            "（終章の『課題研究の進め方』そのもの）。")

st.subheader("このダッシュボードの歩き方")
st.table({
    "ページ": ["🧪 体は何でできている？", "🔤 アミノ酸は20種類", "🍖 食べる→消化→吸収→合成",
             "🧬 遺伝子→タンパク質", "🦠 微生物と発酵・実験2", "💻 情報Ⅰとつなげる", "✅ 確認クイズ",
             "🌾 畑とパン工房につなげる", "🧭 終章 課題研究", "🚀 次の一手"],
    "教科書": ["図1 細胞の成分", "アミノ酸は20種類", "図4 タンパク質の分解", "p.18〜19 図9・図10",
             "p.44〜49 図16・図17・実験2", "─", "─", "フィールドワークの事前学習", "p.182〜188・資料編", "─"],
    "やってみること": ["水を除くスイッチ", "必須アミノ酸を探す", "食べ物を変えて比べる（対照実験）",
                  "塩基を1文字書きかえる・全部試す", "フラスコの条件を変える・温度と速さ（傾き）",
                  "並べ方の数とビット数", f"{len(tc.QUIZ)}問＋問題づくり",
                  "パンだけで足りる？（アミノ酸の補足効果）", "問い→仮説→報告書・盲斑の実験",
                  "人生戦略・戦術のヒント集と『次の一手シート』"],
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

ui.next_move_tag("home")
