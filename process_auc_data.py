"""
Process the AUC data from the HTML files downloaded from the FPI website. The
CSVs with "table0" in the name are the ones with the data we need. The others are just metadata.
date: 2026-17-07
"""

import pandas as pd
import os


def process_auc_clean_cols(dt):
    """
    Handling the multi-index columns by transposing the first 3 rows to get the column names
    """
    # Drop the column with index - it has Sr No
    if dt.iloc[:, 0].str.contains("Sr", na=False).sum():
        dt.drop(columns=dt.iloc[:, 0].name, inplace=True)

    # Column with "Sectors" make it the first column
    # The multi-index sits above it, which also has the
    # Date.

    value_sectors = dt.index[dt["1"] == "Sectors"][0]
    colname = dt.iloc[: value_sectors + 1].transpose()

    # drop the first row with NA
    colname = colname[1:]
    # combine the multi-index columns into a single level by joining the values with a colon
    colname = colname.fillna("NEC")
    col_list = colname.T.agg(lambda x: ":".join(x.values))
    print(colname)
    return col_list, value_sectors


IN_FOLDER = "auc_data/raw/table0"
auc_files = [os.path.join(IN_FOLDER, f) for f in os.listdir(IN_FOLDER)]
print(auc_files)

full_dt = pd.DataFrame()
for dat_file in auc_files:
    print(f"Processing file: {dat_file}")
    dt = pd.read_csv(
        dat_file,
        skip_blank_lines=True,
    )
    col_list, value_sectors = process_auc_clean_cols(dt)
    # reassign the new column names to the dataframe
    dt.columns = ["Sectors"] + list(col_list)
    dt.set_index("Sectors", inplace=True)

    # drop the first 3 rows which are now redundant
    dt = dt[value_sectors + 1 :]
    # asset under custody columns in INR crores
    dt = dt[
        dt.columns[
            (dt.columns.str.contains("AUC"))
            & (dt.columns.str.contains("INR"))
            & (dt.columns.str.contains("Equity|Debt"))
            & (~dt.columns.str.contains("Mutual"))
        ]
    ]
    # print(dt.head())
    combined_data = pd.DataFrame()
    dates_col = dt.columns.str.extract(r"([A-Z][a-z].*\s[0-9]*):")[0].unique()
    for date in dates_col:
        print(f"Processing date: {date}")
        dt_date = dt[dt.columns[dt.columns.str.contains(date)]]
        dt_date.columns = [col.split(":")[-1] for col in dt_date.columns]
        dt_date.insert(0, "Date", date)
        dt_date.reset_index(inplace=True)
        print(dt_date)
        # adding debt columns to the dataframe
        debt_columns = dt_date.columns[dt_date.columns.str.contains("Debt")]
        select_cols = ["Sectors", "Date", "Equity"]
        select_cols = select_cols + list(debt_columns)
        dt_date = dt_date[select_cols]
        # dt["Equity"] =
        # print(dt_date[dt_date.columns.str.contains("Equity")])
        print(dt_date)
        combined_data = pd.concat([combined_data, dt_date])

        # return combined_data

    full_dt = pd.concat([full_dt, combined_data], ignore_index=True, axis=0)

    full_dt["Date"] = pd.to_datetime(full_dt.Date)  # , format="%b %Y")

    # full_dt["Equity"] = full_dt["Equity"].str.replace(",", "").astype(float)

    # Each [sector-quarter] has two data points reported. One is provisional and the other is actual.
    # To save time calculating an average at {sector-date} level. There will be minor differences in
    # the numbers here compared to actual. The changes in provisional to actual is <0.2%.
    full_dt["Equity"] = full_dt["Equity"].astype(float)
    full_dt[debt_columns] = full_dt[debt_columns].apply(pd.to_numeric, errors="coerce")
    # full_dt = full_dt.groupby(["Sectors", "Date"])["Equity"].agg("mean").reset_index()
    full_dt = full_dt.groupby(["Sectors", "Date"]).agg("mean").reset_index()
    full_dt["year"] = full_dt.Date.dt.year
    full_dt["month"] = full_dt.Date.dt.month

# Debt columns
debt_columns = full_dt.columns[full_dt.columns.str.contains("Debt")]
full_dt[debt_columns] = full_dt[debt_columns].apply(pd.to_numeric, errors="coerce")
full_dt["Debt_general"] = full_dt["Debt General Limit"] + full_dt["Debt"]
full_dt.rename(columns={"Debt VRR": "Debt_VRR", "Debt-FAR": "Debt_FAR"}, inplace=True)
full_dt.drop(columns=["Debt General Limit", "Debt"], inplace=True)
# saving the file
full_dt.to_csv("auc_data/processed/combined_auc_equity_clean_test.csv", index=False)
