"""
Extract the head position from DLC .h5 files for all frames and plot


'figure.plot_results' adapted from https://github.com/DeepLabCut/DLCutils/blob/master/Demo_loadandanalyzeDLCdata.ipynb

"""

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass()
class figure():

    name: str
    size: tuple=(4,3)
    cmap: str='jet'

    def __post_init__(self) -> None:

        self.fig = plt.figure(figsize=self.size)
        self.save_name = self.name + '.png'


    def save(self, file_path: str) -> None:

        plt.savefig( Path(file_path) / self.save_name)


    def plot_results(self, df, bodyparts2plot, alphavalue:float=.2, pcutoff:float=.5):
        ''' Plots poses vs time; pose x vs pose y'''
        
        for bpindex, bp in enumerate(bodyparts2plot):
            Index=df[bp]['likelihood'].values > pcutoff
            
            plt.scatter(
                df[bp]['x'].values[Index],    
                df[bp]['y'].values[Index],
                c = df[bp].index[Index],
                marker = '.',
                alpha=alphavalue
            )

        plt.gca().invert_yaxis()
        plt.colorbar()     
    
    
def list_bodyparts(df: pd.DataFrame) -> list:
    ''' Get a list of bodyparts for which markers were fit '''

    bodyparts = df.columns.get_level_values(1) # Read body part names from header 
    return bodyparts.unique().to_list()


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
    
    # Settings
    tdt_fs = 48842.125              # TDT sample rate in Hz

    # For each session
    for file_ in data_dir.glob('*.h5'):

        ft = load_frame_samples(time_dir, file_.stem[0:25])
        ft['TDT_time'] = ft['TDT_Sample'] / tdt_fs

        df = load_tracking_data(file_)
        df = join_frame_times(df, ft)

        print(f"{file_.name}: {df.shape[0]} frames")

        fig = figure(name=file_.stem)

        fig.plot_results(df, ['head'], alphavalue=.2, pcutoff=.05)

        fig.save('Analysis/Null_responses/path_analysis/images/All_frames')




if __name__ == '__main__':
    main()







