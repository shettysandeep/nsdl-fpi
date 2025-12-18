"""Analysis of the FPI data in support of the Shiny APP"""

import pandas as pd
from fpi_delimiting_text import cols_keep
import matplotlib.pyplot as plt
import plotly.express as px
import pyarrow.parquet as pq


#fpi = pd.read_csv("fpi_data/fpi_2024_25.csv")
fpi = pq.read_table("fpi_data/fpi_2024_2025.parquet",
                    coerce_int96_timestamp_unit='ms')
print(fpi)
fpi = fpi.to_pandas()

print(fpi.dtypes)
fpi_dat = fpi[cols_keep]
fpi_dat = fpi_dat[
    (fpi_dat.TR_TYPE == 1) | (fpi_dat.TR_TYPE == 4)
]  # buy/sale transation
fpi_dat.loc[:, "ISIN"] = fpi_dat.ISIN.str.strip()
fpi_dat.loc["mf"] = fpi_dat.ISIN.apply(lambda x: 1 if x[:3] == "INF" else 0)
# print(fpi_dat[250:26666660]['TR_DATE'])
# fpi_dat["TR_DATE"]=fpi_dat.TR_DATE.where(fpi_dat["TR_DATE"]=='2025-01-01',
#                                         '2025-01-01 00:00:00')
fpi_dat.loc["TR_DATE"] = pd.to_datetime(fpi_dat["TR_DATE"], format="mixed")
# fpi_dat.loc["month"] = fpi_dat.TR_DATE.dt.month
print(fpi_dat.head())
print(fpi_dat.SCRIP_NAME.iloc[11])
print(fpi_dat.TR_DATE.value_counts())


# plot a stock


def stock_chart(df, stock_name):
    """
    Stock specific charts of inflow and outflow

    :param stock_name: "Name of stock selected from dropdown.
    Combine the name and ISIN in a tuple
    """
    lineplot = px.bar(
        data_frame=df[df["SCRIP_NAME"] == stock_name],
        x="TR_DATE",
        y="VALUE",
        color="TR_TYPE",
    )
    return lineplot


# %%
st = stock_chart(df=fpi_dat, stock_name="ADANI TOTAL GAS LIMITED")
st.show()


'''
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
            TOTAL_VALUE=pd.NamedAgg(column="VALUE", aggfunc="sum"),
            MIN_PRICE=pd.NamedAgg(column="RATE", aggfunc="min"),
            MAX_PRICE=pd.NamedAgg(column="RATE", aggfunc="max"),
        )
    )


# top 5 equities and not mutual funds
fpi_dat_grp = fpi_dat[fpi_dat["mf"] == 0].groupby("ISIN")


def wghtd_price(df):
    # obtain weighted price of sale / purchase
    df["WTD_PRICE"] = (df["RATE"] * (df["QUANTITY"] / df["QUANTITY"].sum())).sum()
    return df


# test = fpi_dat_grp.apply(wghtd_price, include_groups=False)

fpi_dat_grp.apply(lambda x: (x["RATE"] * (x["QUANTITY"] / x["QUANTITY"].sum())).mean())


# print(fpi_dat_grp.apply(lambda x: x["VALUE"].mean()))

ok1 = fpi_dat_grp["VALUE"].mean().sort_values(ascending=False).iloc[:5].reset_index()
list_isin = pd.read_csv("fpi_data/active_CM_DEBT_list.csv")
# print(list_isin.columns)

# mf_isin = pd.read_csv("fpi_data/mf_isin_list.csv")
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
the duration of sales. how fpis sell lots. 
sometimes it could be within fpi locations, etc. 
there is a lot to unpack.
this will be fun.

"""

"""
'''
