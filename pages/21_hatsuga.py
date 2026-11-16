"""🌱 発芽を予測する：積算温度 ─ 畑の記録（2026-11）を教室で計算する

三原西部の畑の実際の記録（播種・定植・出芽の確認）を題材に、① 計算する → ② 見える化する → ③ 自分で判断する。
入力はこの画面の中だけで使い、保存も送信もしない。
"""
from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import hatsuga_core as hc
import ui

GREEN, ORANGE, GREY = "#2f6f4f", "#c9822b", "#a9bccf"

ui.hero("生命の科学（植物の生育と温度）× 情報Ⅰ モデル化とシミュレーション",
        "🌱 種は『日数』ではなく『あたたかさの合計』で芽を出す",
        f"❓ {hc.LEAD_QUESTION}")
ui.hint(hc.EASY_WORDS)

st.markdown("#### 畑の記録（三原西部・2026年11月）")
st.dataframe(pd.DataFrame([{"日付": f"{r['date']:%m/%d}", "作物": r["crop"], "したこと・見たこと": r["event"]}
                           for r in hc.FIELD_LOG]), hide_index=True, width="stretch")
st.caption("この表だけが実際の記録です。下のグラフの日ごとの気温は説明用の架空データ、"
           f"小麦の積算温度 {hc.WHEAT_GDD} ℃・日 は別の品種での推定値（{hc.GDD_SOURCE}）＝参考値です。")

tab1, tab2, tab3 = st.tabs(["① 計算する：何日で芽が出る？", "② 見える化する：積算温度のグラフ",
                            "③ 判断する：『見た日』と『出た日』"])

# ── ① 計算する ─────────────────────────
with tab1:
    ui.predict("hatsuga_days",
               f"小麦は、まいてからの積算温度が約 **{hc.WHEAT_GDD:.0f} ℃・日** に届くと芽を出すとする。"
               "**平均気温が 10℃ の日が続くと、芽が出るまで何日？**",
               actual=hc.days_to_emerge(10), unit="日", protocol="P4", min_value=1.0, max_value=60.0, value=7.0,
               field="生命の科学")
    c1, c2 = st.columns(2)
    temp = c1.slider("平均気温（℃）", -2.0, 20.0, 10.0, 0.5, key="hg_temp")
    gdd = c2.slider("芽が出るのに必要な積算温度（℃・日）", 60.0, 200.0, hc.WHEAT_GDD, 0.2, key="hg_gdd",
                    help="品種・土の水分・まく深さで変わる。自分の畑の記録で決めなおす値")
    d = hc.days_to_emerge(temp, gdd)
    m1, m2, m3 = st.columns(3)
    m1.metric("芽が出るまで", "届かない" if d == float("inf") else f"{d:.0f} 日")
    m2.metric("式", "積算温度 ÷ 平均気温")
    m3.metric("気温が半分になると", "─" if d == float("inf") else f"{hc.days_to_emerge(temp / 2, gdd):.0f} 日",
              "日数は2倍", delta_color="off", delta_arrow="off")
    xs = [x / 2 for x in range(4, 41)]
    fig = go.Figure(go.Scatter(x=xs, y=[hc.days_to_emerge(x, gdd) for x in xs], mode="lines",
                               line=dict(color=GREEN, width=3)))
    if d != float("inf") and temp >= 2:
        fig.add_trace(go.Scatter(x=[temp], y=[d], mode="markers", marker=dict(color=ORANGE, size=12)))
    fig.update_layout(height=280, margin=dict(t=20, b=10, l=10, r=10), xaxis_title="平均気温（℃）",
                      yaxis_title="芽が出るまで（日）", showlegend=False)
    st.plotly_chart(fig, width="stretch")
    st.markdown("気温と日数は**反比例**。寒くなるほど、同じ1℃の差が日数を大きく動かす。"
                "パンの発酵（🦠 実験2）で『温度が上がると速くなる』と確かめたのと、同じ形の関係。")

# ── ② 見える化する ───────────────────────
with tab2:
    st.markdown("#### 毎日の気温を足していくと、いつ線をこえる？")
    k1, k2 = st.columns(2)
    start = k1.slider("まいた直後の平均気温（℃）", 4.0, 16.0, 11.0, 0.5, key="hg_start")
    drop = k2.slider("1日あたりの下がり方（℃）", 0.0, 0.4, 0.12, 0.02, key="hg_drop")
    temps = hc.synth_temps(start_temp=start, drop_per_day=drop)
    cum = hc.accumulate(temps)
    n = hc.emerge_day(temps)
    days = [hc.WHEAT_SOWN + timedelta(days=i) for i in range(1, len(temps) + 1)]
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=days, y=temps, name="日平均気温（℃）", marker_color=GREY, yaxis="y2", opacity=0.6))
    fig2.add_trace(go.Scatter(x=days, y=cum, name="積算温度（℃・日）", mode="lines", line=dict(color=GREEN, width=3)))
    fig2.add_hline(y=hc.WHEAT_GDD, line_dash="dash", line_color=ORANGE,
                   annotation_text=f"出芽の目安 {hc.WHEAT_GDD} ℃・日", annotation_position="top left")
    fig2.update_layout(height=330, margin=dict(t=30, b=10, l=10, r=10), legend=dict(orientation="h", y=1.15),
                       yaxis=dict(title="積算温度（℃・日）"),
                       yaxis2=dict(title="日平均気温（℃）", overlaying="y", side="right", showgrid=False))
    st.plotly_chart(fig2, width="stretch")
    if n is None:
        st.error("この条件では、45日たっても目安に届かない。寒すぎる時期の播種は、芽が出る前に種が傷むおそれがある。")
    else:
        st.success(f"出芽の予測：**{hc.forecast(hc.WHEAT_SOWN, temps):%m/%d} ごろ**（まいてから {n} 日目）。"
                   "この日の前後に畑を見に行けば、予想と実際のずれ（δ）を測れる。")
    st.caption("🧪 気温は架空データです。気象庁の過去の気象データや、畑に置いた温度計の記録に置きかえると、自分の畑の予測になります。")

# ── ③ 判断する ─────────────────────────
with tab3:
    st.markdown("#### ほうれん草の芽は『いつ出た』と言える？")
    st.markdown(f"**{hc.SPINACH_SOWN:%m/%d}** にまき、**{hc.SPINACH_SEEN:%m/%d}** に芽が出ているのを見た。"
                "では、芽が出たのは何日目だろう。")
    opts = {"見ていない（まいてから一度も）": None}
    opts |= {f"{hc.SPINACH_SOWN + timedelta(days=k):%m/%d}（{k}日目）に見て、まだ出ていなかった":
             hc.SPINACH_SOWN + timedelta(days=k) for k in (5, 8, 11, 14)}
    pick = st.radio("その前に畑を見たのは？", list(opts), key="hg_check")
    lo, hi = hc.emergence_interval(hc.SPINACH_SOWN, hc.SPINACH_SEEN, opts[pick])
    j1, j2 = st.columns(2)
    j1.metric("言えること", f"{lo + 1}〜{hi} 日目のどこか", f"幅 {hi - lo} 日", delta_color="off", delta_arrow="off")
    j2.metric("言えないこと", f"『{hi}日で発芽した』")
    if hi - lo > 7:
        st.warning(f"『{hi}日目に見た』は『{hi}日で出た』ではない。見に行く回数が少ないと、答えの幅が広いままになる。")
    else:
        st.success("見に行く間隔をせばめると、答えの幅もせばまる。毎日は行けないとき、かわりに測り続けてくれるのがセンサー（IoT）。")
    st.markdown("**小麦で同じ失敗をしないために**：② の予測日の**少し前から**見はじめ、『まだ出ていない日』も野帳に書く。"
                "出ていなかった記録が、幅の下限になる。")
    ui.reading_card(
        axis="まいてからの日数（横） と 芽が出たかどうか（縦）", unit="日（積算温度なら ℃・日）",
        control="そろえた：同じ畝・同じ日にまいた種。変えた：見に行く日（測る間隔）",
        can="芽が出たのは、前に見た日より後で、確認した日以前であること",
        cannot="芽が出た正確な日。この品種に必要な積算温度（気温を毎日測っていないと計算できない）",
        protocols=["P3", "P2"], material="畑の記録の表")
    st.caption("➡️ 毎日止めずに測るしくみは、左メニュー「📡 IoTでハウスを測る」へ。")
