"""
科学と人間生活 第1部 生命の科学 1章A「タンパク質と遺伝子」① 体をつくるタンパク質 ─ 計算部品とデータ

画面は pages/ の各ページ。`python tanpaku_core.py` で自己チェック（assert）が走ります。
Streamlit に依存しない純粋な関数だけを置く（テストしやすく、授業のノートブックにもそのまま貼れる）。

出どころ
  - 教科書 p.14〜15：細胞の成分（水67％・タンパク質15％）、アミノ酸は20種類、
    タンパク質は消化されてアミノ酸として吸収され、遺伝子の情報にしたがって合成される
  - ヒトのインスリンA鎖・B鎖、ヘモグロビンβ鎖（先頭30残基）は実在の配列
  - 牛肉・魚・大豆・卵・ゼラチンの配列は説明用の架空データ
    （ゼラチンがトリプトファンをほとんど含まないのは実際の性質）
  - 遺伝暗号表は標準遺伝暗号。遺伝子は説明用に「各アミノ酸の代表コドン」で組み立てたもの
"""
from __future__ import annotations

import math
import random
from collections import Counter

# ─────────────────────────────────────────────
# 図1 哺乳類の細胞をつくる成分（質量％）
# ─────────────────────────────────────────────
CELL = {
    "水": 67.0, "タンパク質": 15.0,                      # 教科書の値
    "脂質": 12.0, "無機塩類": 2.5, "炭水化物": 1.5,
    "DNAやRNA": 1.5, "その他の有機物": 0.5,              # 図から読み取った目安
}
TEXTBOOK_VALUES = {"水", "タンパク質"}


def ratio_without(components: dict[str, float], exclude: str = "水") -> dict[str, float]:
    """ある成分を除いたときの割合（％）。教科書「水を除くと、タンパク質が主成分」の確認用"""
    rest = {k: v for k, v in components.items() if k != exclude}
    total = sum(rest.values())
    return {k: v / total * 100 for k, v in rest.items()}


# ─────────────────────────────────────────────
# アミノ酸 20 種（1文字記号: (名前, 成人の必須アミノ酸か)）
# ─────────────────────────────────────────────
AMINO = {
    "G": ("グリシン", False), "A": ("アラニン", False), "V": ("バリン", True),
    "L": ("ロイシン", True), "I": ("イソロイシン", True), "P": ("プロリン", False),
    "F": ("フェニルアラニン", True), "W": ("トリプトファン", True),
    "M": ("メチオニン", True), "S": ("セリン", False), "T": ("トレオニン", True),
    "C": ("システイン", False), "Y": ("チロシン", False), "N": ("アスパラギン", False),
    "Q": ("グルタミン", False), "D": ("アスパラギン酸", False),
    "E": ("グルタミン酸", False), "K": ("リシン", True), "R": ("アルギニン", False),
    "H": ("ヒスチジン", True),
}
# 色はアミノ酸ごとに固定（どのページでも同じ色＝同じアミノ酸）
_PALETTE = ["#FD3216", "#00FE35", "#6A76FC", "#FED4C4", "#FE00CE", "#0DF9FF", "#F6F926",
            "#FF9616", "#479B55", "#EEA6FB", "#DC587D", "#D626FF", "#6E899C", "#00B5F7",
            "#B68E00", "#C9FBE5", "#FF0092", "#22FFA7", "#E3EE9E", "#86CE00"]
COLOR = dict(zip(AMINO, _PALETTE))

# ─────────────────────────────────────────────
# タンパク質
# ─────────────────────────────────────────────
HUMAN_PROTEINS = {
    "インスリンA鎖（血糖濃度を調節するホルモン）": "GIVEQCCTSICSLYQLENYCN",
    "インスリンB鎖（血糖濃度を調節するホルモン）": "FVNQHLCGSHLVEALYLVCGERGFFYTPKT",
    "ヘモグロビンβ鎖・先頭30個（酸素を運ぶ）": "VHLTPEEKSAVTALWGKVNVDEVGGEALGR",
    "コラーゲン・説明用断片（皮膚や軟骨の構造）": "GPPGPAGPKGEPGPRGPQGPPGEKGAP",
}


def make_food_protein(length: int, bias: str, seed: int, exclude: str = "") -> str:
    """食品ごとに『種類・数・並び順』が違う架空のタンパク質をつくる（乱数を固定して再現可能）"""
    rng = random.Random(seed)
    letters = [a for a in AMINO if a not in exclude]
    weights = [3 if a in bias else 1 for a in letters]
    return "".join(rng.choices(letters, weights=weights, k=length))


FOODS = {
    "🥩 牛肉（ハンバーグ）": make_food_protein(120, "LKEAG", 1),
    "🐟 魚（焼き魚）": make_food_protein(100, "AGEDV", 2),
    "🫘 大豆（納豆）": make_food_protein(110, "ENRSQ", 3),
    "🥚 卵（卵焼き）": make_food_protein(90, "LSVAE", 4),
    "🍮 ゼラチン（トリプトファンを含まない）": make_food_protein(100, "GPGPGP", 5, exclude="W"),
}

# ─────────────────────────────────────────────
# 消化・吸収・合成
# ─────────────────────────────────────────────
def digest(protein: str, seed: int = 0) -> list[str]:
    """消化：鎖を切ってバラバラにする。並び順はシャッフルされ、意味を失う"""
    pieces = list(protein)
    random.Random(seed).shuffle(pieces)
    return pieces


def absorb(menu: list[str], times: int = 1, foods: dict[str, str] = FOODS) -> Counter:
    """吸収：食べたもののアミノ酸を『たくわえ（プール）』に入れる。残るのは種類ごとの個数だけ"""
    pool: Counter = Counter()
    for _ in range(times):
        for f in menu:
            pool.update(foods[f])
    return pool


def lacking(target: str, pool: Counter) -> dict[str, int]:
    """合成に足りないアミノ酸と、あと何個必要か"""
    need = Counter(target)
    return {a: n - pool[a] for a, n in need.items() if pool[a] < n}


# ─────────────────────────────────────────────
# 遺伝子 → タンパク質
# ─────────────────────────────────────────────
BASES = "UCAG"
_CODE = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
CODON = {a + b + c: _CODE[16 * i + 4 * j + k]
         for i, a in enumerate(BASES) for j, b in enumerate(BASES) for k, c in enumerate(BASES)}
_FIRST_CODON: dict[str, str] = {}
for _c, _a in CODON.items():
    _FIRST_CODON.setdefault(_a, _c)


def make_gene(protein: str) -> str:
    """説明用：アミノ酸配列 → 遺伝子(DNA)。開始コドン＋各アミノ酸の代表コドン＋終止コドン"""
    return ("AUG" + "".join(_FIRST_CODON[a] for a in protein) + "UAA").replace("U", "T")


def transcribe(dna: str) -> str:
    """転写：DNA → mRNA（T を U に置きかえる）"""
    return dna.upper().replace("T", "U")


def translate(dna: str) -> tuple[str, list[tuple[str, str]]]:
    """翻訳：AUG から3文字ずつ読み、終止コドンで止める。（タンパク質, [(コドン, アミノ酸)]）"""
    mrna = transcribe(dna)
    start = mrna.find("AUG")
    if start < 0:
        return "", []
    out, codons = [], []
    for i in range(start + 3, len(mrna) - 2, 3):
        c = mrna[i:i + 3]
        aa = CODON.get(c, "?")
        codons.append((c, aa))
        if aa == "*":
            break
        out.append(aa)
    return "".join(out), codons


def synthesize(gene: str, pool: Counter) -> tuple[str | None, dict[str, int]]:
    """合成：遺伝子どおりの順に、プールから材料を取り出して並べる。足りなければ None"""
    target, _ = translate(gene)
    short = lacking(target, pool)
    return (None, short) if short else (target, {})


def mutate(dna: str, pos: int, base: str) -> str:
    """突然変異：pos 番目（1始まり）の塩基を base に置きかえる"""
    return dna[:pos - 1] + base + dna[pos:]


def classify_mutation(original: str, mutated: str) -> tuple[str, list[int]]:
    """変異の結果を3通りに分ける：同義（変わらない）／置換（1個変わる）／短縮（途中で止まる）"""
    if mutated == original:
        return "同義", []
    if len(mutated) < len(original):
        return "短縮", []
    return "置換", [i + 1 for i, (a, b) in enumerate(zip(mutated, original)) if a != b]


# ─────────────────────────────────────────────
# 情報Ⅰ：場合の数と情報量
# ─────────────────────────────────────────────
def combos_log10(n: int, kinds: int = 20) -> float:
    """kinds 種類を n 個並べる場合の数 kinds**n の常用対数"""
    return n * math.log10(kinds)


def bits(n: int, kinds: int = 20) -> float:
    """kinds 種類の記号を n 個並べたときの情報量（ビット）"""
    return n * math.log2(kinds)


# ─────────────────────────────────────────────
# 確認クイズ（問題文, 選択肢, 正解, 解説）
# ─────────────────────────────────────────────
QUIZ = [
    ("哺乳類の細胞で、水を除いたとき最も多い成分は？",
     ["脂質", "タンパク質", "炭水化物", "DNAやRNA"], "タンパク質",
     "水67％を除くと、タンパク質（15％）が残りの約45％を占める。"),
    ("タンパク質を構成するアミノ酸は何種類？", ["4種類", "20種類", "64種類", "約10万種類"], "20種類",
     "4はDNAの塩基、64はコドン、約10万はヒトのタンパク質の種類。ひっかけに注意。"),
    ("食べたタンパク質は、最終的に何として吸収される？",
     ["タンパク質のまま", "アミノ酸", "DNA", "脂質"], "アミノ酸",
     "消化酵素で鎖が切られ、アミノ酸にまで分解されて小腸の柔毛から吸収される。"),
    ("タンパク質のアミノ酸配列を決めるのは？", ["食べた食品", "消化酵素", "遺伝子", "ホルモン"], "遺伝子",
     "遺伝子の情報にしたがってアミノ酸が並び、タンパク質が合成される。"),
    ("牛肉を食べても牛にならない理由として最も適切なのは？",
     ["牛のタンパク質は吸収されないから",
      "アミノ酸に分解され、自分の遺伝子にしたがって並べ直されるから",
      "牛肉にはタンパク質が含まれないから",
      "胃で牛の遺伝子が壊されるだけだから"],
     "アミノ酸に分解され、自分の遺伝子にしたがって並べ直されるから",
     "材料（アミノ酸）は食べ物から、並べ方（設計図）は自分の遺伝子から。"),
]


def _self_check() -> None:
    assert abs(sum(CELL.values()) - 100) < 1e-9
    dry = ratio_without(CELL)
    assert max(dry, key=dry.get) == "タンパク質" and 45 < dry["タンパク質"] < 46
    assert len(AMINO) == 20 and sum(v[1] for v in AMINO.values()) == 9
    assert len(CODON) == 64 and list(CODON.values()).count("*") == 3
    for seq in HUMAN_PROTEINS.values():                      # 遺伝子から元の配列に戻る
        assert translate(make_gene(seq))[0] == seq
    beef = FOODS["🥩 牛肉（ハンバーグ）"]
    assert sorted(digest(beef, 1)) == sorted(beef)            # 消化しても部品の数は同じ
    assert digest(beef, 1) != list(beef)                      # 並び順は変わる
    ins = make_gene(HUMAN_PROTEINS["インスリンB鎖（血糖濃度を調節するホルモン）"])
    made = {synthesize(ins, absorb([f], 3))[0] for f in FOODS}
    assert len(made - {None}) == 1                            # 何を食べても同じヒトの配列
    hb = make_gene(HUMAN_PROTEINS["ヘモグロビンβ鎖・先頭30個（酸素を運ぶ）"])
    assert synthesize(hb, absorb(["🍮 ゼラチン（トリプトファンを含まない）"], 10))[1] == {"W": 1}
    assert "W" not in FOODS["🍮 ゼラチン（トリプトファンを含まない）"]
    assert all(q[2] in q[1] for q in QUIZ)
    assert round(bits(1), 2) == 4.32


if __name__ == "__main__":
    _self_check()
    print("tanpaku_core: 自己チェックOK")
