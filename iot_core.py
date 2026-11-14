"""
フィールドワーク実践：理科の教員免許（科学と人間生活）× IoTアプリ構築・運用支援 ─ データと計算部品

問い：「ハウスの空気は、いま植物と人にとって『ちょうどいい』か。それを測り、貯め、知らせるしくみを自分たちで作って回せるか」

出どころ（作成者がまとめた資料9本。講座名・講師名・事業所名は載せず、内容の骨組みだけを自分の言葉で整理した）
  - IoT講座3本：CO2の換気モニタ ／ 水耕栽培と自動水やり ／ 画像・CO2・温湿度・照度・水深のIoTキット（3Dプリンタ活用）
  - 周辺5本：MLOps（運用の輪）／ 生物系データサイエンス入門 ／ サワー種パン ／ クラウド上のWebアプリ構築 ／ オンライン直売
  - 就労継続支援B型 × 生成AI の仕事像（「教える人」であり「一緒に発見する人」）

このページの立場
  - 理科の免許が効くところ＝「何を測れば、何が言えるか」を決めること（条件をそろえる・単位・誤差）。
  - IoT支援が効くところ＝それを毎日止めずに動かすこと（配線・クラウド・通知・保守）。
  - 2つを掛けたものがフィールドワーク実践：三原西部のハウス（5.5m×15m）と畑で、作って・測って・運用する。

数値の扱い
  - 基準値：建築物衛生法 1000ppm 以下、学校環境衛生基準 1500ppm 以下が望ましい、
    換気の目安 1人あたり毎時30m³（厚生労働省の換気資料）。**授業で使う前に最新の資料で確かめる**
  - CO2の発生量・光合成の吸収速度・消費電力・部品の値段：幅を持たせた仮定。実測や実際の価格で置きかえる前提の値
  - センサーの1日分のデータ：**説明用の架空データ**（乱数の種を固定して毎回同じ形になる）

Streamlit に依存しない。`python iot_core.py` で自己チェック。
"""
from __future__ import annotations

import math

import numpy as np

TITLE = "理科の教員免許（科学と人間生活）× IoTアプリ構築・運用支援 ＝ フィールドワーク実践"
LEAD_QUESTION = "ハウスの空気は、いま植物と人にとって『ちょうどいい』か。測って・貯めて・知らせるしくみを、自分たちで作って回せるか？"
EASY_WORDS = ("IoT（アイオーティー）＝「モノがインターネットにつながること」。"
              "ここでは、センサーで測った数字を自動でネット上の表に書きこみ、いつでも見られるようにするしくみのこと。")

# ─────────────────────────────────────────────
# ① 掛け算の地図：6＋2の段（測る→…→動かす ＋ つくる・届ける）と、資料9本
# ─────────────────────────────────────────────
#   (段, やさしい言い換え, 科学と人間生活での見方, 情報Ⅰの単元)
STAGES: list[tuple[str, str, str, str]] = [
    ("測る", "センサーで数字にする", "単位・誤差・何をそろえて測るか", "アナログとデジタル・標本化"),
    ("貯める", "ネット上の表に自動で書く", "記録の形式をそろえる（野帳と同じ）", "情報通信ネットワーク・API・データベース"),
    ("見る", "グラフとまとめにする", "図表から言えること／言えないこと", "データの活用（代表値・散布図・外れ値）"),
    ("知らせる", "しきい値をこえたらメール", "基準値の根拠・誤報と見逃し", "条件分岐・確率"),
    ("動かす", "数字に応じてポンプを入切", "フィードバック（恒常性と同じ形）", "アルゴリズム・制御"),
    ("つくる", "3Dプリンタで部品を作る", "プラスチックの性質と再利用", "モデル化（3Dデータ）"),
    ("運用する", "止めずに回し、直し続ける", "仮説→測定→ふり返りの輪", "情報セキュリティ・システムの保守"),
    ("届ける", "できた物・わかった事を人に伝える", "科学と人間生活の『生活』の側", "情報デザイン・メディアの特性"),
]
STAGE_NAMES = [s[0] for s in STAGES]

#   id, 表示名, 動画の時間[h], レクチャー数, レベル, かかわる段, 科学と人間生活の領域, FWでの役割
MATERIALS: list[dict] = [
    dict(id="kanki", name="📡 IoT①：CO2の換気モニタ", hours=2.0, lectures=45, level="初級",
         stages=("測る", "貯める", "見る"), field="物質の科学・生命の科学（呼吸と光合成）",
         role="最初の1台。ハンダ付けなしで『測る→貯める』を1日で通す"),
    dict(id="garden", name="🌿 IoT②：水耕栽培と自動水やり", hours=2.5, lectures=35, level="初級",
         stages=("測る", "貯める", "動かす"), field="生命の科学（植物の生育と光・水）",
         role="水深に応じてポンプを入切する『動かす』を足す"),
    dict(id="kit", name="🧰 IoT③：画像・環境データのキット（3Dプリンタ）", hours=6.0, lectures=48, level="初級",
         stages=("測る", "貯める", "見る", "知らせる", "つくる"), field="物質の科学（プラスチック）・光や熱の科学",
         role="ハウスに置く本番機。写真・まとめメール・警報メールまで"),
    dict(id="mlops", name="🔁 MLOps：運用の輪の考え方", hours=2.5, lectures=23, level="中級",
         stages=("見る", "運用する"), field="終章（課題研究の進め方）",
         role="『作って終わり』にしない。データ→見直し→作り直しの輪を先生側が設計する"),
    dict(id="bio", name="🧬 生物系データサイエンス入門", hours=1.0, lectures=25, level="初級",
         stages=("見る",), field="生命の科学（遺伝子）",
         role="生き物のデータを読む目的を知る（タンパク質のページとつなぐ）"),
    dict(id="sour", name="🍞 サワー種パン", hours=5.0, lectures=105, level="全レベル",
         stages=("測る", "届ける"), field="生命の科学（微生物と食生活）",
         role="測る対象そのもの。発酵は温度と時間で決まる＝センサーの出番。材料は体積でなく重さで量る"),
    dict(id="web", name="☁️ クラウド上のWebアプリ構築", hours=10.0, lectures=121, level="中級",
         stages=("貯める", "見る", "運用する"), field="─（情報Ⅰ・情報Ⅱの発展）",
         role="表計算の次の段階。監視・権限・料金アラートの考え方を先生側が持つ"),
    dict(id="marche", name="🛒 オンライン直売：最初の1個を売るまで", hours=3.5, lectures=22, level="初級",
         stages=("届ける",), field="終章（これからの科学と人間生活）",
         role="出口。育てた麦・焼いたパンを、写真と文章で伝える"),
    dict(id="fukushi", name="🤝 福祉の現場 × 生成AI（仕事像）", hours=0.0, lectures=0, level="─",
         stages=("運用する", "届ける"), field="終章（職業につながる科学）",
         role="伴走の立ち位置。決まった教材をなぞらず、その人の『得意』と道具を組み合わせる"),
]
BY_ID = {m["id"]: m for m in MATERIALS}
IOT_CORE_IDS = ("kanki", "garden", "kit")


def coverage(ids) -> dict[str, list[str]]:
    """選んだ資料が、どの段を何本でカバーするか {段: [資料名, …]}"""
    out = {s: [] for s in STAGE_NAMES}
    for i in ids:
        for s in BY_ID[i]["stages"]:
            out[s].append(BY_ID[i]["name"])
    return out


def plan_summary(ids) -> dict:
    """選んだ資料の合計時間・レクチャー数・抜けている段"""
    cov = coverage(ids)
    return dict(hours=sum(BY_ID[i]["hours"] for i in ids), lectures=sum(BY_ID[i]["lectures"] for i in ids),
                missing=[s for s, v in cov.items() if not v], covered=sum(1 for v in cov.values() if v))


def matrix(ids=None) -> list[list[int]]:
    """資料×段 の 0/1 行列（ヒートマップ用）"""
    ids = [m["id"] for m in MATERIALS] if ids is None else list(ids)
    return [[1 if s in BY_ID[i]["stages"] else 0 for s in STAGE_NAMES] for i in ids]


# ─────────────────────────────────────────────
# ② CO2と換気：1つの箱の模型（入ってくる量−出ていく量）
# ─────────────────────────────────────────────
LIMITS = {"建築物衛生法（事務所など）": 1000, "学校環境衛生基準（教室）": 1500}
OUTDOOR_PPM = 420            # 外気のCO2濃度（目安。年々少しずつ上がっている）
CO2_PER_PERSON = 0.020       # 1人が1時間に出すCO2 [m³/h]（座って軽い作業の目安。安静なら少なく、運動で増える）
VENT_PER_PERSON = 30         # 換気の目安 [m³/(h・人)]
CLASSROOM = dict(people=40, volume=180.0)     # 教室：およそ 8m × 7.5m × 高さ3m
HOUSE = dict(width=5.5, length=15.0, height=2.5)   # 三原西部のハウス（高さは平均の仮定）
CO2_G_PER_M3 = 1830.0        # CO2 1m³ の質量 [g]（20℃・1気圧：44 g/mol ÷ 24.0 L/mol）
COMPENSATION_PPM = 50        # CO2補償点（これ以下では光合成が呼吸に追いつかない。C3植物の目安）


def house_volume() -> float:
    return HOUSE["width"] * HOUSE["length"] * HOUSE["height"]


def house_area() -> float:
    return HOUSE["width"] * HOUSE["length"]


def steady_ppm(people: float, vent_m3h: float, gen: float = CO2_PER_PERSON, outdoor: float = OUTDOOR_PPM) -> float:
    """換気し続けたときに落ち着く濃度 [ppm]：外気 ＋ 発生量 ÷ 換気量。換気ゼロなら上がり続ける（inf）"""
    if vent_m3h <= 0:
        return math.inf if people * gen > 0 else outdoor
    return outdoor + people * gen / vent_m3h * 1e6


def co2_series(people: float, volume: float, vent_m3h: float, minutes: int, start: float = OUTDOOR_PPM,
               gen: float = CO2_PER_PERSON, outdoor: float = OUTDOOR_PPM, step_min: int = 1):
    """部屋のCO2濃度の時間変化。V dC/dt = 発生 − 換気×(C − 外気) の厳密解。返り値 (分, ppm)"""
    t = np.arange(0, minutes + 1, step_min, dtype=float)
    th = t / 60.0
    src = people * gen * 1e6 / volume          # 換気ゼロのときの上がり方 [ppm/h]
    if vent_m3h <= 0:
        return t, start + src * th
    n = vent_m3h / volume                      # 換気回数 [回/h]
    eq = outdoor + src / n
    return t, eq + (start - eq) * np.exp(-n * th)


def minutes_to_reach(limit: float, people: float, volume: float, vent_m3h: float, start: float = OUTDOOR_PPM,
                     gen: float = CO2_PER_PERSON, outdoor: float = OUTDOOR_PPM) -> float:
    """limit [ppm] に届くまでの分数。届かないなら inf、最初から超えていれば 0"""
    if start >= limit:
        return 0.0
    src = people * gen * 1e6 / volume
    if vent_m3h <= 0:
        return (limit - start) / src * 60 if src > 0 else math.inf
    n = vent_m3h / volume
    eq = outdoor + src / n
    if eq <= limit:
        return math.inf
    return -math.log((limit - eq) / (start - eq)) / n * 60


def required_vent(people: float, limit: float, gen: float = CO2_PER_PERSON, outdoor: float = OUTDOOR_PPM) -> float:
    """limit [ppm] 以下に保つのに必要な換気量 [m³/h]"""
    return people * gen / ((limit - outdoor) * 1e-6)


def house_steady_ppm(uptake_g_m2h: float, ach: float, outdoor: float = OUTDOOR_PPM) -> float:
    """晴れた日中のハウスで落ち着くCO2濃度 [ppm]。
    模型：植物の吸収は（濃度 − 補償点）に比例する。uptake は外気と同じ濃度のときの吸収速度 [g/(㎡・h)]、ach は換気回数 [回/h]。
      dC/dt = ach×(外気 − C) − k×(C − 補償点)   →   C = (ach×外気 + k×補償点) ÷ (ach + k)"""
    k = house_uptake_rate(uptake_g_m2h, outdoor)
    if ach + k <= 0:
        return outdoor
    return (ach * outdoor + k * COMPENSATION_PPM) / (ach + k)


def house_uptake_rate(uptake_g_m2h: float, outdoor: float = OUTDOOR_PPM) -> float:
    """吸収の強さ k [1/h]：外気と同じ濃度のとき、1時間にハウスの空気から何 ppm 減らすかを（外気−補償点）で割ったもの"""
    ppm_per_h = uptake_g_m2h * house_area() / CO2_G_PER_M3 / house_volume() * 1e6
    return ppm_per_h / (outdoor - COMPENSATION_PPM)


def house_series(uptake_g_m2h: float, ach: float, minutes: int = 180, start: float = OUTDOOR_PPM,
                 outdoor: float = OUTDOOR_PPM):
    """朝、日が当たりはじめてからのハウスのCO2濃度（分, ppm）"""
    t = np.arange(0, minutes + 1, dtype=float)
    k = house_uptake_rate(uptake_g_m2h, outdoor)
    if ach + k <= 0:
        return t, np.full_like(t, start)
    eq = house_steady_ppm(uptake_g_m2h, ach, outdoor)
    return t, eq + (start - eq) * np.exp(-(ach + k) * t / 60.0)


# ─────────────────────────────────────────────
# ③ センサーとデータ：番地（I2C）・表の大きさ・1日分の架空データ
# ─────────────────────────────────────────────
I2C_MIN, I2C_MAX = 0x08, 0x77      # ふつうに使える7ビットの番地の範囲
#   (測るもの, つなぎ方, 単位, 理科での意味, 番地の例)　※番地は機種で違う。必ずデータシートで確かめる
SENSORS: list[tuple[str, str, str, str, str]] = [
    ("温度・湿度", "I2C", "℃・%", "発酵・蒸散・結露（露点）", "0x44"),
    ("照度", "I2C", "lx（ルクス）", "光合成に使える光の目安", "0x23"),
    ("距離（→水深）", "I2C", "mm", "水面までの距離を測り、容器の深さから引く", "0x29"),
    ("CO2", "USB", "ppm", "換気・呼吸・光合成", "─（I2Cではない）"),
    ("画像", "USB（Webカメラ）", "枚", "生育の記録・タイムラプス", "─（I2Cではない）"),
]
SHEET_CELL_LIMIT = 10_000_000      # 表計算（Google スプレッドシート）1ファイルのセル数の上限


def i2c_info(addr: int) -> dict:
    """7ビットの番地を、10進・16進・2進で表す"""
    if not 0 <= addr <= 0x7F:
        raise ValueError("I2Cの番地は 0〜127（7ビット）")
    return dict(dec=addr, hex=f"0x{addr:02X}", bin=f"{addr:07b}", usable=I2C_MIN <= addr <= I2C_MAX)


def i2c_usable_count() -> int:
    return I2C_MAX - I2C_MIN + 1


def rows_per_day(interval_min: float) -> float:
    return 1440.0 / interval_min


def days_until_full(columns: int, interval_min: float, limit: int = SHEET_CELL_LIMIT) -> float:
    """1ファイルの表がいっぱいになるまでの日数（1回の測定で1行・columns 列）"""
    return limit / (columns * rows_per_day(interval_min))


def synth_day(seed: int = 7, interval_min: int = 10, outlier: bool = False, missing: bool = False) -> dict:
    """ハウスの1日分（0:00〜23:50）の**架空データ**。列：時刻[h]・気温・湿度・照度・CO2・水深。
    outlier=True でCO2に1点だけありえない値（センサーの誤動作）、missing=True で昼の1時間が欠測（NaN）になる"""
    rng = np.random.default_rng(seed)
    h = np.arange(0, 24, interval_min / 60.0)
    sun = np.clip(np.sin((h - 6.5) / 11.0 * np.pi), 0, None)          # 6:30〜17:30 に日が当たる
    temp = 9 + 16 * sun ** 1.2 + 2.5 * np.sin((h - 15) / 24 * 2 * np.pi) + rng.normal(0, 0.3, h.size)
    hum = np.clip(92 - 2.6 * (temp - 9) + rng.normal(0, 1.5, h.size), 30, 99)
    lux = 42000 * sun * (0.85 + 0.15 * rng.random(h.size))
    co2 = 560 - 330 * sun ** 0.7 + 60 * (1 - sun) * np.sin(h / 24 * np.pi) + rng.normal(0, 12, h.size)
    depth = 60 - (np.cumsum(0.02 + 0.5 * sun) % 28) + rng.normal(0, 0.6, h.size)
    co2 = co2.copy()
    if outlier:
        co2[int(h.size * 0.62)] = 5000.0
    if missing:
        co2[(h >= 12) & (h < 13)] = np.nan
    return {"時刻": h, "気温": temp, "湿度": hum, "照度": lux, "CO2": co2, "水深": depth}


def summary(values) -> dict:
    """まとめメールに入れる数字（欠測は除いて数える）"""
    v = np.asarray(values, dtype=float)
    ok = v[~np.isnan(v)]
    if ok.size == 0:
        return dict(n=0, missing=int(v.size), mean=math.nan, median=math.nan, min=math.nan, max=math.nan)
    return dict(n=int(ok.size), missing=int(v.size - ok.size), mean=float(ok.mean()), median=float(np.median(ok)),
                min=float(ok.min()), max=float(ok.max()))


# ─────────────────────────────────────────────
# ④ 知らせる・動かす：誤報の確率・ベイズ・ヒステリシス
# ─────────────────────────────────────────────
def _phi(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def exceed_prob(true_value: float, threshold: float, noise_sd: float) -> float:
    """本当の値が true_value のとき、1回の測定がしきい値をこえる確率（測定のばらつきは正規分布と仮定）"""
    if noise_sd <= 0:
        return 1.0 if true_value > threshold else 0.0
    return 1 - _phi((threshold - true_value) / noise_sd)


def false_alarms_per_day(true_value: float, threshold: float, noise_sd: float, interval_min: float,
                         consecutive: int = 1) -> float:
    """異常でないのに警報が出る回数の目安 [回/日]。『n回つづけてこえたら警報』にすると p の n 乗に減る（毎回の測定は独立と仮定）"""
    p = exceed_prob(true_value, threshold, noise_sd)
    return rows_per_day(interval_min) * p ** consecutive


def alert_delay_min(interval_min: float, consecutive: int) -> float:
    """本当に異常になってから警報が出るまでの、最短の遅れ [分]"""
    return interval_min * (consecutive - 1)


def bayes_alert(prior: float, hit: float, false_rate: float) -> float:
    """警報が鳴ったとき、本当に異常である確率（ベイズの定理）。prior＝異常の起こりやすさ、hit＝異常を見つける率、false_rate＝誤報率"""
    den = prior * hit + (1 - prior) * false_rate
    return prior * hit / den if den > 0 else 0.0


def pump_sim(low: float, high: float, hours: float = 24.0, step_min: float = 1.0, start: float = 50.0,
             drain_mm_h: float = 3.0, fill_mm_h: float = 60.0, noise_sd: float = 1.0, seed: int = 3) -> dict:
    """水深でポンプを入切する模型。low より浅くなったら ON、high より深くなったら OFF（low＝high なら『しきい値1本』）。
    センサーの読みにはばらつき noise_sd [mm] がのる。返り値：時刻[h]・本当の水深・ポンプの状態・入切の回数"""
    if high < low:
        raise ValueError("high は low 以上")
    rng = np.random.default_rng(seed)
    n = int(hours * 60 / step_min) + 1
    t = np.arange(n) * step_min / 60.0
    depth = np.empty(n)
    pump = np.zeros(n, dtype=int)
    d, on, switches = start, False, 0
    dt = step_min / 60.0
    for i in range(n):
        reading = d + rng.normal(0, noise_sd)
        new_on = on
        if reading < low:
            new_on = True
        elif reading > high:
            new_on = False
        if new_on != on:
            switches += 1
            on = new_on
        depth[i], pump[i] = d, int(on)
        d = max(d + (fill_mm_h if on else 0.0) * dt - drain_mm_h * dt, 0.0)
    return dict(t=t, depth=depth, pump=pump, switches=switches, min=float(depth.min()), max=float(depth.max()))


# ─────────────────────────────────────────────
# ⑤ コストと運用
# ─────────────────────────────────────────────
BUDGET_RANGE = (20000, 30000)      # 資料にある材料費の目安（1台2〜3万円。クラウドは無料枠の中で使う）
#   (部品, 役割, 仮の値段[円], なくても始められるか)　※値段は**仮の値**。買う前に必ず調べて書きかえる
BOM: list[tuple[str, str, int, bool]] = [
    ("小型コンピュータ本体", "頭脳。センサーを読み、ネットに送る", 10000, False),
    ("電源アダプタ・microSD", "動かすための最低限", 3000, False),
    ("CO2センサー（USB接続）", "換気・光合成を測る", 6000, False),
    ("温湿度・照度・距離センサー（I2C）", "環境と水深を測る（ハンダ付けあり）", 3000, True),
    ("Webカメラ", "生育の写真・タイムラプス", 2500, True),
    ("拡張ボード・配線", "配線をかんたん・安全にする", 1500, True),
    ("リレー＋小型ポンプ", "自動水やり（動かす）", 2000, True),
]
POWER_W = 5.0                # 本体の消費電力の目安 [W]（機種と負荷で 3〜8W ほど）
YEN_PER_KWH = 31.0           # 電気代の目安単価 [円/kWh]


def bom_total(prices, include) -> int:
    return int(sum(p for p, inc in zip(prices, include) if inc))


def power_cost_month(watt: float, yen_per_kwh: float = YEN_PER_KWH, days: int = 30) -> float:
    """つけっぱなしにしたときの1か月の電気代 [円]"""
    return watt * 24 * days / 1000 * yen_per_kwh


def filament_cost(grams: float, yen_per_kg: float) -> float:
    """3Dプリンタで作る部品1個の材料費 [円]"""
    return grams * yen_per_kg / 1000


def cost_per_reading(total_yen: float, months: float, monthly_yen: float, columns: int, interval_min: float) -> float:
    """集めた数字1個あたりの値段 [円]（材料費＋電気代を、期間中に集まる数字の個数で割る）"""
    n = columns * rows_per_day(interval_min) * 30 * months
    return (total_yen + monthly_yen * months) / n if n > 0 else math.inf


# ─────────────────────────────────────────────
# ⑥ 伴走の設計：運用の輪・役割・安全・秘密の管理
# ─────────────────────────────────────────────
#   (輪の段, AIの運用（MLOps）では, このフィールドワークでは)
OPS_LOOP: list[tuple[str, str, str]] = [
    ("集める", "データを集めて整える", "センサーが10分ごとに表へ書きこむ"),
    ("作る", "モデルを学習する", "しきい値・水やりの規則を決める（最初は人が決める）"),
    ("出す", "本番に配備する", "ハウスに置いて動かしはじめる"),
    ("見張る", "精度の低下を監視する", "毎朝のまとめメールと、誤報・見逃しの記録"),
    ("直す", "再学習して入れかえる", "規則を1か所だけ変えて、前の週とくらべる"),
]

#   (仕事, 内容, 向いている『得意』, 安全・配慮, P)
ROLES: list[tuple[str, str, str, str, str]] = [
    ("🔧 組み立て係", "部品をそろえ、図のとおりに差しこむ", "手順どおりにていねいに進める", "電源を抜いてから配線する。ハンダ付けは大人と一緒に", "P1"),
    ("🔍 毎朝の点検係", "まとめメールとハウスの様子を見くらべる", "毎日同じことを続けられる", "数字と実物が合わないときは、さわらずに報告する", "P2"),
    ("📊 グラフ係", "1週間のグラフから『いつもと違う日』を探す", "形や色のちがいに気づく", "『言えないこと』も1つ書く", "P3"),
    ("🖨️ 部品づくり係", "3Dプリンタでセンサーのカバーや台を作る", "ものづくり・形を考える", "ノズルと台は熱い。まわりに燃える物を置かない", "P4"),
    ("✍️ 伝える係", "写真と文章で、育った様子・できたパンを紹介する", "写真・文章・デザイン", "人の顔・名前・住所が写っていないか確かめる", "P5"),
]

#   (点検項目, なぜ, 重み)　重みの合計が点数の満点
SECURITY_CHECKS: list[tuple[str, str, int]] = [
    ("クラウドの鍵ファイル（.json など）を GitHub に置いていない", "鍵があれば、だれでも自分たちの表やメールを使えてしまう", 3),
    ("鍵やパスワードは設定ファイルに分け、.gitignore に書いた", "プログラムを公開しても、秘密は公開されない", 3),
    ("遠隔操作（リモート画面）のパスワードを初期値から変えた", "初期値は世界中の人が知っている", 2),
    ("カメラに人・家の表札・車のナンバーが写らない向きにした", "写真は自動でクラウドに上がる。あとから消すのは大変", 2),
    ("警報メールの宛先は、同意した大人のアドレスだけにした", "連絡先も個人情報", 1),
    ("共有する表は『リンクを知っている全員』ではなく、相手を指定した", "URLは思ったより広がる", 2),
    ("料金の上限・警告を設定した（無料枠をこえたら気づける）", "止め忘れた計測が、請求になることがある", 1),
]
SECURITY_MAX = sum(w for _, _, w in SECURITY_CHECKS)

# 公開リポジトリに入れてはいけないファイル名の目印（名前だけで判定。中身は読まない・入力させない）
_RISKY_EXACT = {".env", "token.json", "credentials.json", "client_secret.json", "service_account.json", "id_rsa",
                "secrets.toml", "token.pickle"}
_RISKY_PARTS = ("secret", "credential", "service_account", "service-account", "token", "password", "passwd", "apikey",
                "api_key", "private")
_RISKY_EXT = (".pem", ".key", ".p12", ".pfx", ".pickle")


def risky_files(names) -> list[tuple[str, str]]:
    """ファイル名のリストから、公開してはいけなさそうなものを [(名前, 理由)] で返す。**ファイルの中身は扱わない**"""
    out = []
    for raw in names:
        name = str(raw).strip().strip("/").split("/")[-1]
        low = name.lower()
        if not low:
            continue
        if low in _RISKY_EXACT:
            out.append((name, "鍵・トークンによく使われる名前"))
        elif low.endswith(_RISKY_EXT):
            out.append((name, "秘密鍵・証明書の拡張子"))
        elif any(p in low for p in _RISKY_PARTS):
            out.append((name, "名前に secret／token／credential などが入っている"))
        elif low.startswith("config") and low.endswith((".ini", ".json", ".yaml", ".yml", ".toml")):
            out.append((name, "設定ファイル。パスワードや宛先が入っていないか確かめる"))
    return out


def gitignore_lines(names) -> list[str]:
    """risky_files で見つかった名前を .gitignore に書く形にする"""
    return sorted({n for n, _ in risky_files(names)})


def security_score(checked) -> int:
    return int(sum(w for (_, _, w), c in zip(SECURITY_CHECKS, checked) if c))


#   (回, 場所, やること, 理科の見方, 情報Ⅰ・IoT, 成果物)
LESSONS: list[tuple[str, str, str, str, str, str]] = [
    ("1", "教室", "CO2の予想と換気の模型（②）", "呼吸・発生量と換気量のつり合い", "モデル化とシミュレーション", "予想とずれの記録"),
    ("2", "教室", "換気モニタを組み、表に書きこむ（③）", "単位 ppm・測る位置をそろえる", "API・表の形式・番地（2進数）", "動いている1台と、最初の100行"),
    ("3", "ハウス", "設置して1週間測る", "光合成と呼吸で日中と夜が逆になる", "欠測・外れ値の見つけ方", "1週間のグラフと読解カード"),
    ("4", "教室", "警報と水やりの規則を決める（④）", "基準値の根拠・誤報と見逃し", "条件分岐・確率", "規則カード（何を見たら、何をするか）"),
    ("5", "工作室", "3Dプリンタでカバーを作る／費用をまとめる（⑤）", "プラスチックの熱の性質", "3Dデータ・費用の計算", "部品1個と費用の表"),
    ("6", "ハウス・教室", "運用をふり返り、次の人に引きつぐ（⑥）", "仮説→測定→ふり返り", "情報セキュリティ・保守", "引きつぎ書と発表"),
]

#   共通テスト型問題（比較を疑う：交絡）
EXAM = dict(
    p="P3", subject="情報Ⅰ 第4問型 × 科学と人間生活",
    q="教室のCO2を1か月測ったところ、『窓を開けていた時間帯のほうが、閉めていた時間帯よりCO2濃度の平均が高い』"
      "という結果になった。ここから言えることとして最も適切なものはどれか。",
    opts=["窓を開けるとCO2濃度は上がる", "窓を開けてもCO2濃度は変わらない",
          "人が多い時間帯ほど窓を開けていた可能性があり、人数をそろえて比べないと窓の効果は言えない",
          "センサーが壊れているので、データはすべて捨てるべきである"],
    ans="人が多い時間帯ほど窓を開けていた可能性があり、人数をそろえて比べないと窓の効果は言えない",
    exp="『人数』が、窓を開けるかどうかにもCO2濃度にも効いている（交絡）。人数が同じ時間帯どうしで比べる、"
        "または同じ人数のまま窓だけを開け閉めして測る（対照実験）と、窓の効果が見える。")


def _self_check() -> None:
    # ① 地図
    assert len(MATERIALS) == 9 and len(STAGE_NAMES) == 8
    assert all(set(m["stages"]) <= set(STAGE_NAMES) for m in MATERIALS)
    assert abs(sum(m["hours"] for m in MATERIALS) - 32.5) < 1e-9
    core = plan_summary(IOT_CORE_IDS)
    assert core["hours"] == 10.5 and core["lectures"] == 128
    assert set(core["missing"]) == {"運用する", "届ける"}          # IoT講座3本だけでは『運用』『届ける』が抜ける
    assert plan_summary([m["id"] for m in MATERIALS])["missing"] == []
    # ② 換気：1000ppm ⇔ 1人あたり毎時約30m³（厚生労働省の資料と同じ関係）
    per_person = required_vent(1, 1000, outdoor=350)
    assert 30 <= per_person <= 31
    assert abs(steady_ppm(40, required_vent(40, 1000)) - 1000) < 1e-6
    t, c = co2_series(40, 180.0, 0, 60)
    assert abs(c[-1] - (OUTDOOR_PPM + 40 * 0.02 / 180 * 1e6)) < 1e-6      # 換気ゼロ：1時間で約4444ppm上がる
    m = minutes_to_reach(1500, 40, 180.0, 0)
    assert abs(m - (1500 - 420) / (40 * 0.02 / 180 * 1e6) * 60) < 1e-9 and 14 < m < 15
    assert math.isinf(minutes_to_reach(1500, 40, 180.0, 1200))            # 十分に換気すれば届かない
    t, c = co2_series(40, 180.0, 600, 600)
    assert abs(c[-1] - steady_ppm(40, 600)) < 1                           # 時間がたてば落ち着く値に近づく
    mm = minutes_to_reach(1500, 40, 180.0, 600)
    assert abs(np.interp(mm, t, c) - 1500) < 1
    # ハウス：換気を増やすほど外気に近づき、閉め切ると補償点に近づく
    assert abs(house_volume() - 206.25) < 1e-9 and abs(house_area() - 82.5) < 1e-9
    assert house_steady_ppm(1.5, 0.0) == COMPENSATION_PPM
    assert house_steady_ppm(0.0, 1.0) == OUTDOOR_PPM
    assert COMPENSATION_PPM < house_steady_ppm(1.5, 1.0) < house_steady_ppm(1.5, 10.0) < OUTDOOR_PPM
    _, hc = house_series(1.5, 1.0, 600)
    assert abs(hc[-1] - house_steady_ppm(1.5, 1.0)) < 1
    # ③ 番地・表
    assert i2c_info(0x44) == dict(dec=68, hex="0x44", bin="1000100", usable=True)
    assert i2c_usable_count() == 112 and not i2c_info(0x03)["usable"]
    assert rows_per_day(10) == 144 and abs(days_until_full(7, 10) - 10_000_000 / 1008) < 1e-9
    d = synth_day()
    assert all(len(v) == 144 for v in d.values())
    day, night = (d["時刻"] > 10) & (d["時刻"] < 14), d["時刻"] < 4
    assert d["CO2"][day].mean() < d["CO2"][night].mean()                  # 日中は光合成で下がる
    s0, s1 = summary(d["CO2"]), summary(synth_day(outlier=True)["CO2"])
    assert s1["max"] == 5000 and s1["mean"] - s0["mean"] > 5 * abs(s1["median"] - s0["median"])   # 平均は動き、中央値はほぼ動かない
    assert summary(synth_day(missing=True)["CO2"])["missing"] == 6
    # ④ 警報・ポンプ
    assert abs(exceed_prob(1000, 1000, 50) - 0.5) < 1e-12
    assert abs(false_alarms_per_day(900, 1000, 50, 10, 1) - 144 * (1 - _phi(2))) < 1e-9
    assert false_alarms_per_day(900, 1000, 50, 10, 3) < 0.01 < false_alarms_per_day(900, 1000, 50, 10, 1)
    assert alert_delay_min(10, 3) == 20
    assert abs(bayes_alert(0.01, 0.95, 0.05) - 0.0095 / (0.0095 + 0.0495)) < 1e-12
    one, two = pump_sim(40, 40), pump_sim(35, 45)
    assert one["switches"] > 3 * two["switches"] > 0                      # しきい値1本は入切が何倍も多い（チャタリング）
    assert two["min"] > 25 and two["max"] < 55
    # ⑤ 費用
    total = bom_total([b[2] for b in BOM], [True] * len(BOM))
    assert BUDGET_RANGE[0] <= total <= BUDGET_RANGE[1]
    assert abs(power_cost_month(5.0, 31.0) - 111.6) < 1e-9
    assert filament_cost(40, 3000) == 120
    assert abs(cost_per_reading(28000, 6, 111.6, 5, 10) - (28000 + 669.6) / (5 * 144 * 180)) < 1e-12
    # ⑥ 秘密
    found = dict(risky_files(["main.py", "service_account.json", "token.json", "config.ini", "key.pem", "README.md",
                              "data/photo_token.pickle"]))
    assert set(found) == {"service_account.json", "token.json", "config.ini", "key.pem", "photo_token.pickle"}
    assert risky_files(["main.py", "README.md", "requirements.txt"]) == []
    assert security_score([True] * len(SECURITY_CHECKS)) == SECURITY_MAX == 14
    assert EXAM["ans"] in EXAM["opts"] and len(LESSONS) == 6 and len(ROLES) == 5


if __name__ == "__main__":
    _self_check()
    print("iot_core: 自己チェックOK")
