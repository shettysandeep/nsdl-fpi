from shiny import reactive  # , req
from shiny.express import input, ui, render
from shinywidgets import render_plotly

import plotly.express as px

from datetime import datetime
from faicons import icon_svg
from pathlib import Path

import pandas as pd
import numpy as np
import calendar
import pyarrow.parquet as pq

CRORE = 10000000
MNTHS = [m.lower() for m in calendar.month_abbr]

pth = Path("fpi_data/")
datfile = "fpi_2024_2025.parquet"

# source data for FPI flows - 2024-25
df = pq.read_table("fpi_data/fpi_2024_2025.parquet")
df = df.to_pandas()

print("~~~~\n")


# ISIN list
list_isin = pd.read_csv(pth / "active_CM_DEBT_list.csv")
STCK_LIST: list[Any] = list_isin[list_isin.instrument_type == "Equity"][
    "company_name"
].to_list()


# ~~Transaction type - buy or sell only
df = df[(df["TR_TYPE"] == 1) | (df["TR_TYPE"] == 4)]  #
df["TR_TYPE"] = df["TR_TYPE"].astype("category")
df["TR_TYPE"] = df.TR_TYPE.cat.rename_categories({1: "Buy", 4: "Sell"})
# df["TR_DATE"] = pd.to_datetime(df["TR_DATE"])


# ------helper
def string_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def filter_by_date(df: pd.DataFrame, date_range: tuple):
    rng = sorted(date_range)
    dates = pd.to_datetime(df["Date"], format="%Y-%m-%d").dt.date
    return df[(dates >= rng[0]) & (dates <= rng[1])]


# ------
ICONS = {
    "usd": icon_svg("dollar-sign"),
}

# ------------------------
# Main Page
# -------------------------
ui.page_opts(title="FPI Monitor - Equity Secondary Markets")  # fillable=True)

# Page 1 - Overall fpi activity ~~~~~~~~~~~~~~~~~~~~~~~~

with ui.nav_panel("Aggregate FPI activity"):
    # with ui.layout_columns():#ui.sidebar(open="desktop"):
    ui.input_selectize("mnth", "Select Month", MNTHS, selected="jan")
    ui.input_selectize("yr", "Select Year", ["2025", "2024"])
    ui.input_slider(
        "usd_inr", "$/INR", min=88.0, max=90.0, value=88.2, step=0.2, pre="$", sep=","
    )

    # with ui.layout_column_wrap():
    with ui.layout_columns(fill=False):
        with ui.value_box(showcase=ICONS["usd"]):
            "Equity Purchased"

            @render.ui
            def bght1():
                return f"${bght():,.0f} cr"

        with ui.value_box(
            showcase=ICONS["usd"],
        ):
            "Equity Sold"

            @render.ui
            def sold1():
                return f"${sold():,.0f} cr"

        with ui.value_box(showcase=icon_svg("house")):
            "Net Purchase"

            @render.ui
            def change():
                net_diff = bght() - sold()
                sign = "+" if net_diff > 0 else ""
                return f"{sign}{net_diff:.0f} Cr"

    # Top 10 by net position in a given month.

    with ui.card():
        ui.card_header("Net purchases (Daily)")

        @render_plotly
        def mnthly_overall_within():
            df_wide = mnthly_net()  # table from below.
            df_use = df_wide[
                (df_wide["month"] == input.mnth())
                & (df_wide["year"] == int(input.yr()))
            ]
            print("inside monthly within line 113 \n")
            print(df_use.month.value_counts())
            lineplot = px.bar(
                data_frame=df_use,
                x="TR_DATE",
                y="net",
                color="Color_Group",  # "TR_TYPE",
                color_discrete_map={"Positive": "green", "Negative": "red"},
                facet_col="year",
                # barmode="group",
                # title=name_scrip,
                labels={
                    "Color_Group": "",
                    "net": "Net Position (Rs. crore)",
                    "TR_DATE": f"{input.mnth()} {input.yr()}",
                },
            )
            return lineplot

    with ui.layout_columns(col_widths=[3, 3, 6]):
        # 1) bought top 5 by net purchases.
        with ui.card(full_screen=True):
            ui.card_header("Top 5 Stocks Net Purchase (in value) ")

            @render.data_frame
            def table():
                d1 = net_stock()
                print(d1.head())
                return render.DataGrid(d1)
                # return render.DataGrid(top_5())

        # 2) sold top 5
        with ui.card(full_screen=True):
            ui.card_header("Top 5 Sold")

            @render.data_frame
            def table1():
                return render.DataGrid(top_5_sold())

        # 3) FPI activity overall
        with ui.card():
            ui.card_header("FPI activity in equity markets...")

            @render_plotly
            def overall_chart():
                """Overall chart across months"""

                dt = df.copy()  # for_that_mnth()
                use_dt = (
                    dt[["month", "year", "TR_TYPE", "VALUE", "TR_DATE"]]
                    .groupby(["month", "year", "TR_TYPE"], observed=True)
                    .sum("VALUE")
                    .reset_index()
                    .sort_values(by=["month", "year"], ascending=True)
                )
                # print(dt.dtypes)
                # use_dt["m_y"]=use_dt["TR_DATE"].apply(lambda x:
                #                                      string_to_date(str(x)))
                use_dt["m_y"] = pd.to_datetime(
                    use_dt["month"] + use_dt["year"].astype(str), format="%b%Y"
                ).astype(str)
                # print(use_dt.head())
                # print(use_dt.dtypes)
                lineplot = px.bar(
                    data_frame=use_dt,
                    x="m_y",
                    y="VALUE",
                    color="TR_TYPE",
                    barmode="group",
                    title="FPI activity across months in Secondary markets",
                    labels={"TR_TYPE": "", "m_y": "", "VALUE": "INR"},
                )
                return lineplot


# ----------Page 2 - Stock level

with ui.nav_panel("Stock level"):
    ui.input_selectize("equity", "Select equity", STCK_LIST)

    with ui.layout_columns():
        # 1) Stock level chart --
        with ui.card():
            ui.card_header("FPI activity in stock...")

            @render_plotly
            def stock_chart():
                """
                Stock specific charts of inflow and outflow

                :param stock_name: "Name of stock selected from dropdown.
                Combine the name and ISIN in a tuple
                """

                dt = df.copy()  # for_that_mnth()
                applied_dt = dt[dt["company_name"] == input.equity()]
                name_scrip = input.equity()
                # print(name_scrip)
                use_dt = (
                    applied_dt[["month", "year", "TR_TYPE", "VALUE"]]
                    .groupby(["month", "year", "TR_TYPE"], observed=True)
                    .sum("VALUE")
                    .reset_index()
                    .sort_values(by=["month", "year"], ascending=True)
                )
                # use_dt["m_y"]=use_dt["TR_DATE"].apply(lambda x:
                #                                      string_to_date(str(x)))
                use_dt["m_y"] = pd.to_datetime(
                    use_dt["month"] + use_dt["year"].astype(str), format="%b%Y"
                ).astype("datetime64[us]")
                lineplot = px.bar(
                    data_frame=use_dt,
                    x="m_y",
                    y="VALUE",
                    color="TR_TYPE",
                    barmode="group",
                    title=name_scrip,
                    labels={"TR_TYPE": "", "m_y": "", "VALUE": "INR"},
                )
                return lineplot


# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------


# net buying by stocks
@reactive.calc
def top_5():
    """Obtain Net position by month & year across all funds.
    Return a table with the top 5 or 10 by (positive) net position.
    """
    return (
        df[
            (df["month"] == input.mnth())
            & (df["TR_TYPE"] == "Buy")
            & (df["year"] == int(input.yr()))
        ]
        .groupby("ISIN")["value_crores"]
        .sum()
        .sort_values(ascending=False)
        .iloc[:5]
        .reset_index()
        .merge(list_isin, left_on="ISIN", right_on="ISIN", how="left")[
            ["company_name", "ISIN", "value_crores"]
        ]
    )


@reactive.calc
def top_5_sold():
    """Returns the list of top 5 bought by value"""
    return (
        df[
            (df["month"] == input.mnth())
            & (df["TR_TYPE"] == "Sell")
            & (df["year"] == int(input.yr()))
        ]
        .groupby("ISIN")["VALUE"]
        .sum()
        .sort_values(ascending=False)
        .iloc[:5]
        .reset_index()
        .merge(list_isin, left_on="ISIN", right_on="ISIN", how="left")[
            ["company_name", "ISIN"]
        ]
    )


@reactive.calc
def bght():
    # month filter
    last_value = (
        df[
            (df["month"] == input.mnth())
            & (df["TR_TYPE"] == "Buy")
            & (df["year"] == int(input.yr()))
        ][["VALUE"]]
        .sum()
        .iloc[0]
        / int(input.usd_inr())
        / CRORE
    )
    return last_value


@reactive.calc
def sold():
    # month filter
    last_value = (
        df[
            (df["month"] == input.mnth())
            & (df["TR_TYPE"] == "Sell")
            & (df["year"] == int(input.yr()))
        ][["VALUE"]]
        .sum()
        .iloc[0]
        / int(input.usd_inr())
        / CRORE
    )
    return last_value


@reactive.calc
def mnthly_net():
    print(f"inside {mnthly_net.__name__}")
    print(df.head())
    df_wide = (
        df.pivot_table(
            index=["TR_DATE", "month", "year"],
            columns="TR_TYPE",
            values="VALUE",
            aggfunc="sum",
            observed=True,
        )
        .rename(columns={1: "Buy", 4: "Sell"})
        .reset_index()
    )

    df_wide["net"] = np.round((df_wide["Buy"] - df_wide["Sell"]) / 10000000, 0)

    df_wide["Color_Group"] = df_wide["net"].apply(
        lambda x: "Positive" if x >= 0 else "Negative"
    )
    print(df_wide.head())
    print(f"Outside {mnthly_net.__name__}")
    return df_wide


@reactive.calc
def net_stock():
    """Returns dataframe with net positions at {stock-month} level"""
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

    df_wide["net_crores"] = np.round((df_wide["Buy"] - df_wide["Sell"]) / 10000000, 0)

    return df_wide
