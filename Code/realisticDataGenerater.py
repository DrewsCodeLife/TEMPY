# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 11:19:47 2024

@author: drewm

This file generates pre-defined data which can be run through the statistics
    calculator and plotter to ensure validity of the derived statistics.
"""
import pandas as pd
import math
import numpy as np

# Initialize list to collect data
data = []

# Number of years in your simulation (assuming 385704 data points)
numYears = math.floor(385704 / 365)

# Parameters for the temperature generation
#   fetched from Lee County 1980-01-01 to 2023-12-31 simulation statistics
amp_surface = 40.92351364  # Surface temperature variation (Celsius)
amp_20mm = 37.73984216     # 0.02 m temperature variation (Celsius)
baseline_surface = 24.06985359  # Baseline surface temperature (Celsius)
baseline_20mm = 24.03072396     # Baseline for 0.02m depth

# Function to simulate temperature
def simulate_temperature(day_of_year, hour, amp, baseline, peak_day=183, peak_hour=12):
    year_variation = amp * np.sin(2 * np.pi * (day_of_year - peak_day) / 365)
    day_variation = amp * 0.25 * np.sin(2 * np.pi * (hour - peak_hour) / 24)
    temperature = baseline + year_variation + day_variation
    return temperature

# Loop over years, days, and hours to generate the temperature data
for year in range(numYears):
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        days_in_year = 366  # Leap year
    else:
        days_in_year = 365

    for day in range(days_in_year):
        for hour in range(24):
            # Calculate temperature for surface and 0.02 m depth
            surface_temp = simulate_temperature(day, hour, amp_surface, baseline_surface)
            temp_20mm = simulate_temperature(day, hour, amp_20mm, baseline_20mm)
            
            # Store the data in a dictionary and append to the list
            data.append({
                'surface': surface_temp,
                '0.02 m': temp_20mm,
                'datetime': f'{year + 1980}-{day + 1}-{hour}:00'
            })

# Create DataFrame from the list of dictionaries
df = pd.DataFrame(data)

df.to_csv('generated_data.csv')

