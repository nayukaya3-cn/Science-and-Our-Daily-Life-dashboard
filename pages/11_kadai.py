"""🧭 終章 これからの科学と人間生活 ─ 課題研究の進め方（教科書 p.182〜188・資料1）

1章A・2章Bで使ってきた「予想 → 測る → ずれ → ふり返る」の型を、課題研究の1周として総まとめする。
入力はこの画面の中だけで使い、保存も送信もしない（報告書の下書きは手元へのダウンロードだけ）。
"""
import pandas as pd
import streamlit as st

import backbone as bb
import guard
import kadai_core as kc
import sister_sites as ss
import ui

ui.hero("科学と人間生活 ｜ 終章 これからの科学と人間生活（p.182〜188）",
        "❓ どうして ○○ は △△ なのだろうか ─ 自分の問いで、1周回してみよう",
        "課題研究の進め方は、このダッシュボードの全ページで使ってきた型そのもの。"
        "新しい単元ではなく、これまでの総まとめとして、問い → 仮説 → 計画 → 実施 → 考察 → 報告 → 発表 を1周する。")

# ── 全体地図 ─────────────────────────────
st.subheader("🗺️ 課題研究の9段階 ＝ このダッシュボードの背骨")
names = [s[0] for s in kc.STEPS]
dot = ["digraph G {", 'rankdir=LR; node [shape=box, style="rounded,filled", fillcolor="#e4ecf5", '
       'color="#4a6a8a", fontname="sans-serif", fontsize=11, margin="0.3,0.1"]; edge [color="#4a6a8a"];']
for i, n in enumerate(names):
    dot.append(f'n{i} [label="{n}"];')
for i in range(len(names) - 1):
    dot.append(f"n{i} -> n{i + 1};")
src = names.index(kc.LOOP_FROM)
for t in kc.LOOP_TO:
    dot.append(f'n{src} -> n{names.index(t)} [style=dashed, color="#c4651a", label="ふり返る", fontsize=10];')
dot.append(f'n{len(names) - 1} -> n0 [style=dotted, label="次の問いへ", fontsize=10];')
dot.append("}")
st.graphviz_chart("\n".join(dot), width="stretch")
st.dataframe(pd.DataFrame([{"段階": a, "教科書の要点": b, "プロトコル": bb.p_label(c), "フェーズ": d,
                            "このダッシュボードで練習した場所": e} for a, b, c, d, e in kc.STEPS]),
             hide_index=True, width="stretch")
ui.hint("オレンジの点線『ふり返る』がいちばん大事。仮説が外れても、都合の悪い結果を無視せず、"
        "その理由を考えて仮説や方法を直す。これは各ページの『ずれ δ』と同じ考え方。")

tab1, tab2, tab3, tab4 = st.tabs(["① 自分の問いを立てる", "② 報告書ビルダー", "③ 調べ方・著作権・安全",
                                  "④ テーマ例と盲斑の実験"])

# ── ① 問いを立てる ─────────────────────────────
with tab1:
    st.markdown("#### 教科書の型に当てはめて、問いと仮説を1行ずつ")
    c1, c2 = st.columns(2)
    x = c1.text_input("○○（何が）", key="kd_x", max_chars=60, placeholder="例：パン生地")
    y = c2.text_input("△△（どうなる）", key="kd_y", max_chars=60, placeholder="例：30℃ だとよくふくらむ")
    if x and y:
        st.success(f"❓ どうして {guard.clean_text(x)} は {guard.clean_text(y)} のだろうか")
    c1, c2, c3 = st.columns(3)
    cond = c1.text_input("○○であるならば（条件）", key="kd_cond", max_chars=80, placeholder="例：酵母の酵素が温度で働きを変える")
    act = c2.text_input("◇◇すると（操作）", key="kd_act", max_chars=80, placeholder="例：20・25・30・35℃ で静置する")
    val = c3.text_input("△△の値が求められる（測るもの）", key="kd_val", max_chars=80, placeholder="例：60分後の生地の体積（mL）")
    if cond and act and val:
        st.info(f"仮説：{guard.clean_text(cond)} ならば、{guard.clean_text(act)} と、{guard.clean_text(val)} に差が出る。")
    with st.container(border=True):
        st.markdown("**📋 計画のチェック（読解カードの③『統制』を先に決める）**")
        ok = [st.checkbox(t, key=f"kd_chk_{i}") for i, t in enumerate([
            "変える条件は1つだけ（温度なら温度だけ）",
            "そろえる条件を3つ以上書き出した（量・時間・器具など）",
            "測る前に、結果の予想を数字で書いた",
            "安全面（火・刃物・薬品・微生物）を先生に相談した",
        ])]
        st.progress(sum(ok) / len(ok), text=f"{sum(ok)} / {len(ok)}")

# ── ② 報告書ビルダー ─────────────────────────────
with tab2:
    st.markdown("#### 報告書の8項目（p.184）を埋めると、下書き（Markdown）を保存できる")
    m1, m2, m3, m4 = st.columns(4)
    meta = {"題目": m1.text_input("研究活動題目", key="rp_title", max_chars=80),
            "報告者": m2.text_input("報告者", key="rp_by", max_chars=40),
            "共同実験者": m3.text_input("共同実験者", key="rp_with", max_chars=80),
            "実施日": m4.text_input("実施日", key="rp_date", max_chars=20, placeholder="2026年11月8日")}
    body = {}
    for item, how, why in kc.REPORT_ITEMS[:-1]:
        body[item] = st.text_area(f"{item}　─ {why}", key=f"rp_{item}", max_chars=guard.MAX_TEXT,
                                  placeholder=how, height=80)
    st.markdown("**参考文献**（1行に1つ。書き方の例どおりか自動で確かめる）")
    st.caption("本：著者名(出版年)『書名』(出版社)　／　論文：著者名(出版年)「論文名」『雑誌名』○○号　／　"
               "Web：「Webサイト名」URL(https://…) xxxx年x月x日確認")
    refs_raw = st.text_area("参考文献", key="rp_refs", max_chars=guard.MAX_TEXT, label_visibility="collapsed",
                            placeholder="ファラデー(2010年)『ロウソクの科学』(岩波書店)")
    refs = [r for r in guard.clean_text(refs_raw).splitlines() if r.strip()]
    for r in refs:
        miss = kc.check_reference(r)
        (st.success if not miss else st.warning)(r if not miss else f"{r} → 足りないもの：{'・'.join(miss)}")
    filled = sum(bool(v.strip()) for v in body.values()) + bool(refs)
    st.progress(filled / len(kc.REPORT_ITEMS), text=f"埋まった項目：{filled} / {len(kc.REPORT_ITEMS)}")
    md = kc.report_markdown({k: guard.clean_text(v, 200) for k, v in meta.items()},
                            {k: guard.clean_text(v) for k, v in body.items()}, refs)
    st.download_button("報告書の下書きを保存（.md）", md.encode("utf-8"), "課題研究_報告書_下書き.md", "text/markdown")
    ui.hint("『方法』は過去形で（…した。）。『考察』は『…と考える。』で結ぶ。"
            "表の番号と表題は表の上、図の番号と表題は図の下。他の人が同じ手順で追試できるかが合格ライン。")

# ── ③ 調べ方・著作権・安全 ─────────────────────────────
with tab3:
    st.markdown("#### いろいろな資料から広く学ぶ（p.183）")
    st.markdown("- **書籍**：辞書・百科事典 → 参考図書 → 科学者が書いた本。データは白書・年鑑など信頼できる資料で\n"
                "- **地域施設**：科学館・博物館（広島県内なら、まず地元の科学館や大学の公開講座を探す）\n"
                "- **インターネット**：大学・研究機関・学会・企業のWebサイト。質問受付の電子メールも使える")
    st.dataframe(pd.DataFrame(kc.INTERNET_CAUTIONS, columns=["注意", "教科書の要点", "情報Ⅰとのつながり"]),
                 hide_index=True, width="stretch")
    st.warning("著作物（文章・写真・イラスト）を許可なく使うと著作権侵害になることがある。引用は「」でくくって出典を書く。"
               "**教科書の紙面を撮った写真は、報告書・SNS・このようなWebアプリに載せない**（このリポジトリにも入れていない）。",
               icon="©️")
    st.markdown("#### 実験・フィールドワークの安全チェック（資料1・資料7）")
    done = [st.checkbox(t, key=f"safe_{i}") for i, t in enumerate(kc.SAFETY)]
    if all(done):
        st.success("全項目を確認しました。当日も先生の指示に従いましょう。")
    else:
        st.caption(f"確認済み {sum(done)} / {len(kc.SAFETY)}。事故が起きたら、すぐに先生に報告する。")

# ── ④ テーマ例 ─────────────────────────────
with tab4:
    st.markdown("#### 教科書のテーマ例を、三原西部のフィールド（畑・ハウス・パン工房）に置きかえる")
    st.dataframe(pd.DataFrame([{"テーマ例": f"{n} {t}", "関連": rel, "教科書の問い": q,
                                "フィールドでの置きかえ": fw, "単元": u} for n, t, rel, q, fw, u in kc.THEMES]),
                 hide_index=True, width="stretch")
    st.caption("テーマ例3・5は今回の資料に含まれていないため未収録。")
    unit = st.selectbox("つながる姉妹サイトの教材（単元）", sorted({t[5] for t in kc.THEMES}), key="kd_unit")
    ss.render_unit(unit, "tanpaku")

    st.markdown("#### 🔬 テーマ例1をその場で：盲斑（もうはん）で消える点は、何色に見える？")
    ui.hint("左眼を閉じ、右眼で ＋ を見つめたまま画面に顔を近づけたり遠ざけたりする。ある距離で ● が消える。"
            "そのとき、消えた場所は何色に見えるだろうか？ 先に予想してから試そう。")
    c1, c2, gap = st.columns([1, 1, 1])
    bg = c1.selectbox("パネルの色", ["黄", "青", "白", "緑"], key="bs_bg")
    dotc = c2.selectbox("点の色", ["青", "黄", "黒", "赤"], key="bs_dot")
    d = gap.slider("＋ と ● の間隔", 4, 14, 8, key="bs_gap")
    cmap = {"黄": "#f2d43a", "青": "#1f5fae", "白": "#ffffff", "緑": "#3a9a4a", "黒": "#111111", "赤": "#c62828"}
    plus = "#111111" if bg in ("黄", "白") else "#ffffff"
    st.markdown(f"<div style='background:{cmap[bg]};height:140px;border:1px solid #888;border-radius:8px;"
                f"display:flex;align-items:center;padding:0 6%;'>"
                f"<span style='font-size:44px;font-weight:700;color:{plus}'>＋</span>"
                f"<span style='display:inline-block;width:{d * 5}%'></span>"
                f"<span style='display:inline-block;width:36px;height:36px;border-radius:50%;background:{cmap[dotc]}'></span>"
                f"</div>", unsafe_allow_html=True)
    st.caption("間隔を2倍・3倍にすると、消える距離はどう変わる？ 結果を表にして、読解カードで読もう。")

    ui.reading_card(
        axis="眼とパネルの距離と、● が消えるかどうか（色の組み合わせごと）",
        unit="cm（距離）と、見えた色（記録）",
        control="そろえた：片眼で＋を見つめる・明るさ・パネルの大きさ。変えた：色の組み合わせ、または＋と●の間隔",
        can="ある距離で●が消える ＝ 網膜に光を感じない場所（盲斑）がある。消えた場所は周りの色で埋めて見えることが多い",
        cannot="脳が『どうやって』周りの色で埋めているかの仕組み（この実験は見え方を記録しただけ）",
        protocols=["P3", "P4"], material="テーマ例1 図a 実験用パネル")

ui.next_move_tag("kadai")
