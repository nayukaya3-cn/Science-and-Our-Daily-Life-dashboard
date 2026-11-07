"""姉妹サイト（教材ネットワーク）のテスト：リンク先のページがこのリポジトリに実在するか"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sister_sites as ss  # noqa: E402
import tanpaku_core as tc  # noqa: E402


def test_self_check():
    ss._self_check()


def test_local_pages_exist():
    assert ss.check_local_pages("tanpaku", ROOT) == []


def test_every_local_page_has_partner():
    for page in ss.local_pages("tanpaku"):
        assert ss.pairs_for("tanpaku", page), page


def test_wheat_complement():
    rows = tc.complement_table(tc.HUMAN_PROTEINS["ヘモグロビンβ鎖・先頭30個（酸素を運ぶ）"])
    assert rows[0]["合成できる？"].startswith("❌")
    assert all(r["合成できる？"].startswith("✅") for r in rows[1:])
