"""🤝 特別支援学校版「科学と人間生活」（作業学習・体験実習連動）

同じ背骨（読解カード・P1〜P5）を、絵カード「みる・はかる・くらべる・つたえる」に置きかえて使う。
このページは生徒の名前・写真・障害に関する情報を入力させない。入力は保存も送信もしない。
"""
import pandas as pd
import streamlit as st

import backbone as bb
import guard
import tokushi_core as tk
import ui

ui.hero("学校に合わせて使う ｜ 特別支援学校 高等部（作業学習・体験実習とつなぐ）",
        "🤝 理科で『なぜ』を学び、その週の作業学習で『やってみる』",
        "ゴールは共通テストではなく、働く場面・暮らしの場面で使えること。"
        "同じ型（みる・はかる・くらべる・つたえる）を、理科・作業学習・体験実習の3つの場面でくり返す。")

st.info("**先生方へ**：このページには、生徒の名前・顔写真・障害に関する情報を入力しないでください。"
        "記録表は『カード × 場面 × 支援の量』だけを扱い、手元へのダウンロード以外には保存も送信もしません。", icon="🔒")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["① 位置づけと4枚カード", "② 年間計画", "③ 授業例：酵母がふくらませる",
                                        "④ 評価：支援の量で見る5段階", "⑤ 支援・安全・次の一手"])

# ── ① 位置づけ ─────────────────────────────
with tab1:
    st.markdown("#### 学校の種類と、理科の扱い")
    st.table(pd.DataFrame(tk.SCHOOL_TYPES, columns=["学校の種類", "理科の扱い", "このカリキュラムの使い方"]).set_index("学校の種類"))
    st.markdown("#### 高校向けの元版から変えた点")
    st.table(pd.DataFrame(tk.CHANGES, columns=["項目", "元版（高校）", "特別支援学校版"]).set_index("項目"))
    st.markdown("#### 🦴 背骨①：4枚カード（読解カードの特別支援版）")
    cols = st.columns(4)
    for col, (name, icon, origin, ask, when) in zip(cols, tk.CARDS):
        with col.container(border=True):
            st.markdown(f"## {icon}")
            st.markdown(f"### {name}")
            st.markdown(f"「{ask}」")
            st.caption(f"元版：{origin}  \n導入：{when}")
    st.caption("『つたえる』カードは、作業学習の終わりの報告と同じ型にする。理科の考察と職場での報告が、同じ一つの習慣になる。")
    st.markdown("#### 🦴 背骨②：P1〜P5（教員側の物差し）")
    st.dataframe(pd.DataFrame([{"記号": bb.p_label(p), "特別支援学校での具体的な姿": form} for p, form in tk.PROTOCOL_FORMS.items()]),
                 hide_index=True, width="stretch")

# ── ② 年間計画 ─────────────────────────────
with tab2:
    st.markdown("#### 年間計画（高等部1年・理科週2時間の想定）")
    st.caption("麦の暦と作業学習の種目に合わせて並べた。理科で『なぜ』を学び、その週の作業学習で『やってみる』、という組で動かす。")
    month = st.select_slider("月をえらぶ", options=[4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3], value=6,
                             format_func=lambda m: f"{m}月", key="tokushi_month")
    hit = tk.plan_for(month)
    if not hit:
        st.info("8月は夏休み（この年間計画では単元を置いていない）。")
    for _, when, area, kubun, unit, work, jisshu, cards in hit:
        with st.container(border=True):
            st.markdown(f"**{when}｜{unit}**")
            a, b, c = st.columns(3)
            a.markdown(f"**理科**（{kubun}）  \n{area}")
            b.markdown(f"**作業学習でやること**  \n{work}")
            c.markdown(f"**体験実習での使い道**  \n{jisshu}")
            st.markdown("主なカード：" + "　".join(f"{i} {n}" for n, i, *_ in tk.CARDS if n in cards))
    with st.expander("1年分をまとめて見る"):
        st.dataframe(pd.DataFrame([{"時期": w, "科学と人間生活の領域": a, "高等部理科の区分": k, "理科の単元（例）": u,
                                    "作業学習でやること": wk, "体験実習での使い道": j, "主なカード": "・".join(c)}
                                   for _, w, a, k, u, wk, j, c in tk.PLAN]), hide_index=True, width="stretch")
    st.caption("理科の内容の一部を作業学習の中で扱う場合は、指導計画に『どの教科のどの目標を達成するのか』を書く。"
               "『高等部理科の区分』の列が、その対応を示すためのもの。小麦の収穫と、収穫した麦でのパン焼きは2年生の作業学習で行う。")

# ── ③ 授業例 ─────────────────────────────
with tab3:
    st.markdown("#### 「酵母がふくらませる」（理科2時間＋作業学習2時間）")
    st.caption("ゴール：『生地をあたたかい所に置くと早くふくらむ』ことを確かめ、作業学習の一次発酵で自分から温度を守れるようになる。")
    st.markdown("**① よそうする**：どれが一番ふくらむと思う？（色シールを貼るだけでよい）")
    guess = st.radio("よそう", [f"{s} {n}" for n, s, _ in tk.YEAST_PLACES], index=None, horizontal=True, key="tokushi_guess",
                     label_visibility="collapsed")
    st.markdown("**② はかる**：30分後の袋のふくらみ（cm）")
    cols = st.columns(3)
    heights = {}
    for col, (name, sticker, color), default in zip(cols, tk.YEAST_PLACES, (1.0, 3.0, 5.0)):
        heights[name] = col.number_input(f"{sticker} {name}（{color}のシール）", 0.0, 20.0, default, 0.5, key=f"tokushi_h_{name}")
    st.markdown("**③ ならべる**：シールの棒グラフ（シール1枚＝1 cm）")
    for name, sticker, _ in tk.YEAST_PLACES:
        st.markdown(f"{name}　{tk.sticker_bar(heights[name], sticker) or '（0）'}　{heights[name]:g} cm")
    top = tk.tallest(heights)
    st.markdown("**④ くらべる**")
    if guess is None:
        st.caption("先によそうを選ぶと、よそうと結果をくらべられる。")
    elif len(top) == 1 and guess.endswith(top[0]):
        st.success(f"よそうどおり、『{top[0]}』が一番ふくらんだ。あたたかいと酵母がよくはたらく。")
    else:
        st.warning(f"一番ふくらんだのは『{'・'.join(top)}』。よそうとちがった ─『なぜだろう』が、次の学びの入口。")
    st.caption("はじめの数字は説明用の例。クラスで測った数字に書きかえて、電子黒板にそのまま映せる。"
               "くわしいデータ（温度と気体の量）は『🦠 微生物と発酵・実験2』のページに。")
    st.markdown("**⑤ つたえる**：作業の報告と同じ型で言う")
    r1, r2, r3 = st.columns(3)
    what = r1.text_input("なにを", "生地の高さしらべ", key="tokushi_what", max_chars=60)
    count = r2.text_input("いくつ", "3つ", key="tokushi_count", max_chars=30)
    unknown = r3.text_input("まだわからないこと", "もっとあたためたらどうなるか", key="tokushi_unknown", max_chars=80)
    st.markdown(f"> {guard.clean_text(tk.report_sentence(what, count, unknown), 300)}")

    with st.expander("🧑‍🏫 指導案（理科2時間）と、作業学習の流れ"):
        st.markdown("**理科・1時間目（50分）**")
        st.dataframe(pd.DataFrame(tk.YEAST_LESSON_1, columns=["時間", "学習活動", "支援・配慮", "カード"]), hide_index=True, width="stretch")
        st.markdown("**理科・2時間目（50分）**")
        st.dataframe(pd.DataFrame(tk.YEAST_LESSON_2, columns=["時間", "学習活動", "支援・配慮", "カード"]), hide_index=True, width="stretch")
        st.markdown("**作業学習（食品加工種目・2時間続き）**  \n" + "  \n".join(f"{i}. {s}" for i, s in enumerate(tk.WORK_STEPS, 1)))
        st.caption("体験実習へのつなぎ：実習先がパン工房・食品工場の場合、『発酵器の温度を読んで報告する』を事前に実習先と共有し、"
                   "実習日誌に『学校と同じだったこと／ちがったこと』の欄を作る。")

# ── ④ 評価 ─────────────────────────────
with tab4:
    st.markdown("#### 支援の量で見る5段階")
    st.caption("『できた／できない』ではなく、どの程度の支援でできたかで記録する。支援が減っていくことが伸び。")
    st.dataframe(pd.DataFrame([{"レベル": lv, "支援の量": s, "具体例（発酵器の温度を合わせる）": ex} for lv, (s, ex) in tk.LEVELS.items()]),
                 hide_index=True, width="stretch")
    st.markdown("#### 場面をまたいでレベルが保たれるか（転移チェック）")
    st.caption("同じカードを、理科・作業学習・体験実習の3場面で記録する。名前は入れない（1人分の記録を手元に保存するための表）。")
    init = pd.DataFrame({s: [3, 3, 3, 3] for s in tk.SCENES}, index=list(tk.CARD_NAMES))
    rec = st.data_editor(init, key="tokushi_rec", width="stretch",
                         column_config={s: st.column_config.NumberColumn(s, min_value=1, max_value=5, step=1) for s in tk.SCENES})
    record = {card: {s: int(rec.loc[card, s]) for s in tk.SCENES if pd.notna(rec.loc[card, s])} for card in tk.CARD_NAMES}
    result = pd.DataFrame(tk.transfer_check(record))
    st.dataframe(result, hide_index=True, width="stretch")
    st.download_button("記録をCSVで保存（名前は入っていません）", guard.csv_safe(result).to_csv(index=False).encode("utf-8-sig"),
                       "支援の量の記録.csv", "text/csv")
    st.caption("通知表や指導要録では、この5段階を理科の3観点に振り分けて文章で書く。どのカードをどの観点に対応させるかは、実施校の評価規準に合わせて決める。"
               "体験実習の評価は、実習先にも同じ形式で記入を依頼する。")

# ── ⑤ 支援・安全 ─────────────────────────────
with tab5:
    st.markdown("#### つまずきと手立て（見てわかる・同じ順番でくり返す・できたことをすぐ認める）")
    st.dataframe(pd.DataFrame(tk.SUPPORTS, columns=["つまずき", "手立て"]), hide_index=True, width="stretch")
    st.markdown("#### 安全のきまり")
    st.dataframe(pd.DataFrame(tk.SAFETY, columns=["場面", "リスク", "きまり"]), hide_index=True, width="stretch")
    st.markdown("#### 情報・ICTとの連携：データを3段階で扱う")
    st.dataframe(pd.DataFrame(tk.ICT, columns=["段階", "やること", "道具"]), hide_index=True, width="stretch")
    st.markdown("#### ☐ 次の一手")
    for s in tk.NEXT_STEPS:
        st.markdown(f"- ☐ {s}")
    st.caption(f"未確定事項：{tk.UNDECIDED} 個々の生徒への具体的な配慮は、個別の指導計画とそろえて決める。")

