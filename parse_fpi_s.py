# Parsing the list of Registered FPI
# source https://www.fpi.nsdl.co.in/reports/registeredfiisafpi.aspx
# Nov 29, 2025
# sandeep.

import os
from pathlib import Path
import pandas as pd
import re

with open("data_fpi.txt", "r") as f:
    text = f.read()

# split each unit of data pertaining to each FPI
result = re.split(r"(\d+\nName)", text)
data1 = pd.DataFrame(result, columns=["FPI_text"])

print(data1.FPI_text[4])


def text_between(txt, left_txt, right_txt):
    return txt.split(left_txt)[-1].split(right_txt)[0].strip()


delimiting_text = {
    "name": [":", "Registration No."],
    "registration_no": ["Registration No.", "Category of FPI"],
    "category": ["\nCategory of FPI", "Address"],
    "fpi_address": ["Address", "SubCategory of FPI"],
    "sub_category": ["SubCategory of FPI", "Valid upto"],
    "validity": ["Valid upto", "Country Name"],
    "country_name": ["Country Name", "Status"],
    "status_fpi": ["Status", "Name"],
}

for keys, value_list in delimiting_text.items():
    data1[keys] = data1.FPI_text.apply(
        lambda txt: text_between(txt, left_txt=value_list[0], right_txt=value_list[1])
    )

fpi_specs = data1[~data1["registration_no"].str.contains("Name")]
fpi_specs = fpi_specs.drop(columns="FPI_text", axis=1)

fpi_specs.to_csv("fpi_clean.csv")

print(fpi_specs)
# print(data1)
