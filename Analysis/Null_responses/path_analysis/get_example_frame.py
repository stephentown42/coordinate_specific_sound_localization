'''
Get sample frames from a video for each subject as example data for publication figure

For each image also add the bodyparts and skeleton

'''

from pathlib import Path
import os

import cv2
import numpy as np
import pandas as pd
from pandas.core import frame
from pandas.tseries import offsets

def check_path(file_path: str):
    return os.path.exists(file_path)



def get_frame(file_path: str, frame_no: int) -> np.ndarray:
    ''' Read specific frame from video for annotation'''

    cap = cv2.VideoCapture(file_path)
    
    try:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)        
        success, image = cap.read()

        if success:
            return image
        else:
            print('Image not returned successfully')
            raise RuntimeError
    
    except RuntimeError:
        print('Failed to set video position')


def get_tracking_data(file_path: str, frame_no: int):
    ''' Load tracking data for one or more landmarks from h5 file'''

    df = pd.read_hdf(file_path)
    scorer = df.columns.get_level_values(0)[0] #you can read out the header to get the scorer name!
    
    df = df[scorer]
    return df[df.index == frame_no]
    

def draw_landmarks(im: np.ndarray, data: pd.DataFrame, ferret: str) -> np.ndarray:

    body_colors = dict(
        nose = (233,1,118),
        head = (217,166,2),
        shoulders = (93,168,216),
        spine = (172,244,123),
        tail = (2,3,234),
    )

    # Apply offset for Dory
    offset_x = 0
    if ferret == 'F1811_Dory':
        offset_x += 640

    # Plot skeleton
    for landmark in body_colors.keys():

        current_x = int(data[landmark]['x'].to_numpy()[0]) + offset_x
        current_y = int(data[landmark]['y'].to_numpy()[0]) 
            
        if not landmark == 'nose':
            im = cv2.line(im, (previous_x, previous_y), (current_x, current_y), (255, 255, 255), thickness=1)        

        previous_x = current_x              # Remember positions to plot skeleton on next iteration       
        previous_y = current_y

    # Plot landmarks        
    for (landmark, color) in body_colors.items():
        
        current_x = int(data[landmark]['x'].to_numpy()[0]) + offset_x
        current_y = int(data[landmark]['y'].to_numpy()[0])
        
        im = cv2.circle(im, (current_x, current_y), radius=4, color=color, thickness=-1)
    
    return im


def main():
    
    # Settings and paths
    frame_no = 2000

    tracking_dir = Path(r'C:\Users\Squid\Documents\Python\DeepLabCut\tracking_results')
    save_dir = Path(r'Analysis\Null_responses\dlc_output')

    # Load video metadata
    video_files = pd.read_csv('Analysis/Null_responses/video_files.csv')

    # For each ferret
    for ferret, fvids in video_files.groupby('ferret'):

        # Get image
        vid_path = fvids['video'].iloc[0]
        im = get_frame(vid_path, frame_no)

        # Get tracking data
        search_str = vid_path.split('\\')[-1].replace('.avi', '*')
        tracking_path = next(tracking_dir.glob(search_str))
        landmarks = get_tracking_data(tracking_path, frame_no)

        # Plot landmarks on image 
        im = draw_landmarks(im, landmarks, ferret)
        
        # Save as jpg    
        save_file = f"{tracking_path.name[0:25]}_Frame{frame_no}.jpg"
        cv2.imwrite( str(save_dir / save_file), im)

        # Print output to console
        print(f"{ferret}: {save_file}")
    


   
   
if __name__ == '__main__':
    main()
