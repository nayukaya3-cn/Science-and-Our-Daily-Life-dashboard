"""👖 衣料と微生物：福山のデニム・尾道の帆布から水の浄化まで（衣料4コマ＋微生物と水の浄化3コマ）

「染める入口」と「排水を浄化する出口」の両方に微生物がいる、を軸に、布と水を1本につなぐ。
入力はこの画面の中だけで使い、保存も送信もしない。
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import sozai_core as sc
import ui

ui.hero("科学と人間生活 ｜ 物質の科学「衣料と食品」× 生命の科学「微生物とその利用」（50分×7コマ）",
        "❓ 同じ綿なのに、デニムと帆布は何が違うのか。布を染めた後の水は、どうやってきれいになるのか",
        "素材（綿）をそろえたまま、織り方と染め方の違いを比べる。そのあと、染めた水の行方を微生物と一緒に追いかけよう。")

with st.container(border=True):
    st.markdown("### 🗺️ この単元を1枚で：布ができるまでと、その後の水の行方")
    st.dataframe(pd.DataFrame([{"工程": a, "何が起きるか": b, "微生物の役割": c, "文系向けの言い換え": e}
                               for a, b, c, _, e in sc.PROCESS]), hide_index=True, width="stretch")
    st.caption("**核心**：デンプンは、芋やパンではおいしさの材料、糸では糊、排水では汚れ、微生物にとってはえさになる。"
               "同じ物質でも、場所によって価値と役割が変わる。")

tab1, tab2, tab3, tab4 = st.tabs(["① 織り方：デニムと帆布", "② 藍はなぜ溶けないのに染まるのか",
                                  "③ 微生物は汚れを食べるか", "④ 産地の水とフィールドワーク"])

# ── ① 織り方 ─────────────────────────────
with tab1:
    st.markdown("#### 第1・2コマ：同じ綿なのに、何が違う？")
    st.table(pd.DataFrame(sc.FABRICS, columns=["観点", "福山のデニム", "尾道の帆布"]).set_index("観点"))
    st.caption("尾道帆布固有の歴史は未確認（工房や市の資料で確かめてから使う）。")
    ui.hint("平織＝「ござのように上下交互に組む」。綾織＝「一筋ずつずらして組むので斜めの線が出る」。")
    c1, c2 = st.columns([2, 1])
    kind = c1.selectbox("織り方をえらぶ", list(sc.WEAVES), key="iryo_weave")
    n = c2.slider("糸の本数", 6, 18, 12, 1, key="iryo_n")
    grid = sc.weave(kind, n)
    fig = go.Figure(go.Heatmap(z=grid, colorscale=[[0, "#f3ead7"], [1, "#2b4c7e"]], showscale=False, xgap=2, ygap=2,
                               hovertemplate="たて糸 %{x}・よこ糸 %{y}<extra></extra>"))
    fig.update_layout(height=360, width=360, margin=dict(t=10, b=10, l=10, r=10),
                      xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x", autorange="reversed"))
    st.plotly_chart(fig, width="content")
    st.caption("紺＝たて糸（藍で染めた糸）が上、生成り＝よこ糸が上。デニムの表が青く、裏が白っぽいのは、たて糸が表に長く出ているから。")
    st.metric("たて糸が表に続けて出る長さ（糸の浮き）", f"{sc.float_length(kind)} 本分")
    st.code("# 💻 情報Ⅰ：2次元配列と『余り』で織り方をつくる\n"
            "# up 本越えて down 本くぐるのを、1段ごとに1本ずつずらす\n"
            "もし (列 − 行) を (up + down) で割った余り < up ならば 「たて糸が上」\n"
            "# Python\ngrid[row][col] = 1 if (col - row) % (up + down) < up else 0", language="python")
    st.warning("**疑うポイント（P3）**：吸水性や強さを比べても、デニムと帆布では厚さや重さ（目付）もそろっていない。"
               "『織り方の違いだ』と言い切れるだろうか。同じ糸で平織と綾織を並べた見本布があれば、よりフェアな比較になる。", icon="🧐")
    ui.reading_card(
        axis="布の種類（デニム・帆布）と、水が上がった高さ／おもりを吊るしたときの伸び",
        unit="cm（10分後の高さ）、mm（伸び）、g（おもり）",
        control="そろえた：繊維（綿）・帯の幅（2 cm）・時間（10分）。そろっていない：織り方・厚さ・重さ・染め方",
        can="この2枚の布では、吸水性や伸びやすさに差がある",
        cannot="その差が『織り方』のせいだということ（厚さ・重さ・染め方も同時にちがう）",
        protocols=["P2", "P3"], material="第2コマの実験データ表")

# ── ② 藍染め ─────────────────────────────
with tab2:
    st.markdown("#### 第3・5コマ：藍（インディゴ）の粉は水に溶けない。それなのに、なぜ染まる？")
    state = st.radio("藍の状態", sc.INDIGO_STATES, horizontal=True, key="iryo_indigo")
    r = sc.indigo(state)
    m1, m2, m3 = st.columns(3)
    m1.metric("色", r["色"])
    m2.metric("水に溶ける？", r["水に溶ける？"])
    m3.metric("繊維の中に入れる？", r["繊維の中に入れる？"])
    (st.success if state.startswith("還元") else st.info)(r["説明"])
    ui.hint("「部屋に入るときは小さくなり、入ったら大きく戻るので、ドアから出られない」。これが、洗っても落ちにくい理由。")
    st.markdown("**デニムの色落ち**：糸の外側だけが染まり、芯が白い（ロープ染色）。こすれると白い芯が見えてくる。")
    st.markdown("#### 江戸時代には薬品がない。どうやって藍を溶かしたのか")
    st.markdown("藍の葉を発酵させたものに、木を燃やした灰を水に溶かした**アルカリ性の液**を加える。"
                "その中で生きる**細菌**が、藍を還元して溶かす（発酵建て）。")
    st.info("微生物は、食品（パンの酵母、ヨーグルト）、染色、排水処理など、さまざまな場面で使われている。"
            "『🦠 微生物と発酵』のページの図17（発酵食品の分類）に、染色と水の浄化を足して考えよう。", icon="🦠")
    st.markdown("#### 第4コマ：綿も芋のデンプンも、同じブドウ糖の鎖")
    st.markdown("綿はブドウ糖の鎖（**セルロース**）。水となじむ部分が多いので水をよく吸う。合成繊維は石油由来の鎖で、吸水性が低いものが多い。")
    with st.expander("問い：なぜ芋は食べられて、ジーンズは食べられないのか（考えてから開く）"):
        st.markdown("ブドウ糖の**つながり方**がちがう。ヒトには、セルロースを分解する酵素がない。"
                    "1章Aの『分解して部品にする』は、分解できる酵素があってはじめて成り立つ。")

# ── ③ 微生物は汚れを食べるか ─────────────────────────────
with tab3:
    st.markdown("#### 第6コマ：デンプン液の減り方を、ヨウ素液の色で比べる（3条件）")
    st.dataframe(pd.DataFrame(sc.WATER_EXP, columns=["条件", "入れるもの", "空気", "ねらい"]), hide_index=True, width="stretch")
    ui.hint("活性汚泥（かっせいおでい）＝「汚れを食べる微生物をたくさん飼っている泥。空気を送ると元気に食べる」。")

    st.markdown("**2つの条件を選んで、何が言えるかを確かめよう**")
    c1, c2 = st.columns(2)
    a = c1.selectbox("条件（1つ目）", ["A", "B", "C"], index=0, key="iryo_a")
    b = c2.selectbox("条件（2つ目）", ["A", "B", "C"], index=2, key="iryo_b")
    diff = sc.differs_only_in(a, b)
    st.metric("ちがっている項目の数", len(diff), "・".join(diff) if diff else "なし", delta_color="off", delta_arrow="off")
    (st.success if len(diff) == 1 else st.error)(sc.water_claim(a, b))

    st.markdown("**ヨウ素液の色の記録（5＝濃い青紫 … 1＝ほぼ無色）**")
    data = st.data_editor(pd.DataFrame(sc.WATER_EXAMPLE, index=[f"{d}日目" for d in sc.WATER_DAYS]), key="iryo_data",
                          width="stretch",
                          column_config={k: st.column_config.NumberColumn(f"条件{k}", min_value=1, max_value=5, step=1)
                                         for k in sc.WATER_EXAMPLE})
    st.caption("はじめの値は、単元案の『予想される結果』から作った**説明用の例**。自分たちの記録に書きかえると、グラフが変わる（保存しません）。")
    style = {"A": ("#c4651a", "solid"), "B": ("#2a78b5", "solid"), "C": ("#7a7a7a", "dash")}
    fig = go.Figure()
    for k in sc.WATER_EXAMPLE:
        col, dash = style[k]
        fig.add_scatter(x=list(sc.WATER_DAYS), y=list(data[k]), mode="lines+markers", name=f"条件{k}",
                        line=dict(color=col, width=2, dash=dash), marker=dict(size=8),
                        hovertemplate=f"条件{k}<br>%{{x}} 日目：色 %{{y}}<extra></extra>")
    fig.update_layout(height=340, margin=dict(t=20, b=10), xaxis_title="仕込んでからの日数", legend=dict(orientation="h"),
                      yaxis=dict(title="ヨウ素液の色の濃さ（色見本の段階）", range=[0.5, 5.5], dtick=1), hovermode="x unified")
    st.plotly_chart(fig, width="stretch")
    ui.reading_card(
        axis="仕込んでからの日数（横軸）と、ヨウ素液の色の濃さ（縦軸）を、3条件で比べる",
        unit="日、色見本の段階（1〜5。長さや重さのような量ではなく、順番を表す数）",
        control="そろえる：デンプン液の濃さと量・温度・微生物の入れ方。A と C は微生物の有無だけ、A と B は空気だけがちがう",
        can="C（煮沸した水）が変わらず A が薄くなったなら、デンプンが減ったのは微生物の働き",
        cannot="『酸素だけが原因で速くなった』こと（エアポンプは液をかき混ぜもする）。色の段階が2倍なら、デンプンも2倍残っていること",
        protocols=["P3", "P2"], material="第6コマの色の記録とグラフ")
    ui.exam_question("iryo_1", sc.EXAMS[1])

# ── ④ 産地の水とFW ─────────────────────────────
with tab4:
    st.markdown("#### 第7コマ：産地の水はどう守られているか")
    st.markdown("- **調べる**：染色排水の処理の流れ（中和 → 活性汚泥 → 沈殿 → 放流）を、自治体や企業の公開資料で調べる  \n"
                "- **測る（P2）**：教員が中和した廃液と、③の条件A・Cの液を、パックテストで pH・COD（水の汚れの指標）を測る  \n"
                "- **問い（P3）**：微生物で分解しにくいものは何か。それはどう処理されているか（染料の色、プラスチック単元の PLA と比べる）  \n"
                "- **成果物**：班ごとに『地域の布づくりと瀬戸内海を両立させるには』の提言ポスター1枚。産地の取り組みと課題の両方を書く")
    st.warning("『産地は水を汚している』という一方的な見方にならないよう、法令に基づく対策を中心に扱う。", icon="⚖️")
    st.markdown("#### 🌾 フィールドワーク・産地とのつながり")
    st.table(pd.DataFrame([
        ("三原の畑区画", "綿や藍を育て、『育てた綿と藍で布を染めるまで』を発展テーマにする", "第3・5コマ"),
        ("三原の井戸", "pH・COD を同じパックテストで測り、地下水と排水を比べる", "第7コマ"),
        ("福山のデニム工場", "糸から布までの工程を見学する（受け入れの可否を事前に確かめる）", "第1・2・4コマ"),
        ("尾道の帆布工房", "帆布の製品づくりを見学する（受け入れの可否を事前に確かめる）", "第1・2コマ"),
    ], columns=["場所", "活動", "つながるコマ"]).set_index("場所"))
    st.markdown("#### 🧵 デンプンの5つの顔")
    st.dataframe(pd.DataFrame(sc.STARCH_FACES, columns=["どこで", "役割", "確かめるページ"]), hide_index=True, width="stretch")
    st.caption("2章Bで見た『同じ分解でも、役に立てば発酵、困れば腐敗』と同じ見方。物質そのものではなく、場所と目的が役割を決める。")

with st.expander("⚠️ 安全の留意点（実習の前に必ず読む）"):
    for s in sc.CLOTH_SAFETY:
        st.markdown(f"- {s}")

ui.next_move_tag("iryo")
