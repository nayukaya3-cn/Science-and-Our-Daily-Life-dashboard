"""🧪 体は何でできている？（教科書 図1 哺乳類の細胞をつくる成分）"""
import pandas as pd
import plotly.express as px
import streamlit as st

import tanpaku_core as tc
import ui

ui.hero("教科書 p.14 図1", "🧪 体は何でできている？",
        "哺乳類の細胞をつくる成分を、質量の割合（％）で見てみよう。")
ui.hint("体の重さの約3分の2は水。では、水を取りのぞいたら何が一番多い？ スイッチを押す前に、まず予想しよう。")

ui.reading_card(
    axis="細胞をつくる成分ごとの質量（どの成分が、全体のどれだけか）",
    unit="質量％（体積や個数ではない）",
    control="成分の値はそのまま。変えるのは『水を含める／除く』だけ",
    can="水を除くとタンパク質が最多（約45％）",
    cannot="水以外の数値の正確な値（一部は図から読み取った目安）。食事で割合が変わるかどうか（比べていない）",
    protocols=["P2", "P3"], material="教科書 図1（哺乳類の細胞をつくる成分）")

ui.predict("seibun_dry", "**水を除くと、タンパク質は残りの何％になる？**（教科書の値：水67％・タンパク質15％）",
           tc.ratio_without(tc.CELL)["タンパク質"], "％", protocol="P1", value=15.0)

remove_water = st.toggle("水を除いて比べる", value=False)
data = {k: v for k, v in tc.CELL.items() if not (remove_water and k == "水")}
total = sum(data.values())
df = pd.DataFrame({"成分": list(data), "質量％": list(data.values())})
df["割合（表示中の合計を100％）"] = (df["質量％"] / total * 100).round(1)
df["出典"] = ["教科書の値" if k in tc.TEXTBOOK_VALUES else "図からの目安" for k in df["成分"]]

c1, c2 = st.columns([3, 2])
with c1:
    fig = px.pie(df, names="成分", values="質量％", hole=0.35, color="成分",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textinfo="label+percent", sort=False, direction="clockwise")
    fig.update_layout(height=430, margin=dict(t=10, b=10))
    st.plotly_chart(fig, width="stretch")
with c2:
    top = df.loc[df["質量％"].idxmax()]
    st.metric("いちばん多い成分", top["成分"], f"{top['割合（表示中の合計を100％）']}%")
    st.dataframe(df, hide_index=True, width="stretch")

if remove_water:
    st.success("水を除くと、**タンパク質が主成分**（約45％）。"
               "教科書の「水を除くと、タンパク質が主成分である」を数字で確認できた。")
    st.caption("計算：15 ÷（100 − 67）× 100 ≒ 45％。割合の『もと（分母）』が変わると、同じ15％でも意味が変わる。"
               "情報Ⅰ第4問の『何に対する割合か』と同じ型。")
