"""🌾 畑とパン工房につなげる ─ 姉妹サイト「スマートパン屋農家」でのフィールドワークへの橋渡し"""
import pandas as pd
import streamlit as st

import backbone as bb
import sister_sites as ss
import tanpaku_core as tc
import ui

ui.hero("教室 → 現場（フィールドワーク）", "🌾 畑とパン工房につなげる",
        "教室で確かめた『食べ物は材料、設計図は自分の遺伝子』を、パン用小麦の畑と工房で見に行こう。")
ui.hint("このページは、姉妹サイト「スマートパン屋農家」でのフィールドワークの事前学習です。"
        "① 計算する（教室） → ② 見える化する（教室） → ③ 自分で判断する（現場） の3段目を、畑で行います。")

st.subheader("① 畑からパン、そして体へ ─ タンパク質の旅")
st.table(pd.DataFrame({
    "段": ["🌱 畑", "🌾 小麦粉", "🍞 パン工房", "🍽️ 食べる", "🧬 体の中"],
    "起きていること": [
        "小麦は自分の遺伝子にしたがって、種子にタンパク質をためる",
        "パン用小麦（強力粉）はタンパク質が多い。主なものはグルテンのもとになるタンパク質",
        "こねるとグルテンの網ができ、酵母が出したガスを閉じこめてパンがふくらむ",
        "パンのタンパク質は消化されて、バラバラのアミノ酸として吸収される",
        "ヒトの遺伝子の順にアミノ酸を並べ直し、ヒトのタンパク質をつくる",
    ],
    "姉妹サイトで見るもの": [
        "パン用小麦（ミナミノカオリ）の畑・播種の適期",
        "小麦粉（たんぱく質・でんぷん）とパンの焼き色",
        "天然酵母の発酵（酵母もタンパク質＝酵素で発酵する）",
        "小麦アレルギーへの配慮（当日の重要管理点）",
        "─（ここは教室で計算したこと）",
    ],
}))

st.subheader("② 計算する：パンだけで、ヒトのタンパク質はつくれる？（アミノ酸の補足効果）")
ui.hint("小麦のタンパク質はグルタミン（Q）とプロリン（P）が多く、必須アミノ酸のリシン（K）が少ない。"
        "ほかの食べ物と組み合わせると、足りない分を補い合える。これを『アミノ酸の補足効果』という。")
c1, c2 = st.columns([2, 1])
target_name = c1.selectbox("つくるヒトのタンパク質", list(tc.HUMAN_PROTEINS), index=2)
times = c2.slider("食べる回数", 1, 10, 3, key="field_times")
target = tc.HUMAN_PROTEINS[target_name]
st.dataframe(pd.DataFrame(tc.complement_table(target, times)), hide_index=True, width="stretch")
ui.reading_card(
    axis="食べ合わせ × 合成できるか（足りないアミノ酸と個数）", unit="個",
    control="小麦の量・食べる回数・つくるタンパク質はそろえ、組み合わせる相手だけを変える",
    can="小麦だけではリシンが足りず、大豆や卵と組み合わせると補える",
    cannot="実際の小麦のリシンが0であること（差を見やすくするため0にしている）。パンが体に悪いこと（比べていない）",
    protocols=["P3", "P2"], material="補足効果の表")

wheat = tc.FOODS[tc.WHEAT]
m1, m2, m3 = st.columns(3)
m1.metric("小麦のQ（グルタミン）", f"{wheat.count('Q') / len(wheat):.0%}")
m2.metric("小麦のP（プロリン）", f"{wheat.count('P') / len(wheat):.0%}")
m3.metric("小麦のK（リシン）", f"{wheat.count('K') / len(wheat):.0%}", "少ない", delta_color="inverse")
st.caption("小麦の配列は説明用の架空データ。実際の小麦はリシンを少しは含みます（第一制限アミノ酸）。"
           "差を見やすくするため、ここでは0にしています。")

st.subheader("③ 現場で判断する：問いのブリッジ（授業の最後に投げる問い）")
st.markdown("姉妹サイトの「単元 ↔ 調査地」表と同じ単元名でそろえています。")
BRIDGE = pd.DataFrame([
    ("衣料と食品", "小麦粉（たんぱく質・でんぷん）とパンの焼き色",
     "国産のパン用小麦は、なぜパンがよくふくらむのか。タンパク質の量を比べるには何を測ればよいか"),
    ("ヒトの生命現象", "小麦アレルギーへの配慮・作業の休憩",
     "同じパンを食べても、体に合わない人がいるのはなぜか。工房ではどんな表示や工夫をしているか"),
    ("微生物とその利用", "天然酵母の発酵",
     "酵母は、自分の遺伝子でつくった酵素で何を分解しているのか。温度を変えるとふくらみ方はどう変わるか"),
], columns=["単元", "現場で見るもの", "問いの例"])
st.dataframe(BRIDGE, hide_index=True, width="stretch")
assert set(BRIDGE["単元"]) <= set(ss.UNITS)  # 共通語彙からはみ出さない

unit = st.selectbox("事前学習でつなぐ単元", BRIDGE["単元"].tolist())
with st.container(border=True):
    st.markdown("**つながる教材**")
    ss.render_unit(unit, "tanpaku")
    q = st.text_area("フィールドワークで確かめたい問い（自分の言葉で）", key="field_q",
                     placeholder="例：強力粉と薄力粉で、こねたときの伸び方はどれくらい違うのか")
    if q:
        st.download_button("問いをテキストで保存", q.encode("utf-8"), "フィールドワークの問い.txt", "text/plain")

st.subheader("④ 測る前に予想を書く（仮説シート項目5「予想グラフ」）")
ui.hint("現場で測る前に『こうなるはず』を数字で書いておく。当日の実測とのずれ（δ）が、いちばんの学びどころになる。"
        "鳥に食べられた・倒れたなどの『失敗』も消さずに野帳に書こう。")
plan = st.data_editor(pd.DataFrame([{"場面": e["場面"], "プロトコル": e["protocol"], "予想": None, "単位": e["unit"]}
                                    for e in bb.FW_EPISODES]),
                      hide_index=True, width="stretch", key="fw_plan",
                      column_config={"予想": st.column_config.NumberColumn("予想（数字）"),
                                     "プロトコル": st.column_config.SelectboxColumn(options=list(bb.PROTOCOLS))})
if plan["予想"].notna().all():
    plan["実測（当日に記入）"] = ""
    st.download_button("予想シートをCSVで保存（野帳に貼る）", plan.to_csv(index=False).encode("utf-8-sig"),
                       "FW予想シート.csv", "text/csv")
else:
    st.caption("4つの場面すべてに予想を書くと、野帳に貼るCSVを保存できます。")

st.info("小麦アレルギーは、小麦のタンパク質に体の免疫がはたらきすぎて起こる反応です。"
        "フィールドワークでは、受け入れ先と学校が事前に参加者の状況を確認し、"
        "当日の重要管理点（アレルゲン）として管理します。", icon="⚠️")

ss.render("tanpaku", "field")

ui.next_move_tag("field")
