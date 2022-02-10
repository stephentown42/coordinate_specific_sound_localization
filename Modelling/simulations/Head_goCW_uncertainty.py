"""
Simulate performance of world-centered localization in which the probability of making a west-ward response is shaped by:
    - Clockwise compensation model assuming uncertainty based on relative distance of response spouts

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

    nIterations = 1000
    color = 'r'

    # Create the same basic stimulus set and task rules
    df_head = csim.create_stimuli()
    df_world = df_head.copy()

    task_map = pd.DataFrame(
        [
            [-180, 3, 0],       # Speaker 12
            [0, 9, 1]            # Speaker 6
            ], 
        columns=['speaker_angle_world','Response','Binary']
        )


    # Model performance resulting from clockwise rotation about head-centered location
    df = csim.create_stimuli()

    df['response_angle_platform'] = df['speaker_angle_platform'] - 90
    
    df['response_angle_world'] = df['response_angle_platform'] + df['CenterSpoutRotation']
    df['response_angle_world'] = df['response_angle_world'].apply(cb.wrap_to_180)
    
    df['Response'] = [(i-180) / -30 for i in df['response_angle_world']]

    df['response_activation'] = df['response_angle_world'] - 90
    df['response_activation'] = np.abs(df['response_activation'].apply(cb.wrap_to_180)) / 180

    # NB: Here, response activation is an inverse, normalised distance from the west response spout. I.e.:
    #   - if the target is the west spout (min distance), the activation is 1    
    #   - if the target is the east spout (max distance), the activation is 0
    #   - if the target is the north/east spout (mid distance), the activation is 0.5
    # The value is symmetric on either side of the vector (equator) between east and west spouts


    cw_out, rng = csim.get_percent_correct(
            df, 
            coldness = 1,
            task_var = 'speaker_angle_world', 
            task_map = task_map,
            generator = rng
            )

    df, rng = csim.get_response_probability(
        df, 
        coldness=1,
        nIterations=nIterations, 
        generator=rng
        )


    #####################################################################################################################
    # Create figure showing probability of responding 'west' as a function of sound angle in head and world-centered space 
    fig_size = (8,2)   
    fig = plt.figure(figsize=fig_size)

    ax_width = 1.75
    ax_height = 1.75

    ax_rect = cfp.cm2norm( [12, 2, ax_width, ax_height] , fig_size)
    ax = fig.add_axes(ax_rect)

    csim.draw_pivot_table(ax, df, 'speaker_angle_world', 'speaker_angle_platform')
        
    #####################################################################################################################
    # Plot model performance as a function of platform angle
    ax_rect = cfp.cm2norm([2, 2, ax_width, ax_height], fig_size)
    ax = fig.add_axes(ax_rect)

    ax.plot([-190, 190], [50, 50], lw=1, ls='--', c='#888888')       # Chance
    csim.plot_pCorrect(ax, cw_out, color)                              


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

    ###########################################################################################################################
    plt.savefig('Modelling/images/jneurosci/Head_CW_uncertainty.png', dpi=600)
    # plt.show()


if __name__ == '__main__':
    main()