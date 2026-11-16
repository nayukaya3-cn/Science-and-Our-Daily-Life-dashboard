"""フィールドワーク：発芽を予測する（pages/21_hatsuga.py・hatsuga_core.py）のテスト"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import hatsuga_core as hc  # noqa: E402

PAGE = "pages/21_hatsuga.py"


def _run(monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.syspath_prepend(str(ROOT))
    return AppTest.from_file(str(ROOT / PAGE), default_timeout=60).run()


def test_self_check():
    hc._self_check()


def test_colder_is_slower(monkeypatch):
    at = _run(monkeypatch)
    assert any(m.label == "芽が出るまで" and m.value == "11 日" for m in at.metric)
    at.slider(key="hg_temp").set_value(5.0).run()
    assert any(m.label == "芽が出るまで" and m.value == "22 日" for m in at.metric)
    at.slider(key="hg_temp").set_value(0.0).run()
    assert any(m.label == "芽が出るまで" and m.value == "届かない" for m in at.metric)


def test_seen_is_not_emerged(monkeypatch):
    """『15日目に見た』を『15日で発芽した』と言わせない。前に見た日があれば幅がせばまる"""
    at = _run(monkeypatch)
    assert any(m.label == "言えること" and m.value == "1〜15 日目のどこか" for m in at.metric)
    assert any("ではない" in w.value for w in at.warning)
    opts = at.radio(key="hg_check").options
    at.radio(key="hg_check").set_value(next(o for o in opts if "14日目" in o)).run()
    assert any(m.label == "言えること" and m.value == "15〜15 日目のどこか" for m in at.metric)


def test_real_record_is_labelled(monkeypatch):
    """実際の記録と、架空データ・参考値の区別を画面に書いている"""
    at = _run(monkeypatch)
    text = " ".join(c.value for c in at.caption)
    assert "架空データ" in text and "参考値" in text
