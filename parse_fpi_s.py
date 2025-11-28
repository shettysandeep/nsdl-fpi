# Parsing the list of Registered FPI
# source https://www.fpi.nsdl.co.in/reports/registeredfiisafpi.aspx
# Nov 29, 2025
# sandeep.

import os
from pathlib import Path
import pandas as pd


with open("fpi_list_nsdl_Nov28_2025.txt", 'r' ) as f:
    content = f.read()
i = 0
data = {}
for line in content:
    if line.startswith(i):
        


