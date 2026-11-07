"""2章B 微生物（bisei_core）と終章 課題研究（kadai_core）のテスト"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import bisei_core as bc  # noqa: E402
import kadai_core as kc  # noqa: E402
import next_move as nm  # noqa: E402


def _run(page, monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.syspath_prepend(str(ROOT))
    return AppTest.from_file(str(ROOT / page), default_timeout=60).run()


def test_self_checks():
    bc._self_check()
    kc._self_check()


def test_textbook_values():
    assert bc.EXP2[20][-1] == 3.8 and bc.EXP2[30][-1] == 10.9 and set(bc.EXP2[80]) == {0}
    assert bc.FERMENTED["パン"] == {"酵母"} and bc.FERMENTED["ヨーグルト"] == {"細菌"}
    assert bc.micrometer_unit(14, 20) == 7.0


def test_pasteur_only_one_variable_changes():
    """S字→首を折る は『微生物が届くか』だけを変える対照実験"""
    a, b = bc.pasteur("S字（白鳥の首）", True), bc.pasteur("首を折る", True)
    assert a["空気は入る？"] == b["空気は入る？"] and a["腐敗する？"] != b["腐敗する？"]


def test_new_pages_have_tags():
    assert nm.PAGE_TAG["biseibutsu"] in nm.BY_ID and nm.PAGE_TAG["kadai"] in nm.BY_ID


def test_bisei_page_prediction_and_rate(monkeypatch):
    at = _run("pages/10_biseibutsu.py", monkeypatch)
    assert not at.exception
    at.number_input[0].set_value(8.0).run()
    at.button[0].click().run()
    assert not at.exception
    rec = at.session_state["td_log"]["bisei_exp2"]
    assert rec["observed"] == 10.9 and rec["field"] == "微生物とその利用"


def test_bisei_page_pasteur_switch(monkeypatch):
    at = _run("pages/10_biseibutsu.py", monkeypatch)
    at.radio(key="pasteur_neck").set_value("首を折る").run()
    assert any("外から微生物が入る" in e.value for e in at.error)


def test_kadai_page_report_download(monkeypatch):
    at = _run("pages/11_kadai.py", monkeypatch)
    assert not at.exception
    at.text_area(key="rp_refs").input("「気象庁」https://www.jma.go.jp/").run()
    assert any("調べた日" in w.value for w in at.warning)
    assert len(at.get("download_button")) == 1
