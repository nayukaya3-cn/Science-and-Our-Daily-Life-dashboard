"""🦠 微生物と人間の食生活（2章B・教科書 p.44〜49）

1章A「タンパク質」の原理（分解して部品にし、組み直す）を、微生物と発酵食品に広げる。
入力はこの画面の中だけで使い、保存も送信もしない。
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import bisei_core as bc
import sister_sites as ss
import ui

ui.hero("科学と人間生活 ｜ 第1部 2章 微生物とその利用 ｜ B 微生物と人間の食生活（p.44〜49）",
        "❓ ヨーグルトの味と、原料の牛乳の味が違うのはなぜだろうか",
        "1章Aで確かめた『取り込んだものは部品に分解され、組み直される』は、微生物にもそのまま当てはまる。"
        "発見の歴史 → 発酵食品 → 実験2（温度）の順に、同じ読解カードで読んでいこう。")

ui.hint("微生物（びせいぶつ）＝カビ・酵母・細菌のように、顕微鏡でないと見えない小さな生き物。"
        "発酵（はっこう）＝微生物が酸素を使わずに有機物を分解し、人間に役立つものができること。")

with st.container(border=True):
    st.markdown("### 🗺️ この単元を1枚で（高いところから見る）")
    st.table(pd.DataFrame(bc.BREAKDOWN, columns=["どこで", "分解されるもの", "できる部品", "その後"]).set_index("どこで"))
    st.caption("どの行も『大きなもの → 小さな部品』。ちがうのは、その部品を**だれの設計図で何に使うか**だけ。"
               "腐敗も発酵と同じ『分解』で、人間にとって不都合なときにそう呼ぶ。")

tab1, tab2, tab3, tab4 = st.tabs(["① 発見の歴史とパスツール", "② 発酵食品を分類する",
                                  "③ 実験2：アルコール発酵と温度", "④ ヨーグルトと資料編"])

# ── ① 発見の歴史 ─────────────────────────────
with tab1:
    st.markdown("#### 見る道具 → 対照実験 → 応用：微生物研究の3段")
    st.dataframe(pd.DataFrame(bc.HISTORY, columns=["いつ", "できごと", "何が変わったか"]),
                 hide_index=True, width="stretch")
    ui.hint("レーウェンフックの顕微鏡はレンズ1枚（約200倍）。それでも『見える』ようになったことで、研究が始まった。")

    st.markdown("#### 🧪 パスツールのフラスコ（図16）：条件を1つだけ変えてみよう")
    c1, c2 = st.columns(2)
    neck = c1.radio("フラスコの首", ["S字（白鳥の首）", "首を折る"], key="pasteur_neck")
    boiled = c2.toggle("液を煮沸して殺菌する", value=True, key="pasteur_boil")
    r = bc.pasteur(neck, boiled)
    m1, m2, m3 = st.columns(3)
    m1.metric("空気は入る？", r["空気は入る？"])
    m2.metric("微生物は液に入る？", r["微生物は液に入る？"])
    m3.metric("液は腐敗する？", "する（にごる）" if r["腐敗する？"] else "しない（何年も澄んだまま）")
    (st.error if r["腐敗する？"] else st.success)(r["理由"])
    st.caption("問1 の答え：生物は、生物のいない状態から親なしに自然に発生することはない（教科書 p.45）。")

    ui.reading_card(
        axis="首の形（S字／折る）と、液が腐敗するかどうか",
        unit="腐敗する・しない（有り無し）と、経過した年数",
        control="そろえた：養分をふくむ液・煮沸殺菌・空気が入ること。変えた：微生物が液まで届くかどうか（首を折るか）",
        can="空気があっても、微生物が入らなければ液は腐敗しない ＝ 微生物は外から来る（自然発生しない）",
        cannot="すべての生物について、どんな条件でも自然発生しないこと（この実験が調べたのは液と微生物だけ）",
        protocols=["P3", "P2"], material="図16 パスツールの実験")

# ── ② 発酵食品 ─────────────────────────────
with tab2:
    st.markdown("#### 図17：使われる微生物で発酵食品を分類する")
    pick = st.multiselect("微生物を選ぶ（複数可）", bc.MICROBES, default=["酵母"], key="ferment_pick")
    exact = st.toggle("ちょうどその組み合わせだけ（OFF なら『少なくとも選んだ微生物を使う』）", value=False, key="ferment_exact")
    foods = bc.classify(set(pick), exact=exact)
    st.markdown("**該当する食品**：" + ("、".join(foods) if foods else "（なし）"))
    counts = bc.venn_counts()
    st.dataframe(pd.DataFrame([{"使われる微生物": k, "食品の数": v,
                                "食品": "、".join(f for f, s in bc.FERMENTED.items()
                                                 if "＋".join(x for x in bc.MICROBES if x in s) == k)}
                               for k, v in counts.items()]),
                 hide_index=True, width="stretch")
    ui.hint("しょう油・みそ・日本酒は、カビ・酵母・細菌の3つの作用を受けてつくられる（図17で3つの枠が重なる部分）。"
            "情報Ⅰでいう『集合の共通部分』。")

    st.markdown("#### コラム：しょう油とみその製造法（図a）")
    c1, c2 = st.columns(2)
    c1.markdown("**しょう油**  \n" + "  \n".join(f"{i}. {s}" for i, s in enumerate(bc.SHOYU_STEPS, 1)))
    c2.markdown("**米みそ**  \n" + "  \n".join(f"{i}. {s}" for i, s in enumerate(bc.MISO_STEPS, 1)))
    st.info("しょう油やみそには、ダイズのタンパク質が分解されて生じた**アミノ酸**が多量にふくまれる。"
            "1章Aの『タンパク質 → アミノ酸』が、ここでは台所で起きている。うま味の本体は、コンブのグルタミン酸、"
            "かつお節のイノシン酸など。", icon="🫘")

    ui.reading_card(
        axis="発酵食品と、使われる微生物（カビ・酵母・細菌）",
        unit="種類（数ではなく、あり・なし）",
        control="分類の基準を『おもに使われる微生物』の1つにそろえている（原材料・製法では分けていない）",
        can="パン・ビール・ワインはおもに酵母、ヨーグルト・納豆はおもに細菌の作用でつくられる",
        cannot="その食品の味や栄養の良し悪し（分類しただけで、比べていない）",
        protocols=["P2", "P5"], material="図17 使われる微生物で分類した発酵食品")

# ── ③ 実験2 ─────────────────────────────
with tab3:
    st.markdown("#### 実験2：酵母のアルコール発酵と温度（p.49 結果例）")
    ui.hint("グルコース水溶液に乾燥酵母を加えて注射器に入れ、20℃・30℃・80℃ の水に立てる。"
            "2分ごとに、発生した気体（二酸化炭素）の量を読む。")
    ui.predict("bisei_exp2", "**30℃ で 26分たったとき、発生した気体はおよそ何 mL？**（20℃ は 3.8 mL だった）",
               actual=bc.EXP2[30][-1], unit="mL", protocol="P4", max_value=30.0, step=0.5, fmt="%.1f",
               field="微生物とその利用")

    show = st.multiselect("表示する温度", list(bc.EXP2), default=list(bc.EXP2), key="exp2_temps",
                          format_func=lambda t: f"{t}℃")
    style = {20: ("#2a78b5", "solid"), 30: ("#c4651a", "solid"), 80: ("#7a7a7a", "dash")}
    fig = go.Figure()
    for t in show:
        col, dash = style[t]
        fig.add_scatter(x=bc.EXP2_TIME, y=bc.EXP2[t], mode="lines+markers", name=f"{t}℃",
                        line=dict(color=col, width=2, dash=dash), marker=dict(size=8),
                        hovertemplate=f"{t}℃<br>%{{x}} 分：%{{y}} mL<extra></extra>")
        fig.add_annotation(x=bc.EXP2_TIME[-1], y=bc.EXP2[t][-1], text=f"{t}℃", showarrow=False,
                           xanchor="left", xshift=8, font=dict(color="#22313f"))
    fig.update_layout(height=380, margin=dict(t=20, b=10, r=50), xaxis_title="時間（分）",
                      yaxis_title="発生した気体の量（mL）", hovermode="x unified", legend=dict(orientation="h"))
    st.plotly_chart(fig, width="stretch")

    st.markdown("#### 💻 情報Ⅰ：傾き＝速さ を計算する")
    t0, t1 = st.select_slider("比べる時間の範囲（分）", options=list(bc.EXP2_TIME), value=(8, 26), key="exp2_range")
    if t1 > t0:
        rows = []
        for t in bc.EXP2:
            a, b = bc.fit_line(t, t0, t1)
            rows.append({"温度": f"{t}℃", "平均の速さ（2点の傾き, mL/分）": round(bc.avg_rate(t, t0, t1), 3),
                         "回帰直線の傾き（mL/分）": round(a, 3)})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        r20, r30 = bc.avg_rate(20, t0, t1), bc.avg_rate(30, t0, t1)
        if r20 > 0:
            st.markdown(f"この範囲では、30℃ は 20℃ の **約 {r30 / r20:.1f} 倍** の速さ。")
    else:
        st.caption("範囲の左端と右端を離してください。")
    with st.expander("2分ごとの増え方（差分）を見る：増え方そのものが大きくなっていく"):
        st.dataframe(pd.DataFrame({f"{t}℃": bc.increments(t) for t in bc.EXP2},
                                  index=[f"{a}→{b}分" for a, b in zip(bc.EXP2_TIME, bc.EXP2_TIME[1:])]).T,
                     width="stretch")
    st.code("# DNCL 風：区間の平均の速さ\n速さ = (量[終わり] - 量[はじめ]) ÷ (時間[終わり] - 時間[はじめ])\n"
            "# Python\nrate = (ys[i1] - ys[i0]) / (t1 - t0)", language="python")

    st.warning("80℃ で 0 のままなのはなぜ？ → 酵母の発酵を進める**酵素はタンパク質**。高温で立体構造がこわれると働かなくなる。"
               "1章Aの『タンパク質は形（並び方）で働く』がここでもつながる。発酵食品づくりで温度管理が重要だといわれる（パン生地は 28℃ 程度で静置する）のも、このため。",
               icon="🌡️")

    ui.reading_card(
        axis="時間（横軸）と、発生した気体の量（縦軸）を、温度ごとに比べる",
        unit="分・mL（気体の量は累積。最小目盛り1 mLの注射器を 0.1 mL まで読んでいる）",
        control="そろえた：グルコース水溶液 20 mL・乾燥酵母 1 g・注射器に 5 mL。変えた：温度（20・30・80℃）",
        can="20℃ より 30℃ のほうが発酵が速い（仮説(2)はこの範囲で支持）。80℃ では発酵が起きない（仮説(1)を支持）",
        cannot="温度が高いほど速い、とは言えない（80℃ は 0）。最も速い温度が 30℃ だとも言えない（30〜80℃ の間を測っていない）",
        protocols=["P2", "P3"], material="実験2 結果例の表とグラフ")

# ── ④ ヨーグルトと資料編 ─────────────────────────────
with tab4:
    st.markdown("#### やってみよう：ヨーグルトをつくろう（p.48）")
    st.markdown("  \n".join(f"{i}. {s}" for i, s in enumerate(bc.YOGURT_STEPS, 1)))
    st.error("⚠️ " + "／".join(bc.YOGURT_SAFETY))
    ui.hint("pH（ピーエイチ）は酸性・アルカリ性の度合い。7が中性、7より小さいと酸性。"
            "乳酸菌が乳酸をつくると pH が下がり、酸っぱくなって固まる ─ これが冒頭の問い（味が違う）の答えの入口。")
    c1, c2 = st.columns(2)
    pa = c1.slider("ヨーグルトの pH", 3.0, 7.0, 4.0, 0.1, key="ph_a")
    pb = c2.slider("牛乳の pH", 3.0, 7.0, 6.6, 0.1, key="ph_b")
    st.metric("ヨーグルトの酸性の強さは牛乳の何倍？", f"約 {bc.ph_ratio(pa, pb):,.0f} 倍",
              help="pH が 1 下がると、酸性の強さ（水素イオンの濃さ）は 10 倍。pH は対数の目盛り")

    st.markdown("#### 資料編：測った数字を正しく扱う")
    c1, c2 = st.columns(2)
    with c1.container(border=True):
        st.markdown("**有効数字（資料5）**")
        s = st.text_input("測定値を入れる（例：48.7 / 0.0032 / 1.20e3）", "48.7", key="sig_in", max_chars=40)
        try:
            float(s.replace("×10^", "e"))
            st.markdown(f"有効数字は **{bc.sig_figs(s)} 桁**")
        except ValueError:
            st.caption("数字で入力してください。")
        st.caption("最小目盛りの 1/10 まで目分量で読む。最後の桁には誤差がふくまれる。")
    with c2.container(border=True):
        st.markdown("**ミクロメーター（資料6）**")
        o = st.number_input("対物ミクロメーターの目盛り数", 1, 100, 14, key="mm_obj")
        e = st.number_input("接眼ミクロメーターの目盛り数", 1, 100, 20, key="mm_eye")
        u = bc.micrometer_unit(o, e)
        st.markdown(f"接眼1目盛り ＝ 10 µm × {o} ÷ {e} ＝ **{u:g} µm**  \n"
                    f"タマネギの細胞（38目盛り × 7目盛り）なら **{38 * u:g} µm × {7 * u:g} µm**")
    with st.expander("💻 情報Ⅰ：SI接頭語（10進）と、情報の単位（2進）のずれ"):
        st.dataframe(pd.DataFrame([{"記号": s_, "読み": r_, "10のべき": f"10^{p_}",
                                    "情報の単位との比（2^10k ÷ 10^3k）": f"{bc.binary_gap(p_):.3f}" if p_ > 0 and p_ % 3 == 0 else "─"}
                                   for s_, r_, p_ in bc.SI_PREFIX]), hide_index=True, width="stretch")
        st.caption("1 kB を 1000 B とするか 1024 B とするかで、テラでは約1割ずれる。単位をそろえるのは読解カードの②。")

with st.container(border=True):
    st.markdown("**🔗 姉妹サイトで確かめる（単元：微生物とその利用）**")
    ss.render_unit("微生物とその利用", "tanpaku")
    st.caption("現場では、天然酵母のパン生地で『温度を変えるとふくらみ方はどう変わるか』を実際に測る（実験2の延長）。")

ui.next_move_tag("biseibutsu")
