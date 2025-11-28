from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
from faicons import icon_svg
#from shinywidgets import render_plotly

from shiny import reactive
from shiny.express import input, render, ui


# source data for FPI flows
df = pd.read_csv("nsdl_data/jan_buy_sell_2025.csv")
#print(df.head())

#------helper
def string_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def filter_by_date(df: pd.DataFrame,date_range: tuple):
    rng = sorted(date_range)
    dates = pd.to_datetime(df["Date"], format="%Y-%m-%d").dt.date
    return df[(dates >= rng[0]) & (dates <= rng[1])]

CRORE = 10000000

#------

#----- Main Page
ui.page_opts(title= "FPI Monitor - Equity Secondary Markets")

with ui.sidebar():
    ui.input_select("state","Filter by State", choices=["AZ", "AK"]),
    ui.input_slider("date_range","Filter by Month",
                min = string_to_date("2018-3-31"),
                max = string_to_date("2024-4-30"),
                value = [string_to_date(x) for x in ["2018-3-31","2024-4-30"]])

with ui.layout_column_wrap():
    with ui.value_box(showcase = icon_svg("dollar-sign")):
        "Equity Purchased"

        @render.ui
        def bght():
            last_value=df.groupby("TR_TYPE")[["VALUE"]].sum().values[0][0]/88.2/CRORE
            return f"${last_value:,.0f} cr"

with ui.layout_column_wrap():
    with ui.value_box(showcase = icon_svg("dollar-sign")):
        "Equity Sold"

        @render.ui
        def sold():
            last_value=df.groupby("TR_TYPE")[["VALUE"]].sum().values[1][0]/88.2/CRORE
            return f"${last_value:,.0f} cr"

with ui.value_box(showcase = icon_svg("house")):
        "Net Purchase"
        @render.ui
        def change():
            bght = df.groupby("TR_TYPE")[["VALUE"]].sum().values[0][0]/88.2/CRORE
            sold = df.groupby("TR_TYPE")[["VALUE"]].sum().values[1][0]/88.2/CRORE
            net_diff = bght-sold
            sign = "+" if net_diff > 0 else "-"
            return f"{net_diff:.0f} Cr"

# insert plot with bar for buy and sale across months