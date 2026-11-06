"""🔤 アミノ酸は20種類"""
import pandas as pd
import streamlit as st

import tanpaku_core as tc
import ui

ui.hero("教科書 p.15", "🔤 タンパク質を構成するアミノ酸は20種類",
        "アミノ酸はタンパク質の『部品』。20種類をアルファベット1文字で表すのが世界共通のルール。")
ui.hint("★は体内で十分につくれず、食べ物からとる必要がある『必須アミノ酸』（成人9種）。"
        "あとの「消化→合成」のページで、これが足りないとどうなるかを確かめるよ。")

ui.reading_card(
    axis="アミノ酸の記号と名前（必須かどうか）", unit="種類（個数ではない）",
    control="表は同じ。変えるのは『必須だけ表示する／しない』",
    can="アミノ酸は20種類で、そのうち成人の必須アミノ酸は9種類",
    cannot="必須でないアミノ酸は体に要らない（体内でつくれるだけで、どれも材料として使う）",
    protocols=["P5", "P2"], material="アミノ酸20種類の表")

only_essential = st.toggle("必須アミノ酸だけ表示", value=False)
adf = pd.DataFrame([{"記号": k, "名前": v[0], "必須アミノ酸": "★" if v[1] else ""}
                    for k, v in tc.AMINO.items() if (v[1] or not only_essential)])

c1, c2 = st.columns([2, 3])
with c1:
    st.dataframe(adf, hide_index=True, width="stretch", height=560)
with c2:
    st.markdown("**部品（色つきの丸）**　※ どのページでも同じ色＝同じアミノ酸")
    ui.chain("".join(adf["記号"]), size=34, gap=4)
    st.metric("表示中のアミノ酸", f"{len(adf)} 種")
    st.caption("4（DNAの塩基）・20（アミノ酸）・64（コドン）・約10万（ヒトのタンパク質）は"
               "共通テストで取り違えやすい数字。")
