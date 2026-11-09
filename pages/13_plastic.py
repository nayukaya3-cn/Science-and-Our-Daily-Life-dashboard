"""🖨️ 3Dプリンタ・フィラメントで学ぶプラスチック（(2)イ(ア) 材料とその再利用・発展）

「性質を比べる → 構造で説明する → ものをつくる → 捨て方まで考える」を回す。
入力はこの画面の中だけで使い、保存も送信もしない。
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import guard
import sozai_core as sc
import ui

ui.hero("科学と人間生活 ｜ 物質の科学 ｜ 材料とその再利用（発展・50分×8コマ）",
        "❓ 同じプラスチックなのに、なぜPLAは熱に弱く、PETGは丈夫なのか。使い終わったらどうなるのか",
        "3Dプリンタの糸（フィラメント）4種を、条件をそろえて比べる。"
        "『植物由来＝自然に還る』という思い込みも、分解試験のデータで確かめよう。")

ui.hint("　／　".join(f"{w}＝「{e}」" for w, e in sc.PLASTIC_WORDS[:3]))

tab1, tab2, tab3, tab4 = st.tabs(["① 比べる：熱に強いのはどれか", "② つくる：圃場で使う部品",
                                  "③ 還す：植物由来なら土に還るか", "④ 特殊な機能をもったプラスチック"])

# ── ① 比べる ─────────────────────────────
with tab1:
    st.markdown("#### 第3コマ：4種の試験片を湯煎で温め、自重で曲がるかを記録する")
    ui.predict("plastic_pla", "**PLA のスマホスタンドは、何℃くらいで柔らかくなる？**（ノズルは約200℃で溶かしている）",
               actual=float(sc.FILAMENTS["PLA"]["soften"]), unit="℃", protocol="P4", min_value=30.0, max_value=250.0,
               value=150.0, step=5.0, field="材料とその再利用")
    st.dataframe(pd.DataFrame(sc.soften_table()), hide_index=True, width="stretch")
    st.caption("〇＝形を保つ／△＝曲がり始める／×＝自重で曲がる／―＝もともと柔らかい。"
               "⚠️ 単元案の『予想される結果』から作った**目安**。授業では自分たちの記録で置きかえる。")
    name = st.selectbox("素材を選ぶ", list(sc.FILAMENTS), key="plastic_name")
    f = sc.FILAMENTS[name]
    st.markdown(f"**{name}**：{f['origin']}。{f['note']}。")
    if name == "TPU":
        st.warning("TPU は最初から曲がる。これは『柔らかさ』で、温めて柔らかくなる『軟化』とは別のもの。", icon="🧐")
    st.info("生活との接続：夏の車内（60℃以上）に PLA のスマホスタンドを置くと？", icon="🚗")

    st.markdown("#### 第4コマ：比べ方はフェアか ─ 充填率だけを変えて、たわみを測る")
    ui.hint("充填率（じゅうてんりつ）＝「中身の詰まり具合」。スポンジとレンガの違い。")
    data = st.data_editor(pd.DataFrame(sc.INFILL_EXAMPLE, columns=["充填率（％）", "たわみ（mm）"]), num_rows="dynamic",
                          key="plastic_infill", width="stretch",
                          column_config={"充填率（％）": st.column_config.NumberColumn(min_value=0, max_value=100, step=1),
                                         "たわみ（mm）": st.column_config.NumberColumn(min_value=0.0, max_value=200.0, step=0.1)})
    st.caption("はじめの6行は**説明用の例**。班の測定値に書きかえると、下のグラフと傾きが変わる（入力は保存しません）。")
    pts = [(float(x), float(y)) for x, y in data.dropna().itertuples(index=False)]
    try:
        a, b = sc.fit_line(pts)
        r = sc.correlation(pts)
    except (ValueError, ZeroDivisionError):
        a = b = r = None
    fig = go.Figure(go.Scatter(x=[p[0] for p in pts], y=[p[1] for p in pts], mode="markers", name="測定値",
                               marker=dict(size=11, color="#2a78b5"),
                               hovertemplate="充填率 %{x}％：たわみ %{y} mm<extra></extra>"))
    if a is not None:
        xs = [min(p[0] for p in pts), max(p[0] for p in pts)]
        fig.add_scatter(x=xs, y=[a * x + b for x in xs], mode="lines", name="回帰直線",
                        line=dict(color="#c4651a", dash="dash"), hoverinfo="skip")
    fig.update_layout(height=340, margin=dict(t=20, b=10), xaxis_title="充填率（％）", yaxis_title="たわみ（mm）",
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, width="stretch")
    if a is not None:
        m1, m2 = st.columns(2)
        m1.metric("回帰直線の傾き", f"{a:.3f} mm/％", help="充填率を1％上げると、たわみが何mm変わるか")
        m2.metric("相関係数 r", f"{r:.2f}")
        st.success("💻 **情報Ⅰ**：これは『充填率だけを変えた実験』のデータ。だから、この相関は**因果**（詰めると曲がりにくくなる）と言える。"
                   "集めただけのデータ（観察データ）の相関とは、ここが違う。")
    else:
        st.caption("充填率のちがう点を2つ以上入れてください。")
    ui.reading_card(
        axis="素材（PLA・PETG・ABS・TPU）と、形が変わり始める温度",
        unit="℃（湯の温度）。記録は 〇△× の3段階",
        control="そろえる：試験片の幅10 mm・長さ80 mm・厚さ2 mm・充填率100％・湯に入れる時間1分。変える：素材",
        can="同じ形の試験片なら、PLA は PETG より低い温度で曲がり始める",
        cannot="厚さや充填率がちがう製品どうしの強さ。『植物由来だから熱に弱い』こと（由来と性質は別の話）",
        protocols=["P2", "P3"], material="第3コマの記録表（素材×温度）")
    ui.exam_question("plastic_1", sc.EXAMS[0])

# ── ② つくる ─────────────────────────────
with tab2:
    st.markdown("#### 第6コマ：三原西部の圃場・ハウスで使う部品を1つ選び、素材を決める")
    st.dataframe(pd.DataFrame([{"部品": p, "設置場所": pl, "求められる性質": nd, "FWでの使い方": use}
                               for p, pl, nd, _, use in sc.PARTS]), hide_index=True, width="stretch")
    c1, c2 = st.columns(2)
    part = c1.selectbox("部品", [p[0] for p in sc.PARTS], key="plastic_part")
    mat = c2.selectbox("素材", list(sc.FILAMENTS), index=None, placeholder="選んでください", key="plastic_mat")
    reason = st.text_input("選んだ理由（第3・4コマのデータを根拠に。『なんとなく丈夫そう』は不可）", key="plastic_reason",
                           max_chars=guard.MAX_TEXT)
    if mat:
        ok, why = sc.part_feedback(part, mat)
        (st.success if ok else st.warning)(("候補に入っている。" if ok else "もう一度データを見よう。") + why)
        if not reason:
            st.caption("理由を1行書こう。データ（何℃で曲がったか・どれだけたわんだか）を使えたら合格。")
    st.markdown("#### 💻 情報Ⅰとつなげる")
    st.markdown("3Dデータは**座標の列**。寸法を数値で決めて形をつくるのは『モデル化』で、"
                "印刷したものが設計とずれる（反る・縮む）のは『モデルと現実のずれ』（P4）。")

# ── ③ 還す ─────────────────────────────
with tab3:
    st.markdown("#### PLA はどこから来る？")
    st.markdown(" → ".join(f"**{s}**" for s in sc.PLA_FLOW))
    st.markdown("#### 分解試験（第2コマで仕込み、5〜6週間おいて第7コマで取り出す）")
    show = st.toggle("5〜6週間後の見込みを見る（先に自分の予想を仮説シートに書いてから）", value=False, key="plastic_show")
    st.dataframe(pd.DataFrame([{"条件": c, "置き場所": pl, "入れるもの": it, "ねらい": aim,
                                **({"5〜6週間後の見込み": res} if show else {})}
                               for c, pl, it, aim, res in sc.DECOMP]), hide_index=True, width="stretch")
    st.caption("各条件3枚ずつ、網袋に入れて深さ10 cm に埋める。はじめの質量を 0.01 g まで記録する。")
    if show:
        st.error("常温の土では、PLA もほとんど減らない見込み。PLA は約58℃で管理された工業用コンポストではじめて速く分解される。"
                 "**仮説が外れること自体**を、『生分解性の表示をどう読むか』という学びに変える。")
    st.markdown("**質量の変化を計算する**")
    c1, c2 = st.columns(2)
    m0 = c1.number_input("はじめの質量（g）", 0.01, 100.0, 2.00, 0.01, format="%.2f", key="plastic_m0")
    m1 = c2.number_input("取り出して、洗って乾かした後の質量（g）", 0.0, 100.0, 1.99, 0.01, format="%.2f", key="plastic_m1")
    res = sc.mass_change(m0, m1)
    k1, k2 = st.columns(2)
    k1.metric("差", f"{res['差（g）']:+.2f} g")
    k2.metric("変化率", f"{res['変化率（％）']:+.1f} %")
    st.markdown(f"**言えること**：{res['言えること']}")
    ui.hint("電子天秤の最小表示は 0.01 g。差がその2倍以下なら、『変化した』とは言えない（資料5 有効数字とつながる）。")
    ui.reading_card(
        axis="条件（A〜D：置き場所と入れるもの）と、質量の変化",
        unit="g（0.01 g まで）、週（埋めた期間）",
        control="そろえる：試験片の形・埋める深さ（10 cm）・期間。A と C は素材だけ、A と B は置き場所だけがちがう",
        can="画用紙・木片（D）が崩れたなら、その土で分解は起きている。同じ土で PLA（A）が減らなければ、PLA はこの条件では分解されにくい",
        cannot="PLA が『ずっと分解されない』こと（測ったのは5〜6週間だけ）。別の温度・湿度での結果",
        protocols=["P3", "P2"], material="分解試験の質量変化のグラフ")
    st.markdown("#### 第8コマ：どう使い、どう捨てるか")
    st.markdown("- リサイクル識別コード（1〜7番）を身の回りの製品で確かめる。PLA・ABS は『7＝その他』で、家庭ごみのリサイクルには乗らない  \n"
                "- 素材によっては燃やすと有害な気体が出る（ABS は窒素を含む）。**生徒は燃やさない**。資料で扱う  \n"
                "- 成果物：班ごとに『学校の3Dプリンタはどの素材を使い、失敗作をどう扱うか』の提言ポスター1枚")

# ── ④ 特殊な機能 ─────────────────────────────
with tab4:
    st.markdown("#### 追加コマ：『安くて軽い』以外の理由で選ばれているプラスチック")
    quiz = st.toggle("『身の回りの製品』の列をかくして、自分で考える", value=False, key="plastic_quiz")
    st.dataframe(pd.DataFrame([{"機能": fn, "身の回りの製品": "？" if quiz else prod, "フィラメントの事例": fil,
                                "文系向けの言い換え": easy, "機能を担うもの": who}
                               for fn, prod, fil, easy, who in sc.FUNCTIONS]), hide_index=True, width="stretch")
    st.markdown("**つまずきやすい点**")
    st.markdown("- 『水に溶ける』と『水を吸う』は別物：紙おむつの吸水性高分子は、水を吸っても溶けずに膨らむ（鎖どうしが網のようにつながっている）。"
                "PVA の鎖はつながっていないので、水に溶けてばらける  \n"
                "- 『生分解性＝どこでも分解』ではない（③の分解試験で確かめる）  \n"
                "- 混ぜ物と高分子そのものの機能を区別する：導電PLA や炭素繊維入りは、混ぜたものが機能を担う**複合材料**")
    st.info("💻 **情報Ⅰ**：『生分解性』『環境にやさしい』と書かれた広告を集め、『どんな条件で？』『根拠は何か？』で読む。"
            "情報の信頼性評価の教材になる。", icon="🔍")

with st.expander("⚠️ 安全の原則（生徒は燃やさない・ノズルに触らない・湯煎は90℃まで）"):
    for s in sc.PLASTIC_SAFETY:
        st.markdown(f"- {s}")

with st.container(border=True):
    st.markdown("**🧵 ほかの単元と、4つの言葉でつながる**")
    st.table(pd.DataFrame(sc.BRIDGE, columns=["共通の言葉", "🖨️ プラスチック", "🍠 熱（石焼き芋・石窯パン）", "👖 衣料と微生物"]).set_index("共通の言葉"))

ui.next_move_tag("plastic")
