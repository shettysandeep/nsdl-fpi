"""Analysis of the FPI data in support of the Shiny APP"""

import pandas as pd
from fpi_delimiting_text import cols_keep

fpi = pd.read_csv("nsdl_data/jan_buy_sell_2025.csv", index_col=0)
fpi = fpi[cols_keep]
fpi_dat = fpi[(fpi.TR_TYPE == 1) | (fpi.TR_TYPE == 4)]


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
        .groupby(["SCRIP_NAME", "ISIN"], as_index=True)
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


min_max_price(fpi_dat, 1)

""" 
There is a lot to do here. 
some isin stocks when it was sold at different times by the FPI.
let's keep it simple. 
the duration of sales. how fpis sell lots. 
sometimes it could be within fpi locations, etc. 
there is a lot to unpack.
this will be fun.

"""
