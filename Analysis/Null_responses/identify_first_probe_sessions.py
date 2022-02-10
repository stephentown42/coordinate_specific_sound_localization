"""

To look for responses at null ports, we first need to know the sessions (blocks) with which
animals were first tested with probe sounds. 

Note that we might not want all blocks, if we consider the possibility that animals learn not to 
go to null spouts with experience (and we're interested in maximising sensitivity here)
"""

from pathlib import Path
import os, sys

import numpy as np
import pandas as pd


sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../../..')))



def list_first_n_probe_dates(data_path: str, ferrets: list, n_files: int) -> pd.DataFrame:
    ''' Get a list of the datetimes for the first N sessions in which probe sounds were presented'''

    session_list = []

    for ferret in ferrets:

        # Load data and filter for probe sounds
        file_path = data_path / f"{ferret}.csv"
        df = pd.read_csv(file_path, skipinitialspace=True, usecols=['SessionDate','not_probe'], parse_dates=['SessionDate'])

        df = df[df['not_probe'] == 0]

        # Sort by date and take earliest n sessions
        df.sort_values(by='SessionDate', inplace=True)
        df.drop_duplicates(inplace=True)
        df['ferret'] = ferret

        session_list.append( df.iloc[0:n_files])

    session_list = pd.concat(session_list)
    session_list.drop(columns='not_probe', inplace=True)

    return session_list



def get_probe_trial_times(data_path: str, sessions: pd.DataFrame) -> pd.DataFrame:

    trial_data = []

    # For each subject
    for ferret, f_sessions in sessions.groupby(by='ferret'):

        # Load data and filter for probe sounds
        file_path = data_path / f"{ferret}.csv"

        df = pd.read_csv(file_path, parse_dates=['SessionDate'])        
        
        # For each session
        for session_date, _ in f_sessions.groupby(by='SessionDate'):

            session_data = df[df['SessionDate'] == session_date].copy()
            trial_data.append(session_data)
        
    trial_data = pd.concat(trial_data)
    trial_data.set_index('SessionDate', inplace=True)

    return trial_data




def get_block_name(data_path: str, sessions: pd.DataFrame) -> pd.DataFrame:
    ''' '''

    # Preassign
    sessions['block'] = 'Unknown'

    # For each session
    for idx, row in sessions.iterrows():

        # Search for behavioral file (which contains block name)
        session_path = data_path / row['ferret']
        assert session_path.exists()

        search_str = row['SessionDate'].strftime('%d_%m_%Y * %H_%M*.txt')
        files = session_path.glob(search_str)

        file_list = [f for f in files]
        assert len(file_list) == 1
        session_file = file_list[0]

        [_, _, _, block] = session_file.stem.split(' ')
        
        sessions['block'].loc[idx] = block

    sessions.set_index('SessionDate', inplace=True)

    return sessions



def main():

    # Q. How many sessions will you consider since the start of probe testing?
    n_files = 10

    # Consider only those with the same training in the world-centered task
    ferrets = ['F1701_Pendleton','F1703_Grainger','F1811_Dory']
    
    # Get the first n sessions and then the times of probe stimuli in each of those sessions
    data_path = Path('Analysis/Main/Data/Formatted')

    sessions = list_first_n_probe_dates(data_path, ferrets, n_files)
    
    trials = get_probe_trial_times(data_path, sessions)

    # Get block names from original data
    data_path = Path('Analysis/Main/Data/Original')

    blocks = get_block_name(data_path, sessions)

    # Combine block info with trial info, and save
    save_path = Path('Analysis/Null_responses')
    save_name = f"First_{n_files}_sessions.csv"

    trials = trials.join(blocks)
    trials.to_csv( save_path / save_name)




if __name__ == '__main__':
    main()