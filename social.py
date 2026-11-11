"""
SNSリンク（Instagram・Facebook・LinkedIn）— 全ページ共通のボタン

URLを変えるときは、ここだけ書きかえれば全ページに反映されます（姉妹サイトの social.py と同じ形）。
  - URL が空文字 "" のSNSは、ボタンを表示しません。
    → Instagram はアカウントを作ったら INSTAGRAM_URL に
       "https://www.instagram.com/ユーザーネーム/" の形で書き込むだけで、ボタンが現れます。
  - LINKEDIN_URL は、閲覧者が開くと「あなたの」プロフィールが出る URL にしてください。
    https://www.linkedin.com/feed/ は「開いた人自身」のフィードになるため、活動内容は見えません。
  - 生徒や先生の個人アカウントは載せない（教材の発信用アカウントだけを載せる）。

Streamlit に依存しない部分（URLの点検）は、buttons() の外に置いてテストできるようにしています。
"""
from __future__ import annotations

import re

INSTAGRAM_URL = ""  # 例："https://www.instagram.com/your_account/"（作成後に書き込む）
FACEBOOK_URL = "https://www.facebook.com/profile.php?id=100079624235158"
LINKEDIN_URL = "https://www.linkedin.com/in/%E9%9A%86%E8%A6%8F-%E6%A5%A0%E9%A6%99%E8%B0%B7-392aa12a0/"

# (アイコン, サービス名, URL, 正しいURLの形)
_ALL = [
    ("📸", "Instagram", INSTAGRAM_URL, r"https://www\.instagram\.com/[A-Za-z0-9._]{1,30}/?"),
    ("📘", "Facebook", FACEBOOK_URL, r"https://www\.facebook\.com/\S+"),
    ("💼", "LinkedIn", LINKEDIN_URL, r"https://www\.linkedin\.com/in/\S+"),
]

# 表示するSNS（URLが入っているものだけ）：(アイコン, サービス名, URL)
SOCIALS = [(icon, name, url) for icon, name, url, _ in _ALL if url]
NAMES = "・".join(name for _, name, _ in SOCIALS)  # 文中で使う「Instagram・Facebook・LinkedIn」


def bad_urls() -> list[str]:
    """形がおかしいURL（例：instagram.com/accounts/… や フィードのURL）を返す。空なら合格"""
    return [f"{name}: {url}" for _, name, url, pattern in _ALL if url and not re.fullmatch(pattern, url)]


def buttons(action: str = "で活動内容を見る", stacked: bool = False) -> None:
    """SNSのボタンを並べて表示する（Streamlit 専用）。

    action  : ボタン文言のサービス名の後ろ（例："で活動内容を見る" → 「Instagramで活動内容を見る」）
    stacked : True で縦に積む（サイドバーなど幅の狭い場所用）
    """
    import streamlit as st

    if not SOCIALS:
        return
    if stacked:
        for icon, name, url in SOCIALS:
            st.link_button(f"{icon} {name}{action}", url, width="stretch")
        return
    for col, (icon, name, url) in zip(st.columns(len(SOCIALS)), SOCIALS):
        with col:
            st.link_button(f"{icon} {name}{action}", url, width="stretch")


if __name__ == "__main__":
    assert bad_urls() == [], bad_urls()
    print("social: OK", NAMES)
