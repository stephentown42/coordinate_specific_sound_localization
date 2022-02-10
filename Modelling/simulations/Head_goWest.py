"""
Simulate performance of world-centered localization in which the probability of making a west-ward response is shaped by:    
    - sound angle relative to the head (sometimes called the 'Partial Egocentric' simulation)

Output is a matplotlib figure saved to disk

"""
import os, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../../..')))
from Analysis import cf_behavior as cb
from Analysis import cf_plot as cfp
from Modelling import cf_simulate as csim

   
def main():

    plt.style.use('seaborn')
    rng = np.random.default_rng()

    color = '#b84bff'
    nIterations = 1000

    # Create the same basic stimulus set and task rules
    df = csim.create_stimuli()

    task_map = pd.DataFrame(
        [
            [-180, 3, 0],       # Speaker 12
            [0, 9, 1]            # Speaker 6
            ], 
        columns=['speaker_angle_world','Response','Binary']
        )

    
    # Define head_centered model parameters
    coefs_head = [0.5, np.radians(0), 0.3, 2]

    df['response_activation'] = csim.run_mdl(df['speaker_angle_platform'], coefs_head)

    head_out, rng = csim.get_percent_correct(
            df, 
            coldness = coefs_head[3],
            task_var = 'speaker_angle_world', 
            task_map = task_map,
            generator = rng
            )

    df, rng = csim.get_response_probability(
        df, 
        coldness= coefs_head[3],
        nIterations=nIterations, 
        generator=rng
        )


    #####################################################################################################################
    # Create figure showing probability of responding 'west' as a function of sound angle in head and world-centered space 
    fig_size = (8,2)   
    fig = plt.figure(figsize=fig_size)

    ax_width = 1.75
    ax_height = 1.75
    
    # Plot head-centered model    
    ax_rect = cfp.cm2norm( [12, 2, ax_width, ax_height] , fig_size)
    ax = fig.add_axes(ax_rect)

    csim.draw_pivot_table(ax, df, 'speaker_angle_world', 'speaker_angle_platform')

    #####################################################################################################################
    # Plot model performance as a function of sound angle in the world
    ax_rect = cfp.cm2norm([2, 2, ax_width, ax_height], fig_size)
    ax = fig.add_axes(ax_rect)

    ax.plot([-190, 190], [50, 50], lw=1, ls='--', c='#888888')          # Chance
    csim.plot_pCorrect(ax, head_out, color)                              

    #######################################################################################################################
    ax_rect = cfp.cm2norm([7, 2, ax_width, ax_height], fig_size)
    ax = fig.add_axes(ax_rect)

    ax.plot([-190, 190], [0.5, 0.5], lw=1, ls='--', c='#888888')          # Chance

    df['nTrial'] = nIterations 
    csim.plot_pResponse_vs_stim_world(df, ax, color)    

    ax.set_xlim([-190, 190])

    #######################################################################################################################
    # Print example cases used in figure
    csim.report_response_p(df, platform_angle=0, speaker_angle_world=0)
    csim.report_response_p(df, platform_angle=180, speaker_angle_world=0)
    csim.report_response_p(df, platform_angle=180, speaker_angle_world=-60)
    csim.report_response_p(df, platform_angle=180, speaker_angle_world=-90)

    ####################################################################################################################### 
    plt.savefig('Modelling/images/jneurosci/Head_goWest.png', dpi=600)
    # plt.show()


if __name__ == '__main__':
    main()