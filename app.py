from shiny import reactive
from shiny.express import input, ui, render
from shinywidgets import render_plotly
from pathlib import Path
import plotly.express as px
from shiny.ui import tags
from datetime import datetime
import pandas as pd
import numpy as np
import calendar
import pyarrow.parquet as pq

CRORE = 10000000
MNTHS = [m.lower() for m in calendar.month_abbr]
FMTHS = [m for m in calendar.month_name]
mth = dict(zip(FMTHS, MNTHS))

www_dir = Path(__file__).parent / "www"
# Use the Path object to construct the correct path to your CSS file
css_file_path = Path(__file__).parent / "www" / "styles.css"

# Include the local CSS file in the UI
# ui.include_css(css_file_path)

COL_NAMES = ["Company", "Net Purchase"]

pth = Path("fpi_data/")
# datfile = "fpi_2024_2025.parquet"
datfile = "fpi_id_2024_2025_mgd_jan2026.parquet"

# source data for FPI flows - 2024-25
df = pq.read_table(Path(pth / datfile))
df = df.to_pandas()

print("~~~~\n")


# --- Transaction type - buy or sell only
df = df[(df["TR_TYPE"] == 1) | (df["TR_TYPE"] == 4)]  #
df["TR_TYPE"] = df["TR_TYPE"].astype("category")
df["TR_TYPE"] = df.TR_TYPE.cat.rename_categories({1: "Buy", 4: "Sell"})
df["month"] = df.month.str.strip()
df["year"] = df.year.astype(int)

# ---- Keep Equity Only
df = df[(df["instrument_type"] == "Equity")]


# ---List of companies
STCK_LIST: list[str] = df["company_name"].sort_values().unique().tolist()


# ------helper
def string_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def filter_by_date(df: pd.DataFrame, date_range: tuple):
    rng = sorted(date_range)
    dates = pd.to_datetime(df["Date"], format="%Y-%m-%d").dt.date
    return df[(dates >= rng[0]) & (dates <= rng[1])]


# ----- images
inr = ui.tags.img(src="rupee.png", height="50px", width="50px")  # ununsed
inr_bl = ui.tags.img(src="dark_inr1.png", height="30px", width="30px")  # buy
inr_wh = ui.tags.img(src="white_inr1.png", height="30px", width="30px")  # sale
inr_io = ui.tags.img(src="inf_outf.png", height="30px", width="30px")  # net

#
# ------------------------
# Main Page
# -------------------------
ui.page_opts(
    title=tags.h1("FPI Monitor: Secondary Equity Markets"),
    theme=ui.Theme("lux"),
    # base_font="Roboto",        # For all general text
    # heading_font="Yusei Magic"
)  # fillable=True

# Page 1 - Overall fpi activity ~~~~~~~~~~~~~~~~~~~~~~~~

with ui.nav_panel("Aggregate FPI activity"):
    with ui.layout_columns():  # ui.sidebar(open="desktop"):
        with ui.card():
            ui.card_header("Select for FPI activity in...")
            ui.input_selectize("mnth", "month", FMTHS, selected="January")
            ui.input_selectize("yr", "year", ["2025", "2024"])
            # ui.input_slider(
            #    "usd_inr", "$/INR", min=88.0, max=90.0, value=88.2, step=0.2, pre="$", sep=","
            # )
        with ui.card():

            @render.ui
            def card1():
                return ui.card_header(
                    "In {} {}, FPIs... ".format(input.mnth(), input.yr())
                )

            with ui.value_box(
                showcase=inr_bl,
                height="120px",
                showcase_layout="left center",
            ):
                tags.h1("purchased (Rs. Crores)", style="font-size: 90%;")

                @render.ui
                def bght1():
                    return tags.h1(f"{bght():,.0f}", style="font-size:80%;")

            with ui.value_box(
                showcase=inr_wh,  # ICONS["usd"],
                height="120px",
                showcase_layout="left center",
            ):
                tags.h1("sold (Rs. Crores)", style="font-size: 90%;")

                @render.ui
                def sold1():
                    return tags.h1(f"{sold():,.0f}", style="font-size:80%;")

            with ui.value_box(
                showcase=inr_io,
                height="120px",
                width="80px",
                showcase_layout="left center",
            ):  # icon_svg("house")):
                tags.h1("net (Rs. Crores)", style="font-size:90%;")

                @render.ui
                def change():
                    net_diff = bght() - sold()
                    sign = "+" if net_diff > 0 else ""
                    # ui.tags.style( style="color: red;")
                    text2 = f"{sign}{net_diff:,.0f}"
                    return tags.h1(text2, style="font-size:80%;")

        # with ui.layout_columns(col_widths=[3, 3, 6]):
        # 1) bought top 5 by net purchases.
        with ui.card(full_screen=True):

            @render.ui
            def card2():
                return ui.card_header(
                    "Top 5 stocks net bought in {}-{}: (Rs. crores)".format(
                        input.mnth(), input.yr()
                    )
                )

            @render.data_frame
            def table():
                f_df = net_stock()
                d1 = (
                    f_df[
                        (f_df["month"] == mth[input.mnth()])
                        & (f_df["year"] == int(input.yr()))
                    ]
                    .sort_values("net_crores", ascending=False)[
                        ["company_name", "net_crores"]
                    ]
                    .iloc[:5]
                )
                d1["net_crores"] = d1["net_crores"].round(1).astype(str)
                d1.columns = COL_NAMES
                # print(d1)
                return render.DataGrid(d1)

        # 2) sold top 5
        with ui.card(full_screen=True):

            @render.ui
            def cardr3():
                return ui.card_header(
                    "Top 5 stocks net sold in {}-{}: (Rs. crores)".format(
                        input.mnth(), input.yr()
                    )
                )

            @render.data_frame
            def table1():
                f_df = net_stock()
                d1 = (
                    f_df.loc[
                        (f_df["month"] == mth[input.mnth()])
                        & (f_df["year"] == int(input.yr()))
                    ]
                    .sort_values("net_crores")[["company_name", "net_crores"]]
                    .iloc[:5]
                )
                d1["net_crores"] = d1["net_crores"].round(1).astype(str)
                d1.columns = COL_NAMES
                return render.DataGrid(d1)

    # Top 10 by net position in a given month.

    with ui.card():

        @render.ui
        def gr_hdr():
            return ui.card_header(
                "Net purchases (Daily) in {} {}".format(input.mnth(), input.yr())
            )

        @render_plotly
        def mnthly_overall_within():
            df_wide: pd.DataFrame = mnthly_net()  # table from below.
            df_use = df_wide[
                (df_wide["month"] == mth[input.mnth()])
                & (df_wide["year"] == int(input.yr()))
            ]
            lineplot = px.bar(
                data_frame=df_use,
                x="TR_DATE",
                y="net_crores",
                color="Color_Group",  # "TR_TYPE",
                color_discrete_map={"Positive": "green", "Negative": "red"},
                # facet_col="year",
                # barmode="group",
                title="",  # f"Net Purchases in {mth[input.mnth()]}",
                labels={
                    "Color_Group": "",
                    "net_crores": "Net purchase (Rs. crore)",
                    "TR_DATE": f"{mth[input.mnth()]} {input.yr()}",
                },
            )
            return lineplot

    # ---- Monthly Net
    with ui.card():
        ui.card_header("FPI monthly net purchases")

        @render_plotly
        def monthly_agg_chart():
            """Net purchase monthly"""

            dt = mnthly_net()
            f_df = (
                dt.groupby(["month", "year"])
                .sum(["net_crores"])
                .sort_values(by="net_crores", ascending=True)
                .reset_index()
            )
            f_df["m_y"] = pd.to_datetime(
                f_df["month"] + f_df["year"].astype(str), format="%b%Y"
            ).astype(str)
            f_df["Color_Group"] = f_df["net_crores"].apply(
                lambda x: "Positive" if x >= 0 else "Negative"
            )

            lineplot = px.bar(
                data_frame=f_df,
                x="m_y",
                y="net_crores",
                color="Color_Group",  # "TR_TYPE",
                color_discrete_map={"Positive": "green", "Negative": "red"},
                # color="TR_TYPE",
                # barmode="group",
                title="",
                labels={
                    "TR_TYPE": "",
                    "m_y": "",
                    "net_crores": "Net purchase (Rs. crore)",
                    "Color_Group": "",
                },
            )
            return lineplot

    # ---- Monthly Buy and Sale
    with ui.card():
        ui.card_header("FPI activity across all months")

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
                title="",
                labels={"TR_TYPE": "", "m_y": "", "VALUE": "INR"},
            )
            return lineplot


# ----------Page 2 - Stock level

with ui.nav_panel("Stock level"):
    ui.input_selectize("equity", "Select equity", STCK_LIST)

    # with ui.layout_columns():
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

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Monthly net purchases in stocks
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~``
    # with ui.layout_columns():
    with ui.card():
        ui.card_header("FPI monthly net purchases")

        @render_plotly
        def stock_chart_net():
            """
            Stock specific charts of inflow and outflow

            :param stock_name: "Name of stock selected from dropdown.
            Combine the name and ISIN in a tuple
            """
            dt = net_stock()
            applied_dt = dt[dt["company_name"] == input.equity()]
            name_scrip = input.equity()
            use_dt = (
                applied_dt[["month", "year", "net_crores"]]
                .groupby(["month", "year"], observed=True)
                .sum("net_crores")
                .reset_index()
                .sort_values(by=["month", "year"], ascending=True)
            )
            use_dt["m_y"] = pd.to_datetime(
                use_dt["month"] + use_dt["year"].astype(str), format="%b%Y"
            ).astype("datetime64[us]")

            use_dt["Color_Group"] = use_dt["net_crores"].apply(
                lambda x: "Positive" if x >= 0 else "Negative"
            )

            lineplot = px.bar(
                data_frame=use_dt,
                x="m_y",
                y="net_crores",
                color="Color_Group",  # "TR_TYPE",
                color_discrete_map={"Positive": "green", "Negative": "red"},
                title=name_scrip,
                labels={
                    "TR_TYPE": "",
                    "m_y": "",
                    "net_crores": "Net purchase (Rs. crore)",
                    # "VALUE": "INR"
                },
            )
            return lineplot

    with ui.card():
        ui.card_header("Monthly VWAP (buy and sale price)")

        @render_plotly
        def wPrice_mnthly():
            indf = weighted_price1()
            # print(indf.head())
            indf_c = indf[(indf["company_name"] == input.equity())].copy()
            indf_c["m_y"] = pd.to_datetime(
                indf_c["month"] + indf_c["year"].astype(str), format="%b%Y"
            )
            indf_c = indf_c.sort_values(by="m_y")
            indf_c["m_y"] = indf_c["m_y"].astype(str)
            lineplot = px.line(
                data_frame=indf_c,
                x="m_y",
                y="VWAP",
                color="TR_TYPE",
                # color_discrete_map={"Positive": "green", "Negative": "red"},
                title="{}".format(input.equity()),
                labels={"TR_TYPE": "", "m_y": "", "VALUE": "INR"},
            )
            # print(indf.head())
            return lineplot

    with ui.layout_columns():
        with ui.card():
            ui.card_header("Number of FIIs bought in the stock")

            @render_plotly
            def fii_in_stock_buy():
                dt = fii_count_stock()
                name_scrip = input.equity()
                lineplot = px.bar(
                    data_frame=dt,
                    x="m_y",
                    y="Buy",
                    # color="Color_Group",  # "TR_TYPE",
                    # color_discrete_map={"Positive": "green", "Negative": "red"},
                    title=name_scrip,
                    labels={
                        "TR_TYPE": "",
                        "m_y": "",
                        "1": "Count of FPIs buying",
                        # "VALUE": "INR"
                    },
                )
                return lineplot

        with ui.card():
            ui.card_header("Number of FIIs sold the stock")

            @render_plotly
            def fii_in_stock_sell():
                dt = fii_count_stock()
                name_scrip = input.equity()
                lineplot = px.bar(
                    data_frame=dt,
                    x="m_y",
                    y="Sell",
                    # color="Color_Group",  # "TR_TYPE",
                    # color_discrete_map={"Positive": "green", "Negative": "red"},
                    title=name_scrip,
                    labels={
                        "TR_TYPE": "",
                        "m_y": "",
                        "1": "Count of FPIs buying",
                        # "VALUE": "INR"
                    },
                )
                return lineplot


# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------


# return months
# @reactive.calc
# def short_mnth():
#    print(mth[input.mnth()])
#    return mth[input.mnth()]


@reactive.calc
def bght():
    # month filter
    last_value = (
        df[
            (df["month"] == mth[input.mnth()])
            & (df["TR_TYPE"] == "Buy")
            & (df["year"] == int(input.yr()))
        ][["VALUE"]]
        .sum()
        .iloc[0]
        / 1  # int(input.usd_inr())
        / CRORE
    )
    return last_value


@reactive.calc
def sold():
    # month filter
    last_value = (
        df[
            (df["month"] == mth[input.mnth()])
            & (df["TR_TYPE"] == "Sell")
            & (df["year"] == int(input.yr()))
        ][["VALUE"]]
        .sum()
        .iloc[0]
        / 1  # int(input.usd_inr())
        / CRORE
    )
    return last_value


@reactive.calc
def mnthly_net() -> pd.DataFrame:
    """Returns dataframe with net positions at monthly level"""
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
    cols_to_fill = ["Buy", "Sell"]
    df_wide[cols_to_fill] = df_wide[cols_to_fill].fillna(0)
    df_wide["net_crores"] = np.round((df_wide["Buy"] - df_wide["Sell"]) / 10000000, 2)
    # df_wide["net"] = np.round((df_wide["Buy"] - df_wide["Sell"]) / 10000000, 0)

    df_wide["Color_Group"] = df_wide["net_crores"].apply(
        lambda x: "Positive" if x >= 0 else "Negative"
    )
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
    cols_to_fill = ["Buy", "Sell"]
    df_wide[cols_to_fill] = df_wide[cols_to_fill].fillna(0)
    df_wide["net_crores"] = (df_wide["Buy"] - df_wide["Sell"]) / 10000000
    df_wide["net_crores"] = df_wide["net_crores"].round(2)
    f_df = (
        df_wide.groupby(["company_name", "month", "year"])
        .sum("net_crores")
        .sort_values(by="net_crores", ascending=True)
        .reset_index()
    )
    return f_df


# Need to think of a postion for this.
# This provides info on monthly weighted buy and sale orices of FPI.
# ~~~~~~~~~~~~~~~~~~~~~


@reactive.calc
def weighted_price():
    dat_grp = df.groupby(["company_name", "month", "year", "TR_TYPE"])
    dat_grp["weighted_price"] = dat_grp.apply(
        lambda x: (x["RATE"] * (x["QUANTITY"] / x["QUANTITY"].sum())).mean()
    )
    # print(df.head())
    sdf = (
        df.groupby(
            ["company_name", "month", "year", "TR_TYPE"], as_index=True, observed=True
        )
        .agg(
            # {"VALUE": "sum", "RATE": ["min", "max"]}
            Max_wPrice=pd.NamedAgg(column="RATE", aggfunc="max"),
            #    TOTAL_VALUE = pd.NamedAgg(column="VALUE", aggfunc="sum"),
            Min_wPrice=pd.NamedAgg(column="RATE", aggfunc="min"),
        )
        .reset_index()
        # .sort_values(by=("VALUE", "sum"), ascending=False)
    )
    return sdf


@reactive.calc
def weighted_price1():
    small_df = df[
        ["company_name", "month", "year", "TR_TYPE", "ISIN", "RATE", "QUANTITY"]
    ].copy()

    small_df["TOTAL_VOLUME"] = small_df.groupby(
        ["company_name", "month", "year", "TR_TYPE"], observed="False"
    )["QUANTITY"].transform("sum")

    small_df["vol_wights"] = small_df["QUANTITY"] / small_df["TOTAL_VOLUME"]

    small_df["int_wrate"] = small_df["RATE"] * small_df["vol_wights"]

    small_df["VWAP"] = small_df.groupby(
        ["company_name", "month", "year", "TR_TYPE"], observed="False"
    )["int_wrate"].transform("sum")

    return small_df


@reactive.calc
def fii_count_stock():
    dt_isin = df[df["company_name"] == input.equity()]
    dt_isin = dt_isin.drop_duplicates(["month", "year", "FII"])
    dt_isin = (
        (
            dt_isin.groupby(["month", "year", "TR_TYPE"], observed=False)["FII"]
            .count()
            .reset_index()
        )
        .pivot_table(
            columns="TR_TYPE", index=["month", "year"], values="FII", observed=False
        )
        .reset_index()
        .sort_values(by=["year", "month"])
    )
    dt_isin["m_y"] = pd.to_datetime(
        dt_isin["month"] + dt_isin["year"].astype(str), format="%b%Y"
    ).astype(str)
    dt_isin.rename(columns={1: "Buy", 4: "Sell"}, inplace=True)
    return dt_isin


# SCRAP VALUE...# SCRAP VALUE...# SCRAP VALUE...
# net buying by stocks
# @reactive.calc
# def top_5():
#     """Obtain Net position by month & year across all funds.
#     Return a table with the top 5 or 10 by (positive) net position.
#     """
#     return (
#         df[
#             (df["month"] == input.mnth())
#             & (df["TR_TYPE"] == "Buy")
#             & (df["year"] == int(input.yr()))
#         ]
#         .groupby("ISIN")["value_crores"]
#         .sum()
#         .sort_values(ascending=False)
#         .iloc[:5]
#         .reset_index()
#         .merge(list_isin, left_on="ISIN", right_on="ISIN", how="left")[
#             ["company_name", "ISIN", "value_crores"]
#         ]
#     )
#

# @reactive.calc
# def top_5_sold():
#     """Returns the list of top 5 bought by value"""
#     return (
#         df[
#             (df["month"] == input.mnth())
#             & (df["TR_TYPE"] == "Sell")
#             & (df["year"] == int(input.yr()))
#         ]
#         .groupby("ISIN")["VALUE"]
#         .sum()
#         .sort_values(ascending=False)
#         .iloc[:5]
#         .reset_index()
#         .merge(list_isin, left_on="ISIN", right_on="ISIN", how="left")[
#             ["company_name", "ISIN"]
#         ]
#     )
#

# ISIN list
# list_isin = pd.read_csv(pth / "active_CM_DEBT_list.csv")

# STCK_LIST: list[str] = list_isin[list_isin.instrument_type == "Equity"][
#     "company_name"
# ].tolist()
#
# del list_isin  # remove this table
