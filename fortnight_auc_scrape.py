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

URL = "https://www.fpi.nsdl.co.in/web/StaticReports/Fortnightly_Sector_wise_FII_Investment_Data/FIIInvestSector"
middle_day = 15
date_range = []
for year in range(2020, 2025):
    for i in range(1, 13):
        month_name = calendar.month_name[i]
        # print(f"Processing {month_name} {year}")
        last_day = calendar.monthrange(year, i)[1]
        url1 = f"{URL}_{month_name}{last_day}{year}.html"
        url2 = f"{URL}_{month_name}{middle_day}{year}.html"
        date_range.append(url1)
        date_range.append(url2)


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
                    f"auc_data/data_{mn.split('/')[-1].replace('.html', '')}_table{key}.csv",
                    index=False,
                )

        print(f"Downloaded: {mn}")
