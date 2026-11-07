"""
保護（プロテクト）の部品 ─ Streamlit に依存しない純粋な関数

  - passcode_ok(): 教員ページの合言葉を、時間差で漏れない比較（hmac.compare_digest）で確かめる
  - clean_text(): 入力から制御文字を除き、長さを制限する（ダウンロードするテキストの安全化）
  - csv_safe(): CSV の各セルが「=」「+」「-」「@」などで始まるとき先頭に ' を付ける
                （Excel 等で開いたとき数式として実行される CSV インジェクションを防ぐ）

`python guard.py` で自己チェック。
"""
from __future__ import annotations

import hmac
import unicodedata

MAX_ATTEMPTS = 5          # 1セッションで合言葉を間違えてよい回数（超えたらこのセッションでは開かない）
MIN_PASSCODE_LEN = 8      # これより短い合言葉は設定ミスとみなして使わない（総当たり対策）
MAX_TEXT = 2000           # 1つの入力欄の最大文字数
_FORMULA_PREFIX = ("=", "+", "-", "@", "\t", "\r", "＝", "＋", "－", "＠")


def passcode_ok(given: str, secret: str | None) -> bool:
    """合言葉が一致するか。secret が未設定・短すぎるときは常に False（安全側に倒す）"""
    if not secret or len(secret) < MIN_PASSCODE_LEN or not given:
        return False
    return hmac.compare_digest(given.encode("utf-8"), secret.encode("utf-8"))


def clean_text(s: str | None, max_len: int = MAX_TEXT) -> str:
    """制御文字（改行・タブ以外）を除き、max_len 文字までに切る"""
    if not s:
        return ""
    out = "".join(ch for ch in s if ch in "\n\t" or unicodedata.category(ch)[0] != "C")
    return out[:max_len]


def csv_cell(v):
    """CSV の1セルを安全にする（文字列だけ。数値はそのまま）"""
    if isinstance(v, str):
        v = clean_text(v, 500)
        if v.startswith(_FORMULA_PREFIX):
            return "'" + v
    return v


def csv_safe(df):
    """pandas.DataFrame の全セルに csv_cell をかけたコピーを返す"""
    out = df.copy()
    for c in out.columns:
        out[c] = out[c].map(csv_cell)
    return out


def _self_check() -> None:
    assert passcode_ok("correct-horse", "correct-horse")
    assert not passcode_ok("wrong-horse!", "correct-horse")
    assert not passcode_ok("", "correct-horse")
    assert not passcode_ok("short", "short")                 # 短すぎる合言葉は無効
    assert not passcode_ok("anything", None)                  # 未設定なら開かない
    assert csv_cell("=HYPERLINK(\"http://x\")").startswith("'=")
    assert csv_cell("＝1+1").startswith("'") and csv_cell("-2+3") == "'-2+3"
    assert csv_cell("ハウス内の気温") == "ハウス内の気温" and csv_cell(3.5) == 3.5
    assert clean_text("a\x00b\x1bc\nd") == "abc\nd" and len(clean_text("x" * 5000)) == MAX_TEXT


if __name__ == "__main__":
    _self_check()
    print("guard: 自己チェックOK")
