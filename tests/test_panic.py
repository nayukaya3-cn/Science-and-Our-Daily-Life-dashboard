"""終章 パニックプルーフ（pages/19_panic.py・panic_core.py）のテスト"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import next_move as nm  # noqa: E402
import panic_core as pc  # noqa: E402

PAGE = "pages/19_panic.py"


def _run(monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.syspath_prepend(str(ROOT))
    return AppTest.from_file(str(ROOT / PAGE), default_timeout=60).run()


def test_self_check():
    pc._self_check()


def test_values_match_the_sources():
    """元の単元案・農林水産省の値と一致するか"""
    assert (pc.JIKYU["calorie_pct"], pc.JIKYU["domestic_kcal"], pc.JIKYU["supply_kcal"]) == (37, 830, 2237)
    assert pc.WATER_L_PER_DAY == 3 and pc.GAS_CANS_PER_WEEK == 6
    assert pc.PLAN["seed_g"] == 320 and pc.PLAN["area_m2"] == 32
    c = pc.comparative(**pc.TRADE_EXAMPLE)
    assert c["self_veg"] == 2.5 and c["div_veg"] == 3


def test_nav_entry():
    """左メニューの「🧭 終章 課題研究」の中にある"""
    src = (ROOT / "app.py").read_text(encoding="utf-8")
    sec = src.index('"🧭 終章 課題研究"')
    nxt = src.index('"🚀 次の一手"')
    assert sec < src.index(PAGE) < nxt
    assert nm.PAGE_TAG["panic"] in nm.BY_ID


def test_page_renders_and_bottleneck(monkeypatch):
    at = _run(monkeypatch)
    assert not at.exception, at.exception
    # 水を減らすと、ボトルネックが水になる
    at.number_input(key="panic_water").set_value(2.0).run()
    assert not at.exception
    assert any("💧 水" in str(m.value) or "💧 水" in str(getattr(m, "delta", "")) for m in at.metric)


def test_harvest_update(monkeypatch):
    at = _run(monkeypatch)
    at.number_input(key="panic_got").set_value(9.6).run()
    at.number_input(key="panic_flour").set_value(8.0).run()
    assert not at.exception
    assert any(m.label == "来年の収量の見込み" for m in at.metric)
