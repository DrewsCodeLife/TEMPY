# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 13:30:49 2024

@author: drewm
"""

import threading
import sys
import os

endEarly = threading.Event()
running = threading.Event()


proj_name = "Project Name"

if getattr(sys, 'frozen', False):
    proj_folder_long = os.path.dirname(sys.executable)
else:
    proj_folder_long = os.path.dirname(os.path.abspath(__file__))
    
proj_folder_parts = proj_folder_long.split('\\')

if len(proj_folder_parts) > 1:
    proj_folder = proj_folder_parts[0] \
        + '\\' \
        + proj_folder_parts[1] \
        + "\\...\\" \
        + proj_folder_parts[-1]
else:
    proj_folder = proj_folder_long
