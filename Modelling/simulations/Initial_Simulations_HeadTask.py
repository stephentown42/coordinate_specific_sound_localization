
import os, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Analysis import cf_plot as cfp
from Modelling import cf_simulate as csim


def plot_pCorrect(ax, df, color):

    wf = cfp.wrap_data(df, 'CenterSpoutRotation', filter_val=180, delta=-360)
    wf.sort_values(by='CenterSpoutRotation', inplace=True)

    x = wf['CenterSpoutRotation'].to_numpy()
    y = wf['pCorrect'].to_numpy()
    ax.plot( x, y, c=color, linestyle='-', marker='.')

    return None


    
def main():

    rng = np.random.default_rng()

    # Create the same basic stimulus set and task rules
    df_head = csim.create_stimuli()
    df_world = df_head.copy()

    task_map = pd.DataFrame(
        [
            [-180, 3, 0],       # Speaker 12
            [0, 9, 1]            # Speaker 6
            ], 
        columns=['speaker_angle_platform','Response','Binary']
        )

    # Define world-centered model parameters
    coefs_world = [0.5, np.radians(0), 0.3, 2]
    
    df_world['response_activation'] = csim.run_mdl(df_world['speaker_angle_world'], coefs_world)

    world_out, rng = csim.get_percent_correct(
        df_world, 
        coldness = coefs_world[3],
        task_var = 'speaker_angle_platform', 
        task_map = task_map,
        generator = rng
        )

    df_world, rng = csim.get_response_probability(
        df_world, 
        coldness= coefs_world[3],
        nIterations=1000, 
        generator=rng
        )

    # Define head_centered model parameters
    coefs_head = [0.5, np.radians(0), 0.3, 2]
    
    df_head['response_activation'] = csim.run_mdl(df_head['speaker_angle_platform'], coefs_head)

    head_out, rng = csim.get_percent_correct(
            df_head, 
            coldness = coefs_head[3],
            task_var = 'speaker_angle_platform', 
            task_map = task_map,
            generator = rng
            )

    df_head, rng = csim.get_response_probability(
        df_head, 
        coldness= coefs_head[3],
        nIterations=1000, 
        generator=rng
        )


    # Plot
    fig_size = (5,2)    # In inches, - make this big, I don't care how big as long as it can fit the figure in
    fig = plt.figure(figsize=fig_size)

    ax_rect = [2, 2, 2.3, 2.3] # cm
    ax_rect = cfp.cm2norm(ax_rect, fig_size)    
    ax = fig.add_axes(ax_rect)

    csim.draw_pivot_table(ax, df_world, 'speaker_angle_world', 'speaker_angle_platform')
    
    ax_rect = [6, 2, 2.3, 2.3] # cm
    ax_rect = cfp.cm2norm(ax_rect, fig_size)
    ax = fig.add_axes(ax_rect)

    csim.draw_pivot_table(ax, df_head, 'speaker_angle_world', 'speaker_angle_platform')

    plt.savefig('Modelling/images/InitialSim_HeadLoc_Mdl.png', dpi=600)


    # Plot percent correct
    fig_size = (2,2)    # In inches, - make this big, I don't care how big as long as it can fit the figure in

    ax_rect = [2, 2, 2.3, 2.3] # cm
    ax_rect = cfp.cm2norm(ax_rect, fig_size)

    plt.style.use('seaborn')

    fig = plt.figure(figsize=fig_size)
    ax = fig.add_axes(ax_rect)

    ax.plot([-200, 200], [50, 50], lw=1, ls='--', c='#888888')
    plot_pCorrect(ax, world_out, 'k')
    plot_pCorrect(ax, head_out, '#b84bff')
    
    ax.set_xlabel('Platform Angle (°)', fontsize=8)
    ax.set_ylabel('% Correct', fontsize=8)
    ax.set_title('Simulation', fontsize=8)

    # cfp.rotate_tick_labels(ax, dim='x', angle=45)    
    
    ax.set_xticks([-180, -90, 0, 90, 180])
    ax.set_xticklabels(['-180', '-90', '0', '90', '180'], rotation=45)
    ax.set_yticks([0, 25, 50, 75, 100])
    # ax.set_ylim([0, 100])


    ax.tick_params(labelsize=7)

    plt.savefig('Modelling/images/InitialSim_HeadLoc_pCorrect_v2.png', dpi=600)
    # plt.show()


    # Format for paper
    # ax_size = 2.3                           # cm (height = width)
    # offsets = [(2, 2), (2, 6), (6, 4)]      # cm

    # for ax, off in zip(axs, offsets):

    #     ax_rect = cfp.cm2norm([off[0], off[1], ax_size, ax_size], fig_size)
    #     ax.set_position(pos=ax_rect)

    

    # plt.show()


if __name__ == '__main__':
    main()