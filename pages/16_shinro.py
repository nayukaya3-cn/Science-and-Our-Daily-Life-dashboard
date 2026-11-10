"""🤖 終章：3Dプリンター×産業用ロボットで拓く進路探究（14コマ＋校外1日）

課題は生徒が設定し、教員はテーマ例と職業の事例で「選べる幅」を用意する。
入力はこの画面の中だけで使い、保存も送信もしない（進路ワークは手元へのダウンロードだけ）。
"""
import datetime as dt

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import guard
import shinro_core as sh
import ui

ui.hero("科学と人間生活 ｜ 終章 これからの科学と人間生活 ｜ 課題研究テーマ例と職業の事例",
        f"❓ {sh.LEAD_QUESTION}",
        "3Dプリンターとロボットに触れて『問いの種』を集め、17のテーマ例から自分の課題を決める。"
        "どのテーマも『変えるもの1つ・そろえるもの・測るもの』が決まる形 ─ 読解カードの③が、そのまま問いになっている。")
ui.hint(sh.EASY_WORDS)

c1, c2 = st.columns([1, 2])
age = c1.number_input("いまの年齢", 12, 80, 16, 1, key="shinro_age")
this_year = dt.date.today().year
c2.metric(f"{sh.TARGET_YEAR}年のあなた", f"{sh.age_in(sh.TARGET_YEAR, this_year, int(age))} 歳",
          f"国の導入目標：{sh.TARGET_YEAR}年までに18分野で{sh.TARGET_UNITS}", delta_color="off", delta_arrow="off")
st.caption("この問いに、決まった正解はない。大人も、学びながら答えを探している ─ 作成者が受講中の講座を、⑤『学びの実例』に載せた。")
with st.expander("18分野を見る"):
    st.markdown("、".join(sh.FIELDS_18))
    st.caption("国の戦略の公開資料（2026年時点）による。目標や分野は改定されることがあるので、授業で使う前に最新の資料で確かめる。")

ui.lesson_plan([{"順": n, "段階": s, "コマ数": k, "内容": c} for n, s, k, c in sh.FLOW],
               "🧑‍🏫 先生向け：終章の進め方（全体14コマ＋校外1日）")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["① 導入実習", "② テーマをえらぶ（17）", "③ 6つの関わり方・進路ワーク",
                                        "④ 安全・特別教育（先生向け）", "⑤ 学びの実例"])

# ── ① 導入実習 ─────────────────────────────
with tab1:
    st.markdown("#### つくる科学・動かす科学（6コマ）")
    st.caption("目的は技能の習得ではなく、各コマで『問いの種』を1つ以上書くこと。種は②のテーマ例にそのままつながる。")
    st.dataframe(pd.DataFrame(sh.INTRO, columns=["コマ", "テーマ", "活動", "対応する内容", "情報Ⅰ連携", "問いの種の例"]),
                 hide_index=True, width="stretch")
    st.markdown("#### 第4コマ：リスク ＝ 起こりやすさ × 被害（💻 情報Ⅰ）")
    k1, k2 = st.columns(2)
    li = k1.select_slider("起こりやすさ", options=list(sh.LIKELIHOOD), value=2, format_func=lambda v: f"{v}：{sh.LIKELIHOOD[v]}",
                          key="shinro_li")
    se = k2.select_slider("被害の大きさ", options=list(sh.SEVERITY), value=2, format_func=lambda v: f"{v}：{sh.SEVERITY[v]}",
                          key="shinro_se")
    score, verdict = sh.risk(li, se)
    st.metric("リスクの点数", f"{li} × {se} ＝ {score}")
    (st.error if score >= 6 else st.warning if score >= 3 else st.success)(verdict)
    st.markdown("**対策の3本柱**：" + "／".join(sh.RISK_ACTIONS))
    st.caption("3×3 の表は説明用の区分。『被害』を下げるのは難しいので、まず『起こりやすさ』を下げる（離す・止める・学ぶ）。")
    st.info("発展（希望者）：ROS 2 のシミュレータで第5コマの動作を再現し、実機とのずれ（モデルと現実の違い）を言葉にする。", icon="🧪")

# ── ② テーマ ─────────────────────────────
with tab2:
    st.markdown("#### 課題研究テーマ例（17テーマ）")
    f1, f2 = st.columns(2)
    areas = f1.multiselect("領域", list(sh.AREAS), default=[], placeholder="すべて", key="shinro_areas")
    level = f2.select_slider("難易度（ここまで）", options=[1, 2, 3], value=3, format_func=sh.stars, key="shinro_level")
    g1, g2 = st.columns(2)
    bun = g1.toggle("文系の生徒に入りやすいテーマだけ", value=False, key="shinro_bun")
    fw = g2.toggle("三原西部の圃場と直結するテーマだけ（No.3・8・14）", value=False, key="shinro_fw")
    themes = sh.filter_themes(areas or None, level, bun, fw)
    st.caption(f"{len(themes)} / {len(sh.THEMES)} テーマ。1年は ★〜★★ の範囲が目安。")
    st.dataframe(pd.DataFrame([{"No.": t["no"], "テーマ（問い）": t["q"], "難易度": sh.stars(t["level"]),
                                "文": "文" if t["bun"] else "", "領域": t["area"], "つながる職業": t["jobs"]}
                               for t in themes]), hide_index=True, width="stretch")
    if themes:
        no = st.selectbox("くわしく見るテーマ", [t["no"] for t in themes], key="shinro_no",
                          format_func=lambda n: f"No.{n} {sh.THEMES[n - 1]['q']}")
        t = sh.THEMES[no - 1]
        with st.container(border=True):
            st.markdown(f"**No.{t['no']} {t['q']}**　{sh.stars(t['level'])}")
            a, b, c = st.columns(3)
            a.markdown(f"**変えるもの（1つ）**  \n{t['change']}")
            b.markdown(f"**そろえるもの**  \n{t['control']}")
            c.markdown(f"**測るもの（単位）**  \n{t['measure']}")
            st.markdown(f"💻 **情報Ⅰ連携**：{t['joho']}　｜　**立ち位置**：{sh.role_of(no) or '（表では未割り当て）'}　｜　"
                        f"**つながる職業**：{t['jobs']}")
            if no in sh.THEME_NOTES:
                st.warning(sh.THEME_NOTES[no], icon="⚠️")
        ui.reading_card(
            axis=f"{t['change']} と、{t['measure']}",
            unit=t["measure"],
            control=f"そろえる：{t['control']}。変える：{t['change']}",
            can="（自分で書く）変えたもの1つと、測ったものの関係",
            cannot="（自分で書く）測っていない範囲・そろえきれなかった条件・ほかの材料や場所での結果",
            protocols=["P3", "P2"], material="自分の課題研究の計画")
    st.info(f"**最初の一手**：{sh.FIRST_STEP}", icon="👣")

# ── ③ 6つの関わり方 ─────────────────────────────
with tab3:
    st.markdown("#### ロボットとの6つの関わり方")
    st.dataframe(pd.DataFrame([{"立ち位置": r, "仕事の例": job, "文系にも開かれた入口": door, "関係する学び": learn,
                                "対応テーマ": "・".join(f"No.{n}" for n in nos)} for r, job, door, learn, nos in sh.ROLES]),
                 hide_index=True, width="stretch")
    st.markdown("#### 職業につながる科学の事例")
    st.dataframe(pd.DataFrame([{"事例": n, "何をしているか": w, "使われている科学": s, "関わる仕事": j,
                                "対応テーマ": "・".join(f"No.{x}" for x in nos) or "導入実習"} for n, w, s, j, nos in sh.CASES]),
                 hide_index=True, width="stretch")
    st.caption("事例は『使われている科学 → 関わる仕事 → 高校で学べること』の順に読む。1事例を読解カード4項目で分析し、"
               "④『この発表から言えないこと』（実証段階である、費用が書いていない等）まで書く。事例の現状は最新の資料で確かめる。")

    st.markdown("#### ✍️ 進路ワーク（1枚）")
    w1, w2 = st.columns(2)
    field = w1.selectbox("18分野から1つ選ぶ", sh.FIELDS_18, index=12, key="shinro_field")
    role = w2.selectbox("自分がなれそうな立ち位置", [r[0] for r in sh.ROLES], key="shinro_role")
    rows, weak = {}, []
    for i, item in enumerate(sh.CAREER_ITEMS):
        a, b = st.columns([4, 1])
        rows[item] = a.text_input(item, key=f"shinro_w{i}", max_chars=guard.MAX_TEXT)
        if b.checkbox("言えない（根拠が弱い）", key=f"shinro_weak{i}"):
            weak.append(item)
    st.download_button("進路ワークをテキストで保存", guard.clean_text(sh.career_sheet(field, role, rows, weak), 10000).encode("utf-8"),
                       "進路ワーク.txt", "text/plain")
    st.caption("根拠の弱い主張に『言えない』の印を付けられることが、読解カード④の力。名前は書かない（このアプリは入力を保存しません）。")

# ── ④ 安全・特別教育 ─────────────────────────────
with tab4:
    st.markdown("#### 安全・倫理（実施前に固定する）")
    for s in sh.SAFETY:
        st.markdown(f"- {s}")
    st.markdown("#### 産業用ロボット特別教育の活用（3段階）")
    st.caption("特別教育は『全員に資格を取らせるもの』ではなく、進路を具体化した生徒が使える切符として終章に組み込む。")
    st.dataframe(pd.DataFrame(sh.TRAINING, columns=["段階", "対象", "内容", "修了証"]), hide_index=True, width="stretch")
    st.error("**未確定事項（実施前に必ず確認）**  \n" + "  \n".join(f"- {s}" for s in sh.TRAINING_NOTES))
    st.caption("普通科・商業科での現実解：①は校内、②は外部連携。校内で正式な修了証まで出すには、指導できる教員と産業用ロボットの実機が必要になる。")

# ── ⑤ 学びの実例 ─────────────────────────────
with tab5:
    today = dt.date.today()
    st.markdown(f"#### 大人も同じ問いの途中にいる：{sh.COURSE_NAME}（作成者が学習中）")
    st.caption("教える側も、学び終えた人ではなく学んでいる途中の人。講座の見出しを『6つの関わり方』に当てはめると、"
               "いまの学びがどの立ち位置を厚くしていて、どこがうすいかが見える。同じことを、自分の時間割や習いごとでもやってみよう。")
    nxt = sh.next_lecture(today)
    done = sum(1 for x in sh.LECTURES if sh.lecture_status(*x[2], today) == "済")
    m1, m2, m3 = st.columns(3)
    m1.metric("受講の進み", f"{done} / {len(sh.LECTURES)} 回")
    m2.metric(f"次回（{nxt[0]} 第{nxt[1]}回）" if nxt else "次回", f"{nxt[2][0]}/{nxt[2][1]}（木）" if nxt else "全回終了")
    m3.metric(f"{sh.TARGET_YEAR}年まで", f"あと {max(0, sh.TARGET_YEAR - today.year)} 年")

    st.markdown("**3つの編のつながり**：基礎編（ロボットがどう学ぶか）→ 応用編1（現場で動かし続ける）→ 応用編2（体を数式で表す）")
    for col, (part, (about, plain)) in zip(st.columns(3), sh.COURSE_PARTS.items()):
        with col.container(border=True):
            n_all = sum(1 for x in sh.LECTURES if x[0] == part)
            n_done = sum(1 for x in sh.LECTURES if x[0] == part and sh.lecture_status(*x[2], today) == "済")
            st.markdown(f"**{part}**")
            st.markdown(f"{about}  \n高校の言葉で：{plain}")
            st.progress(n_done / n_all, text=f"{n_done} / {n_all} 回")

    part = st.radio("編をえらぶ", list(sh.COURSE_PARTS), index=len(sh.COURSE_PARTS) - 1, horizontal=True, key="shinro_course_part")
    st.dataframe(pd.DataFrame(sh.lectures_of(part, today)), hide_index=True, width="stretch")

    st.markdown("#### この学びは、6つの立ち位置のどこを厚くしているか")
    cov = sh.role_coverage()
    top = max(cov.values())
    fig = go.Figure(go.Bar(x=list(cov), y=list(cov.values()), text=list(cov.values()), textposition="outside",
                           marker_color=["#4a6a8a" if v == top else "#a9bccf" for v in cov.values()]))
    fig.update_layout(height=300, margin=dict(t=20, b=10, l=10, r=10), yaxis=dict(title="あてはまる講義の回数", range=[0, top + 1.5]),
                      xaxis=dict(title="ロボットとの6つの関わり方"))
    st.plotly_chart(fig, width="stretch")
    st.info(sh.coverage_comment(), icon="🧭")
    ui.reading_card(
        axis="6つの立ち位置 × あてはまる講義の回数", unit="回（1回の講義が2つの立ち位置にあたることもある）",
        control="そろえた：同じ講座の日程表の見出しだけで数えた。変えた：立ち位置",
        can="この講座の見出しは『つくる』にあたるものがいちばん多い",
        cannot="受講者が『つくる側』になれるか・回数の多い立ち位置が自分に向いているか（当てはめは作成者の見立て。"
               "講義の深さや、講座の外での経験は数えていない）",
        protocols=["P2", "P3"], material="上の棒グラフ")
    with st.expander("この実例の読み方（出どころと限界）"):
        for n in sh.COURSE_NOTES:
            st.markdown(f"- {n}")

ui.next_move_tag("shinro")
