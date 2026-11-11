"""SNSボタンのテスト：URLの形が正しいか・空のSNSはボタンに出ないか"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import social  # noqa: E402


def test_urls_well_formed():
    assert social.bad_urls() == []


def test_empty_url_hidden():
    shown = {name for _, name, _ in social.SOCIALS}
    for _, name, url, _ in social._ALL:
        assert (name in shown) == bool(url), name


def test_instagram_pattern():
    pattern = next(p for _, n, _, p in social._ALL if n == "Instagram")
    import re
    assert re.fullmatch(pattern, "https://www.instagram.com/smart_bakery.farm/")
    assert not re.fullmatch(pattern, "https://www.instagram.com/accounts/edit/x/")
