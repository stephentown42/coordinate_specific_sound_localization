"""
Generates a summary table with the performance of each animal
before and after swapping speakers

Created: 
    2021-07-05: Stephen Town

"""

import os, sys

from datetime import datetime
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath( os.path.join( os.path.dirname(__file__), '../../..')))
from Analysis import cf_behavior as cf
from Analysis.Speaker_swaps import ferrets

data_dir = Path('Analysis/Speaker_swaps/Data')


def get_session_datetime(file):
    """
    Strip session date time from file
    
    Parameters:
    ----------
    file : str
        Name of session 
        
    Returns:
    --------
    session_df : datetime
        Datetime that session began
    """
    
    [f_date, level, f_time, block] = file.split()
    date_string = f_date + ' ' + f_time[0:8]
    
    return datetime.strptime(date_string, '%d_%m_%Y %H_%M_%S')
    

def get_performance(file, task, valid_locations):

    df = cf.load_behavioral_files([file])
    df = cf.add_timing_columns(df)
    df = cf.format_angular_values(df)
    df = cf.flag_probe_trials(df, task, valid_locations)

    df = df[df['not_probe'] == 1]           # Keep non-probe trials
    df = df[df['CorrectionTrial'] == 0]     # Keep non-correction trials    

    return dict( nTrials=df.shape[0], nCorrect=df['Correct'].sum())
    

def list_swaps(file_path, ferrets):

    file_list = []

    for ferret in ferrets:

        ferret_path = file_path / ferret['name']

        for swap_path in ferret_path.glob('Swap*'):

            for file in swap_path.glob("*.txt"):
                
                performance = get_performance(file, ferret['task'], ferret['valid_loc'])

                file_list.append(
                    dict(
                        ferret = ferret_path.stem,
                        swap = int(swap_path.stem.replace("Swap","")),
                        name = file.name,
                        datetime = get_session_datetime(file.stem),
                        nCorrect = performance['nCorrect'],
                        nTrials = performance['nTrials']
                    )
                )

    return pd.DataFrame(file_list)


def main():

    swaps = list_swaps(data_dir, ferrets)
    
    save_path = data_dir / 'Speaker_Summary.csv'
    swaps.to_csv(save_path, index=False)


if __name__ == '__main__':
    main()