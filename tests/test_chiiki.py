"""地域の教材（熱・プラスチック・衣料と水・広島空港）・終章（進路探究）・特別支援学校版のテスト"""
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import kuko_core as kc  # noqa: E402
import netsu_core as nc  # noqa: E402
import next_move as nm  # noqa: E402
import shinro_core as sh  # noqa: E402
import sozai_core as sc  # noqa: E402
import tokushi_core as tk  # noqa: E402

NEW_PAGES = {"netsu": "pages/12_netsu.py", "plastic": "pages/13_plastic.py", "iryo": "pages/14_iryo.py",
             "kuko": "pages/15_kuko.py", "shinro": "pages/16_shinro.py", "tokushi": "pages/17_tokushi.py"}


def _run(page, monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.syspath_prepend(str(ROOT))
    return AppTest.from_file(str(ROOT / page), default_timeout=60).run()


@pytest.mark.parametrize("mod", [nc, sc, kc, sh, tk])
def test_self_checks(mod):
    mod._self_check()


def test_values_match_the_unit_plans():
    """単元案に書かれた数字と一致するか"""
    assert round(nc.equilibrium(100, 0.80, 100, 100, 4.2, 20), 1) == 32.8           # 例題：約33℃
    assert kc.AIRPORT_ELEVATION_M == 331 and (kc.FLIGHTS_TOTAL, kc.CANCELLED, kc.CANCELLED_BY_DEVICE) == (3255, 59, 14)
    assert kc.flight_breakdown()["装置が原因と言える欠航の割合（％）"] == 0.43           # 約0.4％
    assert sc.first_soften("PLA") == 60 and sc.first_soften("PETG") == 80
    assert len(sh.THEMES) == 17 and len(sh.FIELDS_18) == 18 and len(sh.ROLES) == 6
    assert len(tk.PLAN) == 8 and len(tk.CARDS) == 4 and len(tk.LEVELS) == 5


def test_control_experiments_change_one_thing():
    """対照実験は違いが1つだけ：煮沸（微生物）と空気を同時に変えた比較からは原因を言わない"""
    assert sc.differs_only_in("A", "C") == ["微生物がいるか"]
    assert "言えない" in sc.water_claim("B", "C")


def test_new_pages_are_in_menu_and_have_tags():
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    for key, path in NEW_PAGES.items():
        assert (ROOT / path).exists() and path in app
        if key != "tokushi":                      # 特別支援学校版は先生向けのページなので「次の一手」タグなし
            assert nm.PAGE_TAG[key] in nm.BY_ID


def test_netsu_prediction_is_logged(monkeypatch):
    at = _run(NEW_PAGES["netsu"], monkeypatch)
    assert not at.exception
    at.number_input[0].set_value(60.0).run()
    at.button[0].click().run()
    assert not at.exception
    rec = at.session_state["td_log"]["netsu_stone"]
    assert round(rec["observed"], 1) == 32.8 and rec["field"] == "熱の性質とその利用"


def test_exam_question_feedback(monkeypatch):
    at = _run(NEW_PAGES["netsu"], monkeypatch)
    at.radio(key="exam_netsu_1").set_value("60℃").run()
    assert any("32.8" in e.value for e in at.error)
    at.radio(key="exam_netsu_1").set_value("33℃").run()
    assert any("正解" in s.value for s in at.success)


def test_brix_rises_without_sugar(monkeypatch):
    at = _run(NEW_PAGES["netsu"], monkeypatch)
    assert any("糖は1 g も増えていない" in e.value for e in at.error)   # 既定：水分15％減・糖の増加0


def test_plastic_part_choice(monkeypatch):
    at = _run(NEW_PAGES["plastic"], monkeypatch)
    assert not at.exception
    at.selectbox(key="plastic_part").set_value("温湿度計の日差しカバー").run()
    at.selectbox(key="plastic_mat").set_value("PLA").run()
    assert any("60℃前後" in w.value for w in at.warning)
    at.selectbox(key="plastic_mat").set_value("PETG").run()
    assert any("候補に入っている" in s.value for s in at.success)


def test_iryo_two_differences_is_an_error(monkeypatch):
    at = _run(NEW_PAGES["iryo"], monkeypatch)
    assert any("微生物の働き" in s.value for s in at.success)            # 既定：A と C
    at.selectbox(key="iryo_a").set_value("B").run()
    assert any("分けられない" in e.value for e in at.error)              # B と C は違いが2つ


def test_kuko_fog_when_cooled_below_dew_point(monkeypatch):
    at = _run(NEW_PAGES["kuko"], monkeypatch)
    assert not at.exception
    assert any("霧" in e.value for e in at.error)                        # 既定：18℃・70％ → 10℃ まで冷える
    at.slider(key="kuko_night").set_value(18).run()
    assert any("霧は出にくい" in s.value for s in at.success)


def test_shinro_filter_and_download(monkeypatch):
    at = _run(NEW_PAGES["shinro"], monkeypatch)
    assert not at.exception and len(at.get("download_button")) == 1
    at.toggle(key="shinro_fw").set_value(True).run()
    assert not at.exception
    assert at.selectbox(key="shinro_no").options == [f"No.{n} {sh.THEMES[n - 1]['q']}" for n in sh.FW_DIRECT]


def test_tokushi_page_asks_for_no_personal_data(monkeypatch):
    at = _run(NEW_PAGES["tokushi"], monkeypatch)
    assert not at.exception and len(at.get("download_button")) == 1
    labels = " ".join(w.label for w in at.text_input)
    assert "名前" not in labels and "氏名" not in labels
    at.radio(key="tokushi_guess").set_value("🟦 冷蔵庫").run()
    assert any("なぜだろう" in w.value for w in at.warning)
