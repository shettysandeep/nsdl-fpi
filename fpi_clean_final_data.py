"""Making changes to data upstream to produce a single clean dataset.

1. Clean some of the variables.
2. bring in company details from a different file mapping ISIN
3. Return the combined parquet file.
"""

from datetime import datetime
from pathlib import Path

# from numpy import isin
import pandas as pd

# import calendar
import pyarrow as pa
import pyarrow.parquet as pq


class clean_and_merge:
    # returns the cleaned file & saves.

    def __init__(self, path2file, do_save, path2ISIN, save2file) -> None:
        self.CRORE = 10000000
        self.path2file = path2file  # FPI data
        print(self.path2file)
        self.isin_file = path2ISIN
        self.save2path = save2file
        self.yes_save = do_save

    def string_to_date(self, date_str):
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    def fpi_clean(self):
        df = pq.read_table(self.path2file)  # FII stock file
        df = df.to_pandas()
        df["ISIN"] = df["ISIN"].str.strip()
        df["mutual_fund"] = df.ISIN.apply(lambda x: 1 if x[:3] == "INF" else 0)
        df["value_crores"] = df["VALUE"] / self.CRORE
        df["TR_DATE"] = (
            df["TR_DATE"].astype(str).apply(lambda x: self.string_to_date(x.split()[0]))
        )
        return df  # bring ISIN clean data & merge

    def isin_file_clean(self):
        list_isin = pd.read_csv(self.isin_file)  # ISIN FILE
        list_isin["company_name"] = list_isin["company_name"].str.strip()
        list_isin["ISIN"] = list_isin["ISIN"].str.strip()
        return list_isin

    def merge_isin_and_fpi(self):
        isini_file = self.isin_file_clean()
        fpi = self.fpi_clean()
        fpi_comb = pd.merge(
            fpi, isini_file, left_on="ISIN", right_on="ISIN", how="left"
        )
        table = pa.Table.from_pandas(fpi_comb)
        if self.yes_save:
            print("file saved as --> {}".format(self.save2path))
            pq.write_table(table, self.save2path)
        return fpi_comb


if __name__ == "__main__":
    cl = clean_and_merge(
        path2file="fpi_data/fpi_id_2024_2025.parquet",
        do_save=True,
        path2ISIN="fpi_data/active_CM_DEBT_list.csv",
        save2file="fpi_data/fpi_id_2024_2025_mgd_jan2026.parquet",
    )
    dt = cl.self.merge_isin_and_fpi()
    print(dt.head())
