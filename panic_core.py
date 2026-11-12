"""
終章 課題研究：パニックプルーフ ─ データと計算部品

問い：「供給が止まっても、何日パニックにならずに暮らせるか」を測って伸ばすフィールドワーク

出どころ（作成者の単元案4本＋作業記録表）
  - 「自給自足」ではなく「パニックプルーフ」で設計する案（4要素・1kgの種・通い型インターン・安全）
  - 1kg の種の配分案（3列96㎡に播ける量 → 1列32㎡・320g に絞る）
  - 「効率」と「しぶとさ（レジリエンス）」のトレードオフ（比較優位・共通原因）
  - 「パニックプルーフ」という言葉の意味（パニックバー・フールプルーフ・事前に決めておく）
  - 作業記録表（日付・作業・人数・時間・草丈 …）

ブラッシュアップで直したこと（元の案との違い）
  1. 物差しを令和7年度（概算）に更新：総供給熱量 2,237kcal（元の案は前年度の 2,248kcal）。
     さらに「暮らせる日数」は捨てられる分を含む“供給”ではなく、“摂取”の 1,850kcal で数えるのを既定にした。
  2. 1kg を全部播く見積もりと、実際の計画（1列32㎡に320g）を分けた。製粉の目減り（歩留まり）を式に入れた。
  3. 見積もり（事前分布）→ 発芽試験・収穫の実測（データ）→ 更新、を同じ画面で1周できるようにした。

数値の扱い
  - 自給率・供給熱量・備蓄の目安：農林水産省の公開資料（2026年8月公表の令和7年度概算、家庭備蓄の手引き）。
    **授業で使う前に最新の資料で確かめる**
  - 収量・播種量・歩留まり・玄麦の熱量：幅を持たせた仮定。実測で置きかえる前提の値

Streamlit に依存しない。`python panic_core.py` で自己チェック。
"""
from __future__ import annotations

import math

import numpy as np

TITLE = "パニックプルーフ：「供給が止まっても、何日パニックにならずに暮らせるか」を測って伸ばすフィールドワークとして設計する！"
LEAD_QUESTION = "供給が止まっても、何日パニックにならずに暮らせるか？"
EASY_WORDS = ("パニックになりにくい暮らしとは、何でも自分で作る暮らしではない。"
              "蓄えがあり、別の道があり、自分で直せて、デマに振り回されない暮らしのこと。")

# ─────────────────────────────────────────────
# 言葉の意味：-proof ＝「〜に耐える・〜を防ぐ」
# ─────────────────────────────────────────────
WORD_MEANING = [
    ("ウォータープルーフ", "水を通さない", "雨の日も中が濡れない"),
    ("フールプルーフ", "うっかりしても危なくならない", "ふたを閉めないと動かない電子レンジ"),
    ("パニックプルーフ", "慌てていても正しい行動になる", "非常口のパニックバー（押すだけで開く）"),
]
DESIGN_PRINCIPLE = ("パニックプルーフの設計とは『慌てた人に、正しく考えさせる』ことではなく、"
                    "『慌てていても、正しい行動しか選べないように先に決めておく』こと。")

# ─────────────────────────────────────────────
# 4つの要素（測れる形にする）
# ─────────────────────────────────────────────
#   (要素, 意味, 三原西部での具体物, 測る指標, 伸ばし方)
ELEMENTS: list[tuple[str, str, str, str, str]] = [
    ("🥫 バッファ（備蓄）", "途切れたときに持ちこたえる量", "小麦・米・保存食・くんだ水",
     "自給日数（食料・水・熱のうち一番短いもの）", "ふだん食べる物を少し多めに買い、古い物から使う（ローリングストック）"),
    ("🔀 冗長性（代わりの道）", "1本止まっても別の道がある", "井戸、自家の山の薪、親戚",
     "水・熱の代わりの経路の数 ＋ 『同じ原因で一緒に止まらないか』", "止まる原因がちがう道を足す"),
    ("🛠️ 技能（立て直す力）", "自分で作り直せる", "播種 → 収穫 → 脱穀 → 製粉 → パン",
     "自分でできる工程の数", "1工程ずつ、大人と一緒に1回やってみる"),
    ("📡 情報（パニックの抑え方）", "買いだめは情報の広がりで起きる", "地域の連絡網、自治体の発表",
     "噂と事実を確かめた記録の数", "『何を見たら、何をするか』を先に決めて紙に書く（事前の約束）"),
]

# ─────────────────────────────────────────────
# 社会の文脈（農林水産省・令和7年度概算・2026年8月公表）
# ─────────────────────────────────────────────
JIKYU = dict(year="令和7年度（概算）", calorie_pct=37, domestic_kcal=830, supply_kcal=2237,
             intake_kcal=1850, intake_pct=45, wheat_domestic_kcal=50, wheat_supply_kcal=310)
LAW_NOTE = ("食料供給困難事態対策法（2025年4月施行）：食料の供給が大きく減るおそれが出た段階から、"
            "政府に対策本部を置くことなどを定めた法律。『国の備え』と『家庭・地域の備え』をくらべる問いに使える。")

# 家庭備蓄の目安（農林水産省の家庭備蓄の手引き）
WATER_L_PER_DAY = 3.0        # 1人1日およそ3L（飲料水＋調理用水）
GAS_CANS_PER_WEEK = 6        # カセットボンベ 1人1週間およそ6本
RICE_G_PER_MEAL = 75         # 米 1人1食75g程度
BICHIKU_GOAL_DAYS = (3, 7)   # 最低3日分〜1週間分

# 食品の熱量（概数。日本食品標準成分表をもとに丸めた値。授業の計算用）
KCAL_PER_G = {"米（精白米）": 3.4, "小麦粉・乾麺": 3.5, "玄麦（収穫した小麦）": 3.3}
KCAL_PER_PACK = 200          # レトルト・缶詰1個の熱量（目安。ラベルで確かめる）


def kcal_yardstick(kind: str) -> int:
    """1人1日の物差し：'摂取'（暮らしに必要な量）か '供給'（捨てる分を含む量）"""
    return JIKYU["intake_kcal"] if kind == "摂取" else JIKYU["supply_kcal"]


# ─────────────────────────────────────────────
# 1kg の種で、1人何日食べられる？
# ─────────────────────────────────────────────
SEED_G = 1000
PLAN = dict(rows=1, width_m=2, length_m=16, area_m2=32, seed_g=320, rate_g_m2=10, row_cm=30, lines=6)
FULL_AREA_M2 = 96            # 3列全部
# 仮定の幅（実測で置きかえる）
RATE_RANGE = (6.0, 10.0)     # 播種量 g/㎡（＝ kg/10a）
YIELD_RANGE = (200.0, 400.0)  # 収量 kg/10a（＝ 0.2〜0.4 kg/㎡）
MILL_RANGE = (0.70, 0.95)    # 製粉歩留まり（全粒粉ならほぼ全部、白い粉なら6〜7割）


def sow_area_m2(seed_g: float, rate_g_m2: float) -> float:
    return seed_g / rate_g_m2


def harvest_kg(area_m2: float, yield_kg_10a: float) -> float:
    """10a ＝ 1000㎡"""
    return area_m2 / 1000 * yield_kg_10a


def food_days(grain_kg: float, mill: float, kcal_per_day: float, persons: int = 1,
              kcal_per_g: float = KCAL_PER_G["玄麦（収穫した小麦）"]) -> float:
    """穀物 → 粉（歩留まり）→ 熱量 → 1人1日の物差しで割る"""
    return grain_kg * 1000 * mill * kcal_per_g / (kcal_per_day * persons)


def monte_carlo(seed_g: float | None, kcal_per_day: float, *, area_m2: float | None = None,
                rate=RATE_RANGE, yld=YIELD_RANGE, mill=MILL_RANGE, n: int = 20_000, seed: int = 0) -> dict:
    """仮定の幅を一様分布で持ち、日数の分布を出す（不確かさを『分布で持つ』入口）。
    area_m2 を与えると面積は固定（計画どおり）、与えなければ seed_g ÷ 播種量 で面積を決める"""
    rng = np.random.default_rng(seed)
    r = rng.uniform(*rate, n)
    a = np.full(n, float(area_m2)) if area_m2 is not None else seed_g / r
    y = rng.uniform(*yld, n)
    m = rng.uniform(*mill, n)
    days = a / 1000 * y * 1000 * m * KCAL_PER_G["玄麦（収穫した小麦）"] / kcal_per_day
    p5, p50, p95 = np.percentile(days, [5, 50, 95])
    return dict(days=days, area=a, p5=float(p5), p50=float(p50), p95=float(p95))


def percentile_of(samples: np.ndarray, value: float) -> float:
    """実測値が見積もりの分布の何％点にあたるか（0〜100）。端に寄るほど『予想外』"""
    return float((samples < value).mean() * 100)


# ベイズ更新①：発芽試験（100粒）→ 発芽率の分布（ベータ分布）
def beta_posterior(k: int, n: int, a0: float = 1.0, b0: float = 1.0, seed: int = 0) -> dict:
    a, b = a0 + k, b0 + (n - k)
    s = np.random.default_rng(seed).beta(a, b, 20_000)
    lo, hi = np.percentile(s, [2.5, 97.5])
    return dict(a=a, b=b, mean=a / (a + b), lo=float(lo), hi=float(hi))


# ベイズ更新②：収量（正規分布どうしの更新）。来年の見積もりを、今年の実測で直す
def normal_update(prior_mu: float, prior_sd: float, obs: float, obs_sd: float) -> tuple[float, float]:
    w = prior_sd ** -2 + obs_sd ** -2
    mu = (prior_mu * prior_sd ** -2 + obs * obs_sd ** -2) / w
    return mu, math.sqrt(1 / w)


PRIOR_YIELD = ((YIELD_RANGE[0] + YIELD_RANGE[1]) / 2, (YIELD_RANGE[1] - YIELD_RANGE[0]) / math.sqrt(12))

# ─────────────────────────────────────────────
# わが家の自給日数ダッシュボード（食料・水・熱）
# ─────────────────────────────────────────────


def home_days(*, persons: int, kcal_per_day: float, rice_kg: float, flour_kg: float, packs: int,
              water_l: float, gas_cans: int) -> dict[str, float]:
    food_kcal = (rice_kg * 1000 * KCAL_PER_G["米（精白米）"] + flour_kg * 1000 * KCAL_PER_G["小麦粉・乾麺"]
                 + packs * KCAL_PER_PACK)
    return {
        "🍚 食料": food_kcal / (kcal_per_day * persons),
        "💧 水": water_l / (WATER_L_PER_DAY * persons),
        "🔥 熱": gas_cans / (GAS_CANS_PER_WEEK / 7 * persons),
    }


def bottleneck(days: dict[str, float]) -> tuple[str, float]:
    """いちばん短いものが全体を止める（必須アミノ酸の『足りない1個』と同じ形）"""
    k = min(days, key=days.get)
    return k, days[k]


# ─────────────────────────────────────────────
# 効率（分業）と しぶとさ（冗長性）
# ─────────────────────────────────────────────
TRADE_EXAMPLE = dict(hours=6, a_bread=1, a_veg=2, b_bread=3, b_veg=3)


def comparative(hours: float, a_bread: float, a_veg: float, b_bread: float, b_veg: float) -> dict:
    """自給（2人とも時間を半分ずつ）と分業（パンの数は同じにして、野菜を最大にする）をくらべる。
    パン1個あたり時間・野菜1かごあたり時間で入力"""
    self_bread = hours / 2 / a_bread + hours / 2 / b_bread
    self_veg = hours / 2 / a_veg + hours / 2 / b_veg
    cost_a, cost_b = a_veg / a_bread, b_veg / b_bread       # 野菜1かご ＝ パン何個をあきらめるか
    if math.isclose(cost_a, cost_b):
        return dict(self_bread=self_bread, self_veg=self_veg, div_bread=self_bread, div_veg=self_veg,
                    veg_maker=None, cost_a=cost_a, cost_b=cost_b, plan="向き不向きが同じなので、分業しても増えない")
    veg_maker = "B" if cost_b < cost_a else "A"
    tb, tv = (a_bread, a_veg) if veg_maker == "B" else (b_bread, b_veg)   # パン担当
    vb, vv = (b_bread, b_veg) if veg_maker == "B" else (a_bread, a_veg)   # 野菜担当
    need = self_bread * tb
    if need <= hours:
        div_veg = (hours - need) / tv + hours / vv
        plan = (f"{'A' if veg_maker == 'B' else 'B'}さんはパン{need:g}時間・野菜{hours - need:g}時間、"
                f"{veg_maker}さんは野菜だけ{hours:g}時間")
    else:                                                     # パン担当だけではパンが足りない
        rest = self_bread - hours / tb
        div_veg = (hours - rest * vb) / vv
        plan = (f"{'A' if veg_maker == 'B' else 'B'}さんはパンだけ{hours:g}時間、"
                f"{veg_maker}さんはパン{rest * vb:g}時間・野菜{hours - rest * vb:g}時間")
    return dict(self_bread=self_bread, self_veg=self_veg, div_bread=self_bread, div_veg=div_veg,
                veg_maker=veg_maker, cost_a=cost_a, cost_b=cost_b, plan=plan)


def all_fail(ps: list[float], common: float) -> float:
    """経路がすべて止まる確率。common ＝ 全経路を一度に止める共通原因（地域全体の災害など）の確率。
    各経路が止まる確率 p はそのままにして、p のうち共通原因の分を引いた残りを独立に起きるとみなす
    （p ＝ common ＋ (1−common)×q）。common は min(ps) 以下"""
    common = min(common, min(ps))
    if common >= 1:
        return 1.0
    prod = 1.0
    for p in ps:
        prod *= (p - common) / (1 - common)
    return common + (1 - common) * prod


ROUTE_PAIRS = [
    ("自宅の井戸 ＋ 親戚の井戸", "同じ地下水・同じ地震", "共倒れしやすい"),
    ("自宅の畑 ＋ スーパー", "天候 と 物流（原因がちがう）", "比較的強い"),
    ("カセットボンベ ＋ 自家の山の薪", "買い置き と 自分の山（原因がちがう）", "比較的強い"),
    ("スマホの情報 ＋ 近所の連絡網", "停電・通信障害でスマホは止まる", "連絡網が紙なら強い"),
]

STANCES = [
    ("完全な個人自給", "途切れに強い", "非効率で、時間がいくらあっても足りない"),
    ("完全な分業", "ふだんは最も豊か", "途切れに弱い"),
    ("分業 ＋ 地域の余力", "両方の良いとこ取り", "余力を保つ手間とお金（遊休農地の維持など）がかかる ＝ 保険と同じ形"),
]

# ─────────────────────────────────────────────
# 情報：噂と買いだめ（品切れは『ほんとうの不足』がなくても起きる）
# ─────────────────────────────────────────────


def panic_sim(days: int = 14, stock0: float = 3.0, restock: float = 1.0, spread: float = 0.6,
              believe: float = 0.5, multiplier: float = 3.0, seed_frac: float = 0.02) -> list[dict]:
    """店の在庫（ふだんの1日分 ＝ 1）。噂を聞いた人の割合はロジスティックに広がる。
    聞いて信じた人は multiplier 倍買う。入荷は毎日 restock（＝ふだんどおり。ほんとうの不足はない）"""
    informed, stock, rows = seed_frac, stock0, []
    for d in range(days + 1):
        demand = 1 + (multiplier - 1) * informed * believe
        sold = min(stock, demand)
        rows.append(dict(日=d, 噂を聞いた人の割合=round(informed, 3), 買いたい量=round(demand, 2),
                         売れた量=round(sold, 2), 在庫=round(stock, 2), 品切れ=demand > stock + 1e-9))
        stock = stock - sold + restock
        informed = informed + spread * informed * (1 - informed)
    return rows


def first_stockout(rows: list[dict]) -> int | None:
    return next((r["日"] for r in rows if r["品切れ"]), None)


CHECK_RUMOR = [
    "だれが言っている？（発表元が書いてあるか）",
    "いつの話？（日付があるか）",
    "ほかの出どころでも同じことが言われている？（ただし同じ元を写しただけなら1つと数える）",
    "『いますぐ』『拡散して』と急がせていないか",
]
PRECOMMIT = [
    "停電したら：冷蔵庫を開けない → 冷凍庫の物から食べる",
    "断水したら：くみ置きの水は飲み水、井戸水は（検査前は）トイレと掃除に",
    "『品切れ』の噂を見たら：買いに走る前に、上の4つを確かめる",
]

# ─────────────────────────────────────────────
# フィールドワークの設計（通い型・2回）と、科学と人間生活の4領域
# ─────────────────────────────────────────────
FORMATS = [
    ("A. 学校行事の半日FW", "◎", "低", "既存のミニFW案で対応済み"),
    ("B. 長期休暇の通い型（3〜5日×2回）", "○", "中", "推奨"),
    ("C. 宿泊型インターン", "△", "高（夜間の管理・未成年の宿泊・男女別）", "実績ができてから"),
]
CALENDAR = [
    ("11月下旬", "播種（1列32㎡・320g）", "先生が準備。残りの種で発芽試験（100粒）", "見積もり（事前分布）を出す"),
    ("冬休み（1月初旬）", "麦の生育初期", "麦踏み、生育観察、井戸水・土の観察、自給日数ダッシュボード作り",
     "3年生は共通テスト直前なので参加しない設計"),
    ("1〜4月", "分げつ・茎立ち・出穂", "草丈を決めた5株で記録、追肥（硫安）", "作業記録表に入力"),
    ("6月上旬", "収穫（梅雨入り前の晴れ間）", "ミナミノカオリは穂発芽しやすい。刈ったらハウスで干す", "収穫量の実測"),
    ("夏休み（7〜8月）", "収穫後", "製粉、パン焼き（発酵）、太陽熱温水、薪の熱量、成果発表", "実測で見積もりを更新"),
]
AREAS = [
    ("薪・太陽熱温水", "光や熱", "物理基礎：Q＝mcΔT、効率", "温度ログの時系列"),
    ("製粉・パン生地", "物質", "化学基礎：発酵のCO₂を mol で扱う", "単位変換を関数で書く"),
    ("小麦・酵母", "生命", "生物基礎：光合成・呼吸・酵素、対照実験", "条件比較の表"),
    ("井戸・気象・土", "宇宙や地球", "地学基礎：地下水・気象資料の読解", "公開気象データとの重ね合わせ"),
    ("買いだめ・噂", "（人間社会の側）", "─", "情報の伝わり方、デマへの対処（第1問）"),
]
SAFETY = [
    "**労働か学習か**：生産作業に無償で従事させると『労働』と見なされるおそれ。目的は学習・成果物は記録、という建付けを文書にする",
    "**保険**：学校管理下の活動か、民間の体験活動保険かを先に決める（保護者同意書の書き方が変わる）",
    "**機械と刃物**：耕運機・刈払機・チェーンソーは生徒に使わせない。薪は『割った量と熱量を測る』側だけ",
    "**井戸水**：水質検査の結果が出るまで飲用しない。『この水は飲めるか？を判断する手順』を探究テーマにする",
    "**熱中症**：夏の回はWBGT（暑さ指数）で中止基準を決め、作業は午前中に寄せる",
    "**火気**：薪・パン窯は大人が担当。屋内では一酸化炭素に注意",
    "**学習ログ・写真**：同意は事前に取る（事後の同意取得はできない）",
    "**小麦アレルギー**：パン焼き・製粉の回は、参加前に必ず確認する",
]
LESSON_20 = [
    {"分": "5分", "活動": "比較優位の表を配り、分業すると何が増えるかを計算させる", "このページ": "④ 効率としぶとさ"},
    {"分": "5分", "活動": "『物流が止まったらAさん・Bさんはどうなる？』と問い、確率の表を示す", "このページ": "④ 共通原因"},
    {"分": "8分", "活動": "自分の自給日数ダッシュボードに『別の原因で止まる経路』を1つ書き足す", "このページ": "③ わが家の自給日数"},
    {"分": "2分", "活動": "読解カード④でまとめる：確率の計算は、経路が独立だと仮定した場合しか言えない", "このページ": "読解カード"},
]

# 作業記録表（Excel と同じ列）
LOG_COLUMNS = ["日付", "作業", "人数", "時間（分）", "草丈（cm）", "資材と量", "天気", "土の湿り", "定点写真", "メモ"]
WORKS = ("石灰散布", "播種", "麦踏み", "追肥", "観察", "収穫", "その他")
WEATHER = ("晴れ", "曇り", "雨")
SOIL = ("乾", "適湿", "湿")
LOG_EXAMPLE = [
    {"日付": "2026-11-21", "作業": "播種", "人数": 1, "時間（分）": 90, "草丈（cm）": 0.0,
     "資材と量": "種子320g、化成肥料8-8-8 1.8kg", "天気": "晴れ", "土の湿り": "適湿", "定点写真": "あり",
     "メモ": "1列（2m×16m）に6条。条間30cm、深さ2〜3cm"},
]
FERTILIZER = [
    ("播種の1〜2週間前", "苦土石灰", 100, "前作が野菜で肥料が残っていれば、元肥は半分に"),
    ("播種時（元肥）", "化成肥料8-8-8", 55, "多すぎると倒れる（1㎡あたり50〜60g）"),
    ("1月下旬〜2月（分げつ期）", "硫安", 10, ""),
    ("3月（茎が伸び始める頃）", "硫安", 10, ""),
    ("4月（穂が出そろう頃）", "硫安", 10, "パン用に特有。粒のタンパク質を上げ、パンのふくらみを良くする"),
]


def log_summary(rows: list[dict]) -> dict:
    """延べ作業時間（人数×分）など。数字でない欄は数えない"""
    def num(v):
        try:
            f = float(v)
            return None if math.isnan(f) else f
        except (TypeError, ValueError):
            return None
    person_min = sum((num(r.get("人数")) or 0) * (num(r.get("時間（分）")) or 0) for r in rows)
    heights = [h for r in rows if (h := num(r.get("草丈（cm）"))) is not None]
    return dict(n=sum(1 for r in rows if r.get("作業")), person_hours=person_min / 60,
                max_height=max(heights) if heights else 0.0)


def kcal_per_person_hour(grain_kg: float, mill: float, person_hours: float) -> float | None:
    if person_hours <= 0:
        return None
    return grain_kg * 1000 * mill * KCAL_PER_G["玄麦（収穫した小麦）"] / person_hours


# ─────────────────────────────────────────────
# 共通テスト型問題（P1〜P5 ラベルつき）
# ─────────────────────────────────────────────
EXAM = [
    dict(p="P4", subject="情報Ⅰ・データの活用（確率）",
         q="食料の入手経路が2本あり、それぞれが止まる確率は20%で、互いに独立に止まるとする。両方とも止まる確率は？",
         opts=["40%", "20%", "4%", "0.4%"], ans="4%",
         exp="独立なら掛け算：0.2 × 0.2 ＝ 0.04。ただし同じ災害でまとめて止まる（独立でない）なら、20%近くに戻る。"),
    dict(p="P3", subject="科学と人間生活・比較を疑う",
         q="「自宅の井戸と親戚の井戸があるから、水が止まる確率は1%に下がる」という主張の、いちばんの弱点は？",
         opts=["井戸は2本では少ない", "2本とも同じ地下水なので、同じ原因で一緒に止まりうる",
               "井戸水はおいしくない", "確率は掛け算ではなく足し算で求める"],
         ans="2本とも同じ地下水なので、同じ原因で一緒に止まりうる",
         exp="共通原因（同じ地下水・同じ地震）があると、独立の仮定がくずれる。冗長性の価値は本数ではなく『原因がどれだけちがうか』で決まる。"),
    dict(p="P1", subject="物理基礎・熱",
         q="井戸水 10 kg を 15℃ から 45℃ まで温めるのに必要な熱量は？（水の比熱 4.2 J/(g·K)）",
         opts=["1.26 × 10³ J", "1.26 × 10⁵ J", "1.26 × 10⁶ J", "1.89 × 10⁶ J"], ans="1.26 × 10⁶ J",
         exp="Q ＝ mcΔT ＝ 10000 g × 4.2 × 30 K ＝ 1,260,000 J。kg を g に直すのを忘れない（1.89×10⁶ は 45℃ をそのまま使った誤り）。"),
    dict(p="P3", subject="生物基礎・対照実験",
         q="『酵母の量がパンのふくらみを決める』を確かめたい。正しい実験の組み方は？",
         opts=["酵母の量と温度を両方変えて、一番ふくらんだ条件を探す",
               "酵母の量だけを変え、粉・水・温度・時間はそろえる",
               "毎回ちがう人がこねて、平均をとる",
               "酵母の量を変えず、焼き時間だけ変える"],
         ans="酵母の量だけを変え、粉・水・温度・時間はそろえる",
         exp="変えるものは1つ。2つ同時に変えると、どちらが効いたのか言えない（読解カード③）。"),
]


def _self_check() -> None:
    j = JIKYU
    assert round(j["domestic_kcal"] / j["supply_kcal"] * 100) == j["calorie_pct"] == 37
    assert round(j["domestic_kcal"] / j["intake_kcal"] * 100) == j["intake_pct"] == 45
    # 1kg は 3列（96㎡）に播ける量（10g/㎡ だと 100㎡）。計画は 1列32㎡・320g
    assert sow_area_m2(SEED_G, 10) == 100 and PLAN["area_m2"] == PLAN["width_m"] * PLAN["length_m"] == 32
    assert PLAN["seed_g"] == PLAN["area_m2"] * PLAN["rate_g_m2"]
    assert round(PLAN["lines"] * PLAN["length_m"]) == 96                    # 条の総延長 96m
    assert abs(PLAN["seed_g"] / 96 - 3.33) < 0.01                             # 条1mあたり約3.3g
    assert round(harvest_kg(FULL_AREA_M2, 300)) == 29                         # 96㎡で 30kg 前後
    # 元の案の計算（2,248kcal・歩留まりなし）を再現すると中央値 約55日
    mc0 = monte_carlo(SEED_G, 2248, mill=(1.0, 1.0), n=100_000)
    assert 50 < mc0["p50"] < 60 and 33 < mc0["p5"] < 40 and 78 < mc0["p95"] < 88
    mc = monte_carlo(None, 1850, area_m2=PLAN["area_m2"])
    assert 10 < mc["p50"] < 17                                               # 計画の1列だと半月前後
    assert 0 <= percentile_of(mc["days"], mc["p50"]) <= 100
    # 比較優位：資料の表（自給 パン4・野菜2.5 → 分業 パン4・野菜3）
    c = comparative(**TRADE_EXAMPLE)
    assert (c["self_bread"], c["self_veg"], c["div_bread"], c["div_veg"]) == (4, 2.5, 4, 3) and c["veg_maker"] == "B"
    assert comparative(6, 1, 2, 1, 2)["veg_maker"] is None
    # 共通原因：独立なら 1%、全部共通なら 10%
    assert math.isclose(all_fail([0.1, 0.1], 0), 0.01) and math.isclose(all_fail([0.1, 0.1], 0.1), 0.1)
    assert all_fail([0.1, 0.1], 0.05) > all_fail([0.1, 0.1], 0)
    # ボトルネック
    d = home_days(persons=2, kcal_per_day=1850, rice_kg=6, flour_kg=0, packs=0, water_l=24, gas_cans=12)
    assert bottleneck(d)[0] == "💧 水" and math.isclose(d["💧 水"], 4) and math.isclose(d["🔥 熱"], 7)
    # ベイズ
    bp = beta_posterior(90, 100)
    assert 0.88 < bp["mean"] < 0.91 and bp["lo"] < bp["mean"] < bp["hi"]
    mu, sd = normal_update(300, 57.7, 250, 50)
    assert 250 < mu < 300 and sd < 50
    # 噂：ほんとうの不足がなくても品切れが起きる。信じる人が減ると遅れる／起きない
    s1 = first_stockout(panic_sim(believe=0.6))
    s2 = first_stockout(panic_sim(believe=0.1))
    assert s1 is not None and (s2 is None or s2 > s1)
    assert first_stockout(panic_sim(believe=0.0)) is None
    # 作業記録
    sm = log_summary(LOG_EXAMPLE + [{"作業": "観察", "人数": 2, "時間（分）": 30, "草丈（cm）": 5}])
    assert sm["n"] == 2 and math.isclose(sm["person_hours"], 2.5) and sm["max_height"] == 5
    assert kcal_per_person_hour(10, 0.9, 0) is None
    assert all(q["ans"] in q["opts"] and q["p"] in {"P1", "P2", "P3", "P4", "P5"} for q in EXAM)
    assert len(ELEMENTS) == 4 and len(AREAS) == 5


if __name__ == "__main__":
    _self_check()
    print("panic_core: 自己チェックOK")
