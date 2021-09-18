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

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Analysis import ferrets
from Analysis import cf_analysis as cfa
from Analysis import cf_plot as cfp

# Define paths and files
file_path = 'Analysis/Main/Data/Formatted'
save_path = 'Analysis/Main/images'


def main():
        
    opts = [x for x in sys.argv[1:] if x.startswith("-")]
    
    if '--talk' in opts:       # Figure settings for manuscript
        fss = cfp.get_fig_style('talk')        
    else:                       # Default to talk format
        fss = cfp.get_fig_style('paper')  
        
    # Create figure
    plt.style.use("seaborn")
    fig_size = (2, 6.5)

    # For each ferret
    for ferret in ferrets:

        # Load source data
        file_name = f"F{ferret['num']}_{ferret['name']}.csv"
        df = pd.read_csv(os.path.join(file_path, file_name))

        # Create figures for plotting
        fss['fNum'] = f"F{ferret['num']}"
        fss['fcolor'] = ferret['color']

        if ferret['task'] == 'World':           # Switch based on response coding (9 o'clock in each task means different things)
            fss['response_label'] = 'p(West)'
        elif ferret['task'] == 'Head':
            fss['response_label'] = 'p(Left)'

        fig = plt.figure(figsize=fig_size)       

        ax_pCorrect = fig.add_axes( cfp.cm2norm([1.3, 12.5, 1.725, 1.725], fig_size))
        ax_world_P  = fig.add_axes( cfp.cm2norm([1.3, 9, 1.725, 1.725], fig_size))
        ax_head_P   = fig.add_axes( cfp.cm2norm([1.3, 5.5, 1.725, 1.725], fig_size))
        ax_joint_P  = fig.add_axes( cfp.cm2norm([1.3, 2, 1.725, 1.725], fig_size))

        # Task performance (% correct)
        pCorrect = cfa.get_percent_correct(df, sample_size=400, nIterations=100)        

        print(f"F{ferret['num']}: {pCorrect['mean'].min():.1f} to {pCorrect['mean'].max():.1f} % correct, mean = {pCorrect['mean'].mean():.1f}")
        

        cfp.plot_y_vs_theta( fss, 
            ax = ax_pCorrect,
            y = pCorrect['mean'], 
            error = pCorrect['std_dev'], 
            chance = 50, 
            xlabelstr = 'Platform Angle (°)',
            ylabelstr = '% Correct',
            ytix = [0, 25, 50, 75, 100]
            )

        ax_pCorrect.set_title(f"F{ferret['num']}", c=ferret['color'], fontsize=fss['font_size']+2, fontweight='bold')

        # Head vs world centered response probability
        result = cfa.get_joint_responseP(df, sample_size=3, nIterations=100)        
        
        cfp.plot_joint_responseP(fss, ax_joint_P, result) 

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

        # Report variance for each ferret in head and world-centred frames
        var_head = head_res['pResp'].var()
        var_world = world_res['pResp'].var()
        print(f"F{ferret['num']}: {var_world:.3f} vs. {var_head:.3f}")

        # Save or show
        # plt.show()
        # save_name = file_name.replace(".csv", ".png")
        # plt.savefig( os.path.join(save_path, save_name), dpi=300)
        plt.close()


if __name__ == '__main__':
        main()