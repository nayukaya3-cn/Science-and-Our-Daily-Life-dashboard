"""🧭 教員向け：暫定的な設計仮説H ─ 深層強化学習としての背骨（検証中）

生徒に教える内容ではない。教員側の設計原理で、しかも検証中の暫定仮説。
入力はこの画面の中だけで使い、保存も送信もしない（研究として集める版は、保護者同意と倫理審査を経てから）。
"""
import random

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import backbone as bb
import ui

ui.hero("教員向け ｜ 設計原理（検証中の暫定仮説）", "🧭 設計仮説H：深層強化学習としての背骨",
        "生徒に教える内容ではありません。指導結果を説明・予測できる間だけ使い、判定基準で維持・縮小・棄却を決めます。")

with st.container(border=True):
    st.markdown("**H**：「生徒が使う思考の型を最初から最後まで同じにすると、『楽しい思い出』が『得点』に変わる」という仕組みは、"
                "深層強化学習の **共有方策＋経験再生＋転移** としてうまく説明できる。")
    st.caption("文系向けの言い換え：同じ考え方のクセで何度も練習すると、畑での体験が試験でも使える力になる。"
               "その仕組みを、AIが練習から上達する方法になぞらえて設計してみる。うまく説明できなければ、この見立ては捨てる。")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["① 対応表と実装箇所", "② 誤差ログと経験再生", "③ 自己評価と教員評価の差",
                                        "④ 仮説の判定", "⑤ 暫定ルールと比喩の限界"])

# ── ① 対応表 ─────────────────────────────
with tab1:
    only_top = st.toggle("得点への寄与が大きい上位3行だけ表示", value=False)
    df = pd.DataFrame([{"DRLの構成要素": a, "ロードマップでの実体": b, "設計上の意味": c,
                        "このダッシュボードでの実装": d} for a, b, c, d, top in bb.DRL_TABLE if top or not only_top])
    st.table(df.set_index("DRLの構成要素"))
    st.caption("得点への寄与が大きいのは上3行（読み方と型を全フェーズで共通にすること）。"
               "経験再生などの実装は、研究テーマ・生徒に見せる実例という位置づけにとどめる。")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**背骨① 読解カード（共有エンコーダ）**")
        st.markdown("  \n".join(f"{i}. {q}" for i, (_, q) in enumerate(bb.READING_CARD, 1)))
    with c2:
        st.markdown("**背骨② P1〜P5（行動の選択肢）**")
        st.dataframe(pd.DataFrame([{"記号": k, "プロトコル": v[0], "言い換え": v[1]} for k, v in bb.PROTOCOLS.items()]),
                     hide_index=True, width="stretch")

# ── ② 誤差ログと経験再生 ──────────────────
with tab2:
    st.markdown("TD誤差（予想と実測のずれ）が大きかった経験ほど、受験期の復習で優先して出題する。")
    st.caption("δ＝|実測−予想|÷|予想|（単位のちがいを消すため相対誤差を使う）。"
               "優先度＝(δ＋0.01)^α。α＝0 なら全部同じ確率（一様抽選）。")
    session = st.session_state.get(ui.TD_LOG_KEY, {})
    rows = [{"場面": e["場面"], "protocol": e["protocol"], "predicted": e["predicted"],
             "observed": e["observed"], "unit": e["unit"], "出どころ": "FW（文書の例）"} for e in bb.FW_EPISODES]
    rows += [{"場面": r.get("question", k).replace("*", "")[:40], "protocol": r["protocol"],
              "predicted": r["predicted"], "observed": r["observed"], "unit": r["unit"],
              "出どころ": "このセッションの予想"} for k, r in session.items()]
    st.markdown("**経験再生バッファ**（行を足したり、前年度の値を打ち込んだりできる＝オフライン強化学習）")
    buf = st.data_editor(pd.DataFrame(rows), num_rows="dynamic", hide_index=True, width="stretch", key="replay_buf",
                         column_config={"protocol": st.column_config.SelectboxColumn(options=list(bb.PROTOCOLS)),
                                        "predicted": st.column_config.NumberColumn("予想"),
                                        "observed": st.column_config.NumberColumn("実測")})
    buf = buf.dropna(subset=["predicted", "observed", "protocol"]).reset_index(drop=True)
    buf["場面"] = buf["場面"].fillna("（無題）")
    buf["unit"] = buf["unit"].fillna("")
    if buf.empty:
        st.info("予想と実測が入った行がありません。")
    else:
        alpha = st.slider("α（ずれをどれだけ重視するか）", 0.0, 1.0, 0.6, 0.1)
        buf["δ"] = [bb.td_error(p, o) for p, o in zip(buf["predicted"], buf["observed"])]
        buf["引かれる確率"] = bb.sampling_probs(buf["δ"].tolist(), alpha)
        uniform = 1 / len(buf)
        fig = go.Figure()
        fig.add_bar(x=buf["場面"], y=buf["引かれる確率"], name=f"α={alpha:.1f}", marker_color="#4a6a8a")
        fig.add_scatter(x=buf["場面"], y=[uniform] * len(buf), name="一様（α=0）", mode="lines",
                        line=dict(dash="dash", color="#999"))
        fig.update_layout(height=320, margin=dict(t=20, b=10), yaxis_tickformat=".0%",
                          legend=dict(orientation="h"), yaxis_title="復習に引かれる確率")
        st.plotly_chart(fig, width="stretch")
        show = buf[["場面", "protocol", "predicted", "observed", "unit", "δ", "引かれる確率"]].copy()
        show["δ"] = show["δ"].round(2)
        show["引かれる確率"] = (show["引かれる確率"] * 100).round(1).astype(str) + "%"
        st.dataframe(show, hide_index=True, width="stretch")

        k = st.number_input("今日の復習で引く件数", 1, max(1, len(buf)), min(2, len(buf)))
        st.session_state.setdefault("replay_seed", 0)
        if st.button("🎲 復習する経験を引く"):
            st.session_state.replay_seed += 1
        if st.session_state.replay_seed:
            rng = random.Random(st.session_state.replay_seed)
            picks = rng.choices(range(len(buf)), weights=buf["引かれる確率"].tolist(), k=int(k))
            for i in picks:
                r = buf.iloc[i]
                st.markdown(f"- **{r['場面']}**（{bb.p_label(r['protocol'])}）：予想 {r['predicted']:g} → 実測 "
                            f"{r['observed']:g} {r['unit']}　δ＝{r['δ']:.2f} → この場面を型にした共通テスト型問題を出す")
        log_json = pd.DataFrame([bb.log_record("科学と人間生活", "FW", "-", "-", r["protocol"], r["predicted"],
                                               r["observed"], r["unit"]) | {"場面": r["場面"]}
                                 for _, r in buf.iterrows()]).to_json(orient="records", force_ascii=False, indent=1)
        st.download_button("誤差ログを JSON で保存（{subject, field, level, timestamp, judgement, protocol, td_error}）",
                           log_json.encode("utf-8"), "td_log.json", "application/json")
        st.caption("保存は手元へのダウンロードだけ。サーバーには残りません。")

# ── ③ Actor–Critic ───────────────────────
with tab3:
    st.markdown("生徒（Actor）の自己評価と、教員評価（Critic）の差が大きい観点が、個別指導の入口になる。")
    st.caption("1人分をその場で比べる道具です。名前は入れず、保存もしません。")
    grade = list(bb.RUBRIC)
    c1, c2 = st.columns(2)
    self_e = {p: c1.radio(f"自己評価 {bb.p_label(p)}", grade, index=1, horizontal=True, key=f"self_{p}")
              for p in bb.PROTOCOLS}
    teach_e = {p: c2.radio(f"教員評価 {bb.p_label(p)}", grade, index=1, horizontal=True, key=f"teach_{p}")
               for p in bb.PROTOCOLS}
    gaps = bb.critic_gaps(self_e, teach_e)
    gdf = pd.DataFrame(gaps, columns=["P", "差"])
    gdf["観点"] = gdf["P"].map(bb.p_label)
    fig = go.Figure(go.Bar(x=gdf["差"], y=gdf["観点"], orientation="h",
                           marker_color=["#d62728" if d > 0 else "#4a6a8a" if d < 0 else "#bbb" for d in gdf["差"]]))
    fig.update_layout(height=260, margin=dict(t=10, b=10), xaxis=dict(range=[-2.2, 2.2], dtick=1,
                      title="自己評価 − 教員評価（＋＝自己評価が甘い／−＝自信が足りない）"))
    st.plotly_chart(fig, width="stretch")
    top_p, top_d = gaps[0]
    if top_d == 0:
        st.success("自己評価と教員評価がそろっている。")
    else:
        st.warning(f"差がいちばん大きいのは **{bb.p_label(top_p)}**（{top_d:+d}）。ここが個別指導の入口。")

# ── ④ 判定 ──────────────────────────────
with tab4:
    st.markdown("**予測と確かめ方**（Hが正しければ、こうなるはず）")
    st.table(pd.DataFrame(bb.PREDICTIONS, columns=["", "予測", "確かめ方（既存の成果物で）", "Hを弱める結果"]).set_index(""))
    opts = {"未確認": None, "支持": True, "不支持": False}
    cols = st.columns(4)
    results = {k: opts[cols[i].radio(f"予測{k}", list(opts), key=f"pred_res_{k}")]
               for i, (k, *_r) in enumerate(bb.PREDICTIONS)}
    verdict, why = bb.judge(results)
    color = {"維持": "success", "縮小": "warning", "棄却": "error", "保留": "info"}[verdict]
    getattr(st, color)(f"**判定：{verdict}**（{why}）\n\n→ {bb.VERDICT_ACTION[verdict]}")
    if results["④"] is not None:
        st.caption(f"予測④（代替テーマ）は判定には使わない参考情報：{'支持' if results['④'] else '不支持'}")
    st.caption("判定時期の目安：3年生は12月の1日通し演習のあと、1・2年生は7月の収穫・発表のあと。"
               "三原西部モデルは1学年・少人数の想定のため、統計的な検定ではなく**傾向の確認**にとどまる。"
               "研究として結論を出す場合は、事前の保護者同意と倫理審査を経た版で実施する。")

# ── ⑤ 暫定ルールと限界 ────────────────────
with tab5:
    st.markdown("**仮説が維持されている間の暫定ルール**")
    for i, (title, body) in enumerate(bb.RULES, 1):
        st.markdown(f"{i}. **{title}**：{body}")
    st.markdown("このダッシュボードでは、ルール1＝全ページ共通の読解カード、ルール2＝「🎯 先に予想しよう」、"
                "ルール3＝クイズの P3・P4 で理由を書かせる欄と問題づくり、として実装している。")
    st.markdown("**比喩としての限界**")
    st.table(pd.DataFrame(bb.LIMITS, columns=["DRLでの前提", "生徒には当てはまらない点"]).set_index("DRLでの前提"))
