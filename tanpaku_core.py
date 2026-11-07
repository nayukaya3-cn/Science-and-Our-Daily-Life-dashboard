"""
科学と人間生活 第1部 生命の科学 1章A「タンパク質と遺伝子」① 体をつくるタンパク質 ─ 計算部品とデータ

画面は pages/ の各ページ。`python tanpaku_core.py` で自己チェック（assert）が走ります。
Streamlit に依存しない純粋な関数だけを置く（テストしやすく、授業のノートブックにもそのまま貼れる）。

出どころ
  - 教科書 p.14〜15：細胞の成分（水67％・タンパク質15％）、アミノ酸は20種類、
    タンパク質は消化されてアミノ酸として吸収され、遺伝子の情報にしたがって合成される
  - ヒトのインスリンA鎖・B鎖、ヘモグロビンβ鎖（先頭30残基）は実在の配列
  - 牛肉・魚・大豆・卵・ゼラチン・パン用小麦の配列は説明用の架空データ
    （ゼラチンがトリプトファンをほとんど含まない、小麦がリシンに乏しいのは実際の性質）
  - 遺伝暗号表は標準遺伝暗号。遺伝子は説明用に「各アミノ酸の代表コドン」で組み立てたもの
  - 教科書 p.18〜19（③ タンパク質の合成）：転写は DNA の片方の鎖（鋳型）に RNA の塩基が相補的に結合して進む
    （A→U, T→A, G→C, C→G：図10）。翻訳は mRNA の塩基3つで1つのアミノ酸を指定する。
    体のタンパク質は「牛肉由来のアミノ酸のとなりに豚肉由来のアミノ酸」が並ぶこともある
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


WHEAT = "🍞 パン用小麦（ミナミノカオリ・強力粉）"

FOODS = {
    "🥩 牛肉（ハンバーグ）": make_food_protein(120, "LKEAG", 1),
    "🐟 魚（焼き魚）": make_food_protein(100, "AGEDV", 2),
    "🫘 大豆（納豆）": make_food_protein(110, "ENRSQ", 3),
    "🥚 卵（卵焼き）": make_food_protein(90, "LSVAE", 4),
    "🍮 ゼラチン（トリプトファンを含まない）": make_food_protein(100, "GPGPGP", 5, exclude="W"),
    # パン用小麦のタンパク質（グルテン）はグルタミン(Q)・プロリン(P)が多く、リシン(K)が少ない（実際の性質）。
    # 実際にはリシンも少しは含む（小麦の「第一制限アミノ酸」）。差を見やすくするため、ここでは0にしている。
    WHEAT: make_food_protein(120, "QQQPPGLS", 6, exclude="K"),
}

# 小麦と組み合わせる食品（アミノ酸の補足効果を確かめる）
COMPLEMENT_PARTNERS = ["🫘 大豆（納豆）", "🥚 卵（卵焼き）", "🐟 魚（焼き魚）", "🍮 ゼラチン（トリプトファンを含まない）"]

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


def complement_table(target: str, times: int = 3) -> list[dict]:
    """アミノ酸の補足効果：小麦だけ／小麦＋○○ で、ヒトのタンパク質をつくれるか"""
    rows = []
    for partner in [None, *COMPLEMENT_PARTNERS]:
        menu = [WHEAT] + ([partner] if partner else [])
        short = lacking(target, absorb(menu, times))
        rows.append({
            "食べ合わせ": "小麦だけ（パンだけ）" if partner is None else f"小麦 ＋ {partner}",
            "合成できる？": "✅ できる" if not short else "❌ 材料不足",
            "足りないアミノ酸": "、".join(f"{AMINO[a][0]}（あと{n}個）" for a, n in short.items()) or "─",
        })
    return rows


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


def mutation_spectrum(protein: str) -> Counter:
    """1文字の書きかえを『全部』試す（総当たり）。開始・終止コドンを除く全位置×ほかの3塩基。
    戻り値：{"同義": 件数, "置換": 件数, "短縮": 件数}"""
    dna = make_gene(protein)
    counts: Counter = Counter({"同義": 0, "置換": 0, "短縮": 0})
    for pos in range(4, len(dna) - 2):
        for b in "ATGC":
            if b != dna[pos - 1]:
                counts[classify_mutation(protein, translate(mutate(dna, pos, b))[0])[0]] += 1
    return counts


# 転写の相補性（教科書 図10）
DNA_PAIR = {"A": "T", "T": "A", "G": "C", "C": "G"}      # DNA どうし
RNA_PAIR = {"A": "U", "T": "A", "G": "C", "C": "G"}      # 鋳型鎖の塩基 → 結合する RNA の塩基


def template_strand(dna: str) -> str:
    """遺伝子（mRNA と同じ並びの鎖）の相手側＝鋳型鎖"""
    return "".join(DNA_PAIR[b] for b in dna)


def transcribe_from_template(template: str) -> str:
    """鋳型鎖の塩基に RNA の塩基が相補的に結合して mRNA ができる（図10）"""
    return "".join(RNA_PAIR[b] for b in template)


def synthesize_with_origin(gene: str, menu: list[str], times: int = 1, seed: int = 0,
                           foods: dict[str, str] = FOODS) -> list[tuple[str, str]] | None:
    """合成したタンパク質の各アミノ酸が『どの食品から来たか』（教科書 p.19）。
    プールのアミノ酸に出どころの札をつけておき、遺伝子の順に取り出す。足りなければ None"""
    target, _ = translate(gene)
    stock: dict[str, list[str]] = {}
    for _ in range(times):
        for f in menu:
            for a in foods[f]:
                stock.setdefault(a, []).append(f)
    rng = random.Random(seed)
    for v in stock.values():
        rng.shuffle(v)
    if lacking(target, Counter({a: len(v) for a, v in stock.items()})):
        return None
    return [(a, stock[a].pop()) for a in target]


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
# 確認クイズ：p は認知プロトコル（P1 手順を回す／P2 資料を読む／P3 比較を疑う／P4 模型で考える／P5 知識で答える）
#   P3・P4 は「正解したか」ではなく「なぜ言えないか（なぜそう言えるか）」の説明でふり返る（報酬ハッキング対策）
# ─────────────────────────────────────────────
QUIZ: list[dict] = [
    dict(p="P2", q="哺乳類の細胞で、水を除いたとき最も多い成分は？",
         opts=["脂質", "タンパク質", "炭水化物", "DNAやRNA"], ans="タンパク質",
         exp="水67％を除くと、タンパク質（15％）が残りの約45％を占める。"),
    dict(p="P5", q="タンパク質を構成するアミノ酸は何種類？", opts=["4種類", "20種類", "64種類", "約10万種類"],
         ans="20種類", exp="4はDNAの塩基、64はコドン、約10万はヒトのタンパク質の種類。ひっかけに注意。"),
    dict(p="P5", q="食べたタンパク質は、最終的に何として吸収される？",
         opts=["タンパク質のまま", "アミノ酸", "DNA", "脂質"], ans="アミノ酸",
         exp="消化酵素で鎖が切られ、アミノ酸にまで分解されて小腸の柔毛から吸収される。"),
    dict(p="P5", q="タンパク質のアミノ酸配列を決めるのは？", opts=["食べた食品", "消化酵素", "遺伝子", "ホルモン"],
         ans="遺伝子", exp="遺伝子の情報にしたがってアミノ酸が並び、タンパク質が合成される。"),
    dict(p="P4", q="牛肉を食べても牛にならない理由として最も適切なのは？",
         opts=["牛のタンパク質は吸収されないから",
               "アミノ酸に分解され、自分の遺伝子にしたがって並べ直されるから",
               "牛肉にはタンパク質が含まれないから",
               "胃で牛の遺伝子が壊されるだけだから"],
         ans="アミノ酸に分解され、自分の遺伝子にしたがって並べ直されるから",
         exp="材料（アミノ酸）は食べ物から、並べ方（設計図）は自分の遺伝子から。"),
    dict(p="P2", q="小麦（パン）だけを食べ続けたとき、足りなくなりやすい必須アミノ酸は？",
         opts=["グルタミン", "プロリン", "リシン", "グリシン"], ans="リシン",
         exp="小麦のタンパク質はグルタミン・プロリンが多く、リシンが少ない。"
             "大豆や卵と組み合わせると補い合える（アミノ酸の補足効果）。"),
    dict(p="P1", q="20種類のアミノ酸を3個並べるとき、並べ方は何通り？", opts=["60通り", "400通り", "1140通り", "8000通り"],
         ans="8000通り", exp="同じものをくり返し使ってよいので 20×20×20＝8000。60は20×3、1140は『同じものを使わない組合せ』のひっかけ。"),
    dict(p="P3", q="「消化→吸収→合成」の対照実験で、ゼラチンだけが『材料不足』になった。"
                   "この結果から**言えない**ことは？",
         opts=["ゼラチンだけでは、このヒトのタンパク質の材料がそろわない",
               "足りないのはトリプトファンである",
               "ゼラチンは体に悪い食べ物である",
               "食べる回数とつくるタンパク質は、そろえて比べている"],
         ans="ゼラチンは体に悪い食べ物である",
         exp="比べたのは『あるタンパク質の材料がそろうか』だけで、体によい・悪いは測っていない（測っていない範囲）。"
             "ゼラチンもほかの食品と組み合わせれば材料になる。"),
    dict(p="P3", q="教科書の図1（細胞の成分の円グラフ）から**言えない**ことは？",
         opts=["細胞の質量の約3分の2は水である",
               "水を除くと、タンパク質が最も多い",
               "タンパク質を多く食べるほど、細胞のタンパク質の割合が増える",
               "水は細胞をつくる成分の中で最も多い"],
         ans="タンパク質を多く食べるほど、細胞のタンパク質の割合が増える",
         exp="円グラフは『ある細胞の成分の割合』を1回示しただけで、食べる量を変えた比較をしていない。"
             "比較がないので、食事と割合の因果関係は言えない。"),
    # ── 2章B 微生物と人間の食生活（p.44〜49）：同じ型を別の題材で使う ──
    dict(p="P3", q="パスツールの実験（白鳥の首フラスコ）で、首を折ったときだけ液が腐敗した。"
                   "この比較で『変えた条件』は？",
         opts=["液に養分をふくむかどうか", "液を煮沸したかどうか",
               "微生物が液まで届くかどうか", "空気がフラスコに入るかどうか"],
         ans="微生物が液まで届くかどうか",
         exp="どちらも煮沸済みで、空気はどちらにも入る。変えたのは『ほこりとともに微生物が入れるか』だけ。"
             "だから『微生物は外から来る（自然発生しない）』と言える。"),
    dict(p="P2", q="実験2（酵母と温度）の結果例で、0〜26分に発生した気体は 20℃ で 3.8 mL、30℃ で 10.9 mL、80℃ で 0 mL。"
                   "この結果から**言える**ことは？",
         opts=["温度が高いほど発酵は速い", "20℃ より 30℃ のほうが発酵が速い",
               "酵母が最もよく働くのは 30℃ である", "80℃ では酵母が気体を吸収している"],
         ans="20℃ より 30℃ のほうが発酵が速い",
         exp="80℃ で 0 なので『高いほど速い』は言えない。30〜80℃ の間を測っていないので『最適は30℃』とも言えない。"),
    dict(p="P5", q="しょう油・みそが『うま味』と『アミノ酸の供給源』になる理由として最も適切なのは？",
         opts=["微生物がダイズのタンパク質をアミノ酸に分解するから", "食塩がアミノ酸に変わるから",
               "コムギのデンプンがタンパク質に変わるから", "酵母がアミノ酸を光合成でつくるから"],
         ans="微生物がダイズのタンパク質をアミノ酸に分解するから",
         exp="コウジカビ・酵母・乳酸菌がはたらき、ダイズのタンパク質が分解されてアミノ酸が多量に生じる。"
             "1章Aの『タンパク質→アミノ酸』と同じ分解。"),
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
    assert all(q["ans"] in q["opts"] for q in QUIZ) and {q["p"] for q in QUIZ} == {"P1", "P2", "P3", "P4", "P5"}
    assert sum(mutation_spectrum(HUMAN_PROTEINS["インスリンB鎖（血糖濃度を調節するホルモン）"]).values()) == 30 * 3 * 3
    dna = make_gene(HUMAN_PROTEINS["インスリンA鎖（血糖濃度を調節するホルモン）"])
    assert transcribe_from_template(template_strand(dna)) == transcribe(dna)   # 図10の相補性で同じmRNA
    two = synthesize_with_origin(ins, ["🥩 牛肉（ハンバーグ）", "🫘 大豆（納豆）"], 3)
    assert "".join(a for a, _ in two) == translate(ins)[0] and len({f for _, f in two}) == 2
    assert "K" not in FOODS[WHEAT] and FOODS[WHEAT].count("Q") > FOODS[WHEAT].count("A")
    ct = complement_table(HUMAN_PROTEINS["ヘモグロビンβ鎖・先頭30個（酸素を運ぶ）"])
    assert ct[0]["合成できる？"].startswith("❌") and "リシン" in ct[0]["足りないアミノ酸"]  # 小麦だけ
    assert ct[1]["合成できる？"].startswith("✅")                                        # 小麦＋大豆
    assert round(bits(1), 2) == 4.32


if __name__ == "__main__":
    _self_check()
    print("tanpaku_core: 自己チェックOK")
