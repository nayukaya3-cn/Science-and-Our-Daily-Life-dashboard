# 体をつくるタンパク質 ― 「科学と人間生活」×情報Ⅰ インタラクティブ教材

**▶ 公開ダッシュボード：`https://<あなたのアプリ名>.streamlit.app/`**（デプロイ後にここを書きかえる）

![ホーム画面](docs/img/screenshot_top.png)

高校「科学と人間生活」第1部 生命の科学 1章A「タンパク質と遺伝子」① **体をつくるタンパク質**（教科書 p.14〜15）を、
Python と Streamlit で動かして確かめる教材です。

> ❓ **動物の肉を食べても、その動物にならないのはなぜだろうか。**

この問いに、**「① 計算する → ② 見える化する → ③ 自分で判断する」** の3段で答えます。
文系の生徒でも読めるよう、左メニューの「やさしい解説」スイッチで説明を出し入れできます。

## ページ構成

| まとまり | ページ | 教科書 | やってみること | 情報Ⅰとのつながり |
|---|---|---|---|---|
| 🧬 はじめに | 🏠 ホーム | 導入の問い | 答えの見通しを立てる | ─ |
| 📗 教科書を動かす | 🧪 体は何でできている？ | 図1 細胞の成分 | 「水を除く」スイッチ | データの可視化・割合 |
| | 🔤 アミノ酸は20種類 | アミノ酸20種 | 必須アミノ酸を絞り込む | 文字コード |
| | 🍖 消化→吸収→合成 | 図4 タンパク質の分解 | 食べ物を変えて比べる（対照実験） | 文字列の分解・辞書で集計 |
| | 🧬 遺伝子→タンパク質 | 図3・合成 | 塩基を1文字書きかえる（突然変異） | 対応表による変換 |
| 📝 教科×情報Ⅰ | 💻 情報Ⅰとつなげる | ─ | 並べ方の数 20ⁿ とビット数 | 場合の数・情報量・DNCL |
| | ✅ 確認クイズ | ─ | 5問（4・20・64・10万のひっかけ） | ─ |

![消化→吸収→合成](docs/img/screenshot_shoka.png)

## 手元で動かす

```bash
git clone https://github.com/nayukaya3-cn/Science-and-Our-Daily-Life-dashboard.git
cd Science-and-Our-Daily-Life-dashboard
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud で公開する

1. このフォルダを GitHub に新しいリポジトリとして push する
2. <https://share.streamlit.io/> → **Create app** → リポジトリ・ブランチ `main`・Main file path に **`app.py`** を指定
3. App URL（例：`tanpakushitsu.streamlit.app`）を決めて **Deploy**
4. README 冒頭の URL を書きかえる

秘密情報（APIキーなど）は使っていないので、Secrets の設定は不要です。

## ファイル構成

```
app.py              入口（左メニューの組み立て。ページを足すときは NAV に1行足す）
home.py             ホーム
pages/              各ページ（1_seibun.py 〜 6_quiz.py）
tanpaku_core.py     計算部品とデータ（Streamlit に依存しない。`python tanpaku_core.py` で自己チェック）
ui.py               画面の共通部品（見出しカード・やさしい解説・アミノ酸の鎖の表示）
tests/              pytest（計算のテスト＋全ページの描画テスト）
.streamlit/         公開用のセキュリティ設定
.github/            CI（テスト）・脆弱性スキャン・Dependabot
```

## データについて（必ずお読みください）

| データ | 種類 |
|---|---|
| 細胞の成分：水67％・タンパク質15％ | 教科書の値 |
| 細胞の成分：脂質・無機塩類など | 教科書の図から読み取った**目安** |
| ヒトのインスリンA鎖・B鎖、ヘモグロビンβ鎖（先頭30個） | 実在の配列 |
| コラーゲン | 「G-P-○」のくり返しを示す**説明用の断片** |
| 牛肉・魚・大豆・卵・ゼラチンのタンパク質 | **説明用の架空データ**（ゼラチンがトリプトファンを含まない点は実際の性質） |
| 遺伝子（DNA） | 各アミノ酸の代表コドンで組み立てた**説明用**のもの。実際の遺伝子とは塩基配列が異なる |

教科書の紙面画像・スキャンはリポジトリに入れないでください（著作物のため。`.gitignore` で `*.pdf` と `textbook/` を除外済み）。

## テスト

```bash
pip install pytest
python tanpaku_core.py   # 自己チェック
pytest -q                # 計算＋全ページの描画
```

GitHub に push すると `.github/workflows/ci.yml` が同じテストを自動で実行します。

## プライバシー

入力（スイッチ・選択・クイズの回答）は閲覧中のセッションの中だけで使い、保存も送信もしません。詳しくは [SECURITY.md](SECURITY.md)。
