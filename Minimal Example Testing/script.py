# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 16:59:16 2024

@author: drewm
"""

def runTest(BSparam1, BSparam2):
    total = 0
    print(BSparam1, " ", BSparam2)
    
    for i in range(0, 1000000):
        total = total + i
    
    print(total)