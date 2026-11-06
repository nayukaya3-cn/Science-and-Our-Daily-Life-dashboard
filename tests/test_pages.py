"""全ページが例外なく描画できるかのスモークテスト（Streamlit の AppTest を使用）"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["home.py", *sorted(str(p.relative_to(ROOT)) for p in (ROOT / "pages").glob("*.py"))]


@pytest.mark.parametrize("page", PAGES)
def test_page_renders(page, monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.syspath_prepend(str(ROOT))
    at = AppTest.from_file(str(ROOT / page), default_timeout=60).run()
    assert not at.exception, at.exception


def test_app_entry(monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.syspath_prepend(str(ROOT))
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not at.exception, at.exception


def test_gelatin_shows_shortage(monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.syspath_prepend(str(ROOT))
    at = AppTest.from_file(str(ROOT / "pages/3_shoka.py"), default_timeout=60).run()
    at.multiselect[0].set_value(["🍮 ゼラチン（トリプトファンを含まない）"]).run()
    at.selectbox[0].set_value("ヘモグロビンβ鎖・先頭30個（酸素を運ぶ）").run()
    assert any("トリプトファン" in e.value for e in at.error)
