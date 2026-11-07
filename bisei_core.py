"""
2章B 微生物と人間の食生活（教科書 p.44〜49）と資料編（p.194〜201）─ 計算部品とデータ

ねらい（高所・大所から見た位置づけ）
  1章A「タンパク質」で確かめた原理 ──「取り込んだものは部品に分解され、自分の設計図で組み直される」──は、
  微生物にもそのまま当てはまる。酵母は糖を分解してエタノールと二酸化炭素にし、コウジカビは大豆のタンパク質を
  アミノ酸（うま味）にまで分解する。人間はその「分解」に名前をつけて、役に立てば発酵、困れば腐敗と呼ぶ。
  → 同じ現象でも、評価は目的（人間の側の設計図）で決まる。これが「言える／言えない」の練習になる。

データの出どころ
  - 発見の歴史・図17の分類・しょう油とみその製造法・実験2の結果例・ヨーグルトの手順：教科書の記述と表の値
  - 実験2の 30℃・22分 の値は写真で不鮮明なため 8.5 と読み取った（増え方が単調であることは変わらない）
  - ミクロメーターの計算例（7 µm、タマネギ 266 µm × 49 µm）：資料編 p.199 の値

Streamlit に依存しない。`python bisei_core.py` で自己チェック。
"""
from __future__ import annotations

# ─────────────────────────────────────────────
# ① 微生物の発見と研究（p.44〜45）
# ─────────────────────────────────────────────
HISTORY: list[tuple[str, str, str]] = [
    ("紀元前8000〜6000年ごろ", "メソポタミアで最初のビール",
     "微生物を知らないまま、発酵を生活に使っていた（経験の時代）"),
    ("1674年", "レーウェンフック（オランダ）が自作の単レンズ顕微鏡（約200倍）で微生物を発見",
     "見る道具ができて、はじめて「微生物」が研究の対象になった（観察の時代）"),
    ("17世紀〜", "「生物は親なしに無生物から自然に発生する」という自然発生説が信じられる",
     "見えるようになっても、どこから来るかは分からない"),
    ("1861年", "パスツール（フランス）が白鳥の首フラスコの実験で自然発生説を否定",
     "条件を1つだけ変える対照実験で、「生物は生物から生じる」と示した（実験の時代）"),
    ("その後", "パスツールがワインの酸っぱくなる原因（乳酸菌）を突き止め、低温殺菌法を開発",
     "発酵はそれぞれ特別な微生物が起こす ─ 原因が分かると、制御できる（応用の時代）"),
]


def pasteur(neck: str, boiled: bool) -> dict:
    """パスツールの実験（図16）の模型。
    neck: 'S字（白鳥の首）' / '首を折る'。boiled: 煮沸して殺菌したか。
    液が腐敗する ⇔ 液の中に微生物がいる（はじめから生き残っている or 外から入る）"""
    survivors = not boiled
    enters = neck == "首を折る"
    spoil = survivors or enters
    if survivors:
        why = "煮沸していないので、液の中にはじめから微生物がいる"
    elif enters:
        why = "首を折ったので、ほこりといっしょに外から微生物が入る"
    else:
        why = "空気は入るが、首が曲がっているので微生物は液まで届かない"
    return {"空気は入る？": "入る", "微生物は液に入る？": "入る" if (survivors or enters) else "入らない",
            "腐敗する？": spoil, "理由": why}


# ─────────────────────────────────────────────
# ② 発酵食品（図17：使われる微生物で分類）
# ─────────────────────────────────────────────
MICROBES = ("カビ", "酵母", "細菌")

FERMENTED: dict[str, frozenset[str]] = {
    "かつお節": frozenset({"カビ"}),
    "甘酒": frozenset({"カビ"}),
    "みりん": frozenset({"カビ", "酵母"}),
    "ビール": frozenset({"酵母"}),
    "ワイン": frozenset({"酵母"}),
    "パン": frozenset({"酵母"}),
    "日本酒": frozenset({"カビ", "酵母", "細菌"}),
    "しょう油": frozenset({"カビ", "酵母", "細菌"}),
    "みそ": frozenset({"カビ", "酵母", "細菌"}),
    "カマンベールチーズ": frozenset({"カビ", "細菌"}),
    "お酢": frozenset({"酵母", "細菌"}),
    "漬物": frozenset({"酵母", "細菌"}),
    "チーズ": frozenset({"細菌"}),
    "塩辛": frozenset({"細菌"}),
    "納豆": frozenset({"細菌"}),
    "乳酸菌飲料": frozenset({"細菌"}),
    "ヨーグルト": frozenset({"細菌"}),
}


def classify(microbes: set[str], exact: bool = False) -> list[str]:
    """選んだ微生物を『使う』食品（exact=True なら、ちょうどその組み合わせの食品）"""
    m = frozenset(microbes)
    if exact:
        return [f for f, s in FERMENTED.items() if s == m]
    return [f for f, s in FERMENTED.items() if m and m <= s]


def venn_counts() -> dict[str, int]:
    """組み合わせごとの食品の数（情報Ⅰ：集合と場合分け）"""
    out: dict[str, int] = {}
    for s in FERMENTED.values():
        k = "＋".join(x for x in MICROBES if x in s)
        out[k] = out.get(k, 0) + 1
    return out


# 「分解して部品にする」の対応表（1章A ⇄ 2章B をつなぐ背骨）
BREAKDOWN: list[tuple[str, str, str, str]] = [
    ("ヒトの消化（1章A）", "食べ物のタンパク質", "アミノ酸", "自分の遺伝子の順に並べ直して、体のタンパク質に"),
    ("しょう油・みそ（コラム）", "ダイズのタンパク質", "アミノ酸（うま味）", "日本人の重要なアミノ酸の供給源・うま味に"),
    ("糖化（p.48）", "米や麦のデンプン", "グルコース（ブドウ糖）など", "酵母がアルコール発酵の材料に使う"),
    ("アルコール発酵（p.48）", "グルコース", "エタノール＋二酸化炭素", "酒になる／パン生地がふくらむ"),
    ("腐敗（p.48）", "タンパク質（窒素・硫黄をふくむ）", "アンモニア・硫化水素など", "悪臭や毒素 ─ 人間にとって不都合"),
]

SHOYU_STEPS = ("ダイズを蒸して煮る＋コムギを炒って砕く", "混合", "コウジカビを加える（しょう油麹）",
               "食塩水を加える（仕込みもろみ）", "酵母と乳酸菌を加えて発酵", "熟成もろみ",
               "しぼる・火入れ（殺菌）・ろ過")
MISO_STEPS = ("ダイズを蒸して煮る＋米を蒸してコウジカビ（米麹）", "混合", "食塩と水を加える",
              "酵母と乳酸菌を加えて仕込み", "発酵・熟成", "品質調整")

# ─────────────────────────────────────────────
# ③ 実験2 アルコール発酵と温度（p.49 結果例）
# ─────────────────────────────────────────────
EXP2_TIME = tuple(range(0, 27, 2))  # 分
EXP2: dict[int, tuple[float, ...]] = {
    20: (0, 0.1, 0.1, 0.3, 0.4, 0.5, 0.5, 0.6, 1.0, 1.4, 1.8, 2.4, 3.2, 3.8),
    30: (0, 0.1, 0.2, 0.4, 1.2, 2.0, 3.0, 3.9, 5.0, 6.0, 7.1, 8.5, 9.4, 10.9),
    80: (0,) * 14,
}
SYRINGE_MIN_DIV = 1.0   # mL：20 mL 注射器の最小目盛り（資料5：最小目盛りの1/10まで読む → 0.1 mL）


def avg_rate(temp: int, t0: int, t1: int) -> float:
    """t0〜t1分の平均の速さ（mL/分）＝ グラフの2点を結んだ直線の傾き"""
    ys = EXP2[temp]
    i0, i1 = EXP2_TIME.index(t0), EXP2_TIME.index(t1)
    return (ys[i1] - ys[i0]) / (t1 - t0)


def fit_line(temp: int, t0: int, t1: int) -> tuple[float, float]:
    """t0〜t1分の点に最小二乗法で直線 y = a t + b を当てはめる（情報Ⅰ：回帰直線）。(a, b) を返す"""
    pts = [(t, y) for t, y in zip(EXP2_TIME, EXP2[temp]) if t0 <= t <= t1]
    n = len(pts)
    mx = sum(t for t, _ in pts) / n
    my = sum(y for _, y in pts) / n
    sxx = sum((t - mx) ** 2 for t, _ in pts)
    sxy = sum((t - mx) * (y - my) for t, y in pts)
    a = sxy / sxx if sxx else 0.0
    return a, my - a * mx


def increments(temp: int) -> list[float]:
    """2分ごとの増え方（差分）。増え方そのものが大きくなっていく＝酵母が増えたり活発になったりしている"""
    ys = EXP2[temp]
    return [round(b - a, 2) for a, b in zip(ys, ys[1:])]


# ─────────────────────────────────────────────
# ④ やってみよう：ヨーグルト（p.48）
# ─────────────────────────────────────────────
YOGURT_STEPS = (
    "新鮮な牛乳を鍋で煮沸する。沸騰したらすぐ火を止めて冷まし、煮沸消毒して冷ましたガラス容器へ移す",
    "牛乳 500 mL に乳酸菌 1 g（または開封直後のヨーグルト 10 g）を加え、ラップで密封する",
    "40 ℃ の恒温器で約6時間。1時間ごとにきれいなスプーンで採り pH を測る。pH 3〜4 で完成",
)
YOGURT_SAFETY = ("実験の前後に必ずセッケンで手を洗う", "有害な微生物が培養される可能性があるので食べてはいけない",
                 "保護眼鏡・やけどに注意")


def ph_ratio(ph_a: float, ph_b: float) -> float:
    """pH が1小さいと、酸性の強さ（水素イオンの濃さ）は10倍。pH_a の液は pH_b の液の何倍の濃さか"""
    return 10 ** (ph_b - ph_a)


# ─────────────────────────────────────────────
# 資料編：有効数字・ミクロメーター・SI接頭語（p.196〜199）
# ─────────────────────────────────────────────
def sig_figs(s: str) -> int:
    """有効数字の桁数。'48.7'→3、'0.0032'→2、'1.20e3'→3、'1.20×10^3'→3。
    '1200' のように末尾の0の意味があいまいな整数は、0を数えない（指数で書くべき、が教科書の立場）"""
    t = s.strip().replace("×10^", "e").replace("x10^", "e").replace("E", "e")
    mant = t.split("e")[0].lstrip("+-")
    if "." in mant:
        digits = mant.replace(".", "").lstrip("0")
        return len(digits) if digits else 1
    digits = mant.lstrip("0").rstrip("0")
    return len(digits) if digits else 1


def micrometer_unit(obj_div: int, eye_div: int, obj_um: float = 10.0) -> float:
    """接眼ミクロメーター1目盛りの長さ（µm）= 対物ミクロメーター1目盛り(10µm) × 対物の目盛り数 ÷ 接眼の目盛り数"""
    return obj_um * obj_div / eye_div


SI_PREFIX = (("T", "テラ", 12), ("G", "ギガ", 9), ("M", "メガ", 6), ("k", "キロ", 3),
             ("c", "センチ", -2), ("m", "ミリ", -3), ("µ", "マイクロ", -6), ("n", "ナノ", -9), ("p", "ピコ", -12))


def binary_gap(exp10: int) -> float:
    """情報Ⅰの単位とのずれ：10進の接頭語 10^(3k) と 2進の 2^(10k) の比。k（キロ）で 1.024"""
    k = exp10 // 3
    return 2 ** (10 * k) / 10 ** (3 * k)


def _self_check() -> None:
    assert pasteur("S字（白鳥の首）", True)["腐敗する？"] is False         # 図16 ④⑤
    assert pasteur("首を折る", True)["腐敗する？"] is True                # 1861年の確認
    assert pasteur("S字（白鳥の首）", False)["腐敗する？"] is True
    assert set(classify({"カビ", "酵母", "細菌"}, exact=True)) == {"日本酒", "しょう油", "みそ"}
    assert "パン" in classify({"酵母"}) and "パン" not in classify({"細菌"})
    assert sum(venn_counts().values()) == len(FERMENTED) == 17
    assert all(len(v) == len(EXP2_TIME) for v in EXP2.values())
    assert all(b >= a for v in EXP2.values() for a, b in zip(v, v[1:]))      # 累積量は減らない
    assert avg_rate(30, 0, 26) > avg_rate(20, 0, 26) > avg_rate(80, 0, 26) == 0
    a, _ = fit_line(30, 8, 26)
    assert 0.4 < a < 0.6
    assert sig_figs("48.7") == 3 and sig_figs("0.0032") == 2 and sig_figs("1.20e3") == 3 and sig_figs("1200") == 2
    assert micrometer_unit(14, 20) == 7.0 and 38 * micrometer_unit(14, 20) == 266 and 7 * 7 == 49
    assert round(binary_gap(3), 3) == 1.024 and round(ph_ratio(3, 6)) == 1000


if __name__ == "__main__":
    _self_check()
    print("bisei_core: 自己チェックOK")
