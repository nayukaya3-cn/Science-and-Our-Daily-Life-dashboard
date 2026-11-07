"""保護（プロテクト）のテスト：教員ページの鍵・CSVインジェクション・リポジトリの衛生・CIの固定"""
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import guard  # noqa: E402

SECRET = "test-passcode-123"


def _kyoin(monkeypatch, secret=None):
    monkeypatch.chdir(ROOT)
    monkeypatch.syspath_prepend(str(ROOT))
    monkeypatch.delenv("TEACHER_PASSCODE", raising=False)
    at = AppTest.from_file(str(ROOT / "pages/8_kyoin.py"), default_timeout=60)
    if secret is not None:
        at.secrets["teacher_passcode"] = secret
    return at.run()


def _body(at) -> str:
    return " ".join(str(getattr(e, "value", "")) for e in at.markdown) + " ".join(t.label for t in at.tabs)


def test_guard_self_check():
    guard._self_check()


def test_teacher_page_closed_without_secret(monkeypatch):
    at = _kyoin(monkeypatch)
    assert not at.exception
    assert len(at.tabs) == 0 and any("閉じています" in w.value for w in at.warning)


def test_teacher_page_closed_with_short_secret(monkeypatch):
    at = _kyoin(monkeypatch, "short")
    assert len(at.tabs) == 0 and len(at.text_input) == 0


def test_teacher_page_wrong_then_locked(monkeypatch):
    at = _kyoin(monkeypatch, SECRET)
    for _ in range(guard.MAX_ATTEMPTS):
        at.text_input[0].input("wrong-passcode")
        at.button[0].click().run()
        assert len(at.tabs) == 0
    assert len(at.text_input) == 0 and any("開けません" in e.value for e in at.error)


def test_teacher_page_opens_with_secret(monkeypatch):
    at = _kyoin(monkeypatch, SECRET)
    at.text_input[0].input(SECRET)
    at.button[0].click().run()
    assert not at.exception and len(at.tabs) == 5


def test_csv_injection_is_neutralized():
    df = pd.DataFrame({"場面": ["=HYPERLINK(\"http://evil\")", "ハウス内の気温"], "予想": [1.0, 2.0]})
    out = guard.csv_safe(df).to_csv(index=False)
    assert "'=HYPERLINK" in out and ",=" not in out and "\n=" not in out


def _tracked() -> list[str]:
    try:
        r = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)  # nosec B603 B607
        return r.stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]


def test_no_textbook_photos_or_secrets_in_repo():
    bad = re.compile(r"(\.(pdf|jpe?g|heic|zip)$|(^|/)IMG_\d+|(^|/)textbook/|__MACOSX|secrets\.toml$|(^|/)\.env$)", re.I)
    hits = [f for f in _tracked() if bad.search(f)]
    assert hits == [], hits
    images = [f for f in _tracked() if f.lower().endswith(".png")]
    assert all(f.startswith("docs/img/") for f in images), images   # 画像はアプリの画面写真だけ


def test_streamlit_config_is_hardened():
    cfg = tomllib.loads((ROOT / ".streamlit/config.toml").read_text(encoding="utf-8"))
    assert cfg["server"]["enableXsrfProtection"] is True
    assert cfg["server"]["enableCORS"] is True
    assert cfg["server"]["enableStaticServing"] is False
    assert cfg["client"]["showErrorDetails"] == "none"
    assert cfg["client"]["toolbarMode"] == "viewer"
    assert cfg["browser"]["gatherUsageStats"] is False


def test_workflow_actions_are_pinned_and_least_privilege():
    for wf in (ROOT / ".github/workflows").glob("*.yml"):
        text = wf.read_text(encoding="utf-8")
        for ref in re.findall(r"uses:\s*([^\s#]+)", text):
            assert re.search(r"@[0-9a-f]{40}$", ref), f"{wf.name}: {ref} はコミットSHAで固定する"
        assert re.search(r"^permissions:", text, re.M), wf.name
        if "actions/checkout" in text:
            assert "persist-credentials: false" in text, wf.name


def test_unsafe_html_never_takes_raw_user_input():
    """unsafe_allow_html の行で、入力欄の値（session_state 由来）をエスケープせずに埋め込んでいない"""
    for f in [ROOT / "home.py", ROOT / "ui.py", *(ROOT / "pages").glob("*.py")]:
        for ln in f.read_text(encoding="utf-8").splitlines():
            if "unsafe_allow_html" in ln:
                assert "session_state" not in ln, f"{f.name}: {ln.strip()}"
