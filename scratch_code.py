import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np

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


print("~~~~top 5~~~~~~\n\n")
print(
    f_df[(f_df["month"] == "jan") & (f_df["year"] == 2024)]
    .sort_values("net_crores")[["company_name", "net_crores"]]
    .iloc[-5:]
    .sort_values("net_crores", ascending=False)
)

print("~~~~~bottom 5~~~~~~\n\n")

print(
    f_df[(f_df["month"] == "jan") & (f_df["year"] == 2024)]
    .sort_values("net_crores")[["company_name", "net_crores"]]
    .iloc[:5]
    # .sort_values("net_crores", ascending=False)
)
