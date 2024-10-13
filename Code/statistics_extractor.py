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

sim_results = pd.read_csv('generatedData.csv')

# Each dictionary will contain 'year : year_average' pairs for the gui
# max7daySurf = dict()
# max1daySurf = dict()
max7day20mm = dict()
max1day20mm = dict()
min1daySurf = dict()

sheetRowLength = len(sim_results)

numDays = sheetRowLength / 24
numYears = math.floor(numDays / 365)

# Each of these dictionaries will contain:
#   'year : list of n-day averages'
# max7daySurfVals = defaultdict(list)
# max1daySurfVals = defaultdict(list)
max7day20mmVals = defaultdict(list)
max1day20mmVals = defaultdict(list)
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
            values20mm = []
            for hour in range(0, 24):
                values20mm.append(
                    sim_results['0.02 m'][(366 * year + day) * 24 + hour]
                )
                valuesSurf.append(
                    sim_results['surface'][(366 * year + day) * 24 + hour]
                )
            max1day20mmVals[year].append(max(values20mm))
            min1dayVals[year].append(min(valuesSurf))
            
        for i in range(0, 363):
            if i < 359:
                max7day20mmVals[year].append(
                    sum(max1day20mmVals[year][i: i + 7]) / 7
                    )
    else:
        for day in range(0, 365):
            valuesSurf = []
            values20mm = []
            for hour in range(0, 24):
                values20mm.append(
                    sim_results['0.02 m'][(365 * year + day) * 24 + hour]
                )
                valuesSurf.append(
                    sim_results['surface'][(365 * year + day) * 24 + hour]
                )
            max1day20mmVals[year].append(max(values20mm))
            min1dayVals[year].append(min(valuesSurf))
            
        for i in range(0, 362):
            if i < 358:
                max7day20mmVals[year].append(
                    sum(max1day20mmVals[year][i: i + 7]) / 7
                    )

    max7day20mm[year] = max(max7day20mmVals[year])
    max1day20mm[year] = max(max1day20mmVals[year])
    min1daySurf[year] = min(min1dayVals[year])
    
    # For every set of 5 years, add each year's data into the relative index
    int_max_7day_averages[year // 5] = int_max_7day_averages[year // 5] + max7day20mmVals[year]
    int_max_1day_averages[year // 5] = int_max_1day_averages[year // 5] + max1day20mmVals[year]
    int_min_1day_averages[year // 5] = int_min_1day_averages[year // 5] + min1dayVals[year]
    
max7Yearly = dict()  # contains 5 year average of yearly max 7 day average
max1Yearly = dict()  # contains 5 year average of yearly max 1 day max
min1Yearly = dict()  # contains 5 year average of yearly min 1 day min

for year in range(0, numYears, 5):
    end_year = min(year + 4, numYears - 1)
    interval = end_year - year + 1
    
    max7Yearly[year // 5] \
        = sum(max7day20mm[y] for y in range(year, end_year + 1)) / interval
    max1Yearly[year // 5] \
        = sum(max1day20mm[y] for y in range(year, end_year + 1)) / interval
    min1Yearly[year // 5] \
       = sum(min1daySurf[y] for y in range(year, end_year + 1)) / interval

statistics = [max7Yearly, max1Yearly, min1Yearly]
titles = [
    '5-Year Averaged Yearly Maximum 7-Day Rolling Temperatures (44-Year Simulation, 20mm)', 
    '5-Year Averaged Yearly Maximum Daily Temperatures (44-Year Simulation, 20mm)',
    '5-Year Averaged Yearly Minimum Daily Temperatures (44-Year Simulation, Surface)',
    ]
stat_names = ['Temperature at 20mm', 'Temperature at 20mm', 'Surface temperature']
file_names = ['Rolling Average Max At 20mm',
              'Max Daily at 20mm',
              'Min Daily at Surface'
              ]

years = np.arange(1980, 2024, 5)
all_years = np.arange(1980, 2024)

for i, stat in enumerate(statistics):
    plt.figure(figsize=(12,6))
    
    y_values = [stat[j] for j in range(len(stat))]
    
    # extended_years = np.array([1980 + (j + i * 5) for j in range(5)])
    
    # plt.plot(years, y_values, marker='o', label=f'Statistic {i + 1}')
    for j in range(len(stat)):
        plt.hlines(y_values[j], years[j], years[j] + 5, color='b', linewidth=2, label=stat_names[i] if j == 0 else "")
    
    ax = plt.gca()
    if i == 0:  # If 7-day max
        ax.set_ybound(52, 70)
        plt.scatter(all_years, max7day20mm.values(), color='r', alpha=.75, label=f'Yearly {stat_names[i]}', zorder=3)
    elif i == 1:  # If 1-day max
        ax.set_ybound(52, 70)
        plt.scatter(all_years, max1day20mm.values(), color='r', alpha=.75, label=f'Yearly {stat_names[i]}', zorder=3)
    else:  # Else 1-day minimum
        ax.set_ybound(-12, 0)
        plt.scatter(all_years, min1daySurf.values(), color='r', alpha=.75, label=f'Yearly {stat_names[i]}', zorder=3)
    
    
    # Formatting the plot
    plt.title(titles[i])
    plt.xlabel('Year')
    plt.ylabel('Temperature (C)')
    plt.xticks(years)  # Ensure x-ticks are labeled correctly
    plt.legend()
    plt.grid()

    plt.savefig(file_names[i] + '.png')

    # Show the plot
    plt.show()
