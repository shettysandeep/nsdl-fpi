"""Code to clean up the variables of the FPI files obtained from the NSDL website"""

import pandas as pd
from pathlib import Path
from fpi_delimiting_text import cols_keep

# Combine all the months for year 2024
fpi_data = Path() / "nsdl_data" / "2024/"

year_2024 = pd.DataFrame()

for itms in fpi_data.iterdir():
    print(itms)
    if itms.with_suffix(".xlsx"):
        df = pd.read_excel(itms, engine="openpyxl")
        df.rename(
            columns={"TR_TYPE(*)": "TR_TYPE", "VALUE (in Rs)": "VALUE"}, inplace=True
        )
        df.loc[:, "TR_DATE"] = pd.to_datetime(df["TR_DATE"])
        df = df[cols_keep]
        mnth = itms.stem.lower()[:-5]
        year = itms.stem.lower()[-4:]
        df["month"] = mnth
        df["year"] = year
        year_2024 = pd.concat([year_2024, df])

year_2024.to_csv(Path("..") / "fpi_2024.csv")
year_2024.to_parquet(Path("..") / "fpi_2024.parquet")
