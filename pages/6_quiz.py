"""✅ 確認クイズ（回答はこの画面の中だけで使い、保存しない）

背骨との対応
  - 各問に P1〜P5 のラベル → P別の正答数を出す（年1回の共通テスト得点を、途中の評価で補う＝報酬の整形）
  - P3・P4 は正解したかではなく「なぜ言えないか／なぜそう言えるか」を書かせる（丸暗記の近道をつぶす）
  - 最後に転移チェックと、自分で共通テスト型問題をつくる欄
"""
import pandas as pd
import streamlit as st

import backbone as bb
import tanpaku_core as tc
import ui

ui.hero("まとめ", "✅ 確認クイズ", f"{len(tc.QUIZ)}問で、今日の要点を確かめよう。")
ui.hint("まちがえても大丈夫。解説を読んで、もう一度選び直せます。"
        "『比較を疑う（P3）』『模型で考える（P4）』の問題は、答えを選んだあと理由を1行で書こう。")

score = answered = 0
by_p: dict[str, list[int]] = {p: [0, 0] for p in bb.PROTOCOLS}   # [正解, 回答済み]
for i, item in enumerate(tc.QUIZ):
    st.markdown(ui.badges([item["p"]]), unsafe_allow_html=True)
    choice = st.radio(f"Q{i + 1}. {item['q']}", item["opts"], index=None, key=f"quiz_{i}")
    if choice is None:
        continue
    answered += 1
    by_p[item["p"]][1] += 1
    if choice == item["ans"]:
        score += 1
        by_p[item["p"]][0] += 1
        st.success(f"正解！ {item['exp']}")
    else:
        st.error(f"ざんねん。正解は「{item['ans']}」。{item['exp']}")
    if item["p"] in ("P3", "P4"):
        st.text_input("なぜそう言える？／なぜ言えない？（自分の言葉で1行）", key=f"quiz_why_{i}",
                      placeholder="例：比べていない／測っていない範囲／第3の要因がある／相関だけで因果ではない")

st.divider()
st.metric("スコア", f"{score} / {len(tc.QUIZ)}", f"回答済み {answered} 問")
st.dataframe(pd.DataFrame([{"プロトコル": bb.p_label(p), "言い換え": bb.PROTOCOLS[p][1],
                            "正解 / 回答": f"{c} / {n}" if n else "─"} for p, (c, n) in by_p.items()]),
             hide_index=True, width="stretch")
st.caption("点数だけでなく、どの『考え方の型』でつまずいたかを見る。P3・P4 は書いた理由も合わせてふり返る。")
if score == len(tc.QUIZ):
    st.balloons()
    st.success("全問正解！ 『食べ物は材料、設計図は自分の遺伝子』を説明できるようになった。")

st.subheader("🔁 転移チェック")
st.text_input("Q8（ゼラチンの対照実験）は、畑やパン工房のどの場面と同じ『型』？（1行）", key="transfer_q8",
              placeholder="例：3列の小麦で、肥料だけを変えて育ち方を比べる場面")
ui.hint("答えられたら、教室の考え方が現場でも使える形になっている（転移が起きている）。")

st.subheader("✍️ 共通テスト型問題をつくろう")
ui.hint("グラフや表を1つ選び、『言えること』を1つ、『言えないこと』を3つ書く。言えないことには理由をつける。"
        "丸暗記では選んでしまうような誤答をつくれたら、本番のひっかけも見抜ける。")
src = st.selectbox("使う図・表", ["図1 細胞の成分（円グラフ）", "アミノ酸のたくわえ（棒グラフ）",
                                "対照実験の表（食べ物を1種類ずつ）", "総当たりの結果（同義・置換・短縮）",
                                "20ⁿ のグラフ", "小麦の補足効果の表"])
right = st.text_input("言えること（正解）", key="mk_right")
wrong = [(st.text_input(f"言えないこと {k}", key=f"mk_wrong_{k}"),
          st.text_input(f"　└ なぜ言えない？ {k}", key=f"mk_why_{k}")) for k in (1, 2, 3)]
if right and all(w for w, _ in wrong):
    text = f"資料：{src}\n正解：{right}\n" + "".join(f"誤答{k}：{w}（なぜ言えないか：{y or '未記入'}）\n"
                                                 for k, (w, y) in enumerate(wrong, 1))
    st.download_button("つくった問題をテキストで保存", text.encode("utf-8"), "自作問題.txt", "text/plain")

ui.next_move_tag("quiz")
