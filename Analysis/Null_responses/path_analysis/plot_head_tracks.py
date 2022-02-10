"""
Visualization of tracks on each trial

Sanity check that responses at the two spouts have sensible paths

"""

from dataclasses import dataclass
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass()
class figure():

    name: str
    size: tuple=(6,6)
    im_size: tuple=(640, 480)

    def __post_init__(self) -> None:

        self.fig = plt.figure(figsize=self.size)
        self.save_name = self.name + '.png'


    def save(self, file_path: str) -> None:

        plt.savefig( Path(file_path) / self.save_name, dpi=300)
        plt.close()


    def create_axes(self, n:int, size: list) -> None:
        ''' Create plotting axes '''

        self.axs = []
        print(size)

        for ax_idx in range(1, 1+n):
                    
            vert_offset = (0.5*(ax_idx - 1)) + 0.1
            ax_position = [0.1, vert_offset, size[0]/self.size[0], size[1]/self.size[1]]

            ax = self.fig.add_axes(ax_position)
            ax.set_facecolor('#1c1e1b')

            self.axs.append(ax)    

        
    def plot_tracks(self, trax, trials, split_var: str, alphavalue:float=.3) -> None:
        ''' Plots poses vs time; pose x vs pose y'''

        # Add behavioral labels to tracking information (here response, but could be notProbe or Correct)
        trax = trax.set_index('trial').join( 
            trials.set_index('Trial')[split_var]
        )
         
        # For each response port that was part of the task                         
        for split_val, rData in trax.groupby(split_var):            

            ax = self.axs[split_val]            

            for trial, tData in rData.groupby(rData.index):
                        
                t = tData['TDT_time'].to_numpy() - tData['TDT_time'].min()
                t = t / np.max(t)
                # t = tData['likelihood'].to_numpy()

                ax.plot(
                    tData['x'].to_numpy(),
                    tData['y'].to_numpy(),
                    c='.75',
                    alpha=0.05,
                    zorder=0
                )
                
                ax.scatter(
                    tData['x'].to_numpy(),
                    tData['y'].to_numpy(),                        
                    c = t,
                    s = 1,
                    marker = '.',
                    edgecolors='none',
                    alpha=alphavalue,
                    zorder=1,
                    cmap='rainbow',
                    vmin=-0.1,
                    vmax=1.1
                )

            ax.set_xlim([0, self.im_size[0]])
            ax.set_ylim([0, self.im_size[1]])
            ax.set_title(f"{split_var} = {split_val}", fontsize=8)
            ax.invert_yaxis()        
            # plt.colorbar()     

            ax.set_xticks([])
            ax.set_yticks([])

            [ax.spines[s].set_visible(False) for s in ['left','bottom','right','top']] 
            
    


def main():
   
    # Load settings
    with open('Analysis/Null_responses/path_analysis/config.json') as f:
        config = json.load(f)

    # Load trial data for all blocks
    trial_data = Path('Analysis/Null_responses/First_10_sessions.csv')
    trials = pd.read_csv(trial_data)
    
    # Define path to head tracking within frames 
    data_dir = Path('Analysis/Null_responses/path_analysis/head_track_varFrames')

    # For each ferret
    for ferret, f_trials in trials.groupby(by='ferret'):

        # Create one figure for all sessions
        fig = figure(ferret, size=(4, 3), im_size=(640, config['im_width'][ferret]))
        fig.create_axes(n=2, size=config['ax_size'][ferret])        # size in inches

        # For each tracking file        
        for file_ in data_dir.glob(f'{ferret}*.csv'):

            # Load head positions
            trax = pd.read_csv(file_)

            # Replace any uncertain values with nans
            idx = trax[trax['likelihood'] < 0.1].index
            trax.loc[idx, 'x'] = np.nan
            trax.loc[idx, 'y'] = np.nan

            # Filter behavioral data for block
            [_, block] = file_.stem.split('_HT_')
            trial_data = f_trials[f_trials['block'] == block]
            
            assert trial_data.shape[0] > 0

            # Plot data
            fig.plot_tracks(trax, trial_data, 'not_probe')

        fig.save('Analysis/Null_responses/path_analysis/images/triggered_plotByProbe')
            





if __name__ == '__main__':
    main()







