"""計算部品のテスト：`pytest -q`"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tanpaku_core as tc  # noqa: E402

INSULIN_B = "インスリンB鎖（血糖濃度を調節するホルモン）"
HB = "ヘモグロビンβ鎖・先頭30個（酸素を運ぶ）"
GELATIN = "🍮 ゼラチン（トリプトファンを含まない）"


def test_self_check():
    tc._self_check()


def test_water_removed_protein_is_main():
    dry = tc.ratio_without(tc.CELL)
    assert max(dry, key=dry.get) == "タンパク質"


def test_gene_round_trip():
    for seq in tc.HUMAN_PROTEINS.values():
        assert tc.translate(tc.make_gene(seq))[0] == seq


def test_any_food_makes_same_human_protein():
    gene = tc.make_gene(tc.HUMAN_PROTEINS[INSULIN_B])
    made = {tc.synthesize(gene, tc.absorb([f], 3))[0] for f in tc.FOODS}
    assert made - {None} == {tc.HUMAN_PROTEINS[INSULIN_B]}


def test_food_sequence_does_not_survive():
    gene = tc.make_gene(tc.HUMAN_PROTEINS[INSULIN_B])
    beef = tc.FOODS["🥩 牛肉（ハンバーグ）"]
    protein, _ = tc.synthesize(gene, tc.absorb(["🥩 牛肉（ハンバーグ）"], 3))
    assert beef not in protein and protein != beef


def test_gelatin_lacks_tryptophan():
    gene = tc.make_gene(tc.HUMAN_PROTEINS[HB])
    protein, short = tc.synthesize(gene, tc.absorb([GELATIN], 10))
    assert protein is None and short == {"W": 1}
    protein, short = tc.synthesize(gene, tc.absorb([GELATIN, "🥚 卵（卵焼き）"], 10))
    assert protein == tc.HUMAN_PROTEINS[HB]


def test_mutation_kinds():
    seq = tc.HUMAN_PROTEINS[INSULIN_B]
    dna = tc.make_gene(seq)
    # 1個目のアミノ酸 F（TTT）の3文字目を C に → TTC も F（同義）
    assert tc.classify_mutation(seq, tc.translate(tc.mutate(dna, 6, "C"))[0])[0] == "同義"
    # 1文字目を G に → GTT は V（置換）
    kind, diff = tc.classify_mutation(seq, tc.translate(tc.mutate(dna, 4, "G"))[0])
    assert kind == "置換" and diff == [1]
    # Q（CAA）の1文字目を T に → TAA（終止）で途中で止まる（短縮）
    q_pos = 3 + seq.index("Q") * 3 + 1
    assert tc.classify_mutation(seq, tc.translate(tc.mutate(dna, q_pos, "T"))[0])[0] == "短縮"


def test_information_amount():
    assert round(tc.bits(1), 2) == 4.32
    assert round(tc.combos_log10(4), 2) == round(4 * 1.30103, 2)
