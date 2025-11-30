# Parsing the list of Registered FPI
# source https://www.fpi.nsdl.co.in/reports/registeredfiisafpi.aspx
# Nov 29, 2025
# sandeep.

import os
from pathlib import Path
import pandas as pd
import re
from fpi_delimiting_text import delimiting_text

class fpi_info():
    def __init__(self, file_path): #, apply_to=None):
        self.file_path=file_path
        self.apply_to=10
        self.df = self.begin_extract()

    def read_file(self):
        with open(self.file_path, "r") as f:
            text = f.read()
        return text

    def begin_extract(self):
        text_data = self.read_file()

        # split each unit of data pertaining to each FPI
        result = re.split(r"(\d+\nName)", text_data)
        data1 = pd.DataFrame(result, columns=["FPI_text"])
        #if self.apply_to is not None:
        #    return data1.loc[:self.apply_to]
        #else:
        return data1
                        
    
    def text_between(self, txt, left_txt, right_txt):
        return txt.split(left_txt)[-1].split(right_txt)[0].strip()

        # text to grab the relevant chunks of data

if __name__=="__main__":

    fpi_file = fpi_info(file_path="fpi_list_nsdl_Nov28_2025.txt")#, apply_to="all")
    df1 = fpi_file.df
    for keys, value_list in delimiting_text.items():
        df1[keys] = df1['FPI_text'].apply(
         lambda txt: fpi_file.text_between(txt, left_txt=value_list[0], right_txt=value_list[1])
            )

    fpi_data = df1[~df1["registration_no"].str.contains("Name")]
    fpi_specs = fpi_data.drop(columns="FPI_text", axis=1)
    fpi_specs.to_csv("fpi_clean_all.csv")
