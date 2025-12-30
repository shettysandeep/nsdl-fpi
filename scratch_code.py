import pandas as pd
import pyarrow.parquet as pq
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


df_table = pq.read_table("fpi_data/fpi_2024_2025.parquet")
df = df_table.to_pandas()
df = df[(df["TR_TYPE"] == 1) | (df["TR_TYPE"] == 4)]
df_wide = (
    df.pivot_table(  # type: ignore
        index=["TR_DATE", "month", "year", "company_name"],
        columns="TR_TYPE",
        values="VALUE",
        aggfunc="sum",
        observed=True,
    )
    .rename(columns={1: "Buy", 4: "Sell"})
    .reset_index()
)
cols_to_fill = ["Buy", "Sell"]
df_wide[cols_to_fill] = df_wide[cols_to_fill].fillna(0)
df_wide["net_crores"] = np.round((df_wide["Buy"] - df_wide["Sell"]) / 10000000, 2)
f_df = (
    df_wide.groupby(["company_name", "month", "year"])
    .sum("net_crores")
    .sort_values(by="net_crores", ascending=True)
    .reset_index()
)


# print("~~~~top 5~~~~~~\n\n")
# print(
#    f_df[(f_df["month"] == "jan") & (f_df["year"] == 2024)]
#    .sort_values("net_crores")[["company_name", "net_crores"]]
#    .iloc[-5:]
#    .sort_values("net_crores", ascending=False)
# )

# print("~~~~~bottom 5~~~~~~\n\n")

# print(
#    f_df[(f_df["month"] == "jan") & (f_df["year"] == 2024)]
#    .sort_values("net_crores")[["company_name", "net_crores"]]
#    .iloc[:5]
# .sort_values("net_crores", ascending=False)
# )

# ----------------- Monthly dual axes graph

# data 1
df = df[(df["TR_TYPE"] == 1) | (df["TR_TYPE"] == 4)]
df_1 = df.groupby(["TR_TYPE", "month", "year"]).sum("VALUE").reset_index()
df_1["mn_yr"] = pd.to_datetime(
    df_1["month"] + df_1["year"].astype(int).astype(str), format="%b%Y"
)
# print(df_1.head())


# data 2
df_wide[["Buy", "Sell"]] = df_wide[["Buy", "Sell"]] / 10000000

df_wide = df_wide.groupby(["month", "year"]).sum("net_crores").reset_index()
df_wide["mn_yr"] = pd.to_datetime(
    df_wide["month"] + df_wide["year"].astype(int).astype(str), format="%b%Y"
)


print(df_wide)


def chart_month_net_buy():
    # df_use = df_wide
    # fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig = make_subplots(rows=1, cols=2)
    # print(df_use.head())
    # Add traces
    for pst1, grp in df_1.groupby("TR_TYPE"):
        fig.add_trace(
            go.Bar(
                # data_frame=df_wide,
                x=grp["mn_yr"],
                y=grp["VALUE"],
                # fill=df_1["TR_TYPE"],
                # color_discrete_map={"Positive": "green", "Negative": "red"},
                name=pst1,
            ),
            # secondary_y=False,
            row=1,
            col=1,
        )

    fig.add_trace(
        go.Bar(
            # data_frame=df_wide,
            x=df_wide["mn_yr"],
            y=df_wide["net_crores"],
            # color="TR_TYPE",
            # color_discrete_map={"Positive": "green", "Negative": "red"},
            name="yaxis2 data",
            # mode="markers",
            text=df_wide["net_crores"],
            textposition="outside",
        ),
        # secondary_y=True,
        row=1,
        col=2,
    )
    return fig


plot1 = chart_month_net_buy()
plot1.show()


# third type with - using hover data for net crores.

some_plot = px.bar(
    data_frame=df_1,
    x="mn_yr",
    y="VALUE",
    color="TR_TYPE",
    hover_data=df_wide["net_crores"],
)

# some_plot.show()
