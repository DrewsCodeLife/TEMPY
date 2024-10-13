# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 11:49:53 2024

@author: drewm
"""

import json
import pandas as pd
import numpy as np
import requests
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

import fips_processor as fp

# "pcpn" = "precipitation" ???
elements = [
    {"name": "maxt", "interval": "mly", "duration": "mly",
     "reduce": "mean", "area_reduce": "county_mean"},
    {"name": "avgt", "interval": "mly", "duration": "mly",
     "reduce": "mean", "area_reduce": "county_mean"},
    {"name": "mint", "interval": "mly", "duration": "mly",
     "reduce": "mean", "area_reduce": "county_mean"},
    {"name": "pcpn", "interval": "mly", "duration": "mly",
     "reduce": "sum", "area_reduce": "county_mean"}]

states = 'AL,AK,AZ,AR,CA,CO,CT,DE,DC,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MT,NE,' \
    + 'NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,MD,MA,MI,MN,MS,MO,PA,RI,SC,SD,TN,TX,UT,' \
    + 'VT,VA,WA,WV,WI,WY'

start = "1950-01"
end = "2099-12"  # Some models stop in 2099

base_url = 'http://grid2.rcc-acis.org/GridData'
input_dict = {"state": states, "grid": "loca:wmean:rcp85",
              "sdate": start, "edate": end,
              "elems": elements}

while True:
    try:
        with requests.post(base_url, json=input_dict) as response:
            rawjson = response.content
    except:  # bare except because I don't know what response I might receive
        print("failed")
        continue
    else:
        break

newdata = json.loads(rawjson)['data']

print("Expect ", 150 * 12, " months long")
print("Actual: ", len(newdata))

# Print quantity of counties/sections in 1950-01
print(len(newdata[0][1])) # Only checks maxT

# Now convert to dataframe, so we can turn around and save it as an .xlsx file

dataset = pd.DataFrame(columns=['county', 'month',
                                'mint', 'maxt',
                                'avgt', 'pcpn'])

combined = []

for i in range(len(newdata)):
    maxt = pd.DataFrame(newdata[i][1], index=['maxt']).transpose()
    avgt = pd.DataFrame(newdata[i][2], index=['avgt']).transpose()
    mint = pd.DataFrame(newdata[i][3], index=['mint']).transpose()
    pcpn = pd.DataFrame(newdata[i][4], index=['pcpn']).transpose()
    combined_onemonth = pd.concat([maxt, avgt, mint, pcpn], axis=1)
    combined_onemonth.insert(0, 'month', newdata[i][0])
    combined_onemonth = combined_onemonth.reset_index().rename(
        columns={'index': 'fips_id'})
    combined_onemonth = combined_onemonth.merge(fp.county_df,
                                                on='fips_id',
                                                how='left')
    combined.append(combined_onemonth)
    print(i / len(newdata))
    
dataset = pd.concat(combined, ignore_index=True)
dataset.to_csv('projected_temps.csv', sep=',')
