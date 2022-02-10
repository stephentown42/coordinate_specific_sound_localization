'''
Identify video files associated with each behavioral session in which probe trials have been flagged for investigation

2021-12-18: Created by Stephen Town
'''

from pathlib import Path
from shutil import copy2

import pandas as pd
from pandas._libs import missing

# Read in the metadata listing the blocks to look for
repo_dir = Path(r'Analysis\Null_responses')
summary_file = repo_dir / 'First_10_sessions.csv'
df = pd.read_csv(summary_file)

# Ignore individual trial data and get the unique blocks
blocks = df[['ferret','block']].drop_duplicates()

# Check that the path to each block exists on this machine
blocks['path'] = Path(r'G:\UCL_Behaving')
blocks['path'] = blocks['path'] / blocks['ferret'] / blocks['block']
blocks['path_exists'] = blocks['path'].apply(Path.exists)

# Flag any blocks without data
if not all(blocks['path_exists']):
    missing_blocks = blocks[blocks['path_exists']==False]
    print(missing_blocks)

# Find avi files within blocks
def find_avi(x:Path):
    files = x.glob('*.avi')
    return next(files)

blocks['video'] = blocks['path'].apply(find_avi)

# Save list of video files
output_file = repo_dir / 'video_files.csv'
blocks.to_csv(output_file, index=False)

# Copy video files and frame times to analysis directory
dest_dir = Path(r'C:\Users\Squid\Videos\CoordinateFrames')
for _, row in blocks.iterrows():

    copy2( row['video'], dest_dir)

    frame_time_file = row['video'].with_suffix('.txt')
    copy2( frame_time_file, dest_dir)
