"""
The aim of this function is to use the timestamps from behavioral data to recover the paths taken on each trial

This requires that we cross-reference the tracking results with the behavioral data. This requires a bit of thinking because the tracking files have slightly different timestamps from the timestamps in the behavioral file.

What unites the two datasets is the Block ID, but we only have these IDs for the video files and not the results from tracking. This shouldn't be too much of an issue as the tracking files are simply modified in name from videos.


This approach uses the variable duration between stimulus and response triggers rather than a fixed number of frames

Version History
    Created: 2021-12-?? by Stephen Town

"""

from dataclasses import dataclass
import json
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


def get_blocks_for_tracking_files(data_dir: str, video_info: str) -> pd.DataFrame:
    ''' Create a dataframe containing the path of tracking results for each block'''

    # Load and reformat video data 
    vidf = pd.read_csv( Path(video_info), skipinitialspace=True, usecols=['ferret','block','video'])
    vidf['video'] = vidf['video'].apply(lambda x: x.split('\\')[-1].replace('.avi',''))

    # Assign tracking files to relevant blocks (or empty if tracking not complete)
    vidf['tracking'] = np.nan

    for tracking_file in Path(data_dir).glob('*.csv'):
        idx = vidf[vidf['video'] == tracking_file.stem.split('DLC')[0]].index
        vidf.loc[idx, 'tracking'] = tracking_file

    blocks = vidf.dropna()

    # Report any blocks for which tracking data doesn't exist
    print(f"Analysing {blocks.shape[0]} of {vidf.shape[0]} blocks")
    
    return blocks[['tracking','ferret','block']]


def get_trial_tracks(tracking: pd.DataFrame, trial_data: pd.DataFrame, buffer_frames) -> pd.DataFrame:
    ''' Select tracking data that occurs between start and response time'''

    trial_paths = []
    
    for _, trial in trial_data.iterrows():
    
        start_idx = tracking[tracking['TDT_time'] < trial['StartTime']].index.max()
        end_idx = tracking[tracking['TDT_time'] < trial['RespTime']].index.max()

        idx = list(range(start_idx-buffer_frames, end_idx+buffer_frames))

        track = tracking.iloc[idx].copy()
        track['trial'] = trial['Trial']        

        trial_paths.append( track)
        
    return pd.concat(trial_paths)



def main():

    # Load settings
    with open('Analysis/Null_responses/path_analysis/config.json') as f:
        config = json.load(f)
    
    # Get blocks for each tracking file
    data_dir = 'Analysis/Null_responses/path_analysis/head_positions'
    video_info = 'Analysis/Null_responses/video_files.csv'

    blocks = get_blocks_for_tracking_files(data_dir, video_info)

    # Load trial data for all blocks
    trial_data = Path('Analysis/Null_responses/First_10_sessions.csv')
    trials = pd.read_csv(trial_data)

    # For each block
    save_dir = Path('Analysis/Null_responses/path_analysis/head_track_varFrames')

    for _, block in blocks.iterrows():

        # Load head positions
        tracking = pd.read_csv(block['tracking'])

        # Filter behavioral data for block
        trial_data = trials[(trials['ferret'] == block['ferret']) & (trials['block'] == block['block'])]
        assert trial_data.shape[0] > 0

        # Get frame values around the time of the trial (these may require some cleaning later due to timing errors in camera frame times)
        tracks = get_trial_tracks(tracking, trial_data, config['var_buffer'])

        save_path = save_dir / f"{block['ferret']}_HT_{block['block']}.csv"
        tracks.to_csv(save_path, index=False)
        




if __name__ == '__main__':
    main()







