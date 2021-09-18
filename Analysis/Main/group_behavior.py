'''
Plots performance (% correct) for animals in world-centred task

Uses bootstrap resampling to estimate percent correct at each platform angle.
Resampling is required because of the unequal sample sizes in the source data,
where subjects are more commonly tested at some platform angles than others
(particularly the initial first trained angle)

Note that here there's a slight inconsistency in how we're treating the two 
tasks - in the world-centred version, we're keeping the three animals with the
same training and discarding the fourth (Eclair) who was intentionally trained 
with a very different set of conditions. In the head-centred task, we're not
dropping the animal with a different training condition (Ursula) because her 
behavior is very similar to that of other animals, and the differences in training
are not as stark (i.e. we didn't completely reverse the contingency, as we did 
with Eclair). Purists might argue this is the wrong thing to do, but I think we'd
do fine without integrating Ursula's data if a reviewer decides to be a jackass.


Created:
    2020-10-01, by Stephen Town
Modified:
    2021-06-23: Integrated with main package, increased sample sizes to benefit 
    from combining data from multiple subjects
'''

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Analysis import ferrets
from Analysis import cf_analysis as cfa
from Analysis import cf_plot as cfp

# Define paths and files
file_path = 'Analysis/Main/Data/Formatted'
save_path = 'Analysis/Main/images'


def combine_data_across_subjects(members):
    """
    Loads data from multiple subjects and combines in one dataframe
    
    Parameters:
    ----------
    members : list 
        List of group member dictionaries, with ferret name and 
        number as fields
    
    Returns:
    --------
    df : pandas dataframe
        Data from multiple members
    """
    df = []
    for _, ferret in members.iterrows():

        file_name = f"F{ferret['num']}_{ferret['name']}.csv"
        tmp = pd.read_csv(os.path.join(file_path, file_name))
        df.append(tmp) 
    
    return pd.concat(df)


def analysis(fss, ax, ferrets, task, training):
    """
    Run main analysis on a group of ferrets defined by task and training conditions
    
    Parameters:
    ----------
    fss : Dict
        Dictionary containing styling info
    ax : Matplotlib axes
        Axes for plotting
    ferrets : dict
        Dictionary containing subject info
    task : str
        Name of task ('Head' or 'World') - corresponds to value of 'task' in Ferrets
    train : str, optional
        Training rule included - corresponds to value of 'task' in Ferrets
    
    Returns:
    --------
    None
    """

    # Select group members with the same task and training rules
    members = pd.DataFrame(ferrets)

    if training is None:
        members = members[(members['task'] == task)]
    else:
        members = members[(members['task'] == task) & (members['train'] == training)]

    df = combine_data_across_subjects(members)
    
    # Plot response prob as joint function of sound angle in platform and world space
    fss['fNum'] = f'{task}-centered'

    result = cfa.get_joint_responseP(df, sample_size=9, nIterations=100)        
    
    cfp.plot_joint_responseP(fss, ax, result) 

    # Report variance for each ferret in head and world-centred frames
    head_res = result.groupby('stim_platf').sum()
    head_res['pResp'] = head_res['nResp'] / head_res['nTrial']
    var_head = head_res['pResp'].var()

    world_res = result.groupby('stim_world').sum()
    world_res['pResp'] = world_res['nResp'] / world_res['nTrial']
    var_world = world_res['pResp'].var()

    print(f"Task = {task}: {var_world:.3f} vs. {var_head:.3f}")


def main(ferrets):

    opts = [x for x in sys.argv[1:] if x.startswith("-")]
    
    if '--talk' in opts:       # Figure settings for manuscript
        fss = cfp.get_fig_style('talk')        
    else:                       # Default to talk format
        fss = cfp.get_fig_style('paper')  
        
    plt.style.use("seaborn")
    
    fig_size = (7, 5)
    fig = plt.figure(figsize=fig_size)

    ax_world  = fig.add_axes( cfp.cm2norm([2, 2, 2.7, 2.7], fig_size))
    ax_head   = fig.add_axes( cfp.cm2norm([7, 2, 2.7, 2.7], fig_size))

    analysis(fss, ax_head, ferrets, 'Head', None)
    analysis(fss, ax_world, ferrets, 'World', 'North=>East,South=>West')

    save_name = 'Group_behavior.png'
    plt.savefig( os.path.join(save_path, save_name), dpi=300)
    plt.close()

    # plt.show()


if __name__ == '__main__':
    main(ferrets)