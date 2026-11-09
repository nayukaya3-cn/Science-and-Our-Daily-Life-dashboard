"""
画面の共通部品（どのページでも同じ見た目にする）
  - hero(): ページ上部の見出しカード
  - hint(): 「やさしい解説」スイッチがONのときだけ出す説明
  - chain_html(): アミノ酸を色つきの丸で並べる（教科書の図3・図4のイメージ）
  - reading_card(): 読解カード（4項目）。全ページで同じ見た目・同じ言葉（背骨①＝共有エンコーダ）
  - predict(): 先に予想 → 答え → ずれ δ（背骨の「TD誤差が出る場面」。ログはセッションの中だけ）
  - exam_question(): 共通テスト型問題（1問）。P1〜P5 のラベルつきで、選ぶと解説が出る
  - lesson_plan(): 単元の構成（コマ割り）を折りたたんで見せる（先生向けの情報を、生徒の画面のじゃまにしない）
  - next_move_tag(): ページの最後の「🏷️ 次の一手」タグ（人生戦略・戦術のヒント集への入口）
  - teacher_gate(): 教員ページの鍵（合言葉は Secrets か環境変数。未設定なら開かない＝安全側）
"""
from __future__ import annotations

import html
import os
import random

import streamlit as st

import backbone as bb
import guard
import next_move as nm
import tanpaku_core as tc

API_VERSION = 5          # 画面部品の版。app.py が古いモジュールの読み込みを検出するのに使う
EASY_KEY = "easy_mode"  # app.py のサイドバーのスイッチと共有
TD_LOG_KEY = "td_log"   # 予想と実測のずれ（誤差ログ）。このセッションの中だけ

_CSS = """
<style>
.hero {padding: 1.4rem 1.6rem 1.2rem; border-radius: 16px;
       background: linear-gradient(120deg, #e3efd6 0%, #e4ecf5 100%);
       color: #22313f; margin-bottom: 1rem;}
.hero .eyebrow {font-size: .85rem; letter-spacing: .08em; color: #4a6a8a; margin: 0 0 .3rem 0;}
.hero h1 {margin: 0 0 .5rem 0; font-size: 1.7rem; line-height: 1.35; color: #22313f;}
.hero .lead {margin: 0; font-size: 1.02rem; line-height: 1.8;}
.pbadge {display:inline-block; padding:1px 8px; margin-right:4px; border-radius:10px;
          background:#e4ecf5; color:#22313f; font-size:.8rem; font-weight:600;}
.nmtag {display:inline-block; padding:2px 10px; border-radius:10px; background:#fdecc8;
         color:#6b4a00; font-size:.8rem; font-weight:700; margin-right:6px;}
.aa {display:inline-block; border-radius:50%; color:#111; text-align:center;
     font-size:12px; font-weight:600; border:1px solid #555; position:relative;}
</style>
"""


def hero(eyebrow: str, title: str, lead: str) -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(
        f"<div class='hero'><p class='eyebrow'>{html.escape(eyebrow)}</p>"
        f"<h1>{html.escape(title)}</h1><p class='lead'>{html.escape(lead)}</p></div>",
        unsafe_allow_html=True,
    )


def easy() -> bool:
    return st.session_state.get(EASY_KEY, True)


def hint(text: str) -> None:
    if easy():
        st.info(text, icon="💡")


def chain_html(seq: str, size: int = 26, gap: int = 2, scatter: bool = False, seed: int = 0) -> str:
    rng = random.Random(seed)
    cells = []
    for a in seq:
        dy = rng.randint(-14, 14) if scatter else 0
        mx = rng.randint(2, 10) if scatter else gap
        name = tc.AMINO.get(a, ("?",))[0]
        cells.append(
            f"<span class='aa' title='{html.escape(name)}' style='width:{size}px;height:{size}px;"
            f"line-height:{size}px;background:{tc.COLOR.get(a, '#ccc')};margin:0 {mx}px;top:{dy}px'>"
            f"{html.escape(a)}</span>")
    return "<div style='line-height:46px;padding:6px 0'>" + "".join(cells) + "</div>"


def chain(seq: str, **kw) -> None:
    st.markdown(_CSS + chain_html(seq, **kw), unsafe_allow_html=True)


def badges(codes: list[str]) -> str:
    return "".join(f"<span class='pbadge'>{html.escape(bb.p_label(c))}</span>" for c in codes)


def reading_card(axis: str, unit: str, control: str, can: str, cannot: str,
                 protocols: list[str], material: str = "このページの図・表") -> None:
    """読解カード（4項目）。問いは先に見せ、答えは自分で考えてから開く。
    理科基礎・情報Ⅰ第4問・フィールドワークの野帳で同じカードを使う（方策を途中で取り替えない）"""
    st.markdown(_CSS, unsafe_allow_html=True)
    answers = (axis, unit, control, f"**言える**：{can}  \n**言えない**：{cannot}")
    with st.container(border=True):
        st.markdown(f"**🔎 読解カード**　{badges(protocols)}", unsafe_allow_html=True)
        st.caption(f"読むもの：{material}。理科基礎・情報Ⅰ第4問・フィールドワークの野帳でも、同じ4項目で読む。")
        st.markdown("  \n".join(f"{i}. {q}" for i, (_, q) in enumerate(bb.READING_CARD, 1)))
        with st.expander("答え合わせ（自分で考えてから開く）"):
            for (name, _), a in zip(bb.READING_CARD, answers):
                st.markdown(f"**{name}**　{a}")


def predict(key: str, question: str, actual: float, unit: str, *, protocol: str = "P4",
            min_value: float = 0.0, max_value: float = 100.0, step: float = 1.0,
            value: float | None = None, fmt: str = "%.0f", field: str = "生命の科学") -> dict | None:
    """先に予想させ、答えとのずれ δ（相対誤差）を見せる。結果はこのセッションの誤差ログに入る（保存・送信しない）"""
    log = st.session_state.setdefault(TD_LOG_KEY, {})
    with st.container(border=True):
        st.markdown(f"**🎯 先に予想しよう**　{badges([protocol])}", unsafe_allow_html=True)
        st.markdown(question)
        with st.form(f"pred_{key}"):
            guess = st.number_input(f"あなたの予想（{unit}）", min_value=min_value, max_value=max_value,
                                    value=min_value if value is None else value, step=step, format=fmt)
            done = st.form_submit_button("予想を確定して答えを見る")
        if done:
            log[key] = bb.log_record("科学と人間生活", field, "-", "予想", protocol, float(guess), float(actual), unit)
            log[key]["question"] = question
        rec = log.get(key)
        if rec is None:
            st.caption("予想を書いてから答えを見ると、ずれ（δ）が学びの入口になる。")
            return None
        d = rec["td_error"]
        c1, c2, c3 = st.columns(3)
        c1.metric("あなたの予想", f"{rec['predicted']:g} {unit}")
        c2.metric("答え", f"{actual:.3g} {unit}")
        c3.metric("ずれ δ", f"{d:.2f}", help="δ＝|答え−予想|÷|予想|。単位がちがう問題どうしでも比べられる")
        if d < 0.1:
            st.success("ほぼ予想どおり。なぜ当てられたのか、根拠を1行で言えるかな？")
        elif d < 0.5:
            st.warning("少しずれた。どこで見込みがちがったか考えよう。")
        else:
            st.error("大きくずれた！ ここがいちばんの学びどころ。")
        st.text_input("ずれの理由（1行：考え方／測り方／自然のばらつき）", key=f"why_{key}", max_chars=200)
        return rec


def exam_question(key: str, item: dict) -> bool | None:
    """共通テスト型問題を1問出す。item＝dict(p, subject, q, opts, ans, exp)。
    正解なら True、不正解なら False、まだ選んでいなければ None。回答は保存・送信しない"""
    st.markdown(_CSS, unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f"**📝 共通テスト型問題**（{html.escape(item['subject'])}）　{badges([item['p']])}", unsafe_allow_html=True)
        choice = st.radio(item["q"], item["opts"], index=None, key=f"exam_{key}")
        if choice is None:
            st.caption("読解カードの4項目（とくに③ 何をそろえ、何を変えたか）で読んでから選ぼう。")
            return None
        ok = choice == item["ans"]
        (st.success if ok else st.error)(("正解！ " if ok else f"ざんねん。正解は「{item['ans']}」。") + item["exp"])
        return ok


def lesson_plan(rows: list[dict], title: str = "🧑‍🏫 先生向け：単元の構成（コマ割り）") -> None:
    """コマ割りの表。生徒の画面では閉じておく"""
    with st.expander(title):
        st.dataframe(rows, hide_index=True, width="stretch")


def next_move_tag(page_key: str) -> None:
    """ページの最後に付けるタグ：このページの学びを、人生の戦略・戦術に持ち出すヒント1つ"""
    h = nm.BY_ID[nm.PAGE_TAG[page_key]]
    st.markdown(_CSS, unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f"<span class='nmtag'>🏷️ 次の一手</span><b>{html.escape(h['icon'] + ' ' + h['title'])}</b>",
                    unsafe_allow_html=True)
        st.markdown(f"**戦略**：{h['strategy']}  \n**戦術**：{h['tactics']}")
        st.caption("ほかのヒントと『次の一手シート』は、左メニュー「🚀 次の一手」へ（今後の人生戦略・戦術を立案する際のヒント集）。")


TEACHER_OK_KEY = "teacher_ok"
_TEACHER_TRIES = "teacher_tries"


def _teacher_secret() -> str | None:
    """合言葉：Streamlit の Secrets（teacher_passcode）→ 環境変数 TEACHER_PASSCODE の順に探す"""
    try:
        v = st.secrets.get("teacher_passcode")
    except Exception:  # secrets.toml が無い環境（手元・テスト）
        v = None
    return v or os.environ.get("TEACHER_PASSCODE") or None


def teacher_gate() -> bool:
    """教員ページの鍵。True のときだけ中身を表示する。
    - 合言葉が未設定（または8文字未満）なら、誰にも開かない（公開アプリで生徒が評価欄を見られないように）
    - 間違いは1セッション guard.MAX_ATTEMPTS 回まで。比較は時間差で漏れない方法で行う
    - 開いた状態はこのセッションの中だけ（保存しない）"""
    secret = _teacher_secret()
    if st.session_state.get(TEACHER_OK_KEY):
        if st.sidebar.button("🔒 教員ページを閉じる", key="teacher_logout"):
            st.session_state[TEACHER_OK_KEY] = False
            st.rerun()
        return True
    with st.container(border=True):
        st.markdown("### 🔒 教員向けページ（合言葉が必要です）")
        if not secret or len(secret) < guard.MIN_PASSCODE_LEN:
            st.warning("このアプリには教員用の合言葉が設定されていないため、教員ページは閉じています。"
                       "管理者は Streamlit Community Cloud の **Settings → Secrets** に "
                       "`teacher_passcode = \"8文字以上\"` を設定してください（手元では環境変数 TEACHER_PASSCODE でも可）。")
            return False
        tries = st.session_state.get(_TEACHER_TRIES, 0)
        if tries >= guard.MAX_ATTEMPTS:
            st.error("合言葉を続けて間違えたため、このセッションでは開けません。ページを開き直してください。")
            return False
        with st.form("teacher_login"):
            given = st.text_input("合言葉", type="password", max_chars=128)
            ok = st.form_submit_button("開く")
        if ok:
            if guard.passcode_ok(given, secret):
                st.session_state[TEACHER_OK_KEY] = True
                st.session_state[_TEACHER_TRIES] = 0
                st.rerun()
            st.session_state[_TEACHER_TRIES] = tries + 1
            if tries + 1 >= guard.MAX_ATTEMPTS:
                st.rerun()   # すぐに入力欄を消してロック表示に切りかえる
            st.error(f"合言葉がちがいます（残り {guard.MAX_ATTEMPTS - tries - 1} 回）。")
        st.caption("生徒向けのページは合言葉なしで使えます。教員ページの入力も、保存・送信はしません。")
    return False
