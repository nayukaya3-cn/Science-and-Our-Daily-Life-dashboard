# セキュリティについて

## このアプリが守っていること

| 層 | 対策 | 置き場所 |
|---|---|---|
| 教員ページ | **合言葉で保護**。未設定・8文字未満なら誰にも開かない（安全側）。比較は時間差で漏れない方法（`hmac.compare_digest`）、1セッション5回まちがえるとロック | `ui.teacher_gate()`・`guard.py` |
| 入力 | 入力欄に文字数の上限。ダウンロードするテキストから制御文字を除去 | `guard.clean_text()` |
| CSV | `=`・`+`・`-`・`@` で始まるセルの先頭に `'` を付け、表計算ソフトで数式として実行されないようにする（CSVインジェクション対策） | `guard.csv_safe()`（FW予想シート） |
| 画面 | HTML を出す箇所はすべて `html.escape` を通し、入力値を直接埋め込まない（テストで確認） | `ui.py`・`tests/test_security.py` |
| サーバー設定 | XSRF・CORS を明示的に有効、static 公開なし、アップロード上限1MB、エラー詳細を表示しない、開発者メニューを隠す | `.streamlit/config.toml` |
| 著作物・秘密 | 教科書の写真（jpg/heic/IMG_*）・PDF・ZIP・`.env`・`secrets.toml` をリポジトリに入れない（.gitignore とテスト） | `.gitignore`・`tests/test_security.py` |
| CI | GitHub Actions はコミットSHAで固定、トークンは読み取りのみ・checkout で資格情報を残さない。pip-audit・bandit・CodeQL を実行 | `.github/workflows/` |
| ブランチ | `main` はルールセットで保護：削除・強制pushの禁止、PR必須、`test`・`scan` の成功が必須 | GitHub の Settings → Rules |

## 合言葉の設定

Streamlit Community Cloud の **Settings → Secrets** に `teacher_passcode = "8文字以上"` を書きます。
手元では環境変数 `TEACHER_PASSCODE` でも構いません。合言葉は**コードやREADMEに書かない**でください。
共有した相手が異動・卒業したら合言葉を変えます。

## 守っていないこと（限界）

- 生徒向けページは公開アプリなので、URLを知っていればだれでも見られます（個人情報は扱いません）。
- 合言葉はセッション単位の簡易な鍵です。成績や個人情報を扱う版を作るときは、Streamlit の認証（OIDC）や学校の認証基盤を使ってください。
- 入力（スイッチ・選択・クイズの回答・予想・教員ページの評価）は閲覧中のセッションの中だけで使い、保存も送信もしません。
  生徒の学習ログを収集する版を作る場合は、**実施前に保護者同意と研究倫理審査**を得てください（事後の同意取得はできません）。

## 脆弱性の報告

公開の Issue ではなく、リポジトリの「Security → Report a vulnerability」（非公開の脆弱性報告）から連絡してください。
