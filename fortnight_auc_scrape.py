"""
Download fortnightly AUC data from NSDL website and save it to the 'auc_data' directory.
author: Sandeep Shetty
date: 2026-06-16
"""

import requests
import calendar
import pandas
from bs4 import BeautifulSoup
from io import StringIO

import os
import glob
import shutil

URL = "https://www.fpi.nsdl.co.in/web/StaticReports/Fortnightly_Sector_wise_FII_Investment_Data/FIIInvestSector"
middle_day = 15
date_range = []
# Inconsistent month representation in the NSDL files
for year in range(2026, 2027):
    for i in range(1, 13):
        month_name = calendar.month_name[i]
        month_abbr = calendar.month_abbr[i]
        print(month_name)
        # print(f"Processing {month_name} {year}")
        last_day = calendar.monthrange(year, i)[1]
        url1 = f"{URL}_{month_name}{last_day}{year}.html"
        url2 = f"{URL}_{month_name}{middle_day}{year}.html"
        alt_url1 = f"{URL}_{month_abbr}{last_day}{year}.html"
        alt_url2 = f"{URL}_{month_abbr}{middle_day}{year}.html"
        date_range.append(url1)
        date_range.append(url2)
        date_range.append(alt_url1)
        date_range.append(alt_url2)
        print(url1)
        print(alt_url2)


header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.4 Safari/605.1.15",
}

for mn in date_range:
    response = requests.get(mn, headers=header)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        if soup.find_all("table"):
            for key, table in enumerate(soup.find_all("table")):
                dat = pandas.read_html(StringIO(str(table)))[0]
                dat.to_csv(
                    f"auc_data/raw/data_{mn.split('/')[-1].replace('.html', '')}_table{key}.csv",
                    index=False,
                )

        print(f"Downloaded: {mn}")

# collect all table0 into one place

source_dir = "./auc_data/raw/"
target_dir = "./auc_data/raw/table0"

# Create target directory if needed
os.makedirs(target_dir, exist_ok=True)

csv_files = glob.glob(os.path.join(source_dir, "*.csv"))
t0_files = [f for f in csv_files if "table0" in os.path.basename(f)]

# Loop and move all files
for file_name in t0_files:
    # Construct full file path
    source_path = os.path.join(source_dir, file_name)

    # Ensure it's a file (skips subfolders)
    if os.path.isfile(source_path):
        shutil.move(source_path, target_dir)

print("All files transferred successfully.")
