"""Analysis of the FPI data in support of the Shiny APP"""

import pandas as pd
from fpi_delimiting_text import cols_keep


fpi = pd.read_csv("nsdl_data/jan_buy_sell_2025.csv", index_col=0)
fpi = fpi[cols_keep]
fpi_dat = fpi[(fpi.TR_TYPE == 1) | (fpi.TR_TYPE == 4)]
fpi_dat["ISIN"] = fpi_dat["ISIN"].str.strip()
fpi_dat["mf"] = fpi_dat.ISIN.apply(lambda x: 1 if x[:3] == "INF" else 0)

print(fpi_dat["ISIN"].unique().shape)


def top_5(func):
    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        print(output[:5])

    return wrapper


@top_5
def min_max_price(df, action=1):
    """Returns top 5 bought and sold stocks in a given time period.
    action = 1 --> buy eq in secondary markets
    action = 4 --> sell eq in secondary markets
    """

    return (
        df[df.TR_TYPE == action]
        .groupby(["ISIN"], as_index=True)
        .agg(
            # {"VALUE": "sum", "RATE": ["min", "max"]}
            TOTAL_VALUE=pd.NamedAgg(column="VALUE", aggfunc="sum"),
            MIN_PRICE=pd.NamedAgg(column="RATE", aggfunc="min"),
            MAX_PRICE=pd.NamedAgg(column="RATE", aggfunc="max"),
            # WEGHTED_RATE =
            # lambda x: x.sum()
        )
        # .sort_values(by=("VALUE", "sum"), ascending=False)
    )


# top 5 equities and not mutual funds
fpi_dat_grp = fpi_dat[fpi_dat["mf"] == 0].groupby("ISIN")
# print(len(fpi_dat_grp.groups.keys()))


def wghtd_price(df):
    df["WTD_PRICE"] = (df["RATE"] * (df["QUANTITY"] / df["QUANTITY"].sum())).sum()
    return df


# test = fpi_dat_grp.apply(wghtd_price, include_groups=False)

fpi_dat_grp.apply(lambda x: (x["RATE"] * (x["QUANTITY"] / x["QUANTITY"].sum())).mean())


# print(fpi_dat_grp.apply(lambda x: x["VALUE"].mean()))

ok1 = fpi_dat_grp["VALUE"].mean().sort_values(ascending=False).iloc[:5].reset_index()
list_isin = pd.read_csv("fpi_data/active_CM_DEBT_list.csv")
# print(list_isin.columns)

mf_isin = pd.read_csv("fpi_data/mf_isin_list.csv")
# print(mf_isin.columns)


print(pd.merge(ok1, list_isin, left_on="ISIN", right_on="ISIN", how="left"))
# print(test[test["RATE"] == 0].value_counts())
# print(test.drop_duplicates().shape)
# fpi_dat["tot_qty"] = fpi_dat.groupby("ISIN")[["QUANTITY"]].transform(lambda x: sum(x))
# fpi_dat["pri_qty"] = fpi_dat["QUANTITY"]*fpi_dat["PRICE"]
# fpi_dat["weighted_"]
# print(fpi_dat[fpi_dat.ISIN == "INE128S01021"].head())
# lambda x: pd.Series((x["RATE"] * x["QUANTITY"]) / np.sum(x["QUANTITY"]))


""" 
There is a lot to do here. 
some isin stocks when it was sold at different times by the FPI.
let's keep it simple. 
the duration of sales. how fpis sell lots. 
sometimes it could be within fpi locations, etc. 
there is a lot to unpack.
this will be fun.

"""
