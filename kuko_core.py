"""
「科学と人間生活」×広島空港：霧が多いのに着陸できるのはなぜか（50分×4コマ）─ 計算部品とデータ

出どころ：簡易カリキュラム「科学と人間生活 × 広島空港」

ねらい（高いところから見た位置づけ）
  1つの問い「広島空港は霧が多い。それでも飛行機が着陸できるのはなぜか」から、4領域を横断する。
    第1コマ 宇宙や地球の科学：なぜ霧ができるのか（露点・飽和水蒸気量）
    第2コマ 光や熱の科学　　：霧の中でも届くものは何か（波長）
    第3コマ 物質の科学　　　：飛行機は何でできているか（密度・複合材料）
    第4コマ まとめ・情報Ⅰ　 ：着陸装置が使えなかった期間の欠航を、読解カードで読む

データの種類
  - 飽和水蒸気圧・露点：気象で広く使われる近似式（マグヌスの式）。地学基礎の「飽和水蒸気量」と同じ内容
  - 雲のできはじめる高さ：(気温−露点)×約125 m という**目安の式**
  - 欠航の数字：2015年の報道による（単元案の出典）。現在の運用や便数は変わっているので、最新の資料で確かめてから使う
  - 密度：一般的な目安の値

Streamlit に依存しない。`python kuko_core.py` で自己チェック。
"""
from __future__ import annotations

import math

AIRPORT_ELEVATION_M = 331      # 広島空港（三原市）の標高
RVR_MIN_M = 100                # 最も精度の高い区分での、着陸に必要な滑走路の見通し（単元案より）

# ─────────────────────────────────────────────
# 第1コマ：なぜ霧ができるのか（露点）
# ─────────────────────────────────────────────
_A, _B = 17.62, 243.12         # マグヌスの式の定数（水面上、およそ −45〜60℃ で使える）


def sat_pressure(temp_c: float) -> float:
    """飽和水蒸気圧（hPa）"""
    return 6.112 * math.exp(_A * temp_c / (_B + temp_c))


def sat_amount(temp_c: float) -> float:
    """飽和水蒸気量（g/m³）＝ 空気1 m³ が抱えられる水蒸気の上限。温度が下がると減る"""
    return 216.7 * sat_pressure(temp_c) / (temp_c + 273.15)


def vapor_amount(temp_c: float, rh: float) -> float:
    """いま空気1 m³ にふくまれている水蒸気の量（g/m³）。rh＝湿度（％）"""
    return sat_amount(temp_c) * rh / 100.0


def dew_point(temp_c: float, rh: float) -> float:
    """露点（℃）＝ 空気が水を抱えきれなくなって、水滴を出し始める温度"""
    if not 0 < rh <= 100:
        raise ValueError("湿度は 0 より大きく 100 以下")
    g = math.log(rh / 100.0) + _A * temp_c / (_B + temp_c)
    return _B * g / (_A - g)


def humidity_after_cooling(temp_c: float, rh: float, new_temp_c: float) -> float:
    """水蒸気はそのままで、気温だけ new_temp_c に下がったときの湿度（％、上限100）。
    水蒸気の圧力（水蒸気圧）が変わらないとして計算する"""
    return min(100.0, rh * sat_pressure(temp_c) / sat_pressure(new_temp_c))


def fog_water(temp_c: float, rh: float, new_temp_c: float) -> float:
    """冷えて抱えきれなくなり、水滴（霧）になった分（g/m³）"""
    extra = sat_pressure(temp_c) * rh / 100.0 - sat_pressure(new_temp_c)
    return max(0.0, 216.7 * extra / (new_temp_c + 273.15))


def condensation_height(temp_c: float, rh: float) -> float:
    """空気が斜面を上るとき、水滴ができ始める高さの目安（m）＝ (気温−露点)×約125。
    上る空気は100 mにつき約1℃冷え、露点も約0.2℃下がる、という目安から"""
    return max(0.0, 125.0 * (temp_c - dew_point(temp_c, rh)))


# ─────────────────────────────────────────────
# 第2コマ：霧の中でも届くものは何か（波長）
# ─────────────────────────────────────────────
LIGHT_SPEED = 3.0e8            # m/s
FOG_DROPLET_M = 1.0e-5         # 霧の粒の大きさの目安：約0.01 mm（10 µm）。数 µm〜数十 µm の幅がある


def wavelength(freq_hz: float) -> float:
    """波長（m）＝ 速さ ÷ 振動数。λ ＝ c / f"""
    if freq_hz <= 0:
        raise ValueError("振動数は正の数")
    return LIGHT_SPEED / freq_hz


#   (名前, 波長 m（代表値）, 使われ方, 霧の中で)
WAVES: list[tuple[str, float, str, str]] = [
    ("可視光（進入灯・懐中電灯）", 5.5e-7, "目で見る光。滑走路手前の進入灯", "粒より短い → 粒にぶつかって散らばる（散乱）"),
    ("赤外線", 1.0e-5, "熱を伝える光。リモコン、放射", "粒と同じくらい → 散らばり、吸収もされる"),
    ("着陸装置の電波（高さの道しるべ、約330 MHz）", wavelength(330e6), "計器着陸装置（ILS）の降下角の案内", "粒よりはるかに長い → ほとんど気にせず通り抜ける"),
    ("着陸装置の電波（左右の道しるべ、約110 MHz）", wavelength(110e6), "計器着陸装置（ILS）の左右の案内", "粒よりはるかに長い → ほとんど気にせず通り抜ける"),
]


def size_ratio(wave_m: float, droplet_m: float = FOG_DROPLET_M) -> float:
    """波長が霧の粒の何倍か"""
    return wave_m / droplet_m


# ─────────────────────────────────────────────
# 第3コマ：飛行機は何でできているか（密度）
# ─────────────────────────────────────────────
DENSITY = {"鉄": 7.9, "アルミニウム": 2.7, "CFRP（炭素繊維強化プラスチック）": 1.55, "水": 1.0}   # g/cm³（目安）


def density(mass_g: float, v_before_ml: float, v_after_ml: float) -> float:
    """密度（g/cm³）＝ 質量 ÷ 体積。体積は、メスシリンダーの水が増えた分（1 mL ＝ 1 cm³）"""
    v = v_after_ml - v_before_ml
    if v <= 0:
        raise ValueError("水面は上がっているはず（入れた後 ＞ 入れる前）")
    return mass_g / v


def nearest_material(rho: float) -> str:
    """測った密度にいちばん近い材料（水は除く）"""
    return min((k for k in DENSITY if k != "水"), key=lambda k: abs(DENSITY[k] - rho))


def mass_if_made_of(volume_cm3: float) -> dict[str, float]:
    """同じ体積の部品を、それぞれの材料でつくったときの質量（g）"""
    return {k: round(v * volume_cm3, 1) for k, v in DENSITY.items() if k != "水"}


# ─────────────────────────────────────────────
# 第4コマ：着陸装置が使えなかった期間（2015年5月6日〜8月26日の報道の数字）
# ─────────────────────────────────────────────
FLIGHTS_TOTAL = 3255           # 発着した便
CANCELLED = 59                 # 欠航（台風など、ほかの原因も含む）
CANCELLED_BY_DEVICE = 14       # もう一段精度の高い区分なら欠航せずに済んだ、と報じられた便


def flight_breakdown() -> dict:
    other = CANCELLED - CANCELLED_BY_DEVICE
    return {
        "運航できた便": FLIGHTS_TOTAL - CANCELLED,
        "欠航（装置の区分が原因と言える）": CANCELLED_BY_DEVICE,
        "欠航（それ以外・台風など）": other,
        "欠航の割合（％）": round(100 * CANCELLED / FLIGHTS_TOTAL, 2),
        "装置が原因と言える欠航の割合（％）": round(100 * CANCELLED_BY_DEVICE / FLIGHTS_TOTAL, 2),
        "欠航のうち装置が原因と言える割合（％）": round(100 * CANCELLED_BY_DEVICE / CANCELLED, 1),
    }


# 単元の構成（50分×4コマ）：(コマ, 領域, テーマ, 空港の題材, 主な活動, プロトコル)
LESSONS: list[tuple[int, str, str, str, str, str]] = [
    (1, "宇宙や地球の科学", "なぜ霧ができるのか", "山間の高台、夜の冷え込み", "ペットボトルで雲をつくる、露点を測る", "P4・P1"),
    (2, "光や熱の科学", "霧の中でも届くものは何か", "計器着陸装置（ILS）の電波", "霧の中で可視光と赤外線・電波を比べる", "P3・P4"),
    (3, "物質の科学", "飛行機は何でできているか", "機体のアルミ合金と炭素繊維強化プラスチック", "金属と複合材料の密度を比べる", "P1・P2"),
    (4, "まとめ（情報Ⅰと連携）", "着陸装置が使えなかった5か月", "装置が一時使えなかった期間の欠航", "報道のデータを読解カードで読む", "P2・P3"),
]

NOTES = (
    "2015年の事故は、航空会社名を出さず「滑走路からそれた事故」として扱う。事故そのものではなく、着陸装置の役割を考える材料にする",
    "欠航の数字は2015年の報道による。空港の現在の運用や便数は変わっているので、最新の資料で確かめてから使う",
    "空港見学を組み合わせる場合は、空港の運営会社に受け入れを相談する",
    "第2コマの演示でレーザーポインターは使わない（目に入ると危険）",
)


def _self_check() -> None:
    assert abs(sat_amount(20) - 17.3) < 0.15 and abs(sat_amount(10) - 9.4) < 0.15 and abs(sat_amount(30) - 30.4) < 0.3     # 地学基礎の表の値
    assert abs(dew_point(20, 100) - 20) < 1e-9
    td = dew_point(20, 60)
    assert 11.5 < td < 12.5                                                          # 20℃・60％ → 約12℃
    assert abs(humidity_after_cooling(20, 60, td) - 100) < 1e-6                      # 露点まで冷えるとちょうど100％
    assert fog_water(20, 60, td + 1) == 0 and fog_water(20, 60, td - 3) > 0
    assert 950 < condensation_height(20, 60) < 1050
    assert condensation_height(15, 85) < AIRPORT_ELEVATION_M < condensation_height(15, 60)   # 湿った日は空港の高さで霧
    assert 0.8 < wavelength(330e6) < 1.0 and 2.6 < wavelength(110e6) < 2.8           # 波長は1 m前後
    assert size_ratio(WAVES[0][1]) < 1 < size_ratio(WAVES[2][1])                     # 可視光は粒より短く、電波は長い
    assert round(density(27.0, 50.0, 60.0), 1) == 2.7 and nearest_material(2.6) == "アルミニウム"
    assert nearest_material(1.6).startswith("CFRP")
    b = flight_breakdown()
    assert b["装置が原因と言える欠航の割合（％）"] == 0.43 and b["欠航のうち装置が原因と言える割合（％）"] == 23.7
    assert b["運航できた便"] + CANCELLED == FLIGHTS_TOTAL and b["欠航（それ以外・台風など）"] == 45
    assert len(LESSONS) == 4


if __name__ == "__main__":
    _self_check()
    print("kuko_core: 自己チェックOK")
