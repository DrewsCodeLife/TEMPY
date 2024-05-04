# -*- coding: utf-8 -*-
"""
Created on Sat May  4 13:42:01 2024

@author: drewm
"""

import pandas as pd
import numpy as np

# Load your Excel file
df = pd.read_excel('testProj-Simulation.xlsx')

# Reshape the data to have one day per row
daily_data = df['Temperature'].values.reshape(-1, 24)

# Calculate the max temperature for each day
daily_max = np.max(daily_data, axis=1)

# Pad daily_max with np.nan
daily_max_padded = np.pad(daily_max, (0, 7 - daily_max.shape[0] % 7), mode='constant', constant_values=np.nan)

# Reshape so each row represents a week
weekly_data = daily_max_padded.reshape(-1, 7)

# Calculate the average max temperature for every set of 7 consecutive days
weekly_avg = np.nanmean(weekly_data, axis=1)

# Find the maximum of those averages
max_avg = np.nanmax(weekly_avg)

print(f"The maximum average temperature over any 7-day period is {max_avg}")

