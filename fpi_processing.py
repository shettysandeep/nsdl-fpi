"""Code to clean up the variables of the FPI files obtained from the NSDL website"""

import pandas as pd
from pathlib import Path
from fpi_delimiting_text import cols_keep


class combine_data:
    def __init__(self, pathfile):
        self.cols_keep = cols_keep
        if isinstance(pathfile, Path):
            self.pathfile = pathfile
        else:
            self.pathfile = Path(pathfile)
        self.file_list = self.extract_files()

    def extract_files(self) -> list:
        # Combine all the months for year 2024
        if self.pathfile.is_dir():
            file_list = [
                itms for itms in self.pathfile.iterdir() if itms.with_suffix(".xlsx")
            ]
            return file_list
        else:
            [self.pathfile]

    def clean_combine(self):

        aug_df = pd.DataFrame()
        for itms in self.file_list:
            df = pd.read_excel(itms, engine="openpyxl")
            (
                df.rename(
                    columns={"TR_TYPE(*)": "TR_TYPE", "VALUE (in Rs)": "VALUE"},
                    inplace=True,
                )
            )
            df.loc[:, "TR_DATE"] = pd.to_datetime(df["TR_DATE"])
            df = df[self.cols_keep]
            mnth = itms.stem.lower()[:-5]
            year = itms.stem.lower()[-4:]
            df["month"] = mnth
            df["year"] = year
            aug_df = pd.concat([aug_df, df])
        return aug_df


if __name__ == "__main__":

    testpath = Path() / "nsdl_data" / "2025"
    file_2025 = combine_data(testpath)
    combined_2025 = file_2025.clean_combine()

    combined_2025.to_csv(Path("..") / "fpi_2025.csv")
    # year_2024.to_parquet(Path("..") / "fpi_2024.parquet")
