"""
- Extract the position of the head landmark on each frame from deeplabcut output 
- Get time for each frame 
- Save as csv for later analysis

TO DO:
- Output file sizes could be reduced without losing information by reducing precision of tracking output being saved (currently we're over-specifying values that only require one decimal place [or 6 d.p. in the case of frame times and likelihood])

"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


    
def load_tracking_data(file_path: Path) -> pd.DataFrame:
    ''' Load tracking data for one or more landmarks from h5 file'''

    df = pd.read_hdf(file_path)
    scorer = df.columns.get_level_values(0)[0] #you can read out the header to get the scorer name!
    return df[scorer]


def load_frame_samples(file_path: Path, tracking_file: str) -> pd.DataFrame:
    ''' Load frame samples from tab delimited files with same datetime prefix as tracking file '''
    
    file_path = file_path / f"{tracking_file}.txt"
    return pd.read_csv(file_path, delimiter='\t')


def join_frame_times(df, ft) -> pd.DataFrame:
    ''' Add frame time as an extra column to tracking data '''

    # Check that the two files have the same number of frames
    assert df.shape[0] == ft.shape[0]
    
    df.index = ft['TDT_time']
    return df


def main():
    
    # Define paths to data
    data_dir = Path('/home/stephen/Data/CF_probeTrialTracking')
    time_dir = Path('Analysis/Null_responses/path_analysis/frame_samps')
    save_dir = Path('Analysis/Null_responses/path_analysis/head_positions')
    
    # Settings
    tdt_fs = 48842.125              # TDT sample rate in Hz
    bodypart = 'head'

    # For each session
    for file_ in data_dir.glob('*.h5'):

        ft = load_frame_samples(time_dir, file_.stem[0:25])
        ft['TDT_time'] = ft['TDT_Sample'] / tdt_fs

        df = load_tracking_data(file_)
        df = join_frame_times(df, ft)

        df = df[bodypart].reset_index(level=0)

        save_path = save_dir / file_.name.replace('.h5', '.csv')
        df.to_csv(save_path, index=False)



if __name__ == '__main__':
    main()







