# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 12:37:19 2024

@author: drewm
"""
import pandas as pd
import numpy as np

# Parameters
num_days = 366
hours_per_day = 24

# Create an empty DataFrame to store the data
data = []

# Generate data for 365 days with 24 hourly readings per day
for day in range(num_days):
    for hour in range(hours_per_day):
        # Simple structure: every day has flat temperatures, with minor hourly variation
        # For example, every day has 20 as the baseline, with max at hour 12 (noon)
        surf_temp = 20 + (5 if hour == 12 else 0)  # Max at noon for surface
        depth_temp = 18 + (4 if hour == 12 else 0)  # Max at noon for 0.02 m depth

        # Add data to the list
        data.append({
            'surface': surf_temp,
            '0.02 m': depth_temp,
            'datetime': f'2024-D{day + 1}-H{hour}'  # Label for clarity
        })

# Convert list to DataFrame
df = pd.DataFrame(data)

df.to_csv('generatedData.csv')