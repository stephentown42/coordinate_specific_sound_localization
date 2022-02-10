# Null responses

The goal of this analysis is to determine whether animals attempted to respond at spouts other than the East or West during initial presentation of probe sounds.

## Analysis pipeline
1. Identify probe trials from the first N sessions (here, N=10) that animals were tested with probe sounds using [identify_first_probe_sessions.py](identify_first_probe_sessions.py) to generate [First_10_sessions.csv](First_10_sessions.csv)
2. Check that the local PC has access to videos from each of those blocks (some machines don't have space for the full project data). Running [identify_video_files.py](identify_video_files.py) will identify the videos within each block, summarize the data available in a table ([video_files.csv](video_files.csv)) and copy the videos and associated frame information in a corresponding text file into a selected directory.
3. Run DeepLabCut (see below for details)
4. Analyse paths

## DeepLabCut (DLC)

Plotting of all head positions from DLC output (stored in [h5 files](Analysis/Null_responses/dlc_output)) is done via [plot_head_positions.py](plot_head_positions.py) to validate results.

[<img src="Analysis/Null_responses/path_analysis/images/All_frames/2018-10-03_Track_09-03-35DLC_resnet50_F1700_ProbeTracksDec18shuffle1_330000.png">](Analysis/Null_responses/path_analysis/images/All_frames/2018-10-03_Track_09-03-35DLC_resnet50_F1700_ProbeTracksDec18shuffle1_330000.png)


## Path Analysis

For this relatively simple analysis, we start by focussing on the head (i.e. a single landmark that should be visible on most frames). We first extract the head positions from the output files produced by DLC using [get_head_positions.py](get_head_positions.py) to give summary files of head position in each frame as csv files ('Analysis/Null_responses/path_analysis/head_positions'). This step also allows us to move to analysis entirely within the repository with no further reference to data elsewhere on disk.

We then select the frames around the time of each trial and obtain the head trajectory within this period using [get_head_tracks.py](get_head_tracks.py) to give a smaller csv file in 'Analysis/Null_responses/path_analysis/head_track_varFrames'

Finally we plot that data in a separate visualization script: [plot_head_tracks.py](plot_head_tracks.py).


