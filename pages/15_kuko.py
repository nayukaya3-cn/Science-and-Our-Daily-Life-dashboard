"""✈️ 「科学と人間生活」×広島空港：霧が多いのに着陸できるのはなぜか（50分×4コマ）

1つの問いから、4領域（宇宙や地球・光や熱・物質・情報Ⅰ）を横断する。
入力はこの画面の中だけで使い、保存も送信もしない。
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import kuko_core as kc
import ui

ui.hero("科学と人間生活 ｜ 4つの領域を1つの問いで横断する（50分×4コマ）",
        "❓ 広島空港は霧が多い。それでも飛行機が着陸できるのはなぜか",
        f"広島空港は三原市にあり、標高{kc.AIRPORT_ELEVATION_M} m の山間の高台にある。"
        "霧（地球）・電波（光と熱）・機体（物質）の3つを順に確かめ、最後に報道のデータを読解カードで読もう。")

ui.lesson_plan([{"コマ": n, "領域": a, "テーマ": t, "空港の題材": m, "主な活動": act, "プロトコル": p}
                for n, a, t, m, act, p in kc.LESSONS])
st.caption("各コマは単独でも使える。それぞれの領域の単元の最後に『地域への応用』として1コマずつ入れるか、学期末に4コマをまとめて行う。")

tab1, tab2, tab3, tab4 = st.tabs(["① なぜ霧ができるのか", "② 霧の中でも届くものは何か",
                                  "③ 飛行機は何でできているか", "④ 着陸装置が使えなかった期間"])

# ── ① 霧 ─────────────────────────────
with tab1:
    st.markdown("#### 第1コマ：空気が冷えると、抱えきれなくなった水蒸気が水滴になる")
    ui.hint("露点（ろてん）＝「空気が水を抱えきれなくなって、水滴を出し始める温度」。冷たいジュースのコップが濡れるのと同じ。")
    ui.predict("kuko_dew", "**気温 20℃・湿度 60％ の空気は、何℃まで冷えると水滴が出はじめる？**",
               actual=kc.dew_point(20, 60), unit="℃", protocol="P4", min_value=-10.0, max_value=20.0, value=0.0,
               step=1.0, field="宇宙や地球の科学")
    c1, c2, c3 = st.columns(3)
    t = c1.slider("夕方の気温（℃）", 0, 35, 18, 1, key="kuko_t")
    rh = c2.slider("夕方の湿度（％）", 20, 100, 70, 1, key="kuko_rh")
    night = c3.slider("夜明け前の気温（℃）", -5, 35, 10, 1, key="kuko_night")
    td = kc.dew_point(t, rh)
    m1, m2, m3 = st.columns(3)
    m1.metric("露点", f"{td:.1f} ℃")
    m2.metric("夜明け前の湿度", f"{kc.humidity_after_cooling(t, rh, night):.0f} %")
    m3.metric("水滴になった分", f"{kc.fog_water(t, rh, night):.1f} g/m³")
    if night <= td:
        st.error(f"夜明け前の気温（{night}℃）が露点（{td:.1f}℃）以下 → 抱えきれなくなった水蒸気が水滴になる ＝ **霧（または露）**。")
    else:
        st.success(f"夜明け前の気温（{night}℃）は露点（{td:.1f}℃）より高い → まだ抱えていられる。霧は出にくい。")

    xs = list(range(-5, 36))
    fig = go.Figure(go.Scatter(x=xs, y=[kc.sat_amount(x) for x in xs], mode="lines", name="抱えられる上限（飽和水蒸気量）",
                               line=dict(color="#2a78b5", width=2.5), hovertemplate="%{x}℃：上限 %{y:.1f} g/m³<extra></extra>"))
    now = kc.vapor_amount(t, rh)
    fig.add_scatter(x=[t], y=[now], mode="markers+text", name="夕方の空気", marker=dict(size=13, color="#c4651a"),
                    text=["夕方"], textposition="top center", hovertemplate="夕方 %{x}℃：%{y:.1f} g/m³<extra></extra>")
    fig.add_scatter(x=[td, t], y=[now, now], mode="lines", name="冷えていく", line=dict(color="#c4651a", dash="dot"),
                    hoverinfo="skip")
    fig.update_layout(height=360, margin=dict(t=20, b=10), xaxis_title="気温（℃）", yaxis_title="水蒸気の量（g/m³）",
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, width="stretch")
    st.caption("点を左へ（冷える向きに）動かして、青い線にぶつかった温度が露点。線より上にはいられないので、あふれた分が水滴になる。")

    st.markdown("**なぜ高いところや山に霧が多いのか**")
    h = kc.condensation_height(t, rh)
    st.markdown(f"空気が山の斜面を上ると、ふくらんで冷える（ペットボトルの実験と同じ）。いまの空気なら、水滴ができ始める高さの目安は "
                f"**約 {h:,.0f} m**。空港の標高は **{kc.AIRPORT_ELEVATION_M} m**。")
    (st.error if h <= kc.AIRPORT_ELEVATION_M else st.info)(
        "空港の高さまで上る前に水滴ができる → 空港は雲（霧）の中。" if h <= kc.AIRPORT_ELEVATION_M
        else "この空気では、空港の高さではまだ水滴にならない。湿度を上げて試してみよう。")
    st.caption("高さは『(気温−露点)×約125 m』という目安の式。晴れた夜に地面が冷える放射冷却は、熱の単元の『放射』の応用。")
    ui.reading_card(
        axis="気温（横軸）と、空気1 m³ が抱えられる水蒸気の上限（縦軸）",
        unit="℃、g/m³（湿度は％＝いまの量÷上限）",
        control="そろえた：空気にふくまれる水蒸気の量。変えた：気温だけ（冷やした）",
        can="水蒸気の量が同じなら、気温が露点まで下がると水滴ができる",
        cannot="その日、空港でほんとうに霧が出るかどうか（風・地形・雲のようすは、このグラフに入っていない）",
        protocols=["P4", "P2"], material="飽和水蒸気量のグラフ")

# ── ② 波長 ─────────────────────────────
with tab2:
    st.markdown("#### 第2コマ：霧の中で、光は散らばり、電波は通り抜ける")
    st.markdown(f"着陸する飛行機は、滑走路から出る電波（計器着陸装置）をたどって降りてくる。"
                f"いちばん精度の高い区分では、滑走路の見通しが **{kc.RVR_MIN_M} m** あれば着陸できる。")
    rows = [{"波": n, "波長（m）": f"{w:.2g}", "霧の粒の何倍？": f"{kc.size_ratio(w):,.2g} 倍", "使われ方": use, "霧の中で": fog}
            for n, w, use, fog in kc.WAVES]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    fig = go.Figure(go.Bar(y=[r[0] for r in kc.WAVES] + ["霧の粒（大きさの目安）"],
                           x=[r[1] for r in kc.WAVES] + [kc.FOG_DROPLET_M], orientation="h",
                           marker_color=["#c4651a", "#c4651a", "#2a78b5", "#2a78b5", "#7a7a7a"],
                           hovertemplate="%{y}：%{x:.2g} m<extra></extra>"))
    fig.add_vline(x=kc.FOG_DROPLET_M, line_dash="dot", line_color="#7a7a7a")
    fig.update_layout(height=320, margin=dict(t=20, b=10), xaxis=dict(type="log", title="長さ（m）※1目盛りで10倍になる目盛り"))
    st.plotly_chart(fig, width="stretch")
    st.caption("横軸は対数の目盛り（1目盛りで10倍）。pH と同じ考え方で、けたのちがうものを1枚の図に並べられる。"
               "霧の粒は数 µm〜数十 µm の幅があり、ここでは約0.01 mm を目安にしている。")
    st.markdown("**💻 情報Ⅰ・物理基礎：波長を計算する**（波長 ＝ 速さ ÷ 振動数）")
    f_mhz = st.number_input("電波の振動数（MHz）", 1.0, 100000.0, 110.0, 1.0, key="kuko_f")
    lam = kc.wavelength(f_mhz * 1e6)
    st.markdown(f"波長 ＝ 3.0×10⁸ m/s ÷ {f_mhz:g}×10⁶ Hz ＝ **{lam:.3g} m**（霧の粒の約 {kc.size_ratio(lam):,.0f} 倍）")
    ui.hint("可視光の波長は霧の粒より短いので、粒にぶつかって散らばる（散乱）。着陸装置の電波は波長が1 m前後と、"
            "粒よりはるかに長いので、粒をほとんど気にせずに通り抜ける。")
    st.markdown("**生活との接続**：滑走路の手前にある赤い橋のような進入灯（光）と、着陸装置（電波）は、どう役割を分けているだろうか。")
    ui.reading_card(
        axis="波の種類（可視光・赤外線・電波）と、霧の向こうまで届くかどうか",
        unit="m（波長）、Hz（振動数）。届く・届かないは有り無し",
        control="そろえる：距離・霧の濃さ。変える：光か電波か",
        can="霧の中では、懐中電灯の光は散らばって見えなくなるが、ラジオやスマートフォンの電波は届く",
        cannot="電波ならどんな天気でも必ず着陸できること（装置の精度の区分や、風などほかの条件がある）",
        protocols=["P3", "P4"], material="水槽の霧の演示")

# ── ③ 密度 ─────────────────────────────
with tab3:
    st.markdown("#### 第3コマ：軽くて強い材料は何か ─ 密度を測って確かめる")
    ui.hint("密度（みつど）＝「同じ大きさで比べた重さ」。1 cm³ あたり何 g か。水は 1 g/cm³。")
    c1, c2, c3 = st.columns(3)
    mass = c1.number_input("小片の質量（g）", 0.1, 500.0, 27.0, 0.1, key="kuko_mass")
    v0 = c2.number_input("入れる前の水（mL）", 1.0, 500.0, 50.0, 0.5, key="kuko_v0")
    v1 = c3.number_input("入れた後の水（mL）", 1.0, 500.0, 60.0, 0.5, key="kuko_v1")
    try:
        rho = kc.density(mass, v0, v1)
        m1, m2 = st.columns(2)
        m1.metric("密度", f"{rho:.2f} g/cm³")
        m2.metric("いちばん近い材料", kc.nearest_material(rho))
    except ValueError as e:
        st.caption(str(e))
    vol = st.slider("同じ体積の部品をつくるとしたら（cm³）", 10, 1000, 100, 10, key="kuko_vol")
    ms = kc.mass_if_made_of(vol)
    fig = go.Figure(go.Bar(x=list(ms), y=list(ms.values()), marker_color=["#7a7a7a", "#2a78b5", "#5a8f3c"],
                           text=[f"{v:g} g" for v in ms.values()], textposition="outside",
                           hovertemplate="%{x}：%{y} g<extra></extra>"))
    fig.update_layout(height=320, margin=dict(t=30, b=10), yaxis_title="質量（g）")
    st.plotly_chart(fig, width="stretch")
    st.caption("密度は一般的な目安の値（鉄 約7.9、アルミ 約2.7、CFRP 約1.5〜1.6 g/cm³）。")
    st.info("CFRP（炭素繊維強化プラスチック）は、強い炭素繊維をプラスチックで固めた**複合材料**。"
            "鉄筋コンクリートと同じように、役割の違う材料を組み合わせている。プラスチック単元の『炭素繊維入りフィラメント』と同じ考え方。"
            "金属は『さびる』、CFRP は『リサイクルしにくい』という課題も並べて考える。", icon="🧩")

# ── ④ 欠航のデータ ─────────────────────────────
with tab4:
    st.markdown("#### 第4コマ：着陸装置が使えなかった期間の欠航を、読解カードで読む")
    st.markdown(f"2015年、滑走路からそれる事故で着陸装置のアンテナが壊れ、元に戻るまで精度の低い区分で運用した。"
                f"そのうち5月6日〜8月26日には **{kc.FLIGHTS_TOTAL:,} 便** が発着し、欠航は **{kc.CANCELLED} 便** だった。")
    ui.predict("kuko_cancel", f"**欠航 {kc.CANCELLED} 便のうち、『装置の精度がもう一段高ければ欠航せずに済んだ』と報じられたのは何便？**",
               actual=float(kc.CANCELLED_BY_DEVICE), unit="便", protocol="P3", min_value=0.0, max_value=float(kc.CANCELLED),
               value=float(kc.CANCELLED), step=1.0, field="情報Ⅰ・データの活用")
    b = kc.flight_breakdown()
    scope = st.radio("帯グラフの分母（全体）を何にする？", ["欠航した59便", "発着した3,255便"], horizontal=True, key="kuko_scope")
    parts = {"欠航（装置の区分が原因と言える）": ("#c4651a", b["欠航（装置の区分が原因と言える）"]),
             "欠航（それ以外・台風など）": ("#7a7a7a", b["欠航（それ以外・台風など）"])}
    if scope.startswith("発着"):
        parts["運航できた便"] = ("#b9d3ea", b["運航できた便"])
    total = sum(v for _, v in parts.values())
    fig = go.Figure()
    for name, (col, v) in parts.items():
        fig.add_bar(y=["便"], x=[100 * v / total], name=f"{name} {v:,}便", orientation="h", marker_color=col,
                    hovertemplate=f"{name}<br>{v:,} 便（%{{x:.1f}}％）<extra></extra>")
    fig.update_layout(barmode="stack", height=200, margin=dict(t=10, b=10), xaxis=dict(title="割合（％）", range=[0, 100]),
                      yaxis=dict(visible=False), legend=dict(orientation="h", y=-0.6))
    st.plotly_chart(fig, width="stretch")
    m1, m2, m3 = st.columns(3)
    m1.metric("欠航の割合", f"{b['欠航の割合（％）']} %", "59 ÷ 3,255", delta_color="off", delta_arrow="off")
    m2.metric("装置が原因と言える欠航", f"{b['装置が原因と言える欠航の割合（％）']} %", "14 ÷ 3,255", delta_color="off", delta_arrow="off")
    m3.metric("欠航のうち装置が原因", f"{b['欠航のうち装置が原因と言える割合（％）']} %", "14 ÷ 59", delta_color="off", delta_arrow="off")
    st.warning("同じ14便でも、分母を変えると **約0.4％** にも **約24％** にもなる。割合を見たら、まず『何を100％にしたか』を確かめる"
               "（🧪『体は何でできている？』の『水を除く』スイッチと同じ）。", icon="➗")
    ui.reading_card(
        axis="欠航の原因（装置の区分／それ以外）と、便の数",
        unit="便、％（分母が『発着便』か『欠航便』かで値が変わる）",
        control="そろっていない：天気・季節・便の数。装置があった年の同じ時期の欠航数は、この資料にない",
        can="この期間の欠航59便のうち、装置の区分が原因と言えるのは14便（発着便の約0.4％）",
        cannot="『装置がないと欠航が59便増える』こと（59便には台風などほかの原因も含まれる）。ほかの年・ほかの空港でも同じ割合になること",
        protocols=["P2", "P3"], material="2015年の報道の数字")
    with st.container(border=True):
        st.markdown("**まとめ**：霧（地球）、電波（光と熱）、機体（物質）の**どれが欠けても、空港は動かない**。これを1枚の図にまとめよう。")
    with st.expander("⚠️ 授業で使う前に（注意点）"):
        for s in kc.NOTES:
            st.markdown(f"- {s}")

with st.container(border=True):
    st.markdown("**🌾 フィールドワーク（三原西部）へ**")
    st.markdown("空港と同じ三原市内。ハウスの温湿度ログから①の計算で**露点**を求め、霧が出た朝と比べる（第1コマの発展）。"
                "地学基礎（飽和水蒸気量・断熱膨張）、物理基礎（波長・電磁波）、化学基礎（金属・高分子・密度）、情報Ⅰ（割合とグラフ・相関と因果）につながる。")

ui.next_move_tag("kuko")
