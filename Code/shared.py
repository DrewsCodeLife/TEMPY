# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 13:30:49 2024

@author: drewm
"""

import queue
import threading

# Shared queue for communication between threads
q = queue.Queue()
endEarly = threading.Event()
running = threading.Event()