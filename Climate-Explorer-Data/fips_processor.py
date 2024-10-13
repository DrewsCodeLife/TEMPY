# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 13:10:09 2024

@author: drewm
"""

import pandas as pd
import re

with open('fips.txt', 'r') as file:
    lines = file.readlines()

data_lines = lines[16:]

# Run through the lines and remove excess white space, leaving only one space
proc_lines = [re.sub(r'\s+', ' ', line).strip() for line in data_lines]

state_dict = {}
for i in range(0, 55):
    # ID number is key, state name is value
    state_dict[proc_lines[i][:2]] = proc_lines[i][2:]

# With any luck, should skip all the states and jump to the county section
next_lines = proc_lines[56:]

county_df = pd.DataFrame(columns=['fips_id', 'County', 'State'])
for line in next_lines:
    # Insert new row at -1 index
    county_df.loc[-1] = [line[:5], line[5:], state_dict[line[:2]]]
    # Shift index by 1, so we can add at -1 again
    county_df.index = county_df.index + 1

# May be unnecessary, unclear. There may be value in keeping the OG ordering
county_df = county_df.sort_index()
