# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 13:18:02 2024

@author: drewm
"""

# Usual library imports
import json
import pandas as pd
import numpy as np
import requests

# Set some parameters
start = "1980-01-01"
end = "2023-12-31"
county = ["01081"]  # FIPS Code

# Set base URL, and pull the json data down using requests
base_url = "http://data.rcc-acis.org/MultiStnData"
input_dict = {"county": county, "meta": [], 
              "sdate": start, "edate": end, 
              "elems": "maxt,mint,avgt"}
with requests.post(base_url, json=input_dict) as response:
    rawjson = response.content

# Convert raw json to a Python variable
newdata = json.loads(rawjson)['data']

# Here we convert the newdata variable to a Pandas dataframe

# Set some more parameters that will be reused
dates = pd.date_range(start=start,end=end)
columns = ["maxt", "mint", "avgt"]

station1 = pd.DataFrame(
    [[(float(item) - 32) * (5 / 9) if item != 'M' else None for item in sublist] for sublist in newdata[0]['data']],
    index=dates,
    columns=columns
)
station2 = pd.DataFrame(
    [[(float(item) - 32) * (5 / 9) if item != 'M' else None for item in sublist] for sublist in newdata[1]['data']],
    index=dates,
    columns=columns
)
station3 = pd.DataFrame(
    [[(float(item) - 32) * (5 / 9) if item != 'M' else None for item in sublist] for sublist in newdata[2]['data']],
    index=dates,
    columns=columns
)
station4 = pd.DataFrame(
    [[(float(item) - 32) * (5 / 9) if item != 'M' else None for item in sublist] for sublist in newdata[3]['data']],
    index=dates,
    columns=columns
)

# station1 = pd.DataFrame(((newdata[0]['data'] - 32) * (5 / 9)), index=dates, columns=columns1)
# station2 = pd.DataFrame(((newdata[1]['data'] - 32) * (5 / 9)), index=dates, columns=columns2)
# station3 = pd.DataFrame(((newdata[2]['data'] - 32) * (5 / 9)), index=dates, columns=columns3)
# station4 = pd.DataFrame(((newdata[3]['data'] - 32) * (5 / 9)), index=dates, columns=columns4)

station1.to_csv('station1data.csv')
station2.to_csv('station2data.csv')
station3.to_csv('station3data.csv')
station4.to_csv('station4data.csv')

# Might join them into one later, however for now we will keep them separate
# alldata = station1.join(station2)
# alldata.insert(0, 'county', newdata[1]['meta']['county'])
# alldata.insert(1, 'uid', newdata[1]['meta']['uid'])

### THIS MAY BE USED LATER,
###     FOR NOW WE TAKE A MORE DIRECT APPROACH TO ENSURE VALIDITY

# With some pandas gymnastics, loop through the json data and put it in a dataframe
# appended_data = []

# for i in range(len(newdata)):
#     data = pd.DataFrame(newdata[i]['data'], index=dates, columns=columns)
#     data.insert(0,"county", newdata[i]['meta']['county'] )
#     data.insert(1,"uid", newdata[2]['meta']['uid'] )
#     appended_data.append(data)
    
# appended_data = pd.concat(appended_data)