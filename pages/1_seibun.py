"""🧪 体は何でできている？（教科書 図1 哺乳類の細胞をつくる成分）"""
import pandas as pd
import plotly.express as px
import streamlit as st

import tanpaku_core as tc
import ui

ui.hero("教科書 p.14 図1", "🧪 体は何でできている？",
        "哺乳類の細胞をつくる成分を、質量の割合（％）で見てみよう。")
ui.hint("体の重さの約3分の2は水。では、水を取りのぞいたら何が一番多い？ スイッチを押して確かめよう。")

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

with st.expander("🔎 読解プロトコル（理科基礎・情報Ⅰ第4問と共通）"):
    st.markdown("① **何と何の割合？** 細胞をつくる成分ごとの質量　② **単位は？** 質量％  \n"
                "③ **何を変えた？** 水を含める／除く　④ **言えること／言えないこと** "
                "水を除くとタンパク質が最多。ただし水以外の数値の一部は図からの目安で、正確な値ではない。")
