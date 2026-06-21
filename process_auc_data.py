"""
Process the AUC data from the HTML files downloaded from the FPI website. The
CSVs with "table0" in the name are the ones with the data we need. The others are just metadata.
date: 2026-17-07
"""

import pandas as pd
import glob
import os


def collect_auc_data(input_folder):
    # Get all CSV files in the input folder
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))

    # Filter for files with "table0" in the name
    auc_files = [f for f in csv_files if "table0" in os.path.basename(f)]
    return auc_files


def process_auc_data(input_file, output_folder=None):

    df = pd.read_csv(
        input_file, skiprows=3, index_col=0
    )  # Skip the first 3 rows and set the first column as index
    return df


auc_files = collect_auc_data("auc_data")

full_dt = pd.DataFrame()

for file in auc_files:
    print(f"Processing file: {file}")
    dt = process_auc_data(file)
    # full_dt = pd.concat([full_dt, dt])
    print(dt.iloc[:, 1:2])
    break
# full_dt.to_csv("auc_data/processed/combined_auc_data.csv", index=False)

"""
        # Extract relevant columns (assuming 'Date' and 'AUC' are the columns we need)
        if 'Date' in df.columns and 'AUC' in df.columns:
            processed_df = df[['Date', 'AUC']]
            # Save the processed data to a new CSV file
            output_file = os.path.join(output_folder, os.path.basename(file))
            processed_df.to_csv(output_file, index=False)
        else:
            print(f"Warning: {file} does not contain the required columns.")

"""
