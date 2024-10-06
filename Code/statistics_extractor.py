# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 11:29:56 2024

@author: drewm
"""

# This file is equivalent in operation to "five_year_stats.py", the only
#   difference is that this file writes our statistics to a file, instead of
#   returning them from some function. This will aid in more rapid development,
#   testing, bug fixing, etc.

from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import openpyxl as xl
import pandas as pd
import math

sim_results = pd.read_csv('Lee County (excel extraction)-Simulation.csv')

# Each dictionary will contain 'year : year_average' pairs for the gui
max7daySurf = dict()
max1daySurf = dict()

min1daySurf = dict()

sheetRowLength = len(sim_results)

numDays = sheetRowLength / 24
numYears = math.floor(numDays / 365)

# Each of these dictionaries will contain:
#   'year : list of n-day averages'
max7daySurfVals = defaultdict(list)
max1daySurfVals = defaultdict(list)
min1dayVals = defaultdict(list)

# contains all of the weeks within a certain 5 year interval
int_max_7day_averages = defaultdict(list)
# all the days within a certain 5 year interval
int_max_1day_averages = defaultdict(list)
int_min_1day_averages = defaultdict(list)

# may need to later accommodate for the actual value of year
for year in range(0, numYears):
    # If the year is a leap year
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        for day in range(0, 366):
            valuesSurf = []
            for hour in range(0, 24):
                valuesSurf.append(
                    sim_results['surface'][(366 * year + day) * 24 + hour]
                )
            max1daySurfVals[year].append(max(valuesSurf))
            min1dayVals[year].append(min(valuesSurf))
            
        for i in range(0, 363):
            if i < 359:
                max7daySurfVals[year].append(
                    sum(max1daySurfVals[year][i : i + 7]) / 7
                    )
    else:
        for day in range(0, 365):
            valuesSurf = []
            for hour in range(0, 24):
                valuesSurf.append(
                    sim_results['surface'][(365 * year + day) * 24 + hour]
                )
            max1daySurfVals[year].append(max(valuesSurf))
            min1dayVals[year].append(min(valuesSurf))
            
        for i in range(0, 362):
            if i < 358:
                max7daySurfVals[year].append(
                    sum(max1daySurfVals[year][i : i + 7]) / 7
                    )

    max7daySurf[year] = max(max7daySurfVals[year])
    max1daySurf[year] = max(max1daySurfVals[year])
    min1daySurf[year] = min(min1dayVals[year])
    
    # For every set of 5 years, add each year's data into the relative index
    int_max_7day_averages[year // 5] = int_max_7day_averages[year // 5] + max7daySurfVals[year]
    int_max_1day_averages[year // 5] = int_max_1day_averages[year // 5] + max1daySurfVals[year]
    int_min_1day_averages[year // 5] = int_min_1day_averages[year // 5] + min1dayVals[year]
    
max7Yearly = dict()  # contains 5 year average of yearly max 7 day average
max1Yearly = dict()  # contains 5 year average of yearly max 1 day max
min1Yearly = dict()  # contains 5 year average of yearly min 1 day min

max7dayWeekly = dict()  # contains 5 year average of weekly max 7 day average
max1dayDaily = dict()  # contains 5 year average of daily max
min1dayDaily = dict()  # contains 5 year average of daily min

for year in range(0, numYears, 5):
    end_year = min(year + 4, numYears - 1)
    interval = end_year - year + 1
    
    max7Yearly[year // 5] \
        = sum(max7daySurf[y] for y in range(year, end_year + 1)) / interval
    max1Yearly[year // 5] \
        = sum(max1daySurf[y] for y in range(year, end_year + 1)) / interval
    min1Yearly[year // 5] \
       = sum(min1daySurf[y] for y in range(year, end_year + 1)) / interval

for interval in range(0, len(int_max_7day_averages)):
    # Calculate 5 year averages for the statistics
    max7dayWeekly[interval] \
        = sum(int_max_7day_averages[interval]) / len(int_max_7day_averages[interval])
    max1dayDaily[interval] \
        = sum(int_max_1day_averages[interval]) / len(int_max_1day_averages[interval])
    min1dayDaily[interval] \
        = sum(int_min_1day_averages[interval]) / len(int_min_1day_averages[interval])

statistics = [max7Yearly, max1Yearly, min1Yearly, max7dayWeekly, max1dayDaily, min1dayDaily]
stat_names = ['max7Yearly', 'max1Yearly', 'min1Yearly', 'max7dayWeekly', 'max1dayDaily', 'min1dayDaily']

years = np.arange(1980, 2024, 5)

for i, stat in enumerate(statistics):
    plt.figure(figsize=(12,6))
    
    y_values = [stat[j] for j in range(len(stat))]
    
    extended_years = np.array([1980 + (j + i * 5) for j in range(5)])
    
    #plt.plot(years, y_values, marker='o', label=f'Statistic {i + 1}')
    for j in range(len(stat)):
        plt.hlines(y_values[j], years[j], years[j] + 5, color='b', linewidth=2, label=stat_names[i] if j == 0 else "")
    
    # Formatting the plot
    plt.title(stat_names[i] + ' Over Time')
    plt.xlabel('Year')
    plt.ylabel('Temperature (C)')
    plt.xticks(years)  # Ensure x-ticks are labeled correctly
    plt.legend()
    plt.grid()

    plt.savefig(stat_names[i] + '.png')

    # Show the plot
    plt.show()
