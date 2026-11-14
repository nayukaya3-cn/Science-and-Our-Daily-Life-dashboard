"""📡 フィールドワーク実践：理科の教員免許（科学と人間生活）× IoTアプリ構築・運用支援

「測る → 貯める → 見る → 知らせる → 動かす」を、三原西部のハウスで作って回す。
理科は『何を測れば何が言えるか』、IoTは『それを毎日止めずに動かす』を受け持つ。
入力はこの画面の中だけで使い、保存も送信もしない（センサーのグラフは説明用の架空データ。鍵・パスワードの入力欄は作らない）。
"""
import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import guard
import iot_core as ic
import ui

BLUE, GREEN, ORANGE, GREY = "#4a6a8a", "#4a8a3a", "#c9822b", "#a9bccf"

ui.hero("科学と人間生活 ｜ 4領域を横断 ｜ フィールドワーク実践（三原西部のハウス・圃場）× 情報Ⅰ",
        f"📡 {ic.TITLE}",
        f"❓ {ic.LEAD_QUESTION}　理科は『何を測れば、何が言えるか』を決め、IoTは『それを毎日止めずに動かす』。"
        "2つを掛けると、作って終わりの工作でも、見て終わりの見学でもないフィールドワークになる。")
ui.hint(ic.EASY_WORDS)

ui.lesson_plan([{"回": a, "場所": b, "やること": c, "理科の見方": d, "情報Ⅰ・IoT": e, "成果物": f}
                for a, b, c, d, e, f in ic.LESSONS], "🧑‍🏫 先生向け：6回の構成（50分×6・うち2回はハウス）")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "① 掛け算の地図", "② CO2と換気（測る）", "③ センサーとデータ（貯める・見る）",
    "④ 知らせる・動かす", "⑤ いくらで何ができる？", "⑥ 伴走と運用（先生・支援者向け）"])

# ── ① 掛け算の地図 ─────────────────────────────
with tab1:
    st.markdown("#### 免許 × IoT支援 ＝ フィールドワーク実践")
    a, b, c = st.columns(3)
    with a.container(border=True):
        st.markdown("**🔬 理科の教員免許**  \n（科学と人間生活）")
        st.caption("何を測れば、何が言えるか。条件をそろえる・単位・誤差・基準値の根拠。")
    with b.container(border=True):
        st.markdown("**📡 IoTアプリ構築・運用支援**")
        st.caption("配線・クラウド・通知・保守。毎日止めずに動かし、直し続ける。")
    with c.container(border=True):
        st.markdown("**🌾 フィールドワーク実践**")
        st.caption("ハウスと畑で、作って・測って・運用する。数字と実物を見くらべる。")

    st.markdown("#### 8つの段：どの段を、理科と情報Ⅰのどこで学ぶか")
    st.dataframe(pd.DataFrame(ic.STAGES, columns=["段", "やさしく言うと", "科学と人間生活での見方", "情報Ⅰの単元"]),
                 hide_index=True, width="stretch")

    st.markdown("#### 学習計画をつくる：資料を選ぶと、抜けている段が見える")
    names = {m["name"]: m["id"] for m in ic.MATERIALS}
    picked = st.multiselect("使う資料（最初はIoT講座3本）", list(names), key="iot_pick",
                            default=[ic.BY_ID[i]["name"] for i in ic.IOT_CORE_IDS])
    ids = [names[n] for n in picked]
    ps = ic.plan_summary(ids)
    k1, k2, k3 = st.columns(3)
    k1.metric("動画の合計", f"{ps['hours']:g} 時間", f"{ps['lectures']} レクチャー", delta_color="off", delta_arrow="off")
    k2.metric("カバーした段", f"{ps['covered']} / {len(ic.STAGE_NAMES)}")
    k3.metric("抜けている段", "なし" if not ps["missing"] else "・".join(ps["missing"]))
    if ids:
        fig = go.Figure(go.Heatmap(
            z=ic.matrix(ids), x=ic.STAGE_NAMES, y=[ic.BY_ID[i]["name"] for i in ids],
            colorscale=[[0, "#f3f5f7"], [1, GREEN]], showscale=False, xgap=3, ygap=3,
            hovertemplate="%{y}<br>段：%{x}<extra></extra>"))
        fig.update_layout(height=90 + 38 * len(ids), margin=dict(t=10, b=10, l=10, r=10),
                          yaxis=dict(autorange="reversed"), xaxis=dict(side="top"))
        st.plotly_chart(fig, width="stretch")
        st.caption("緑のマス＝その資料がその段を扱っている。縦に見て緑が1つもない列が『抜けている段』。")
        st.dataframe(pd.DataFrame([{"資料": ic.BY_ID[i]["name"], "レベル": ic.BY_ID[i]["level"],
                                    "科学と人間生活の領域": ic.BY_ID[i]["field"], "フィールドワークでの役割": ic.BY_ID[i]["role"]}
                                   for i in ids]), hide_index=True, width="stretch")
    if ps["missing"]:
        st.warning(f"**{'・'.join(ps['missing'])}** の段が抜けている。IoT講座だけでは『作って動いた』で終わりやすい。"
                   "運用の輪・直売・伴走の資料を足すと、列が埋まる。", icon="🧩")
    else:
        st.success("8つの段がすべて埋まった。あとは、どの順番で・だれが・どこまでやるかを ⑥ で決める。", icon="✅")
    ui.reading_card(
        axis="資料（縦） と 段（横）", unit="扱っている／いない（2値）、時間",
        control="そろえた：段の分け方（8つ）。変えた：選ぶ資料",
        can="選んだ資料で、どの段が手薄か・全部で何時間かかるか",
        cannot="その段がどれだけ深く学べるか（マスは深さを表さない）・自分にとっての難しさ",
        protocols=["P2", "P3"], material="資料×段のマス目")
    st.caption("出どころ：作成者がまとめた資料10本の概要。講座名・講師名・事業所名は載せていません。時間とレクチャー数は資料に書かれていた値です（📐 3DプリンタとCAD は未記入のため 0）。")

# ── ② CO2と換気 ─────────────────────────────
with tab2:
    st.markdown("#### 教室：40人が窓を閉めたままだと、何分で基準をこえる？")
    cr = ic.CLASSROOM
    actual = ic.minutes_to_reach(1500, cr["people"], cr["volume"], 0)
    ui.predict("iot_co2_min", f"{cr['people']}人の教室（{cr['volume']:.0f} m³）で、窓も換気扇も止めた。"
               f"外気と同じ {ic.OUTDOOR_PPM} ppm から始めて、**1500 ppm（学校環境衛生基準）に届くまで何分？**",
               round(actual, 1), "分", protocol="P4", min_value=0.0, max_value=300.0, step=1.0, value=60.0,
               fmt="%.0f", field="フィールドワーク実践")

    c1, c2, c3 = st.columns(3)
    people = c1.slider("人数", 1, 60, cr["people"], key="iot_people")
    volume = c2.slider("部屋の体積（m³）", 30, 600, int(cr["volume"]), 10, key="iot_volume", help="床の広さ × 天井の高さ")
    vent = c3.slider("換気量（m³/時）", 0, 3000, 300, 50, key="iot_vent", help="窓や換気扇で1時間に入れかわる空気の量")
    gen = st.slider("1人が1時間に出すCO2（m³/時）", 0.010, 0.040, ic.CO2_PER_PERSON, 0.002, format="%.3f", key="iot_gen",
                    help="座って軽い作業で 0.02 ほど。じっとしていれば少なく、体を動かすと増える")
    t, c = ic.co2_series(people, volume, vent, 100, gen=gen)
    eq = ic.steady_ppm(people, vent, gen)
    m1500 = ic.minutes_to_reach(1500, people, volume, vent, gen=gen)
    need = ic.required_vent(people, 1000, gen)
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("落ち着く濃度", "上がり続ける" if math.isinf(eq) else f"{eq:,.0f} ppm")
    r2.metric("1500 ppm まで", "届かない" if math.isinf(m1500) else f"{m1500:.0f} 分")
    r3.metric("換気回数", f"{vent / volume:.1f} 回/時", help="1時間に部屋の空気が何回入れかわるか")
    r4.metric("1000 ppm に保つ換気量", f"{need:,.0f} m³/時", f"1人あたり {need / people:.0f} m³/時", delta_color="off",
              delta_arrow="off")
    fig = go.Figure(go.Scatter(x=t, y=c, mode="lines", line=dict(color=BLUE, width=3), name="CO2濃度"))
    for name, v in ic.LIMITS.items():
        fig.add_hline(y=v, line_dash="dash", line_color=ORANGE, annotation_text=f"{name} {v} ppm",
                      annotation_position="top left")
    fig.update_layout(height=320, margin=dict(t=20, b=10, l=10, r=10), xaxis_title="時間（分・授業2コマ分）",
                      yaxis_title="CO2濃度（ppm）", showlegend=False, yaxis_range=[300, max(2200, float(min(c.max(), 6000)) + 200)])
    st.plotly_chart(fig, width="stretch")
    st.code("落ち着く濃度[ppm] ＝ 外気[ppm] ＋ 人数 × 1人の発生量[m³/時] ÷ 換気量[m³/時] × 1,000,000", language="text")
    ui.hint("お風呂にたとえると、蛇口（人の呼吸）から入る量と、排水口（換気）から出る量が同じになったところで水位（濃度）が止まる。"
            "排水口を閉めれば、水位は上がり続ける。")
    st.caption("基準値の出どころ：建築物衛生法（1000 ppm 以下）、学校環境衛生基準（1500 ppm 以下が望ましい）、"
               f"換気の目安 1人あたり毎時{ic.VENT_PER_PERSON} m³（厚生労働省の換気資料）。授業の前に最新の資料で確かめる。")

    st.divider()
    st.markdown("#### ハウス：晴れた朝、閉め切るとCO2は逆に『足りなく』なる")
    st.caption(f"三原西部のハウス（{ic.HOUSE['width']} m × {ic.HOUSE['length']} m・平均の高さ {ic.HOUSE['height']} m と仮定 ＝ "
               f"{ic.house_volume():.0f} m³）。人は出す側、植物は日中に吸う側。")
    h1, h2 = st.columns(2)
    uptake = h1.slider("植物がCO2を吸う速さ（g/㎡・時、外気と同じ濃度のとき）", 0.0, 4.0, 1.5, 0.1, key="iot_uptake",
                       help="葉がよく茂った作物で 1〜3 ほど（幅のある仮定）。苗が小さいうちはずっと小さい")
    ach = h2.slider("ハウスの換気回数（回/時）", 0.0, 20.0, 1.0, 0.5, key="iot_ach",
                    help="閉め切りで 0.5〜2 ほど、側面を開けると 10 以上になる（目安）")
    ht, hc = ic.house_series(uptake, ach, 180)
    heq = ic.house_steady_ppm(uptake, ach)
    q1, q2 = st.columns(2)
    q1.metric("落ち着く濃度", f"{heq:.0f} ppm", f"外気 {ic.OUTDOOR_PPM} ppm より {ic.OUTDOOR_PPM - heq:.0f} 低い",
              delta_color="off", delta_arrow="off")
    q2.metric("光合成の速さ（外気のときを100として）",
              f"{(heq - ic.COMPENSATION_PPM) / (ic.OUTDOOR_PPM - ic.COMPENSATION_PPM) * 100:.0f}",
              help="この模型では、吸う速さは（濃度 − 補償点）に比例すると仮定している")
    fig = go.Figure(go.Scatter(x=ht, y=hc, mode="lines", line=dict(color=GREEN, width=3)))
    fig.add_hline(y=ic.OUTDOOR_PPM, line_dash="dot", line_color=BLUE, annotation_text="外気")
    fig.add_hline(y=ic.COMPENSATION_PPM, line_dash="dot", line_color=ORANGE, annotation_text="補償点（これ以下では育たない）")
    fig.update_layout(height=280, margin=dict(t=20, b=10, l=10, r=10), xaxis_title="日が当たりはじめてからの時間（分）",
                      yaxis_title="CO2濃度（ppm）", showlegend=False, yaxis_range=[0, 480])
    st.plotly_chart(fig, width="stretch")
    st.markdown("**ここから議論すること**  \n"
                "1. 教室では『高すぎる』が問題、ハウスでは『低すぎる』が問題。**同じセンサー・同じ式で、基準が逆向き**になる  \n"
                "2. 冬は保温のために閉めたい、でもCO2は入れたい。**温度とCO2のどちらを優先するか**は、測らないと決められない  \n"
                "3. この模型の仮定（吸う速さは濃度に比例）は、**1週間の実測で確かめる**（第3回）")
    ui.reading_card(
        axis="時間（横） と CO2濃度（縦）", unit="分、ppm（100万分の1）",
        control="そろえた：部屋の体積・外気の濃度・1人の発生量。変えた：人数と換気量（ハウスでは吸う速さと換気回数）",
        can="発生量と換気量のつり合いで、濃度がどこに落ち着くか・基準をこえるまでの時間",
        cannot="部屋の中の場所による濃度のむら（模型は空気がよく混ざっていると仮定）・感染のリスクそのもの（CO2は換気の目安）",
        protocols=["P4", "P2"], material="2つのグラフ（教室・ハウス）")
    ui.exam_question("iot_exam", ic.EXAM)

# ── ③ センサーとデータ ─────────────────────────────
with tab3:
    st.markdown("#### 何を測る？　5つの数字と、理科での意味")
    st.dataframe(pd.DataFrame(ic.SENSORS, columns=["測るもの", "つなぎ方", "単位", "理科での意味", "番地の例"]),
                 hide_index=True, width="stretch")
    st.caption("番地は機種によって違う。買ったセンサーの説明書（データシート）で必ず確かめる。")

    st.markdown("#### 番地（アドレス）を2進数で読む：情報Ⅰとつなぐ")
    ui.hint("I2C（アイ・ツー・シー）は、2本の線に何個ものセンサーをぶら下げるつなぎ方。"
            "先生が『出席番号68番の人、温度は？』と呼ぶように、番地で相手を選ぶ。")
    addr = st.slider("番地（10進数）", 0, 127, 0x44, key="iot_addr")
    info = ic.i2c_info(addr)
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("10進数", info["dec"])
    b2.metric("16進数", info["hex"])
    b3.metric("2進数（7ビット）", info["bin"])
    b4.metric("ふつうに使える？", "はい" if info["usable"] else "予約済み")
    st.caption(f"7ビットで表せるのは 2⁷ ＝ 128 通り。そのうち両端は特別な用途に予約されていて、ふつうに使えるのは "
               f"{ic.I2C_MIN}〜{ic.I2C_MAX}（0x08〜0x77）の {ic.i2c_usable_count()} 個。同じ番地のセンサーを2個つなぐと、区別できない。")

    st.markdown("#### 表はいつ、いっぱいになる？")
    ui.predict("iot_rows", "CO2・気温・湿度・照度・水深の5つに、日付と時刻を足した **7列** を **10分ごと** に1行ずつ書きこむ。"
               "1ファイルの上限は1000万セル。**いっぱいになるまで、およそ何年？**",
               round(ic.days_until_full(7, 10) / 365, 1), "年", protocol="P1", min_value=0.0, max_value=100.0, step=1.0,
               value=3.0, fmt="%.0f", field="フィールドワーク実践")
    d1, d2 = st.columns(2)
    cols = d1.slider("列の数", 2, 20, 7, key="iot_cols")
    interval = d2.select_slider("測る間隔（分）", [1, 2, 5, 10, 15, 30, 60], 10, key="iot_interval")
    days = ic.days_until_full(cols, interval)
    e1, e2, e3 = st.columns(3)
    e1.metric("1日の行数", f"{ic.rows_per_day(interval):.0f} 行")
    e2.metric("1日に増えるセル", f"{cols * ic.rows_per_day(interval):,.0f}")
    e3.metric("いっぱいになるまで", f"{days / 365:.1f} 年" if days >= 365 else f"{days:.0f} 日")
    ui.hint("間隔を10分から1分にすると、データは10倍になる。細かく測るほどよいとは限らない。"
            "『何を知りたいか』で間隔を決める（気温の日変化なら10分で十分）。")

    st.divider()
    st.markdown("#### ハウスの1日（架空データ）を読む：まとめメールの中身をつくる")
    st.warning("このグラフは、しくみを説明するための**架空データ**です。実測ではありません。設置後は自分たちの表の数字に置きかえます。", icon="🧪")
    f1, f2, f3 = st.columns(3)
    item = f1.selectbox("見る数字", ["CO2", "気温", "湿度", "照度", "水深"], key="iot_item")
    outlier = f2.toggle("センサーの誤動作を1点まぜる（CO2）", key="iot_outlier")
    missing = f3.toggle("昼の1時間を欠測にする（CO2）", key="iot_missing")
    day = ic.synth_day(interval_min=10, outlier=outlier, missing=missing)
    unit = {"CO2": "ppm", "気温": "℃", "湿度": "%", "照度": "lx", "水深": "mm"}[item]
    s = ic.summary(day[item])
    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("平均", f"{s['mean']:,.0f} {unit}")
    g2.metric("中央値", f"{s['median']:,.0f} {unit}")
    g3.metric("最小", f"{s['min']:,.0f} {unit}")
    g4.metric("最大", f"{s['max']:,.0f} {unit}")
    g5.metric("欠測", f"{s['missing']} 件", f"{s['n']} 件は有効", delta_color="off", delta_arrow="off")
    fig = go.Figure(go.Scatter(x=day["時刻"], y=day[item], mode="lines+markers", marker=dict(size=4),
                               line=dict(color=BLUE, width=2), connectgaps=False))
    fig.add_hline(y=s["mean"], line_dash="dash", line_color=ORANGE, annotation_text="平均")
    fig.add_hline(y=s["median"], line_dash="dot", line_color=GREEN, annotation_text="中央値", annotation_position="bottom right")
    fig.update_layout(height=300, margin=dict(t=20, b=10, l=10, r=10), xaxis_title="時刻（時）", yaxis_title=f"{item}（{unit}）",
                      showlegend=False, xaxis=dict(dtick=3, range=[0, 24]))
    st.plotly_chart(fig, width="stretch")
    if item == "CO2" and outlier:
        base = ic.summary(ic.synth_day(interval_min=10, missing=missing)["CO2"])
        st.error(f"ありえない値が1点入っただけで、平均は {base['mean']:.0f} → {s['mean']:.0f} ppm に動いた。"
                 f"中央値は {base['median']:.0f} → {s['median']:.0f} ppm でほとんど動かない。"
                 "まとめメールに『平均』だけを書くと、1点の誤動作でだまされる。")
    if item == "CO2" and missing:
        st.info("線が切れているところが欠測。『0 ppm』と書きこむプログラムにすると、平均が大きく下がってしまう。"
                "測れなかったときは、空欄のまま残す。", icon="🕳️")
    ui.reading_card(
        axis="時刻（横） と センサーの値（縦）", unit=f"時、{unit}",
        control="そろえた：測る間隔（10分）・同じ1日・同じ置き場所。変えた：見る数字、誤動作・欠測のあり／なし",
        can="1日の中での上がり下がりの形・外れ値に強い代表値はどれか",
        cannot="ほかの日も同じ形か（1日分だけ）・CO2が下がった原因が光合成か換気か（窓の開閉の記録がないと分けられない）",
        protocols=["P2", "P3"], material="1日分のグラフと5つのまとめの数字")

# ── ④ 知らせる・動かす ─────────────────────────────
with tab4:
    st.markdown("#### 警報メール：『オオカミ少年』にしない設計")
    ui.hint("警報が1日に何度も鳴ると、だれも見なくなる。鳴らなすぎると、本当の異常を見逃す。"
            "センサーの読みは毎回少しずつぶれるので、しきい値のすぐ下にいるだけで、たまたま上にはみ出すことがある。")
    a1, a2, a3 = st.columns(3)
    true_v = a1.slider("本当のCO2濃度（ppm・異常ではない状態）", 400, 1500, 900, 10, key="iot_true")
    thr = a2.slider("警報のしきい値（ppm）", 600, 2000, 1000, 50, key="iot_thr")
    sd = a3.slider("センサーの読みのぶれ（ppm）", 0, 150, 50, 5, key="iot_sd",
                   help="同じ空気を何回も測ったときのばらつき（標準偏差）。安いセンサーほど大きい")
    a4, a5 = st.columns(2)
    iv = a4.select_slider("測る間隔（分）", [1, 2, 5, 10, 15, 30, 60], 10, key="iot_iv2")
    ncon = a5.slider("何回つづけてこえたら警報にする？", 1, 6, 1, key="iot_ncon")
    p1 = ic.exceed_prob(true_v, thr, sd)
    fa = ic.false_alarms_per_day(true_v, thr, sd, iv, ncon)
    w1, w2, w3 = st.columns(3)
    w1.metric("1回の測定がたまたまこえる確率", f"{p1:.1%}")
    w2.metric("まちがい警報（誤報）", f"{fa:.2f} 回/日" if fa >= 0.01 else "ほぼ0 回/日",
              f"月に約 {fa * 30:.0f} 回" if fa >= 0.05 else "月に1回未満", delta_color="off", delta_arrow="off")
    w3.metric("本当の異常に気づく遅れ", f"{ic.alert_delay_min(iv, ncon):.0f} 分〜", help="つづけて数える分だけ、警報は遅くなる")
    ns = list(range(1, 7))
    fig = go.Figure(go.Bar(x=[f"{n}回" for n in ns], y=[ic.false_alarms_per_day(true_v, thr, sd, iv, n) for n in ns],
                           marker_color=[ORANGE if n == ncon else GREY for n in ns]))
    fig.update_layout(height=260, margin=dict(t=20, b=10, l=10, r=10), xaxis_title="つづけてこえた回数の条件",
                      yaxis_title="誤報（回/日）", showlegend=False)
    st.plotly_chart(fig, width="stretch")
    st.caption("計算の仮定：読みのぶれは正規分布で、毎回の測定は独立。実際は続けて同じ向きにぶれることもあるので、設置後に誤報の回数を数えて確かめる。")

    st.markdown("##### 警報が鳴った。本当に異常である確率は？（ベイズの考え方）")
    y1, y2, y3 = st.columns(3)
    prior = y1.slider("異常の起こりやすさ（100回の測定のうち）", 0.1, 20.0, 1.0, 0.1, key="iot_prior") / 100
    hit = y2.slider("異常を見つける率（%）", 50, 100, 95, key="iot_hit") / 100
    fr = y3.slider("異常でないのに鳴る率（%）", 0.1, 20.0, 5.0, 0.1, key="iot_fr") / 100
    post = ic.bayes_alert(prior, hit, fr)
    st.metric("警報が鳴ったとき、本当に異常である確率", f"{post:.0%}",
              f"鳴る前の見込み {prior:.1%} から更新", delta_color="off", delta_arrow="off")
    if post < 0.5:
        st.warning("鳴った警報の半分以上がまちがい。異常がめったに起きないと、誤報率が小さくても『はずれ』の警報のほうが多くなる。"
                   "警報が来たら、まずハウスへ行って実物を見る（数字と実物を見くらべる）。")

    st.divider()
    st.markdown("#### 自動水やり：しきい値は1本より2本")
    ui.predict("iot_pump", "水深が 40 mm より浅くなったらポンプON、深くなったらOFF、という**しきい値1本**の規則にした。"
               "読みが ±1 mm ぶれるとき、**1日にポンプが入切する回数**は？（しきい値を 35 mm と 45 mm の2本にすると12回）",
               float(ic.pump_sim(40, 40)["switches"]), "回", protocol="P4", min_value=0.0, max_value=1000.0, step=1.0,
               value=12.0, fmt="%.0f", field="フィールドワーク実践")
    z1, z2, z3 = st.columns(3)
    lo, hi = z1.slider("ONにする水深 〜 OFFにする水深（mm）", 20, 60, (35, 45), key="iot_band")
    nz = z2.slider("水深センサーの読みのぶれ（mm）", 0.0, 3.0, 1.0, 0.1, key="iot_nz")
    drain = z3.slider("水が減る速さ（mm/時）", 0.5, 10.0, 3.0, 0.5, key="iot_drain", help="植物が吸う分と蒸発する分")
    sim = ic.pump_sim(lo, hi, noise_sd=nz, drain_mm_h=drain)
    one = ic.pump_sim((lo + hi) / 2, (lo + hi) / 2, noise_sd=nz, drain_mm_h=drain)
    v1, v2, v3 = st.columns(3)
    v1.metric("入切の回数（この設定）", f"{sim['switches']} 回/日")
    v2.metric("しきい値1本なら", f"{one['switches']} 回/日", f"中央の {(lo + hi) / 2:.0f} mm 1本", delta_color="off",
              delta_arrow="off")
    v3.metric("水深の動く幅", f"{sim['min']:.0f}〜{sim['max']:.0f} mm")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sim["t"], y=sim["depth"], mode="lines", line=dict(color=BLUE, width=2), name="水深"))
    fig.add_trace(go.Scatter(x=sim["t"], y=sim["pump"] * (hi - lo + 4) + lo - 2, mode="lines", line=dict(color=ORANGE, width=1),
                             name="ポンプON", opacity=0.6, line_shape="hv"))
    fig.add_hline(y=lo, line_dash="dash", line_color=GREEN, annotation_text="ON", annotation_position="bottom left")
    fig.add_hline(y=hi, line_dash="dash", line_color=GREEN, annotation_text="OFF", annotation_position="top left")
    fig.update_layout(height=300, margin=dict(t=20, b=10, l=10, r=10), xaxis_title="時間（時）", yaxis_title="水深（mm）",
                      legend=dict(orientation="h", y=1.12), xaxis=dict(dtick=3))
    st.plotly_chart(fig, width="stretch")
    st.markdown("2本のしきい値のあいだは『いまの状態を続ける』。この工夫を**ヒステリシス**という。"
                "エアコンやこたつの温度調節、そして体温や血糖値を一定に保つしくみ（恒常性）も、同じ形をしている。")
    ui.reading_card(
        axis="時間（横） と 水深・ポンプの入切（縦）", unit="時、mm、回/日",
        control="そろえた：水が減る速さ・ポンプの強さ・読みのぶれ。変えた：しきい値の本数と幅",
        can="しきい値の幅を広げると入切は減り、水深の動く幅は広がる（どちらかを取れば、どちらかをゆずる）",
        cannot="植物にとって最適な水深（それは育てて測らないとわからない）・ポンプや配管が故障したときの動き",
        protocols=["P4", "P1"], material="水深とポンプのグラフ")

# ── ⑤ いくらで何ができる？ ─────────────────────────────
with tab5:
    st.markdown("#### 1台つくると、いくら？")
    st.warning("下の値段は**仮の値**です。部品の値段は時期と店で大きく変わります。買う前に必ず調べて、表を書きかえてください。", icon="🧾")
    bom = pd.DataFrame([{"買う": True, "部品": n, "役割": r, "値段（円）": p, "なくても始められる": opt} for n, r, p, opt in ic.BOM])
    edited = st.data_editor(bom, hide_index=True, width="stretch", key="iot_bom", num_rows="fixed",
                            disabled=["部品", "役割", "なくても始められる"],
                            column_config={"値段（円）": st.column_config.NumberColumn(min_value=0, max_value=200000, step=100)})
    total = ic.bom_total(edited["値段（円）"].fillna(0).tolist(), edited["買う"].tolist())
    o1, o2, o3 = st.columns(3)
    watt = o1.slider("本体の消費電力（W）", 2.0, 10.0, ic.POWER_W, 0.5, key="iot_watt", help="機種と負荷で 3〜8W ほど")
    yen = o2.slider("電気代の単価（円/kWh）", 20.0, 50.0, ic.YEN_PER_KWH, 1.0, key="iot_yen", help="契約で違う。検針票で確かめる")
    months = o3.slider("使う期間（月）", 1, 36, 8, key="iot_months", help="麦なら播種（11月）から収穫（6月）まで約8か月")
    monthly = ic.power_cost_month(watt, yen)
    per = ic.cost_per_reading(total, months, monthly, 5, 10)
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("材料費", f"{total:,} 円", f"資料の目安 {ic.BUDGET_RANGE[0] // 10000}〜{ic.BUDGET_RANGE[1] // 10000}万円",
              delta_color="off", delta_arrow="off")
    t2.metric("電気代", f"{monthly:,.0f} 円/月", f"{watt * 24 * 30 / 1000:.1f} kWh", delta_color="off", delta_arrow="off")
    t3.metric(f"{months}か月の合計", f"{total + monthly * months:,.0f} 円")
    t4.metric("数字1個あたり", f"{per:.3f} 円", "5つの数字を10分ごと", delta_color="off", delta_arrow="off")
    fig = go.Figure(go.Bar(x=["材料費（最初に1回）", f"電気代（{months}か月）", "クラウド（無料枠の中）"],
                           y=[total, monthly * months, 0], marker_color=[BLUE, ORANGE, GREEN],
                           text=[f"{total:,}円", f"{monthly * months:,.0f}円", "0円"], textposition="outside"))
    fig.update_layout(height=280, margin=dict(t=30, b=10, l=10, r=10), yaxis_title="円", showlegend=False)
    st.plotly_chart(fig, width="stretch")
    ui.hint("毎朝ハウスまで見に行く手間とくらべてみよう。片道15分の道を1日1回へらせるなら、8か月で約120時間。"
            "ただし『行かなくてよくなる』のではなく、『行くべき日がわかる』のがIoTの役目。")

    st.markdown("#### 3Dプリンタで作る部品（センサーのカバー・カメラの台）")
    p1c, p2c = st.columns(2)
    grams = p1c.slider("部品1個の重さ（g）", 5, 300, 40, 5, key="iot_grams")
    ykg = p2c.slider("フィラメントの値段（円/kg）", 1500, 8000, 3000, 100, key="iot_ykg")
    st.metric("部品1個の材料費", f"{ic.filament_cost(grams, ykg):,.0f} 円")
    st.caption("ハウスの中は夏に50℃をこえることがある。PLAは60℃前後で柔らかくなるので、置き場所と材料を「🖨️ プラスチック：3Dプリンタの糸」のページで確かめる。")

    st.markdown("#### 自分で設計する：3Dプリンタ向けのコツ")
    st.dataframe(pd.DataFrame(ic.DESIGN_TIPS, columns=["コツ", "なぜ", "ハウスのIoTでの例"]), hide_index=True, width="stretch")
    st.caption("資料に挙がっていた設計のコツのうち3つ。扱う材料：" + "・".join(ic.FILAMENTS_IOT) +
               "（熱への強さは「🖨️ プラスチック：3Dプリンタの糸」で比べる）。")
    st.markdown("##### はめ合いの隙間：図面どおりに描くと入らない")
    ui.hint("3Dプリンタは、溶かした糸を少しずつ重ねる。重ねた糸がわずかに広がるので、穴は図面より狭く、出っぱりは太く仕上がる。")
    f1, f2, f3 = st.columns(3)
    hole = f1.number_input("穴（溝）の幅：図面（mm）", 1.0, 100.0, 10.0, 0.05, key="iot_hole", format="%.2f")
    part = f2.number_input("差しこむ物の幅：図面（mm）", 1.0, 100.0, 10.0, 0.05, key="iot_part", format="%.2f")
    swell = f3.slider("印刷で太る量（片側・mm）", 0.0, 0.3, 0.1, 0.01, key="iot_swell",
                      help="機種・材料・設定で変わる仮定の値。小さな試し刷り（隙間を0.1mmずつ変えた見本）で確かめる")
    fit = ic.clearance_fit(hole, part, swell)
    msg = f"印刷後のすき間 {fit['gap']:+.2f} mm → **{fit['verdict']}**"
    {"入らない": st.error, "きつい": st.warning, "ちょうど": st.success, "ゆるい": st.info}[fit["verdict"]](msg)
    st.caption("『ちょうど』の幅（0.1〜0.4 mm）も目安。外して付け直すふたは広め、動かない差しこみは狭め、と目的で決める。")

    st.markdown("##### 人の3Dデータを使うときは、ライセンスを読む")
    st.dataframe(pd.DataFrame(ic.CC_TERMS, columns=["条件", "意味", "使うときにすること"]), hide_index=True, width="stretch")
    l1, l2, l3 = st.columns(3)
    terms = l1.multiselect("データに付いている条件", [t[0] for t in ic.CC_TERMS], default=["BY（表示）", "NC（非営利）"],
                           key="iot_cc")
    sell = l2.toggle("直売で売る品物・販促に使う", key="iot_cc_sell")
    mod = l3.toggle("形を変えて使う（穴を足す など）", key="iot_cc_mod")
    ok, notes = ic.cc_ok({t.split("（")[0] for t in terms}, commercial=sell, modify=mod)
    (st.success if ok else st.error)(("この使い方はできる。" if ok else "この使い方はできない。") +
                                     ("　" + "／".join(notes) if notes else ""))
    st.caption("クリエイティブ・コモンズ（CC）の考え方の要点だけ。実際に使う前に、データのページに書かれたライセンスの本文を確かめる。"
               "情報Ⅰの『知的財産権』の単元とつながる。")
    ui.reading_card(
        axis="費用の内わけ（材料費・電気代・クラウド）", unit="円、円/月、円/個",
        control="そろえた：測る数字（5つ）と間隔（10分）。変えた：部品の選び方・期間・電気代の単価",
        can="最初にかかるお金と、続けるのにかかるお金のどちらが大きいか",
        cannot="作る時間・直す時間の値段（人の手間は入っていない）・無料枠がこの先も続くか・太る量が自分の機種で何mmか（試し刷りが必要）",
        protocols=["P1", "P3"], material="部品の表と3本の棒グラフ")

# ── ⑥ 伴走と運用 ─────────────────────────────
with tab6:
    st.markdown("#### 『作って終わり』にしない：運用の輪")
    st.dataframe(pd.DataFrame(ic.OPS_LOOP, columns=["輪の段", "AIの運用（MLOps）では", "このフィールドワークでは"]),
                 hide_index=True, width="stretch")
    st.caption("輪を1周するたびに、変えるのは1か所だけ（しきい値、測る間隔、置き場所…）。そうすれば、前の週とくらべて効果が言える（対照実験と同じ）。")

    st.markdown("#### 役割：その人の『得意』と仕事を組み合わせる")
    st.dataframe(pd.DataFrame([{"仕事": a, "内容": b, "向いている『得意』": c, "安全・配慮": d, "考え方の型": e}
                               for a, b, c, d, e in ic.ROLES]), hide_index=True, width="stretch")
    ui.hint("先生・支援者は『教える人』であると同時に『一緒に新しい使い方を発見する人』。"
            "決まった手順をなぞるのではなく、その人の武器になる関わり方を、役割を入れかえながら探す。")
    st.info("**安全の約束**：① 配線は電源を抜いてから　② ハンダごて・3Dプリンタのノズルと台は熱い（やけど）　"
            "③ 3Dプリンタのまわりに燃える物を置かず、動かしたまま無人にしない　④ 動いている基板を長く触らない　"
            "⑤ 水（ポンプ）と電気（コンセント）を同じ台に置かない", icon="🦺")

    st.markdown("#### 🔐 公開する前の点検（情報セキュリティ）")
    st.caption("このしくみは、クラウドの鍵・メールの送信・カメラの写真を扱う。プログラムを GitHub で公開するなら、下を1つずつ確かめる。")
    checked = [st.checkbox(f"{q}（{why}）", key=f"iot_sec_{i}") for i, (q, why, _) in enumerate(ic.SECURITY_CHECKS)]
    score = ic.security_score(checked)
    st.progress(score / ic.SECURITY_MAX, text=f"点検 {score} / {ic.SECURITY_MAX} 点")
    if score == ic.SECURITY_MAX:
        st.success("すべて確認できた。公開したあとも、鍵を作り直したときや人が入れかわったときに、もう一度点検する。")
    elif not all(checked[:2]):
        st.error("上の2つ（鍵を置かない・.gitignore）が済むまでは、公開しない。")

    st.markdown("##### ファイル名だけで点検する")
    st.caption("公開するフォルダの**ファイル名だけ**を1行に1つ書く。鍵やパスワードの**中身は絶対に貼らない**（この欄も、名前しか受け取らない設計です）。")
    raw = st.text_area("ファイル名（1行に1つ）", "main.py\nconfig.ini\nservice_account.json\ntoken.json\nREADME.md",
                       height=130, max_chars=1500, key="iot_files")
    names_in = [guard.clean_text(x, 120) for x in raw.splitlines() if x.strip()][:60]
    risky = ic.risky_files(names_in)
    if risky:
        st.dataframe(pd.DataFrame(risky, columns=["ファイル名", "気をつける理由"]), hide_index=True, width="stretch")
        st.markdown("`.gitignore` に書く行：")
        st.code("\n".join(ic.gitignore_lines(names_in)), language="text")
        st.caption("すでに公開してしまった鍵は、.gitignore に足しても履歴に残る。その鍵はクラウド側で無効にして、作り直す。")
    else:
        st.success("名前から見て危なそうなファイルは見つからなかった（中身までは確かめていないので、設定ファイルは自分の目で見る）。")

    st.markdown("#### 引きつぎ書をつくる")
    with st.form("iot_handover"):
        place = st.text_input("置き場所（個人の住所は書かない。例：ハウスの北側の棚）", max_chars=80)
        rule = st.text_area("警報と水やりの規則（何を見たら、何をするか）", max_chars=400, height=80)
        trouble = st.text_area("止まったときに最初に見るところ", max_chars=400, height=80)
        nextq = st.text_input("次の人にためしてほしいこと（変えるのは1か所）", max_chars=200)
        made = st.form_submit_button("引きつぎ書をつくる")
    if made:
        sheet = "\n".join([
            "📡 IoTフィールドワーク 引きつぎ書",
            f"問い：{ic.LEAD_QUESTION}",
            f"公開前の点検：{score} / {ic.SECURITY_MAX} 点",
            "", f"■ 置き場所\n{guard.clean_text(place, 80) or '（未記入）'}",
            f"■ 警報と水やりの規則\n{guard.clean_text(rule, 400) or '（未記入）'}",
            f"■ 止まったときに最初に見るところ\n{guard.clean_text(trouble, 400) or '（未記入）'}",
            f"■ 次の人にためしてほしいこと\n{guard.clean_text(nextq, 200) or '（未記入）'}",
            "", "※ 鍵・パスワード・個人の連絡先は、この紙に書かない。"])
        st.download_button("⬇️ 引きつぎ書（テキスト）をダウンロード", sheet.encode("utf-8"), "iot_hikitsugi.txt", "text/plain")
        st.caption("入力はこの画面の中だけで使い、サーバーには保存しません。")

st.divider()
st.markdown("**つながるページ**：🦠 微生物と発酵（温度と発酵の速さ）／ 🖨️ プラスチック：3Dプリンタの糸（PLAの熱の弱さ）／ "
            "🛡️ パニックプルーフ（井戸・ハウスの備え）／ 🧰 AIを自分の武器にする（伴走の型）／ 🌾 畑とパン工房につなげる")
ui.next_move_tag("iot")
