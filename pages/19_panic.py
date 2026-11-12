"""🛡️ 終章 課題研究：パニックプルーフ ─「供給が止まっても、何日パニックにならずに暮らせるか」を測って伸ばす

「自給自足」をそのまま目標にせず、バッファ・冗長性・技能・情報の4つを『測れる形』にしたフィールドワーク。
入力はこの画面の中だけで使い、保存も送信もしない（作業記録・ダッシュボードは手元へのダウンロードだけ）。
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import guard
import panic_core as pc
import ui

ui.hero("科学と人間生活 ｜ 終章 これからの科学と人間生活 ｜ 課題研究 × フィールドワーク（三原西部の圃場・ハウス）",
        f"🛡️ {pc.TITLE}",
        f"❓ {pc.LEAD_QUESTION}　『全部自分で作る』ではなく『何日もつか』で考えると、"
        "科学と人間生活の4領域と、共通テスト・情報Ⅰの得点の両方につながる。楽しい田舎暮らし体験で終わらせない。")
ui.hint(pc.EASY_WORDS)

ui.lesson_plan([{"時期": a, "圃場で起きていること": b, "活動": c, "メモ": d} for a, b, c, d in pc.CALENDAR],
               "🧑‍🏫 先生向け：麦の暦と長期休暇（通い型・2回）")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "① パニックプルーフとは", "② 1kgの種で何日？", "③ わが家の自給日数", "④ 効率 vs しぶとさ",
    "⑤ 噂と買いだめ", "⑥ 作業記録・安全（先生向け）"])

# ── ① パニックプルーフとは ─────────────────────────────
with tab1:
    st.markdown("#### 言葉の意味：-proof ＝「〜に耐える・〜を防ぐ」")
    st.dataframe(pd.DataFrame(pc.WORD_MEANING, columns=["言葉", "意味", "身近な例"]), hide_index=True, width="stretch")
    st.success(pc.DESIGN_PRINCIPLE, icon="🚪")
    st.markdown("#### 4つの要素を『測れる形』にする")
    st.dataframe(pd.DataFrame(pc.ELEMENTS, columns=["要素", "意味", "三原西部での具体物", "測る指標", "伸ばし方"]),
                 hide_index=True, width="stretch")

    st.markdown("#### 社会の文脈：日本の食料自給率")
    j = pc.JIKYU
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"カロリーベース（{j['year']}）", f"{j['calorie_pct']} %")
    m2.metric("1人1日 国産供給熱量", f"{j['domestic_kcal']:,} kcal")
    m3.metric("1人1日 総供給熱量", f"{j['supply_kcal']:,} kcal")
    m4.metric("暮らしに必要な摂取熱量", f"{j['intake_kcal']:,} kcal", f"摂取熱量ベース {j['intake_pct']}%",
              delta_color="off", delta_arrow="off")
    st.caption(f"小麦は {j['wheat_supply_kcal']} kcal のうち国産 {j['wheat_domestic_kcal']} kcal（約"
               f"{round(j['wheat_domestic_kcal'] / j['wheat_supply_kcal'] * 100)}%）。"
               "出どころ：農林水産省『令和7年度食料自給率』（2026年8月公表・概算）。授業の前に最新の値を確かめる。")
    ui.hint("『供給』には、売れ残りや食べ残しで捨てられる分も入っている。暮らせる日数を数えるときは、"
            "実際に食べる量に近い『摂取』の 1,850 kcal を物差しにする（②・③の既定）。")
    st.info(pc.LAW_NOTE, icon="⚖️")
    ui.reading_card(
        axis="国産の熱量 と 全体の熱量（割合）", unit="kcal／人・日、％",
        control="そろえた：同じ年度・同じ換算表（食品標準成分表）。変えた：分母（供給か摂取か）",
        can="分母を『供給』から『摂取』に変えると、同じ国産 830 kcal でも自給率は 37% → 45% に見える",
        cannot="どちらの数字が『正しい』か（目的によって使い分ける）・家庭や地域で何日もつか（国全体の平均だから）",
        protocols=["P2", "P3"], material="上の4つの数字")

# ── ② 1kgの種で何日？ ─────────────────────────────
with tab2:
    st.markdown("#### 最初の問い：「1kgの種（ミナミノカオリ）で、1人何日食べられる？」")
    base = pc.monte_carlo(pc.SEED_G, pc.JIKYU["intake_kcal"])
    ui.predict("panic_1kg", "1kg の種を**全部**播いて、とれた小麦を粉にしたら、1人（1日 1,850 kcal）の何日分の主食になる？",
               round(base["p50"]), "日", protocol="P4", min_value=0.0, max_value=400.0, step=5.0, value=30.0,
               field="課題研究")

    st.markdown("##### 仮定の幅を動かして、日数の分布を見る（モンテカルロ法）")
    c1, c2 = st.columns(2)
    scope = c1.radio("どこまで播く？", ["計画どおり（1列32㎡・320g）", "1kg 全部"], horizontal=True, key="panic_scope")
    yard = c2.radio("1日の物差し", ["摂取（1,850 kcal）", "供給（2,237 kcal）"], horizontal=True, key="panic_yard")
    kcal = pc.kcal_yardstick("摂取" if yard.startswith("摂取") else "供給")
    s1, s2, s3 = st.columns(3)
    rate = s1.slider("播種量（g/㎡）", 4.0, 14.0, pc.RATE_RANGE, 0.5, key="panic_rate",
                     disabled=scope.startswith("計画"), help="計画どおりなら面積は 32㎡ に固定")
    yld = s2.slider("収量（kg/10a）", 100.0, 600.0, pc.YIELD_RANGE, 10.0, key="panic_yld",
                    help="10a ＝ 1000㎡。300 kg/10a ＝ 1㎡あたり 300 g")
    mill = s3.slider("製粉歩留まり", 0.5, 1.0, pc.MILL_RANGE, 0.05, key="panic_mill",
                     help="玄麦100のうち粉になる割合。全粒粉ならほぼ全部、白い粉なら6〜7割")
    area = pc.PLAN["area_m2"] if scope.startswith("計画") else None
    mc = pc.monte_carlo(pc.SEED_G, kcal, area_m2=area, rate=rate, yld=yld, mill=mill)
    k1, k2, k3 = st.columns(3)
    k1.metric("播く面積", f"{pc.PLAN['area_m2']} ㎡" if area else f"{mc['area'].min():.0f}〜{mc['area'].max():.0f} ㎡")
    k2.metric("日数（中央値）", f"{mc['p50']:.0f} 日")
    k3.metric("日数（90%の幅）", f"{mc['p5']:.0f}〜{mc['p95']:.0f} 日")
    fig = go.Figure(go.Histogram(x=mc["days"], nbinsx=50, marker_color="#a9bccf"))
    for v, name in ((mc["p5"], "5%"), (mc["p50"], "中央値"), (mc["p95"], "95%")):
        fig.add_vline(x=v, line_dash="dash", line_color="#4a6a8a", annotation_text=name)
    fig.update_layout(height=280, margin=dict(t=30, b=10, l=10, r=10), xaxis_title="1人分の主食の日数", yaxis_title="回数",
                      showlegend=False)
    st.plotly_chart(fig, width="stretch")
    st.markdown("**ここから議論すること**")
    st.markdown("1. **小麦だけで1年分は無理** → 自給は『全部』ではなく『何日分か』で考える  \n"
                "2. **計画の1列だと半月ほど** → 1kg 全部（約3倍の面積）でも2か月前後。手刈り・手脱穀の手間とくらべる（④）  \n"
                "3. **玄麦を粉にすると目減りする** → 歩留まりを測ることが、そのまま事後学習の課題になる")
    with st.expander("元の案（前年度 2,248 kcal・歩留まりなし）との違い"):
        orig = pc.monte_carlo(pc.SEED_G, 2248, mill=(1.0, 1.0))
        st.markdown(f"元の案の式を再現すると、1kg 全部で **{orig['p5']:.0f}〜{orig['p95']:.0f} 日（中央値 {orig['p50']:.0f} 日）**。"
                    "このページでは ①物差しを令和7年度の摂取熱量 1,850 kcal に、②製粉の目減りを入れ、"
                    "③実際に播くのは1列32㎡（320g）として分けて見積もった。どの仮定で数字が動くかを、スライダーで確かめよう。")
        st.code("days = 面積[㎡] / 1000 × 収量[kg/10a] × 1000 × 歩留まり × 3.3[kcal/g] / 1日の物差し[kcal]", language="text")

    st.markdown("##### ベイズ更新①：発芽試験（残りの種 100 粒）")
    st.caption("湿らせたキッチンペーパーに100粒並べ、毎日の発芽数を数える。何も知らない状態（一様分布）から、数えた結果で発芽率の分布を更新する。")
    g1, g2 = st.columns(2)
    n_seed = g1.number_input("並べた粒数", 10, 500, 100, 10, key="panic_gn")
    k_seed = g2.number_input("発芽した粒数", 0, int(n_seed), min(90, int(n_seed)), 1, key="panic_gk")
    bp = pc.beta_posterior(int(k_seed), int(n_seed))
    st.metric("発芽率の見込み（95%の幅）", f"{bp['mean']:.0%}", f"{bp['lo']:.0%}〜{bp['hi']:.0%}", delta_color="off",
              delta_arrow="off")
    if bp["hi"] < 0.8:
        st.warning("発芽率が低めかもしれない。12月上旬までなら残りの種で補播できる。")

    st.markdown("##### ベイズ更新②：6月の収穫で、来年の見積もりを直す")
    h1, h2, h3 = st.columns(3)
    got = h1.number_input("収穫した玄麦（kg・32㎡）", 0.0, 50.0, 0.0, 0.1, key="panic_got")
    flour = h2.number_input("製粉後の粉（kg）", 0.0, 50.0, 0.0, 0.1, key="panic_flour")
    obs_sd = h3.slider("測り方のばらつき（kg/10a）", 10, 150, 50, 10, key="panic_obs_sd",
                       help="1列だけの結果は天気や場所のくせを含む。大きくするほど『今年の1回』を信用しない")
    plan_mc = pc.monte_carlo(None, kcal, area_m2=pc.PLAN["area_m2"], yld=yld, mill=mill)
    if got > 0:
        m_obs = flour / got if 0 < flour <= got else (mill[0] + mill[1]) / 2
        actual = pc.food_days(got, m_obs, kcal)
        pctl = pc.percentile_of(plan_mc["days"], actual)
        obs_yield = got / pc.PLAN["area_m2"] * 1000
        mu, sd = pc.normal_update(*pc.PRIOR_YIELD, obs_yield, obs_sd)
        r1, r2, r3 = st.columns(3)
        r1.metric("実測の日数", f"{actual:.1f} 日", f"見積もりの {pctl:.0f}% 点", delta_color="off", delta_arrow="off")
        r2.metric("今年の収量", f"{obs_yield:.0f} kg/10a", f"歩留まり {m_obs:.0%}", delta_color="off", delta_arrow="off")
        r3.metric("来年の収量の見込み", f"{mu:.0f} ± {sd:.0f} kg/10a",
                  f"前の見込み {pc.PRIOR_YIELD[0]:.0f} ± {pc.PRIOR_YIELD[1]:.0f}", delta_color="off", delta_arrow="off")
        if pctl < 5 or pctl > 95:
            st.error("見積もりの端からはみ出した。仮定（収量・歩留まり）のどれが外れていたかを、1行で書こう。")
    else:
        st.caption("6月に収穫したら、玄麦と粉の重さを入れる。見積もり（事前分布）のどこに実測が落ちたかと、来年の見込みが出る。")
    ui.reading_card(
        axis="仮定（播種量・収量・歩留まり） と 日数", unit="日（1人・1日の物差し kcal で割った値）",
        control="そろえた：玄麦の熱量 3.3 kcal/g・1日の物差し。変えた：仮定の幅（スライダー）",
        can="どの仮定が日数を大きく動かすか（幅の広い仮定ほど、実測する価値が高い）",
        cannot="小麦だけで栄養が足りるか（タンパク質・ビタミンは数えていない）・天候不順や鳥害の年の結果",
        protocols=["P4", "P2"], material="日数のヒストグラム")

# ── ③ わが家の自給日数 ─────────────────────────────
with tab3:
    st.markdown("#### 成果物は1つ：『わが家の自給日数ダッシュボード』（食料・水・熱の3本立て）")
    st.caption(f"目安（農林水産省の家庭備蓄の手引き）：水は1人1日 約{pc.WATER_L_PER_DAY:g}L（飲み水＋調理用）、"
               f"カセットボンベは1人1週間 約{pc.GAS_CANS_PER_WEEK}本、最低{pc.BICHIKU_GOAL_DAYS[0]}日分〜1週間分。"
               "家族の名前や住所は書かない。")
    d1, d2, d3 = st.columns(3)
    persons = d1.number_input("人数", 1, 10, 3, 1, key="panic_persons")
    rice = d1.number_input("米（kg）", 0.0, 100.0, 5.0, 0.5, key="panic_rice")
    flourk = d2.number_input("小麦粉・乾麺（kg）", 0.0, 50.0, 1.0, 0.5, key="panic_flourk")
    packs = d2.number_input(f"レトルト・缶詰（個・1個{pc.KCAL_PER_PACK}kcalで計算）", 0, 200, 6, 1, key="panic_packs")
    water = d3.number_input("飲める水（L）", 0.0, 500.0, 12.0, 2.0, key="panic_water")
    gas = d3.number_input("カセットボンベ（本）", 0, 100, 3, 1, key="panic_gas")
    days = pc.home_days(persons=int(persons), kcal_per_day=pc.JIKYU["intake_kcal"], rice_kg=rice, flour_kg=flourk,
                        packs=int(packs), water_l=water, gas_cans=int(gas))
    worst, wd = pc.bottleneck(days)
    fig = go.Figure(go.Bar(x=list(days), y=list(days.values()), text=[f"{v:.1f}日" for v in days.values()],
                           textposition="outside",
                           marker_color=["#c4651a" if k == worst else "#a9bccf" for k in days]))
    fig.add_hline(y=pc.BICHIKU_GOAL_DAYS[1], line_dash="dot", annotation_text="1週間")
    fig.add_hline(y=pc.BICHIKU_GOAL_DAYS[0], line_dash="dot", annotation_text="最低3日")
    fig.update_layout(height=300, margin=dict(t=20, b=10, l=10, r=10), yaxis_title="何日もつか",
                      yaxis_range=[0, max(max(days.values()), 7) * 1.25])
    st.plotly_chart(fig, width="stretch")
    st.metric("🛡️ わが家の自給日数（いちばん短いもの）", f"{wd:.1f} 日", f"ボトルネック：{worst}", delta_color="off",
              delta_arrow="off")
    st.info("米がいくら多くても、水が2日で尽きれば2日しかもたない。これは『トリプトファンが1個足りないだけで"
            "ヘモグロビンはつくれない』（🍖 消化→吸収→合成）と同じ形 ─ いちばん足りないものが全体を止める。", icon="🪣")

    st.markdown("#### 残りの3要素（冗長性・技能・情報）")
    e1, e2, e3 = st.columns(3)
    with e1.container(border=True):
        st.markdown("**🔀 代わりの経路**（止まる原因を書く）")
        w_alt = st.text_input("水の代わり", key="panic_alt_w", max_chars=80, placeholder="例：井戸（検査前は生活用水）")
        h_alt = st.text_input("熱の代わり", key="panic_alt_h", max_chars=80, placeholder="例：自家の山の薪")
        why = st.text_input("それはふだんの経路と同じ原因で止まる？", key="panic_alt_why", max_chars=120,
                            placeholder="例：停電では止まらない／地震では井戸も濁るかも")
        n_alt = sum(bool(x) for x in (w_alt, h_alt))
    with e2.container(border=True):
        st.markdown("**🛠️ 自分でできる工程**")
        steps = ["播種", "麦踏み", "収穫", "脱穀", "製粉", "パン焼き"]
        n_skill = sum(st.checkbox(s, key=f"panic_sk_{i}") for i, s in enumerate(steps))
    with e3.container(border=True):
        st.markdown("**📡 事前に決めたこと**")
        n_pre = sum(st.checkbox(s, key=f"panic_pre_{i}") for i, s in enumerate(pc.PRECOMMIT))
    st.markdown(f"**4要素のまとめ**：バッファ {wd:.1f} 日 ／ 代わりの経路 {n_alt} 本 ／ 工程 {n_skill}/{len(steps)} ／ "
                f"事前の約束 {n_pre}/{len(pc.PRECOMMIT)}")
    lack = st.text_input("発表で必ず言う：わが家に足りないもの（1行）", key="panic_lack", max_chars=200)
    sheet = "\n".join([
        "# わが家の自給日数ダッシュボード（名前・住所は書かない）",
        f"人数: {int(persons)} 人（1日 {pc.JIKYU['intake_kcal']} kcal で計算）",
        *[f"{k}: {v:.1f} 日" for k, v in days.items()],
        f"自給日数（いちばん短いもの）: {wd:.1f} 日（{worst}）",
        f"代わりの経路: 水={guard.clean_text(w_alt, 80) or '（なし）'} / 熱={guard.clean_text(h_alt, 80) or '（なし）'}",
        f"同じ原因で止まるか: {guard.clean_text(why, 120) or '（未記入）'}",
        f"自分でできる工程: {n_skill}/{len(steps)}",
        f"事前の約束: {n_pre}/{len(pc.PRECOMMIT)}",
        f"足りないもの: {guard.clean_text(lack, 200) or '（未記入）'}",
    ])
    st.download_button("ダッシュボードをテキストで保存", sheet.encode("utf-8"), "自給日数ダッシュボード.txt", "text/plain")
    ui.reading_card(
        axis="食料・水・熱 と 何日もつか", unit="日（人数 × 1日の目安量で割った値）",
        control="そろえた：人数と1日の目安量。変えた：備蓄の量",
        can="今の備蓄なら、どれが最初に尽きるか（ボトルネック）",
        cannot="停電で冷蔵庫の物が何日もつか・薬やトイレなど数えていない物・家族の体調による必要量のちがい",
        protocols=["P2", "P4"], material="3本の棒グラフ")

# ── ④ 効率 vs しぶとさ ─────────────────────────────
with tab4:
    st.markdown("#### 問い：「全部自分で作る」と「分業して交換する」、どちらがパニックに強い？")
    st.markdown("##### 1. 分業の強み：比較優位を数字で見る（持ち時間は1人6時間）")
    ex = pc.TRADE_EXAMPLE
    t1, t2, t3, t4 = st.columns(4)
    a_b = t1.number_input("Aさん：パン1個（時間）", 0.5, 6.0, float(ex["a_bread"]), 0.5, key="panic_ab")
    a_v = t2.number_input("Aさん：野菜1かご（時間）", 0.5, 6.0, float(ex["a_veg"]), 0.5, key="panic_av")
    b_b = t3.number_input("Bさん：パン1個（時間）", 0.5, 6.0, float(ex["b_bread"]), 0.5, key="panic_bb")
    b_v = t4.number_input("Bさん：野菜1かご（時間）", 0.5, 6.0, float(ex["b_veg"]), 0.5, key="panic_bv")
    c = pc.comparative(ex["hours"], a_b, a_v, b_b, b_v)
    st.dataframe(pd.DataFrame([
        {"やり方": "各自で自給（2人とも半分ずつの時間）", "パン": round(c["self_bread"], 2), "野菜": round(c["self_veg"], 2)},
        {"やり方": f"分業（{c['plan']}）", "パン": round(c["div_bread"], 2), "野菜": round(c["div_veg"], 2)},
    ]), hide_index=True, width="stretch")
    st.caption(f"野菜1かごのために、Aさんはパン {c['cost_a']:g} 個、Bさんはパン {c['cost_b']:g} 個をあきらめる。"
               "あきらめる量が少ない人が、その仕事に『相対的に向いている』。")
    ui.hint("どちらも下手な人にも、比べれば向いている仕事がある。分け合えば全体が豊かになる。")

    st.markdown("##### 2. 反論：分業は「途切れる」と弱い ─ 冗長性の価値は『原因の独立さ』で決まる")
    r1, r2, r3 = st.columns(3)
    p1 = r1.slider("経路1が止まる確率", 0.0, 0.5, 0.10, 0.01, key="panic_p1")
    p2 = r2.slider("経路2が止まる確率", 0.0, 0.5, 0.10, 0.01, key="panic_p2")
    cc = r3.slider("両方を一度に止める共通原因（地域全体の災害）", 0.0, float(min(p1, p2)), 0.0, 0.01, key="panic_cc")
    both = pc.all_fail([p1, p2], cc)
    q1, q2, q3 = st.columns(3)
    q1.metric("1本だけのとき", f"{p1:.1%}")
    q2.metric("2本・別々に止まるなら", f"{p1 * p2:.1%}")
    q3.metric("2本・共通原因ありなら", f"{both:.1%}", f"{both - p1 * p2:+.1%}", delta_color="inverse")
    st.graphviz_chart(
        'digraph G { rankdir=LR; node [shape=box, style="rounded,filled", fillcolor="#e4ecf5", color="#4a6a8a", '
        'fontname="sans-serif", fontsize=11]; '
        'D [label="地域全体の災害（共通原因）", fillcolor="#fdecc8"]; R1 [label="経路1が止まる"]; R2 [label="経路2が止まる"]; '
        'X [label="両方止まる＝困る"]; D -> R1; D -> R2; R1 -> X; R2 -> X; }', width="content")
    st.dataframe(pd.DataFrame(pc.ROUTE_PAIRS, columns=["備え", "止まる原因", "評価"]), hide_index=True, width="stretch")
    st.caption("先生向け：これは DAG（因果の矢印図）の『共通原因』そのもの。生徒には"
               "『同じ理由で一緒にダメになる備えは、備えが1つと同じ』とだけ伝えれば十分。")

    st.markdown("##### 3. 結論は二択にしない：「平時は分業、非常時の余力は地域で」")
    st.dataframe(pd.DataFrame(pc.STANCES, columns=["立場", "強み", "弱み"]), hide_index=True, width="stretch")
    st.info("最後の行の弱みは『保険』と同じ形：何も起きなければ損に見えるコストを、誰がどれだけ払うか。"
            "これは科学の問題であると同時に、社会の問題。", icon="🤝")
    ui.lesson_plan(pc.LESSON_20, "🧑‍🏫 先生向け：この話を授業20分で")
    ui.reading_card(
        axis="経路の本数・共通原因の大きさ と 全部止まる確率", unit="％（確率）",
        control="そろえた：1本ずつの止まる確率。変えた：共通原因の大きさ",
        can="共通原因が大きいほど、2本目の備えの効き目が小さくなる",
        cannot="現実の確率そのもの（スライダーは説明用の値）・経路どうしがほんとうに独立か（計算は独立を仮定したときしか言えない）",
        protocols=["P4", "P3"], material="3つの確率と矢印図")

# ── ⑤ 噂と買いだめ ─────────────────────────────
with tab5:
    st.markdown("#### 問い：ほんとうは足りているのに、なぜ店の棚が空になるのか")
    ui.hint("入荷はふだんどおり（ほんとうの不足はない）でも、『なくなるらしい』と聞いた人が多めに買うと、"
            "棚が空になる。空の棚を見た人がまた買う ─ 噂が自分で本当になってしまう。")
    u1, u2, u3 = st.columns(3)
    spread = u1.slider("噂の広がる速さ", 0.1, 1.5, 0.6, 0.1, key="panic_spread")
    believe = u2.slider("聞いて信じる人の割合", 0.0, 1.0, 0.5, 0.05, key="panic_believe",
                        help="確かめる人が増えるほど小さくなる")
    mult = u3.slider("信じた人が買う量（ふだんの何倍）", 1.0, 6.0, 3.0, 0.5, key="panic_mult")
    rows = pc.panic_sim(spread=spread, believe=believe, multiplier=mult)
    so = pc.first_stockout(rows)
    df = pd.DataFrame(rows)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["日"], y=df["在庫"], name="店の在庫", mode="lines+markers", line_color="#4a6a8a"))
    fig.add_trace(go.Scatter(x=df["日"], y=df["買いたい量"], name="買いたい量", mode="lines", line=dict(color="#c4651a", dash="dash")))
    fig.update_layout(height=300, margin=dict(t=20, b=10, l=10, r=10), xaxis_title="日",
                      yaxis_title="ふだんの1日分 ＝ 1", legend=dict(orientation="h"))
    st.plotly_chart(fig, width="stretch")
    if so is None:
        st.success("この条件では、品切れは起きない。")
    else:
        st.error(f"{so} 日目に品切れ。入荷はずっとふだんどおりなのに。")
    st.markdown("#### 噂を見たら確かめる4つ（情報Ⅰ 第1問：情報の信ぴょう性）")
    st.markdown("\n".join(f"- {s}" for s in pc.CHECK_RUMOR))
    st.caption("3つ目に注意：10個のサイトが同じ元の記事を写しているなら、出どころは1つ（④の『共通原因』と同じ形）。")
    ui.reading_card(
        axis="日 と 在庫・買いたい量", unit="ふだんの1日分を1とした量",
        control="そろえた：入荷量（毎日1）・はじめの在庫。変えた：信じる人の割合",
        can="確かめる人が増える（信じる割合が下がる）と、品切れが遅れるか起きなくなる",
        cannot="実際の店で何日目に品切れになるか（広がり方は単純化した模型）・SNSの影響の大きさ",
        protocols=["P4", "P3"], material="在庫の折れ線グラフ")

# ── ⑥ 作業記録・安全 ─────────────────────────────
with tab6:
    st.markdown("#### 作業記録表（Excel と同じ列）：手間を数字にする")
    st.caption("1行＝1回の作業。延べ時間＝人数×時間。名前は書かない。表はこの画面の中だけで使い、保存はダウンロードだけ。")
    log = st.data_editor(
        pd.DataFrame(pc.LOG_EXAMPLE, columns=pc.LOG_COLUMNS), num_rows="dynamic", hide_index=True, width="stretch",
        key="panic_log",
        column_config={
            "作業": st.column_config.SelectboxColumn(options=list(pc.WORKS)),
            "天気": st.column_config.SelectboxColumn(options=list(pc.WEATHER)),
            "土の湿り": st.column_config.SelectboxColumn(options=list(pc.SOIL)),
            "定点写真": st.column_config.SelectboxColumn(options=["あり", "なし"]),
            "人数": st.column_config.NumberColumn(min_value=0, max_value=50, step=1),
            "時間（分）": st.column_config.NumberColumn(min_value=0, max_value=1440, step=5),
            "草丈（cm）": st.column_config.NumberColumn(min_value=0.0, max_value=200.0, step=0.5),
            "資材と量": st.column_config.TextColumn(max_chars=120),
            "メモ": st.column_config.TextColumn(max_chars=200),
        })
    sm = pc.log_summary(log.to_dict("records"))
    l1, l2, l3 = st.columns(3)
    l1.metric("作業回数", f"{sm['n']} 回")
    l2.metric("延べ作業時間", f"{sm['person_hours']:.1f} 時間")
    l3.metric("草丈の最大", f"{sm['max_height']:.1f} cm")
    hdf = log.dropna(subset=["草丈（cm）"]).query("`草丈（cm）` > 0") if "草丈（cm）" in log else log.iloc[0:0]
    if len(hdf) >= 2:
        st.plotly_chart(go.Figure(go.Scatter(x=hdf["日付"], y=hdf["草丈（cm）"], mode="lines+markers", line_color="#4a6a8a"))
                        .update_layout(height=260, margin=dict(t=20, b=10, l=10, r=10), yaxis_title="草丈（cm）"),
                        width="stretch")
    est = pc.harvest_kg(pc.PLAN["area_m2"], 300)
    kph = pc.kcal_per_person_hour(est, 0.85, sm["person_hours"])
    if kph:
        st.info(f"収量 300 kg/10a・歩留まり 85% と仮定すると、これまでの作業1時間あたり約 **{kph:,.0f} kcal**"
                f"（1人1日 1,850 kcal の約 {kph / 1850:.1f} 日分）。作業が増えるほど、この数字は下がる ─ "
                "『農＋Xは大変』という感覚を数字で確かめる材料になる（④の比較優位とつなげる）。", icon="⏱️")
    st.download_button("作業記録をCSVで保存", guard.csv_safe(log).to_csv(index=False).encode("utf-8-sig"),
                       "作業記録.csv", "text/csv")

    with st.expander("施肥量（1列32㎡分）と播種の配分"):
        st.dataframe(pd.DataFrame([{"時期": t, "資材": m, "1㎡あたり（g）": g, "32㎡分（g）": g * pc.PLAN["area_m2"], "注意": n}
                                   for t, m, g, n in pc.FERTILIZER]), hide_index=True, width="stretch")
        st.markdown(f"1kg は3列（{pc.FULL_AREA_M2}㎡）に播ける量だが、収穫が30kg前後になり、手刈り・手脱穀で6月の週末が埋まる。"
                    f"そこで **1列（{pc.PLAN['width_m']}m×{pc.PLAN['length_m']}m＝{pc.PLAN['area_m2']}㎡）に {pc.PLAN['seed_g']}g**"
                    f"（条間{pc.PLAN['row_cm']}cmで{pc.PLAN['lines']}条・条1mあたり約3.3g）。"
                    "残り約680gは紙袋で冷暗所に保管し、補播・発芽試験・2列目に使う。")
        st.caption("ミナミノカオリは雨に当たると穂についたまま芽が出やすい。6月上旬、穂が黄金色で粒が爪で割れない硬さになったら、"
                   "梅雨入り前の晴れ間にすぐ刈り、ハウス内で干す。")

    st.markdown("#### インターン形式：『通い型・2回分割』を推奨")
    st.dataframe(pd.DataFrame(pc.FORMATS, columns=["形式", "実現性", "リスク", "評価"]), hide_index=True, width="stretch")
    st.markdown("#### 科学と人間生活の4領域と、共通テスト・情報Ⅰ")
    st.dataframe(pd.DataFrame(pc.AREAS, columns=["自給の要素", "科学と人間生活の領域", "共通テストへの接続", "情報Ⅰ"]),
                 hide_index=True, width="stretch")
    st.markdown("#### 安全・法務で先に決めること")
    st.markdown("\n".join(f"- {s}" for s in pc.SAFETY))
    st.caption("ここに並べたのは実施前に確かめる項目で、法的な判断ではない。保険・労働の扱いは学校・教育委員会と確認する。")

st.markdown("#### 📝 共通テスト型問題")
for i, q in enumerate(pc.EXAM):
    ui.exam_question(f"panic_{i}", q)

ui.next_move_tag("panic")
