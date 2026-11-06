"""✅ 確認クイズ（回答はこの画面の中だけで使い、保存しない）"""
import streamlit as st

import tanpaku_core as tc
import ui

ui.hero("まとめ", "✅ 確認クイズ", "5問で、今日の要点を確かめよう。")
ui.hint("まちがえても大丈夫。解説を読んで、もう一度選び直せます。")

score = answered = 0
for i, (q, opts, ans, exp) in enumerate(tc.QUIZ):
    choice = st.radio(f"Q{i + 1}. {q}", opts, index=None, key=f"quiz_{i}")
    if choice is None:
        continue
    answered += 1
    if choice == ans:
        score += 1
        st.success(f"正解！ {exp}")
    else:
        st.error(f"ざんねん。正解は「{ans}」。{exp}")

st.divider()
st.metric("スコア", f"{score} / {len(tc.QUIZ)}", f"回答済み {answered} 問")
if score == len(tc.QUIZ):
    st.balloons()
    st.success("全問正解！ 『食べ物は材料、設計図は自分の遺伝子』を説明できるようになった。")
