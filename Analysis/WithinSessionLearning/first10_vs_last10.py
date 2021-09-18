"""

This function takes in the whole dataset for each animal, and runs through each
session, selecting the first and last 10 trials, and then saving the output for
later analysis


Created:
    2021-07-17 - Stephen Town


Notes:
A small number of sessions (e.g. 8/184 for Eclair) began with multiple stimulus 
repeats and these trials were excluded from the formatted data. However as a 
consequence, we can't rely on trial numbers starting at 1.

"""
import os, sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Analysis import ferrets
from Analysis import cf_analysis as cfa
from Analysis import cf_plot as cfp

file_path = 'Analysis/Main/Data/Formatted'
filtered_data = 'Analysis/WithinSessionLearning/Data_After_Rotation'
img_path = 'Analysis/WithinSessionLearning/images'

K = 10      # K = Number of trials to consider at start / end
regenerate_filtered_data = False


def require_platform_change(df):
    """
    Description
    
    Parameters:
    ----------
    df : pandas dataframe
        Data for all sessions from one ferret
    
    Returns:
    --------
    df : pandas dataframe
        Subset of input data, but only containing sessions after platform rotation
    """

    df.sort_values(by=['SessionDate', 'Trial'], inplace=True)   

    count = 0
    new_data = []

    for session, sData in df.groupby('SessionDate'):

        current_angle = sData['CenterSpoutRotation'].unique()

        if len(current_angle) > 1:                      
            print(f"Skipping rotation within session")      # Ignore rare cases of rotation within session
            continue
        
        if count > 0:                                   # Ignore the first session
            if current_angle != previous_angle:         # If the platform angle has changed since the previous session, keep that data
                new_data.append(sData) 
                    
        previous_angle = current_angle                  # Update value for next loop
        count += 1

    return pd.concat(new_data)    


def filter_for_K_trials(K):
    """
    Reduces the dataset to 
    
    Parameters:
    ----------
    K : int
        Number of trials to sample from each session
    
    Output:
    --------
    CSV files containing datasets for each ferret from first or last K trials
    in each session

    Returns:
    --------
    None
    """

    # For each ferret
    for ferret in ferrets:

        # Load source data
        file_name = f"F{ferret['num']}_{ferret['name']}.csv"
        df = pd.read_csv(os.path.join(file_path, file_name))

        df = df[df['not_probe'] == 1]
        df = require_platform_change(df)

        first_trials = df.copy()  
        last_trials = df.copy()              # I know we don't need this copy, but for dev purposes I'll keep the original

        for session, sData in df.groupby(by='SessionDate'):            
            if sData.shape[0] > K:                                                          # <==== THIS SHOULD PROBABLY BY > (2*K)
                first_trials.drop( sData.iloc[K:].index, inplace=True)
                last_trials.drop( sData.iloc[:-K:].index, inplace=True)
            else:
                first_trials.drop( sData.index, inplace=True)   # For the sharpest contrast, don't include sessions with <K datapoints (which are both the first and last trials)
                last_trials.drop( sData.index, inplace=True)

        # Write data
        file_name = f"F{ferret['num']}_{ferret['name']}_first{K}.csv"
        first_trials.to_csv( os.path.join(filtered_data, file_name))

        file_name = f"F{ferret['num']}_{ferret['name']}_last{K}.csv"
        last_trials.to_csv( os.path.join(filtered_data, file_name))        
            

def get_behavior(groupstr):
    """
        groupstr -- str, ammendment to file name for first or last K trials
    """

    # Create figure
    plt.style.use("seaborn")
    fig_size = (2, 3)
    fss = cfp.get_fig_style('paper')


    # For each ferret
    for ferret in ferrets:

        if ferret['task'] == 'Head':        # Only interested in this for world-centred animals
            continue

        # Load source data
        file_name = f"F{ferret['num']}_{ferret['name']}_{groupstr}.csv"
        df = pd.read_csv(os.path.join(filtered_data, file_name))

        # Create figures for plotting
        fss['fNum'] = f"F{ferret['num']}"
        fss['fcolor'] = ferret['color']

        if ferret['task'] == 'World':           # Switch based on response coding (9 o'clock in each task means different things)
            fss['response_label'] = 'p(West)'
        elif ferret['task'] == 'Head':
            fss['response_label'] = 'p(Left)'

        fig = plt.figure(figsize=fig_size)       

        ax_pCorrect = fig.add_axes( cfp.cm2norm([1.3, 2, 1.725, 1.725], fig_size))

        # Task performance (% correct)
        pCorrect = cfa.get_percent_correct(df, sample_size=50, nIterations=100)        

        print(f"F{ferret['num']}: {pCorrect['mean'].min():.1f} to {pCorrect['mean'].max():.1f} % correct")
        
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
        
        # Save or show
        # plt.show()
        save_name = file_name.replace(".csv", ".png")
        plt.savefig( os.path.join(img_path, save_name), dpi=300)
        plt.close()


def main():
    
    if regenerate_filtered_data:
        filter_for_K_trials(K)       

    get_behavior(f"first{K}")
    get_behavior(f"last{K}")

if __name__ == '__main__':
    main()


