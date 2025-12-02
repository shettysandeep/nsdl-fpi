"""Analysis of the FPI data in support of the Shiny APP"""

import pandas as pd
from fpi_delimiting_text import cols_keep

fpi = pd.read_csv("nsdl_data/jan_buy_sell_2025.csv", index_col=0)
fpi = fpi[cols_keep]


def print_please(func, rows=10):
    output = func()
    if isinstance(output, pd.DataFrame):
        print(output[:rows])
    else:
        print(output)


@print_please
def min_max_price(df, action="buy"):
    if action == "buy":
        return (
            df[df.TR_TYPE == action]
            .groupby(["SCRIP_NAME", "ISIN"], as_index=True)
            .agg(
                {"VALUE": "sum", "RATE": ["min", "max"]}
                # TOTAL_VALUE = pd.NamedAgg(column="VALUE", aggfunc="sum"),
                # LOWEST_PRICE =pd.NamedAgg(column="RATE", aggfunc="min"),
                # WEGHTED_RATE =
            )
            .sort_values(by=("VALUE", "sum"), ascending=False)
        )
    if action == "sell":
        return (
            df[df.TR_TYPE == action]
            .groupby(["SCRIP_NAME", "ISIN"], as_index=True)
            .agg(
                {"VALUE": "sum", "RATE": ["min", "max"]}
                # TOTAL_VALUE = pd.NamedAgg(column="VALUE", aggfunc="sum"),
                # LOWEST_PRICE =pd.NamedAgg(column="RATE", aggfunc="min"),
                # WEGHTED_RATE =
            )
            .sort_values(by=("VALUE", "sum"), ascending=False)
        )
