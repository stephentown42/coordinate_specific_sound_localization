"""


"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import seaborn as sns

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../../..')))
from Analysis import ferrets
from Analysis import cf_behavior as cf


original_data = Path('Analysis/Main/Data/Original')
save_summary = False


def main():
    
    for ferret in ferrets:

        ferret['original_path'] = original_data / f"F{ferret['num']}_{ferret['name']}"

        # Get files with test results (but not training results from earlier levels)
        all_files = cf.list_files(ferret['original_path'] )
        print(f"{ferret['name']}: Found {len(all_files)} files")

        # Load data but do minimal formatting
        behavior = cf.load_behavioral_files(all_files)      
        print(f"Loaded {behavior.shape[0]} trials")

        # Optional save
        if save_summary:            
            summary_path = original_data.parent / 'Summary' / (ferret['name'] + '.csv')
            behavior.to_csv(summary_path)

        # Add columns with timing and angular data
        behavior = cf.add_timing_columns(behavior)
        behavior = cf.format_angular_values(behavior)

        behavior['Response'] = (behavior['Response'] - 3) / 6  # convert to binary (2021-07-04: Confirmed this was used for all animals regardless of training/task)

        # Exclude correction trials and trials with multiple stimuli
        test_data = cf.remove_correction_trials(behavior)
        test_data = cf.remove_repeatStim_trials(test_data)
        print(f"Test data: {test_data.shape[0]} / {behavior.shape[0]} trials")

        # Identify probe data 
        test_data = cf.flag_probe_trials(test_data, ferret['task'], ferret['valid_loc'])
        test_data['not_probe'] = test_data['not_probe'].astype(int)

        # Save formatted data
        formatted_path = original_data.parent / 'Formatted' / f"F{ferret['num']}_{ferret['name']}.csv"
        test_data.to_csv( formatted_path) 


if __name__ == '__main__':
    main()