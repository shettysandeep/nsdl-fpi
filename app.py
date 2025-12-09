from datetime import datetime
from faicons import icon_svg
from pathlib import Path

import plotly.express as px
from shinywidgets import render_plotly

from shiny import reactive, render, req
from shiny.express import input, ui

# import fpi_analysis

import pandas as pd
import calendar

pth = Path("fpi_data/")
datfile = "fpi_2024_25.csv"
# source data for FPI flows - 2024-25
df = pd.read_csv(pth / datfile)
df["ISIN"] = df["ISIN"].str.strip()
df["mf"] = df.ISIN.apply(lambda x: 1 if x[:3] == "INF" else 0)


# ISIN list
list_isin = pd.read_csv(pth / "active_CM_DEBT_list.csv")


# ------helper
def string_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def filter_by_date(df: pd.DataFrame, date_range: tuple):
    rng = sorted(date_range)
    dates = pd.to_datetime(df["Date"], format="%Y-%m-%d").dt.date
    return df[(dates >= rng[0]) & (dates <= rng[1])]


CRORE = 10000000
MNTHS = [m.lower() for m in calendar.month_abbr]

# ------
ICONS = {
    "usd": icon_svg("dollar-sign"),
}

# ----- Main Page
ui.page_opts(title="FPI Monitor - Equity Secondary Markets")  # fillable=True)

with ui.sidebar(open="desktop"):
    ui.input_selectize("mnth", "Select Month", MNTHS, selected="jan")
    ui.input_selectize("yr", "Select Year", ["2025", "2024"])
    ui.input_slider(
        "usd_inr", "$/INR", min=88.0, max=90.0, value=88.2, step=0.2, pre="$", sep=","
    )


# print(df_mnth.head())

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


with ui.layout_columns(col_widths=[6, 6, 12]):

    with ui.card(full_screen=True):
        ui.card_header("Top 5 Stocks Bought (in value) ")

        @render.data_frame
        def table():
            return render.DataGrid(top_5())

    with ui.card(full_screen=True):
        ui.card_header("Top 5 Sold")

        @render.data_frame
        def table1():
            return render.DataGrid(top_5_sold())


# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------


@reactive.calc
def top_5():
    return (
        df[
            (df["month"] == input.mnth())
            & (df["TR_TYPE"] == 1)
            & (df["year"] == int(input.yr()))
        ]
        .groupby("ISIN")["VALUE"]
        .sum()
        .sort_values(ascending=False)
        .iloc[:10]
        .reset_index()
        .merge(list_isin, left_on="ISIN", right_on="ISIN", how="left")[
            ["company_name", "ISIN"]
        ]
    )


@reactive.calc
def top_5_sold():
    return (
        df[
            (df["month"] == input.mnth())
            & (df["TR_TYPE"] == 4)
            & (df["year"] == int(input.yr()))
        ]
        .groupby("ISIN")["VALUE"]
        .sum()
        .sort_values(ascending=False)
        .iloc[:10]
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
            & (df["TR_TYPE"] == 1)
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
            & (df["TR_TYPE"] == 4)
            & (df["year"] == int(input.yr()))
        ][["VALUE"]]
        .sum()
        .iloc[0]
        / int(input.usd_inr())
        / CRORE
    )
    return last_value


# @reactive.effect
# @reactive.event(input.reset)
# def _():
#    ui.update_slider("total_bill", value=bill_rng)
#    ui.update_checkbox_group("time", selected=["Lunch", "Dinner"])


# insert plot with bar for buy and sale across months
