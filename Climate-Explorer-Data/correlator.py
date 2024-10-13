# -*- coding: utf-8 -*-
"""
Created on Sun Oct 13 12:05:36 2024

@author: drewm
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# lttpData = pd.read_csv('Lee County (excel extraction)-Simulation.csv')
climateData = pd.read_csv('station4data.csv')

# Create a figure
fig, ax = plt.subplots(figsize=(10, 6))

# Plot 'maxt'
ax.plot(climateData['Unnamed: 0'], climateData['maxt'], label='maxt', color='blue')

# Find where data is missing
missing_indices = climateData[climateData['maxt'].isna()].index

# Highlight missing data ranges
for start, group in climateData['maxt'].isna().astype(int).groupby(climateData['maxt'].isna().diff().ne(0).cumsum()):
    if group.iloc[0] == 1:
        ax.axvspan(climateData['Unnamed: 0'].iloc[group.index[0]], climateData['Unnamed: 0'].iloc[group.index[-1]], 
                   color='red', alpha=0.3, label='Missing Data' if start == 0 else "")

# Add labels, title, and legend
ax.set_title('Max Temperature with Missing Data Highlighted')
ax.set_xlabel('Date')
ax.set_ylabel('Temperature (°C)')
ax.legend()

plt.savefig('Station 4 Missing Data.png')

plt.show()

num_missing = climateData.isnull().any(axis=1).sum()
print(f"Missing {(num_missing / len(climateData)) * 100}%")
