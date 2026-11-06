"""背骨（読解カード・P1〜P5・仮説Hの判定）と、それを使うページのテスト"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import backbone as bb  # noqa: E402
import tanpaku_core as tc  # noqa: E402

STUDENT_PAGES = ["1_seibun", "2_amino", "3_shoka", "4_idenshi", "5_joho1", "7_field"]


def _run(page, monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.syspath_prepend(str(ROOT))
    return AppTest.from_file(str(ROOT / page), default_timeout=60).run()


def test_self_check():
    bb._self_check()


def test_td_error_matches_document_example():
    d = {e["id"]: round(bb.td_error(e["predicted"], e["observed"]), 2) for e in bb.FW_EPISODES}
    assert d == {"wheat_rows": 0.29, "house_temp": 0.36, "well_ph": 0.03, "dough_co2": 0.04}


def test_judge_rules():
    assert bb.judge({"①": True, "②": True, "③": None})[0] == "維持"
    assert bb.judge({"①": True, "②": False, "③": False})[0] == "縮小"
    assert bb.judge({"①": False, "②": False, "③": False})[0] == "棄却"
    assert bb.judge({"①": None, "②": True, "③": True})[0] == "保留"


def test_every_student_page_uses_same_reading_card():
    """方策を途中で取り替えない：どの生徒ページにも同じ読解カードがある"""
    for name in STUDENT_PAGES:
        src = (ROOT / "pages" / f"{name}.py").read_text(encoding="utf-8")
        assert "ui.reading_card(" in src, name


def test_quiz_covers_all_protocols():
    assert {q["p"] for q in tc.QUIZ} == set(bb.PROTOCOLS)
    assert sum(q["p"] == "P3" for q in tc.QUIZ) >= 2


def test_mutation_spectrum_has_all_kinds():
    spec = tc.mutation_spectrum(tc.HUMAN_PROTEINS["インスリンB鎖（血糖濃度を調節するホルモン）"])
    assert all(spec[k] > 0 for k in ("同義", "置換", "短縮"))


def test_prediction_records_td_error(monkeypatch):
    at = _run("pages/5_joho1.py", monkeypatch)
    at.number_input[0].set_value(10).run()
    at.button[0].click().run()
    assert not at.exception
    log = at.session_state["td_log"]
    assert log["joho1_n"]["observed"] == 4 and log["joho1_n"]["td_error"] == 0.6


def test_teacher_page_judgement(monkeypatch):
    at = _run("pages/8_kyoin.py", monkeypatch)
    assert not at.exception
    at.radio(key="pred_res_①").set_value("支持").run()
    at.radio(key="pred_res_②").set_value("支持").run()
    assert any("判定：維持" in s.value for s in at.success)
