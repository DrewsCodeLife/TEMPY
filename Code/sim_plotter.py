# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 08:35:14 2024

@author: drewm
"""

import pandas as pd
import plotly
import plotly.express as px

name = 'Lee County (excel extraction)-Simulation.xlsx'

sim_results = pd.read_excel(name)
histor_vals = pd.read_excel('01_0101_full_temp.xlsx')

sim_results = sim_results.drop(index=0) # first row is initialization

# Join date and time into a singular variable, drop individual columns
# sim_results['datetime'] = sim_results[['Date', 'time']].astype(str).agg(' '.join, axis=1)
# sim_results['datetime'] = sim_results['datetime'].str[:-8].str.strip()

sim_results['Date'] = \
    sim_results['Date'].astype(str).str.slice(stop=-8).str.strip()
sim_results['datetime'] = pd.to_datetime(
    sim_results['Date'].astype(str) + ' ' + sim_results['time'].astype(str),
    format='%Y-%m-%d %I:%M:%S %p')
sim_results = sim_results.drop(['Date', 'time'], axis=1)

# Make the same column for historical values so we can use it as a joining key
# histor_vals['DATE'] = \
#    histor_vals['DATE'].astype(str).str.slice(stop=-8).str.strip()
histor_vals['datetime'] = pd.to_datetime(
    histor_vals['DATE'].astype(str) + ' ' + histor_vals['TIME'].astype(str),
    format='%Y-%m-%d %I:%M:%S %p')
histor_vals = histor_vals.drop(['DATE', 'TIME'], axis=1)
# histor_vals['datetime'] = histor_vals[['DATE', 'TIME']].astype(str).agg(' '.join, axis=1).str.strip()
# histor_vals['datetime'] = histor_vals['datetime'].str[:-8].str.strip()

# Grab a subset of histor_vals, merge on datetime, keep observations that appear in both dataframes
merged_df = pd.merge(
    sim_results,
    histor_vals[['datetime', 'TEMPERATURE']], on='datetime', how='inner'
)

# Pivot_longer on temperature and surface so we can plot both
melted_df_surf = pd.melt(merged_df, id_vars='datetime',
                         value_vars=['surface', 'TEMPERATURE'],
                         var_name='variable',
                         value_name='value')
# Repeat for 20mm
melted_df_20mm = pd.melt(merged_df, id_vars='datetime',
                         value_vars=['0.02 m', 'TEMPERATURE'],
                         var_name='variable',
                         value_name='value')

surf_plot = px.line(melted_df_surf, x='datetime', y='value', color='variable')

under_plot = px.line(melted_df_20mm, x='datetime', y='value', color='variable')

# Save figure
plotly.offline.plot(surf_plot, filename='surface_plot.html')
plotly.offline.plot(under_plot, filename='mm20_plot.html')

newname = name[:-4] + 'csv'

sim_results.to_csv(newname)
