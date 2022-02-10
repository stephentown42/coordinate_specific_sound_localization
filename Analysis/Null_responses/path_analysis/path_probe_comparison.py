"""
Visualization of tracks on each trial

Sanity check that responses at the two spouts have sensible paths

"""

from dataclasses import dataclass
import json
from pathlib import Path
import os, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../../..')))
from Analysis import ferrets


@dataclass()
class figure():

    name: str
    ax_size: tuple=(1.9, 1.4)
    size: tuple=(6,6)

    def __post_init__(self) -> None:

        self.fig = plt.figure(figsize=self.size)
        self.save_name = self.name + '.png'

        # Create axes
        pos = [0.2, 0.2, self.ax_size[0]/self.size[0], self.ax_size[1]/self.size[1]]
        self.ax = self.fig.add_axes(pos)

        # Setup plotting information
        self.x_head = 0
        self.x_ticks = []
        self.x_tick_labels = []


    def save(self, file_path: str) -> None:
        ''' Save data to png file '''

        plt.savefig( Path(file_path) / self.save_name, dpi=300)


    def plot_ferret_data(self, ferret, f_data, color):

        self.x_head += 1
        x_map = {0:0.2, 1:-0.2}
        x_label = {0:'probe', 1:'test'}

        for probe, p_data in f_data.groupby('not_probe'):

            y = p_data['path_length'].to_numpy()
            j = np.random.rand(y.shape[0]) / 10
            x = self.x_head + x_map[probe]

            self.ax.scatter(
                x + j,
                y,
                s = 1,
                c = color,
                alpha = 0.2
                )
            
            
            self.ax.plot(
                [x+0.2, x+0.2],
                [np.mean(y)-np.std(y), np.mean(y)+np.std(y)],
                color=color,
                linewidth=1,
                linestyle='-',
                zorder=2)
            
            self.ax.plot(x+0.2, np.mean(y),color=color,zorder=2, markersize=2, marker='d')


            # Keep list of tick marks    
            self.x_ticks.append(x+0.1)
            self.x_tick_labels.append(x_label[probe])


    def format_axes(self):
        ''' Put in place the correct labels for the plot'''
        
        self.ax.set_xticks(self.x_ticks)
        self.ax.set_xticklabels(self.x_tick_labels, fontdict={'fontsize':8}, rotation=45)

        self.ax.set_ylabel('Path Length (px)', fontsize=8)
        self.ax.set_ylim([100, 750])
        self.ax.tick_params(labelsize=8)

        [self.ax.spines[s].set_visible(False) for s in ['right','top']] 







def load_sessions(data_dir: str) -> pd.DataFrame:
    ''' Load tracking data from each session as dataframes and return concatenated data '''

    list_of_dfs = []

    # For each session file
    for file_ in Path(data_dir).glob('*.csv'):

        # Load head positions
        df = pd.read_csv(file_)

        # Filter behavioral data for block
        [ferret, block] = file_.stem.split('_HT_')
        
        # Include info on subject tested
        df['ferret'] = ferret
        df['block'] = block

        list_of_dfs.append(df)

    return pd.concat(list_of_dfs)


def get_path_stats(df: pd.DataFrame, pcutoff: float) -> pd.DataFrame:
    ''' Get summary statistics (e.g. path length) for tracks on each trial '''

    my_list = []

    # For each trial    
    for (ferret, block, trial_num), trial in df.groupby(by=['ferret','block','trial']):

         # Skip if any missing data (this is a bit extreme but easy to implement)
        if any(trial['likelihood'] < pcutoff):       
            continue

        delta = trial[['x','y']].diff(axis=0)[1:]                       # Change in x and y position between frames
        distance = np.linalg.norm(delta[['x','y']].values, axis=1)       # Distance covered

        my_list.append(
            dict(
                ferret = ferret,
                block = block,
                trial = trial_num,
                path_length = np.sum(distance)
            )
        )

    return pd.DataFrame(my_list)


def get_fcolor(ferrets, ferret):
    ''' Get color for specific subject from list imported from module '''

    return [f for f in ferrets if f['num'] == int(ferret[1:5])][0]['color']
    



def main():
   
    # Load settings
    with open('Analysis/Null_responses/path_analysis/config.json') as f:
        config = json.load(f)

    # Load tracking data for all sessions
    trax = load_sessions('Analysis/Null_responses/path_analysis/head_track_varFrames')
    
    # Get path info for each trial
    path_stats = get_path_stats(trax, config['pcutoff'])

    # Load trial data for all sessions 
    trial_data = Path('Analysis/Null_responses/First_10_sessions.csv')
    trials = pd.read_csv(trial_data)

    trials.rename({'Trial':'trial'}, axis=1, inplace=True)
    trials.set_index(keys=['ferret','block','trial'], inplace=True)

    # Join trial information with tracking data
    path_stats.set_index(keys=['ferret','block','trial'], inplace=True)
    
    path_stats = path_stats.join(trials['not_probe'])
    path_stats.reset_index(level=['ferret','block','trial'], inplace=True)

    md = smf.mixedlm("path_length ~ not_probe", path_stats, groups=path_stats["ferret"])
    mdf = md.fit()
    print(mdf.summary())

  
    # Create figure
    fig = figure(name='Path_length_analysis')

    for ferret, f_data in path_stats.groupby(by='ferret'):

        fig.plot_ferret_data(ferret, f_data, get_fcolor(ferrets, ferret))

    fig.format_axes()
    # plt.show()

    fig.save('Analysis/Null_responses/path_analysis/images')





if __name__ == '__main__':
    main()







