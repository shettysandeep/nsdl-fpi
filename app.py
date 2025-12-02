from datetime import datetime
from faicons import icon_svg

import plotly.express as px
from shinywidgets import render_plotly

from shiny import reactive, render, req
from shiny.express import input, ui

# import fpi_analysis

import pandas as pd

# source data for FPI flows - only one month
df = pd.read_csv("nsdl_data/jan_buy_sell_2025.csv")
df["mnth"] = "Jan"
test = df[df["mnth"] == "Jan"]
print(test[["mnth", "VALUE", "ISIN"]].head())


# ------helper
def string_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def filter_by_date(df: pd.DataFrame, date_range: tuple):
    rng = sorted(date_range)
    dates = pd.to_datetime(df["Date"], format="%Y-%m-%d").dt.date
    return df[(dates >= rng[0]) & (dates <= rng[1])]


CRORE = 10000000

# ------
ICONS = {
    "usd": icon_svg("dollar-sign"),
}

# ----- Main Page
ui.page_opts(title="FPI Monitor - Equity Secondary Markets")  # fillable=True)

with ui.sidebar(open="desktop"):
    ui.input_selectize("mnth", "Select Month", ["Jan", "Feb"])
    ui.input_selectize("yr", "Select Year", ["2025", "2024"])
    # ui.input_slider("date_range","Filter by Month",
    #            min = string_to_date("2018-3-31"),
    #            max = string_to_date("2024-4-30"),
    #            value = [string_to_date(x) for x in ["2018-3-31","2024-4-30"]])

# with ui.layout_column_wrap():
with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["usd"]):
        "Equity Purchased"

        @render.ui
        def bght():
            # month filter
            last_value = (
                df.groupby("TR_TYPE")[["VALUE"]].sum().values[0][0] / 88.2 / CRORE
            )
            return f"${last_value:,.0f} cr"

    with ui.value_box(showcase=ICONS["usd"]):
        "Equity Sold"

        @render.ui
        def sold():
            last_value = (
                df.groupby("TR_TYPE")[["VALUE"]].sum().values[1][0] / 88.2 / CRORE
            )
            return f"${last_value:,.0f} cr"

    with ui.value_box(showcase=icon_svg("house")):
        "Net Purchase"

        @render.ui
        def change():
            bght = df.groupby("TR_TYPE")[["VALUE"]].sum().values[0][0] / 88.2 / CRORE
            sold = df.groupby("TR_TYPE")[["VALUE"]].sum().values[1][0] / 88.2 / CRORE
            net_diff = bght - sold
            #            sign = "+" if net_diff > 0 else "-"
            return f"{net_diff:.0f} Cr"


with ui.layout_columns(col_widths=[6, 6, 12]):

    with ui.card(full_screen=True):
        ui.card_header("Top 5 bght")

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
    idx1 = df[df.mnth == input.mnth()].copy()
    # return df[["ISIN", "VALUE"]].head()
    return idx1[["ISIN", "VALUE"]].head()


@reactive.calc
def top_5_sold():
    idx1 = df[df.mnth == input.mnth()].copy()
    # return df[["ISIN", "VALUE"]].head()
    return idx1[["ISIN", "VALUE"]].head()


# @reactive.effect
# @reactive.event(input.reset)
# def _():
#    ui.update_slider("total_bill", value=bill_rng)
#    ui.update_checkbox_group("time", selected=["Lunch", "Dinner"])


# insert plot with bar for buy and sale across months
