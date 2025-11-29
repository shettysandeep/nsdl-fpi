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


# Parsing the text into structured columns
def name_fpi(txt):
    fpi_name = txt.split(":")[-1].split("Registration No.")[0].strip()
    return fpi_name


def reg_extract(txt):
    reg_no = txt.split("Registration No.")[-1].split("Category of FPI")[0].strip()
    return reg_no


def fpi_cat(txt):
    cat_fpi = txt.split("\nCategory of FPI")[-1].split("Address")[0].strip()
    return cat_fpi


def addrs(txt):
    addr = txt.split("Address")[-1].split("SubCategory of FPI")[0].strip()
    return addr


def subcat(txt):
    subcat1 = txt.split("SubCategory of FPI")[-1].split("Valid upto")[0].strip()
    return subcat1


def valid_upto(txt):
    valid_upto = txt.split("Valid upto")[-1].split("Country Name")[0].strip()
    return valid_upto


def country_name(txt):
    cntry_name = txt.split("Country Name")[-1].split("Status")[0].strip()
    return cntry_name


def status_r(txt):
    stat_r = txt.split("Status")[-1].split("Name")[0].strip()
    return stat_r


# ~~~~~~~~~~~~~~~~~
# Adding columns to dataset
# ~~~~~~~~~~~~~~~~~~
data1["Name_FPI"] = data1.FPI_text.apply(name_fpi)
data1["Registration_No"] = data1.FPI_text.apply(reg_extract)
data1["Category_FPI"] = data1.FPI_text.apply(fpi_cat)
data1["Address_FPI"] = data1.FPI_text.apply(addrs)
data1["Subcat_FPI"] = data1.FPI_text.apply(subcat)
data1["Valid_upto"] = data1.FPI_text.apply(valid_upto)
data1["Country_name_FPI"] = data1.FPI_text.apply(country_name)
data1["Status_FPI"] = data1.FPI_text.apply(status_r)

fpi_specs = data1[~data1["Registration_No"].str.contains("Name")]
fpi_specs = fpi_specs.drop(columns="FPI_text", axis=1)

fpi_specs.to_csv("fpi.csv")
