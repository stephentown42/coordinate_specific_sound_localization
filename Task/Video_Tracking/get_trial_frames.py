'''
get_trial_frames.py

Identifies frames in video around the time of stimulus presentation.
This allows us to reduce the number of frames required for tracking
and to focus on those frames when the subject is likely to be at the
central spout (reducing the range of behavioral conditions we track).

Stephen Town - October 2020
'''

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# Settings
fS = 48848.125  # Sample rate of stimulus device (Hz)
tWindow = np.array([-1.5, 1.5])    # Seconds

parent_dir = '/home/stephen/Documents/CoordinateFrames/DLC_Tracking'
files = {
    'behavior': '22_10_2020 level54_Eclair 16_14_05.320 Block_J8-219.txt',
    'frames': '2020-10-22_Track_16-14-14.txt'
    }


def select_frames_around_start_time(bd, ft, window_samps):

    new_ft = []

    for rIdx, row in bd.iterrows():

        start_time = row['StartTime'] + tWindow[0]
        start_samp = np.round(start_time * fS)
        frame_idx = ft['TDT_Sample'].between(start_samp, start_samp + window_samps[0])

        new_ft.append(ft.loc[frame_idx])

    return pd.concat(new_ft)


def visualize_frame_times(ft, new_ft):

    plt.style.use('ggplot')
    fig, ax = plt.subplots(1, 1)

    ft.plot.scatter(x='FrameCount', y='TDT_status', ax=ax, s=6, c='#888888', label='All')
    new_ft.plot.scatter(x='FrameCount', y='TDT_status', ax=ax, s=2, c='r', label='Selected')

    ax.set_xlabel('Frame')
    ax.set_ylabel('White Bar Signal')
    
    plt.legend(loc=1, shadow=True, facecolor='w')
    plt.tight_layout()
    plt.show()


def main():

    bd = pd.read_csv(os.path.join(parent_dir, files['behavior']), delimiter='\t')
    ft = pd.read_csv(os.path.join(parent_dir, files['frames']), delimiter='\t')

    window_samps = np.round(np.diff(tWindow) * fS)
    new_ft = select_frames_around_start_time(bd, ft, window_samps)

    visualize_frame_times(ft, new_ft)
    


if __name__ == '__main__':
    main()
