"""
背骨（3フェーズ共通の思考の型）と、暫定的な設計仮説H ─ 計算部品とデータ

出どころ：「暫定的な設計仮説：深層強化学習としての背骨（教員向け・検証中）」
  - 生徒に教える内容ではない。DAG・バックドア基準と同じく**教員側の設計原理**。
  - しかも確定した前提ではなく、**検証中の暫定仮説**。判定基準で維持・縮小・棄却を決める。

このダッシュボードでの使い方
  - 生徒ページ：どのページも同じ「読解カード（4項目）」と「P1〜P5」で締める（方策を1つにする）。
    測る前に予想させ、ずれ δ を見せる（TD誤差が出る場面を意図的に作る）。
  - 教員ページ（pages/8_kyoin.py）：対応表・経験再生・Actor–Critic の差・判定を扱う。

Streamlit に依存しない純粋な関数だけを置く。`python backbone.py` で自己チェック。
"""
from __future__ import annotations

from datetime import datetime

# ─────────────────────────────────────────────
# 背骨① 読解プロトコル（4項目カード）＝共有エンコーダ
# ─────────────────────────────────────────────
READING_CARD = (
    ("軸", "何と何を比べている？（軸は何と何か）"),
    ("単位", "単位は何か"),
    ("統制", "何をそろえ（統制）、何を変えたか"),
    ("言える／言えない", "この比較で言えること／言えないことは何か"),
)

# ─────────────────────────────────────────────
# 背骨② 認知プロトコル P1〜P5 ＝行動の選択肢
# ─────────────────────────────────────────────
PROTOCOLS = {
    "P1": ("手順を回す", "決まった順番どおりに処理する"),
    "P2": ("資料を読む", "グラフや表から事実を取り出す"),
    "P3": ("比較を疑う", "「その比べ方、フェア？」と問う"),
    "P4": ("模型で考える", "単純化した絵や式で説明する"),
    "P5": ("知識で答える", "覚えていることを使う"),
}


def p_label(code: str) -> str:
    """'P3' → 'P3 比較を疑う'"""
    return f"{code} {PROTOCOLS[code][0]}"


# ─────────────────────────────────────────────
# 対応表（ロードマップの要素 ↔ DRLの構成要素 ↔ このダッシュボードでの実装）
# ─────────────────────────────────────────────
#   (DRLの構成要素, ロードマップでの実体, 設計上の意味, このダッシュボードでの実装, 得点への寄与が大きい上位3行か)
DRL_TABLE: list[tuple[str, str, str, str, bool]] = [
    ("状態 s", "目の前の資料・場面（野帳、文献、共通テストの図表）",
     "環境は変わっても、入力の形式はそろえる",
     "各ページの図・表（円グラフ、プール、暗号表、20ⁿ のグラフ）", True),
    ("共有エンコーダ（深層部分）", "読解プロトコル4項目カード",
     "どんな資料も「軸・単位・統制・言える／言えない」の4項目で読む",
     "全ページ末尾の「🔎 読解カード」（同じ4項目・同じ見た目）", True),
    ("行動 a", "P1〜P5のどれを使うか", "行動の選択肢を5つに絞ることで、学習を速くする",
     "読解カードとクイズに P1〜P5 のラベル", True),
    ("方策 π", "思考の型（全フェーズで共通）",
     "方策を1つにする＝背骨。フェーズごとに別の型を教えると、転移が起きにくくなる",
     "教室（このサイト）と現場（姉妹サイト）で同じカード・同じ単元名", False),
    ("価値予測 V(s)", "仮説シート項目5「予想グラフ」", "測る前に「こうなるはず」を数値で書かせる",
     "「🎯 先に予想しよう」（図1・遺伝子・情報Ⅰの3ページ）", False),
    ("TD誤差 δ", "予想グラフと実測のずれ／誤差ログ", "学習が起きるのはここ。鳥害・倒伏も消さずに記録する",
     "予想と答えのずれ δ を表示し、このセッションの誤差ログに残す", False),
    ("探索", "❷FW本番", "試験演習では出会えない状態を経験させる",
     "🌾 畑とパン工房につなげる → 姉妹サイト", False),
    ("活用", "❸-① 共通テスト演習", "すでにある方策で得点を取りにいく", "✅ 確認クイズ（P分類つき）", False),
    ("経験再生バッファ", "野帳・誤差ログ・写真", "3年生の12月までのデータを受験期に引き出して使う",
     "教員ページの経験再生（ずれの大きい経験ほど復習に出やすい）", False),
    ("報酬の整形", "P1〜P5ルーブリック（A/B/C）",
     "年1回しか出ない共通テストの得点（まばらな報酬）を、途中の評価で補う",
     "クイズのP別スコア・教員ページのルーブリック", False),
    ("Actor–Critic", "生徒（Actor）と、教員評価・自己評価の差（Critic）",
     "評価の差が大きい観点が、個別指導の入口になる", "教員ページの「自己評価と教員評価の差」", False),
    ("オフライン強化学習", "前年度の上級生データを次の3年生の教材にする", "自分が集めていないデータからも学べる",
     "教員ページの経験再生バッファに、前年度の値を表へ打ち込んで使える（ファイルのアップロードはしない）", False),
    ("ドメインランダム化", "代替テーマ（川・地層・里山）", "環境を変えても同じ方策が通用するかを確かめる",
     "─（代替テーマ版は未実装。読解カードは題材に依存しない形にしてある）", False),
    ("汎化テスト", "転移チェック「この問題はFWのどの場面と同じ型か」", "未知の環境で方策を評価する",
     "クイズ末尾の転移チェック（1行で答える）", False),
]

# ─────────────────────────────────────────────
# 予想 → 実測 → ずれ δ（TD誤差の代わり）
# ─────────────────────────────────────────────
EPS = 0.01


def td_error(predicted: float, observed: float) -> float:
    """相対誤差 |実測-予測| / |予測| をTD誤差の代わりに使う（単位の違いを消すため）。
    予測が0のときは |実測| で割る（両方0ならずれ0）。"""
    denom = abs(predicted) or abs(observed)
    return 0.0 if denom == 0 else abs(observed - predicted) / denom


def priorities(deltas: list[float], alpha: float = 0.6, eps: float = EPS) -> list[float]:
    """優先度付き経験再生の優先度 (δ+ε)^α。alpha=0 なら全部同じ（一様抽選）"""
    return [(d + eps) ** alpha for d in deltas]


def sampling_probs(deltas: list[float], alpha: float = 0.6, eps: float = EPS) -> list[float]:
    """各経験が復習に引かれる確率（優先度を合計1に正規化）"""
    pr = priorities(deltas, alpha, eps)
    total = sum(pr)
    return [p / total for p in pr] if total else []


# 経験再生バッファの初期値（文書5節の例。FWのエピソード＝野帳＋誤差ログ）
FW_EPISODES: list[dict] = [
    {"id": "wheat_rows", "場面": "3列の生育比較（株数）", "protocol": "P3",
     "predicted": 120.0, "observed": 85.0, "unit": "本/㎡"},
    {"id": "house_temp", "場面": "ハウス内の気温", "protocol": "P2",
     "predicted": 18.0, "observed": 24.5, "unit": "℃"},
    {"id": "well_ph", "場面": "井戸水のpH", "protocol": "P5",
     "predicted": 7.0, "observed": 6.8, "unit": "-"},
    {"id": "dough_co2", "場面": "パン生地の発酵（気体の量）", "protocol": "P1",
     "predicted": 50.0, "observed": 48.0, "unit": "mL"},
]


def log_record(subject: str, field: str, level: str, judgement: str,
               protocol: str, predicted: float, observed: float, unit: str = "",
               timestamp: str | None = None) -> dict:
    """学習ログ1件。既存形式 {subject, field, level, timestamp, judgement} に protocol・td_error を足したもの"""
    assert protocol in PROTOCOLS, protocol
    return {
        "subject": subject, "field": field, "level": level,
        "timestamp": timestamp or datetime.now().isoformat(timespec="seconds"),
        "judgement": judgement, "protocol": protocol,
        "predicted": predicted, "observed": observed, "unit": unit,
        "td_error": round(td_error(predicted, observed), 4),
    }


# ─────────────────────────────────────────────
# Actor–Critic：自己評価と教員評価の差
# ─────────────────────────────────────────────
RUBRIC = {"A": 3, "B": 2, "C": 1}


def critic_gaps(self_eval: dict[str, str], teacher_eval: dict[str, str]) -> list[tuple[str, int]]:
    """P1〜P5ごとの差（自己評価−教員評価）。|差|が大きい順。正＝自己評価が甘い、負＝自信がない"""
    gaps = [(p, RUBRIC[self_eval[p]] - RUBRIC[teacher_eval[p]]) for p in PROTOCOLS
            if p in self_eval and p in teacher_eval]
    return sorted(gaps, key=lambda x: (-abs(x[1]), x[0]))


# ─────────────────────────────────────────────
# 仮説Hの検証：予測①〜④ と判定
# ─────────────────────────────────────────────
PREDICTIONS = [
    ("①", "方策が共有されていれば、FWで鍛えた観点の得点が初見問題でも上がる",
     "P1〜P5ルーブリックの変化と、模試の該当問題の正答率を観点ごとに比べる",
     "観点別の評価は上がるのに、該当問題の正答率が動かない"),
    ("②", "TD誤差が大きかった経験ほど記憶に残り、転移しやすい",
     "誤差ログの大きさと、転移チェックに答えられた率の関係を見る",
     "予想グラフを書かせた班と書かせなかった班で差が出ない"),
    ("③", "方策が1つなら、教科をまたいでも効き目が出る",
     "生物基礎で読解カードを訓練したあと、情報Ⅰ第4問の正答率を見る",
     "効果がその教科の中だけにとどまる"),
    ("④", "代替テーマに替えても同じ型が通用する", "別テーマを経験した学年と比べる",
     "テーマが変わると効果が消える"),
]
VERDICT_ACTION = {
    "維持": "設計原理として本文に入れる（「暫定」の表記を外す）",
    "縮小": "「読み方を共通にする」という部分だけを残し、経験再生やTD誤差の話は外す",
    "棄却": "DRLの枠組みはやめ、DAG（因果の矢印図）中心の説明に戻す",
    "保留": "判定に必要な結果がそろっていない。判定時期（3年生は12月の通し演習後、1・2年生は7月の収穫・発表後）まで待つ",
}


def judge(results: dict[str, bool | None]) -> tuple[str, str]:
    """予測①〜③の結果（True=支持 / False=不支持 / None=未確認）から判定する。④は参考（判定に使わない）。

    文書の基準：維持＝①〜③のうち2つ以上が支持 / 縮小＝①だけが支持 / 棄却＝①が支持されない。
    ①は他の予測の前提なので、①が不支持なら②③の結果にかかわらず「棄却」とし、注記を返す。
    """
    r1 = results.get("①")
    if r1 is None:
        return "保留", "①（土台の予測）が未確認"
    if r1 is False:
        note = "①が不支持"
        if results.get("②") and results.get("③"):
            note += "。②③は支持されたが、基準の想定外の組み合わせなので棄却扱いにし、原因を個別に検討する"
        return "棄却", note
    others = [results.get(k) for k in ("②", "③")]
    supported = 1 + sum(1 for v in others if v)
    if supported >= 2:
        return "維持", f"①〜③のうち{supported}つが支持"
    if any(v is None for v in others):
        return "保留", "①は支持。②③の結果待ち（どちらかが支持されれば維持）"
    return "縮小", "①だけが支持"


# 比喩としての限界
LIMITS = [
    ("大量の試行（数百万エピソード）", "人は数回の経験から学べる。FWは「1回の体験の濃さ」で勝負する"),
    ("報酬は外から与えられる", "「面白い」という内発的な動機が探索の原動力になる（内発的報酬に近い）"),
    ("方策は勾配法で更新される", "人の学習の仕組みは別物。あくまで設計を説明するための仮の枠組み"),
]

# 暫定ルール（仮説が維持されている間）
RULES = [
    ("方策を途中で取り替えない", "どの教科の資料でも、まず読解カードから入る。教科ごとに別の「解き方テクニック」を足さない。"),
    ("TD誤差が出る場面を意図的に作る", "❶3コマ目の項目5「予想グラフ」は省略不可（予測②の検証にも使う）。"),
    ("報酬ハッキングを防ぐ", "得点だけを報酬にすると丸暗記という近道を覚える（グッドハートの法則）。"
     "P3・P4は正解したかではなく「なぜ言えないか」の説明で評価する。"),
]


def _self_check() -> None:
    assert len(READING_CARD) == 4 and len(PROTOCOLS) == 5
    assert len(DRL_TABLE) == 14 and sum(r[4] for r in DRL_TABLE) == 3
    # 文書5節の例と同じ値になる
    deltas = [td_error(e["predicted"], e["observed"]) for e in FW_EPISODES]
    assert [round(d, 2) for d in deltas] == [0.29, 0.36, 0.03, 0.04]
    assert td_error(0, 0) == 0 and td_error(0, 5) == 1
    p = sampling_probs(deltas)
    assert abs(sum(p) - 1) < 1e-9 and p[1] == max(p) and p[2] == min(p)   # ハウスの気温が最も引かれやすい
    assert len(set(round(x, 9) for x in sampling_probs(deltas, alpha=0))) == 1  # alpha=0 は一様
    rec = log_record("科学と人間生活", "生命", "S", "正", "P2", 40, 45.5, "%")
    assert set(rec) >= {"subject", "field", "level", "timestamp", "judgement", "protocol", "td_error"}
    assert critic_gaps({"P3": "A", "P1": "B"}, {"P3": "C", "P1": "B"}) == [("P3", 2), ("P1", 0)]
    T, F, N = True, False, None
    assert judge({"①": T, "②": T, "③": F})[0] == "維持"
    assert judge({"①": T, "②": F, "③": F})[0] == "縮小"
    assert judge({"①": F, "②": T, "③": T})[0] == "棄却"
    assert judge({"①": T, "②": N, "③": F})[0] == "保留"
    assert judge({})[0] == "保留"


if __name__ == "__main__":
    _self_check()
    print("backbone: 自己チェックOK")
