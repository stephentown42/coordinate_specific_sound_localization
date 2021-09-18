'''
Plots performance (% correct) for animals in egocentric (reds) and allocentric

Uses bootstrap resampling to measure the probability of making a specific response
at each platform angle.
Resampling is required because of the unequal sample sizes in the source data,
where subjects are more commonly tested at some platform angles than others
(particularly the initial first trained angle)

Notes:
-----
The definition of response is not given here, it's inherited from the data (which 
is itself inherited from the task). We should think more about how to make 
the response location and coordinate frame explicit in the project. 

There are also a lot of performance gains left on the table here, as there's 
redundancy between the 1d and 2d response probability measurements (i.e. they do 
the same thing, then collapse across individual dimensions)

TO DO:
    Add cmd line options for talk/paper version, and file / show requirements

Created:
    2021-06-22: Branched from show_head_centred_repsonse.py (ST)

'''

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Analysis import cf_analysis as cfa
from Analysis import cf_plot as cfp

# Define paths and files
file_path = Path( os.path.dirname(__file__)) / 'Data/Formatted'
save_path = Path( os.path.dirname(__file__)) / 'images'

training_platform = dict(
    F1806_Amy = 0,
    F1811_Dory = 90
)


def main():
               
    # Create figure
    plt.style.use("seaborn")
    fig_size = (2, 6.5)

    fss = cfp.get_fig_style('paper')

    # For each ferret
    for ferret in file_path.glob('*.csv'):

        # Load source data        
        df = pd.read_csv(str(ferret))
        df = df[df['not_probe'] == 1]

        # Create figures for plotting
        fss['fNum'] = ferret.stem[1:5]
        fss['fcolor'] = '#000000'
        fss['response_label'] = 'p(Response)'
        
        fig = plt.figure(figsize=fig_size)       

        ax_pCorrect = fig.add_axes( cfp.cm2norm([1.3, 12.5, 1.725, 1.725], fig_size))
        ax_world_P  = fig.add_axes( cfp.cm2norm([1.3, 9, 1.725, 1.725], fig_size))
        ax_head_P   = fig.add_axes( cfp.cm2norm([1.3, 5.5, 1.725, 1.725], fig_size))
        ax_joint_P  = fig.add_axes( cfp.cm2norm([1.3, 2, 1.725, 1.725], fig_size))

        # Task performance (% correct)
        pCorrect = cfa.get_percent_correct(df, sample_size=20, nIterations=100)        

        print(f"F{fss['fNum']}: {pCorrect['mean'].min():.1f} to {pCorrect['mean'].max():.1f} % correct")
        
        cfp.plot_y_vs_theta( fss, 
            ax = ax_pCorrect,
            y = pCorrect['mean'], 
            error = pCorrect['std_dev'], 
            chance = 50, 
            xlabelstr = 'Platform Angle (°)',
            ylabelstr = '% Correct',
            ytix = [0, 25, 50, 75, 100],
            wrapOn=-180,
            )

        ax_pCorrect.plot( training_platform[ferret.stem], 85, marker='v', c='#31C436', markersize=4)

        ax_pCorrect.set_title(f"F{fss['fNum']}", c=fss['fcolor'], fontsize=fss['font_size']+2, fontweight='bold')

        # Head vs world centered response probability
        result = cfa.get_joint_responseP(df, sample_size=3, nIterations=100)        
        
        # cfp.plot_joint_responseP(fss, ax_joint_P, result) 

        # Head-centred response probability
        head_res = result.groupby('stim_platf').sum()
        head_res['pResp'] = head_res['nResp'] / head_res['nTrial']

        cfp.plot_y_vs_theta(fss, 
            ax = ax_head_P, 
            y = head_res['pResp'],
            chance = 0.5,
            wrapOn=-180,
            xlabelstr = 'Speaker Angle: Head (°)',
            ylabelstr = fss['response_label'],
            ytix = [0, 0.25, 0.5, 0.75, 1]
            )        

        # World-centred response probability
        world_res = result.groupby('stim_world').sum()
        world_res['pResp'] = world_res['nResp'] / world_res['nTrial']

        cfp.plot_y_vs_theta(fss, 
            ax = ax_world_P, 
            y = world_res['pResp'],
            chance = 0.5,
            wrapOn=-180,
            xlabelstr = 'Speaker Angle: World (°)',
            ylabelstr = fss['response_label'],
            ytix = [0, 0.25, 0.5, 0.75, 1]
            )               

       
        # Save or show
        # plt.show()
        save_name = ferret.stem + ".png"
        plt.savefig( os.path.join(save_path, save_name), dpi=300)
        plt.close()


if __name__ == '__main__':
        main()