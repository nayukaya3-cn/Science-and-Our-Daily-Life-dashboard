"""フィールドワーク実践：IoT（pages/20_iot.py・iot_core.py）のテスト"""
import math
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import iot_core as ic  # noqa: E402
import next_move as nm  # noqa: E402

PAGE = "pages/20_iot.py"


def _run(monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.syspath_prepend(str(ROOT))
    return AppTest.from_file(str(ROOT / PAGE), default_timeout=90).run()


def test_self_check():
    ic._self_check()


def test_values_match_the_sources():
    """資料に書かれていた時間・レクチャー数・材料費の目安、公的な基準値と一致するか"""
    got = {m["id"]: (m["hours"], m["lectures"]) for m in ic.MATERIALS}
    assert got == {"kanki": (2.0, 45), "garden": (2.5, 35), "kit": (6.0, 48), "mlops": (2.5, 23), "bio": (1.0, 25),
                   "sour": (5.0, 105), "web": (10.0, 121), "marche": (3.5, 22), "fukushi": (0.0, 0),
                   "cad": (0.0, 0)}
    assert ic.BUDGET_RANGE == (20000, 30000)
    assert ic.LIMITS == {"建築物衛生法（事務所など）": 1000, "学校環境衛生基準（教室）": 1500}
    assert ic.VENT_PER_PERSON == 30
    assert (ic.HOUSE["width"], ic.HOUSE["length"]) == (5.5, 15.0)


def test_no_names_of_courses_or_people():
    """講座名・講師名・事業所名・URL を教材に持ちこんでいない"""
    text = (ROOT / "iot_core.py").read_text(encoding="utf-8") + (ROOT / PAGE).read_text(encoding="utf-8")
    for word in ("udemy", "Udemy", "http://", "大手町", "株式会社"):
        assert word not in text, word
    # URLは自分たちのリポジトリ（独立版ダッシュボード）だけ
    import re
    assert set(re.findall(r"https://[^\s\"')]+", text)) <= {"https://github.com/nayukaya3-cn/IoT-Fieldwork-dashboard"}


def test_ventilation_model_is_consistent():
    # 換気量を2倍にすると、外気からの上乗せ分は半分になる
    a, b = ic.steady_ppm(40, 600), ic.steady_ppm(40, 1200)
    assert math.isclose(a - ic.OUTDOOR_PPM, 2 * (b - ic.OUTDOOR_PPM))
    # 落ち着く濃度が基準より低ければ、いつまでたっても届かない
    assert math.isinf(ic.minutes_to_reach(1500, 40, 180, ic.required_vent(40, 1400)))
    assert ic.minutes_to_reach(1500, 40, 180, 0, start=1600) == 0


def test_secret_check_never_needs_file_contents():
    """名前だけで判定する（中身を受け取る引数がない）"""
    assert ic.risky_files(["  path/to/Service_Account.JSON  ", ""]) == [("Service_Account.JSON", "鍵・トークンによく使われる名前")]
    assert ic.gitignore_lines(["a.py", ".env", "key.pem", ".env"]) == [".env", "key.pem"]


def test_nav_ci_and_tag():
    src = (ROOT / "app.py").read_text(encoding="utf-8")
    sec, nxt = src.index('"🌾 フィールドワークへ"'), src.index('"🧭 終章 課題研究"')
    assert sec < src.index(PAGE) < nxt
    assert "python iot_core.py" in (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert nm.PAGE_TAG["iot"] in nm.BY_ID


def test_page_renders_and_plan_gap(monkeypatch):
    at = _run(monkeypatch)
    assert not at.exception, at.exception
    # 最初（IoT講座3本）は『運用する・届ける』が抜けている
    assert any(m.label == "抜けている段" and "運用する" in str(m.value) for m in at.metric)
    at.multiselect(key="iot_pick").set_value([m["name"] for m in ic.MATERIALS]).run()
    assert not at.exception
    assert any(m.label == "抜けている段" and m.value == "なし" for m in at.metric)


def test_closed_room_and_outlier(monkeypatch):
    at = _run(monkeypatch)
    at.slider(key="iot_vent").set_value(0).run()
    assert not at.exception
    assert any(m.label == "落ち着く濃度" and m.value == "上がり続ける" for m in at.metric)
    assert any(m.label == "1500 ppm まで" and m.value == "15 分" for m in at.metric)
    at.toggle(key="iot_outlier").set_value(True).run()
    assert not at.exception
    assert any("平均は" in e.value for e in at.error)


def test_security_gate_and_file_names(monkeypatch):
    at = _run(monkeypatch)
    assert any("service_account.json" in c.value for c in at.code)          # 既定の例で .gitignore の行が出る
    at.checkbox(key="iot_sec_2").set_value(True).run()
    assert any("公開しない" in e.value for e in at.error)                    # 上の2つが済むまでは公開しない
    for i in range(len(ic.SECURITY_CHECKS)):
        at.checkbox(key=f"iot_sec_{i}").set_value(True)
    at.run()
    assert not at.exception
    assert any("すべて確認できた" in s.value for s in at.success)


def test_fit_and_license(monkeypatch):
    """図面どおりだと入らない／NC のデータは売る品物に使えない"""
    at = _run(monkeypatch)
    assert any("入らない" in e.value for e in at.error)
    at.number_input(key="iot_hole").set_value(10.4).run()
    assert any("ちょうど" in x.value for x in at.success)
    at.toggle(key="iot_cc_sell").set_value(True).run()
    assert not at.exception
    assert any("できない" in e.value and "NC" in e.value for e in at.error)
