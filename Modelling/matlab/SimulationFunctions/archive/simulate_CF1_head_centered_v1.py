# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 11:57:48 2019

@author: Town
"""

from datetime import datetime
import glob
from math import pi
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import sys

# Options
ferret = 'F1701_Pendleton'

# Define file paths
dirs = {'root': 'C:/Users/Town/CloudStation/CoordinateFrames/'}
dirs['behav'] = os.path.join( dirs['root'], 'Behavior')
dirs['analysis'] = os.path.join( dirs['root'], 'BehavioralAnalysis')
dirs['ferret'] = os.path.join( dirs['behav'], ferret)

# Check behavioral file exists
if not os.path.exists( dirs['ferret']):
    print('Ferret behavioral path does not exist')
    return

# Add module to path
sys.path.append(dirs['analysis'])
import cf_behavior as cf

# Load in data with which the animal was tested
frame = cf.behavioral_files_to_dataframe(dirs['ferret'], glob, pd, datetime)
test_data = cf.remove_correction_trials(frame)

# Get true ferret behavior
probe_results = cf.get_probe_performance(test_data, np, pd, ferret)

# Specify model
theta = np.linspace(-pi, pi, 120, endpoint=False)


def fun_1(theta):    
    return (np.cos(theta) + 1) / 2

model_1 = {'stim_cf':'world',
           'response_cf': 'world',
           'response_var':'p_spout_9',            
           'input': theta,
           'fun': fun_1}

model_1['output'] = model_1['fun']( model_1['input'])

plt.plot(model_1['input'], model_1['output'], xunits=radians)
plt.show()
