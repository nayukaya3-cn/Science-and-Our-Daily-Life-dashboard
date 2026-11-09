"""🍠 熱とは何か：石焼き芋と石窯パンのおいしさから（(2)ア(イ) 熱の性質とその利用）

FWの標準テーマ「播いた麦で、パンを焼くまで」の最後の工程「焼く」を、熱の言葉で説明する。
入力はこの画面の中だけで使い、保存も送信もしない。
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import netsu_core as nc
import ui

ui.hero("科学と人間生活 ｜ 光や熱の科学 ｜ 熱の性質とその利用（50分×8コマ）",
        "❓ 同じさつまいもなのに、なぜ石焼き芋は電子レンジより甘いのか",
        "おいしさを決めるのは「何℃に、何分いたか」。石は熱をため、ゆっくり出すので、ちょうどよい温度帯を長く保てる。"
        "熱と温度 → ためる → 伝わる → 焼く の順に、同じ読解カードで読んでいこう。")

ui.hint("温度＝「熱さの度合い」。熱＝「熱い方から冷たい方へ移るエネルギーの量」。"
        "お風呂のお湯とスプーン1杯のお湯は、同じ42℃でも、体を温める力（熱の量）がまるで違う。")

ui.lesson_plan([{"コマ": n, "ブロック": b, "テーマ": t, "プロトコル": p, "成果物": o} for n, b, t, p, o in nc.LESSONS])

tab1, tab2, tab3, tab4 = st.tabs(["① ためる：石はなぜ冷めにくいのか", "② 伝わる：3つの伝わり方",
                                  "③ 焼く：温度と時間で甘さが決まる", "④ その比べ方はフェアか"])

# ── ① 熱量保存 ─────────────────────────────
with tab1:
    st.markdown("#### 第3コマ：同じ質量の石・鉄・アルミを100℃に温めて、20℃の水に入れる")
    ui.predict("netsu_stone", "**100℃ の石 100 g を、20℃ の水 100 g に入れた。水は何℃になる？**"
               "（熱は外に逃げないとする。まん中の 60℃ になるだろうか）",
               actual=nc.equilibrium(100, nc.SPECIFIC_HEAT["石"], 100, 100, nc.SPECIFIC_HEAT["水"], 20),
               unit="℃", protocol="P1", min_value=20.0, max_value=100.0, value=60.0, step=1.0,
               field="熱の性質とその利用")

    c1, c2, c3 = st.columns(3)
    mass = c1.slider("試料の質量（g）", 50, 300, 100, 10, key="netsu_mass")
    water = c2.slider("水の質量（g）", 50, 300, 100, 10, key="netsu_water")
    t_water = c3.slider("水のはじめの温度（℃）", 5, 30, 20, 1, key="netsu_tw")
    rows = nc.exp3_table(mass, 100.0, water, t_water)
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    fig = go.Figure(go.Bar(x=[r["試料"] for r in rows], y=[r["水の温度（計算値）℃"] for r in rows],
                           marker_color="#c4651a", text=[f"{r['水の温度（計算値）℃']}℃" for r in rows],
                           textposition="outside", hovertemplate="%{x}：%{y}℃<extra></extra>"))
    fig.add_hline(y=t_water, line_dash="dot", line_color="#4a6a8a", annotation_text=f"はじめの水 {t_water}℃")
    fig.update_layout(height=320, margin=dict(t=30, b=10), yaxis_title="水の温度（℃）", yaxis_range=[0, 60])
    st.plotly_chart(fig, width="stretch")
    st.code("# 石が出した熱量 ＝ 水が受け取った熱量\n"
            "# 質量 × 比熱容量 × 温度変化 どうしを等しいと置く\n"
            "m_石 × c_石 × (100 − T) ＝ m_水 × c_水 × (T − 20)\n"
            "# Python\nT = (m1*c1*t1 + m2*c2*t2) / (m1*c1 + m2*c2)", language="python")
    st.warning("**どんでん返し**：同じ質量なら、石（約33℃）はアルミ（約34℃）とほぼ同じで、『石が特別にたくさん熱をためる』わけではない。"
               "石の強みは、熱を**ゆっくり出す**（熱を伝えにくい）ことと、安くて**量をたくさん使える**こと。"
               "『冷めにくい』には、ためる量（熱容量）と、出す速さ（熱の伝わりやすさ）の2つがある。", icon="🪨")
    ui.hint("比熱容量＝「1 g を 1℃ 上げるのに必要な熱の量。大きいほど温まりにくく、ため込める」。"
            "水の比熱容量は石の約5倍あるので、温度は水の側に大きく寄る。")
    ui.reading_card(
        axis="試料の種類（石・鉄・アルミ）と、試料を入れた後の水の温度",
        unit="℃（温度）、g（質量）、J/(g・K)（比熱容量）、J（熱量）",
        control="そろえた：試料の質量・温める温度（100℃）・水の量とはじめの温度。変えた：試料の種類",
        can="同じ質量なら、比熱容量が大きい試料ほど水を大きく温める（ためていた熱が多い）",
        cannot="石がいちばん『冷めにくい』こと（この実験は、ためる量を比べただけ。出す速さは測っていない）",
        protocols=["P1", "P3"], material="第3コマの実験データ表")
    ui.exam_question("netsu_1", nc.EXAMS[0])

# ── ② 3つの伝わり方 ─────────────────────────────
with tab2:
    st.markdown("#### 第4コマ：熱はどう運ばれるか")
    st.table(pd.DataFrame(nc.TRANSFER, columns=["伝わり方", "文系向けの言い換え", "石焼き芋では", "石窯パンでは"]).set_index("伝わり方"))
    food = st.radio("どちらの断面図に矢印を書き込む？", ["石焼き芋", "石窯パン"], horizontal=True, key="netsu_food")
    st.markdown("**書き込む矢印**")
    idx = 2 if food == "石焼き芋" else 3
    for row in nc.TRANSFER:
        st.markdown(f"- **{row[0]}** → {row[idx]}")
    if food == "石焼き芋":
        st.info("石からの放射（赤外線）と、石との接触（伝導）で、皮がこげずに全体が均一に温まる。"
                "外側からゆっくり熱が伝わるので、中心は長い時間、酵素が働く温度帯にとどまる。", icon="🍠")
    else:
        st.info("石窯は壁と床に熱をためている（熱容量が大きい）。冷たい生地を入れても窯の温度が下がりにくい。"
                "床からの伝導で底が一気に焼け、壁と天井からの放射で表面が焼ける。窯内の空気の対流は補助的。", icon="🍞")
    ui.hint("演示は3つ：伝導＝金属棒にロウを並べ端を温める。対流＝ビーカーの水に絵の具を落とし底を温める。"
            "放射＝黒い紙と白い紙に電球（または日光）を当て、温度を比べる。")

# ── ③ 温度と時間 ─────────────────────────────
with tab3:
    st.markdown("#### 温度ごとに起きること（低い順）")
    st.dataframe(pd.DataFrame([{"およその温度": nc.band_label(lo, hi), "起きること": w, "食べ物": f, "つながる科目": s}
                               for lo, hi, w, f, s in nc.BANDS]), hide_index=True, width="stretch")
    st.caption("温度は品種や条件で変わるおよその幅。授業では『帯』として扱い、数字の暗記は求めない。")
    temp = st.slider("いまの温度（℃）", 20, 250, 65, 5, key="netsu_temp")
    ev = nc.events_at(temp)
    st.markdown("**この温度で起きていること**" + ("" if ev else "：（この表の中では、とくに何も起きていない）"))
    st.markdown("\n".join(f"- {e}" for e in ev))

    st.markdown("#### 第5コマ：加熱の仕方で、甘くなる帯（55〜75℃）にいる時間はどう変わる？")
    ui.predict("netsu_band", "**小石を敷いた鍋（弱火・約75分）で焼くと、芋の中心が 55〜75℃ にいる時間は何分くらい？**"
               "（電子レンジは約1分。下の模型での値）",
               actual=nc.minutes_in_band(25.0, 75.0), unit="分", protocol="P4", min_value=0.0, max_value=75.0,
               value=1.0, step=1.0, field="熱の性質とその利用")
    fig = go.Figure()
    style = {"A": "#7a7a7a", "B": "#2a78b5", "C": "#c4651a", "D": "#5a8f3c"}
    for name, total, tau, _ in nc.METHODS:
        ts = [total * i / 60 for i in range(61)]
        fig.add_scatter(x=ts, y=[nc.core_temp(t, tau) for t in ts], mode="lines", name=name,
                        line=dict(color=style[name[0]], width=2.5),
                        hovertemplate=f"{name}<br>%{{x:.0f}} 分：%{{y:.0f}}℃<extra></extra>")
    fig.add_hrect(y0=nc.SWEET_BAND[0], y1=nc.SWEET_BAND[1], fillcolor="#fdecc8", opacity=0.6, line_width=0,
                  annotation_text="甘くなる帯（酵素が働く）", annotation_position="top left")
    fig.update_layout(height=380, margin=dict(t=20, b=10), xaxis_title="加熱を始めてからの時間（分）",
                      yaxis_title="芋の中心の温度（℃）", legend=dict(orientation="h"), hovermode="x unified")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(pd.DataFrame(nc.method_table()), hide_index=True, width="stretch")
    st.caption("⚠️ このグラフは**説明用の模型**（中心温度が100℃へだんだん近づく、と単純化）。実測ではない。"
               "第5コマでは、芋の中心に温度計を刺して、自分たちの値で確かめる。")
    with st.expander("模型を自分で動かす：熱が中心に届く『遅さ』を変える"):
        tau = st.slider("熱が中心に届く遅さ（分。大きいほどゆっくり）", 1.0, 40.0, 25.0, 0.5, key="netsu_tau")
        total = st.slider("加熱する時間（分）", 1, 120, 75, 1, key="netsu_total")
        m1, m2 = st.columns(2)
        m1.metric("甘くなる帯にいた時間", f"{nc.minutes_in_band(tau, total):.1f} 分")
        m2.metric("加熱を終えたときの中心温度", f"{nc.core_temp(total, tau):.0f} ℃")
    st.warning("電子レンジは数分で中心を熱くするので、酵素が働く帯を一瞬で通り過ぎる。"
               "しかも **酵素もタンパク質**なので、熱すぎると働かなくなる（1章A・2章Bの実験2とつながる）。", icon="🌡️")

# ── ④ その比べ方はフェアか ─────────────────────────────
with tab4:
    st.markdown("#### 第6コマ：糖度計（Brix）の値が上がった。『甘くなった』と言える？")
    ui.hint("Brix（ブリックス）は、汁に溶けているもの全体の濃さ。糖だけを測っているわけではない。"
            "加熱で水分が飛ぶと、糖が増えなくても値は上がる。")
    c1, c2 = st.columns(2)
    loss = c1.slider("加熱で飛んだ水分（％）", 0, 40, 15, 1, key="brix_loss")
    gain = c2.slider("酵素で増えた糖（生の芋100 gあたり g）", 0.0, 10.0, 0.0, 0.5, key="brix_gain")
    before, after = nc.brix(20, 80), nc.brix_after(20, 80, loss / 100, gain)
    m1, m2, m3 = st.columns(3)
    m1.metric("加熱前の Brix", f"{before:.1f} %")
    m2.metric("加熱後の Brix", f"{after:.1f} %", f"{after - before:+.1f}")
    m3.metric("水分だけで上がった分", f"{nc.brix_after(20, 80, loss / 100, 0) - before:+.1f}")
    st.caption("説明用の例：生の芋100 g のうち、溶けているもの20 g・水80 g として計算。")
    if gain == 0 and loss > 0:
        st.error("糖は1 g も増えていないのに、Brix は上がった。『甘くなった』と『水が減った』を区別できるかな？")
    ui.reading_card(
        axis="加熱の仕方（A〜D）と、すりおろした汁の糖度（Brix）",
        unit="Brix（％）、分（加熱時間）、℃（中心温度）",
        control="そろえる：品種・芋の太さ・測る位置（中央の輪切り）。各条件を複数本で行う。変える：加熱の仕方",
        can="時間をかけて加熱した条件のほうが Brix が高い",
        cannot="糖が増えたこと（水分が飛んだだけでも Brix は上がる）。石そのものに甘くする力があること",
        protocols=["P2", "P3"], material="第5コマの糖度データ表")
    ui.exam_question("netsu_2", nc.EXAMS[1])
    st.markdown("#### 💻 情報Ⅰとつなげる")
    st.markdown("加熱時間を横軸、糖度を縦軸にした**散布図**、条件ごとの**箱ひげ図**を表計算ソフトで作る（第4問「データの活用」）。"
                "成果物は「この実験で言えること／言えないこと」を各2つ。")

with st.expander("⚠️ 安全の留意点（実験・調理の前に必ず読む）"):
    for s in nc.SAFETY:
        st.markdown(f"- {s}")

with st.container(border=True):
    st.markdown("**🌾 フィールドワーク（三原西部）へ**")
    st.markdown("- **畑区画**：育てた小麦を石窯パンに。さつまいもを育てれば『育てる → 焼く → 測る』を一貫して扱える  \n"
                "- **山**：薪を燃料にし、発熱量を比べる。岩石の種類（地学基礎）とも結びつく  \n"
                "- **ハウス**：日中にたまった熱と夜の冷え込みを温度ログで比べる（熱容量・放射）")
    st.caption("第7コマ（天板と、予熱した焼き石の焼き比べ）は、FWで収穫した麦のパンでも同じ比較ができる。")

ui.next_move_tag("netsu")
