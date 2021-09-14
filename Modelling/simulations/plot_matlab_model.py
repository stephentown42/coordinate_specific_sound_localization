"""
Create figure (5D in manuscript) showing the output of best fitting models
in simulations

Data is plotted separately for each ferret in the project (columns), and for models 
using sound angle relative to the head or world as predictors (rows). Plots contain
heatmaps showing the proportion of responses west (ferrets tested in world-centered
localization) or left (ferrets tested in head-centered localization) that are directly
comparable with behavioral heatmaps shown in Fig. 2D and 4D.

Parameter values for each ferret/model are printed to the console (and given in
the paper as Supplementary Table 1)

Version History
    - 2021-08-29: Created
    - 2021-08-31: Split out functionality to plot_model_parameters.py, plot_validation_performance.py
"""

import os, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import seaborn as sns

sns.set_theme(style="whitegrid")

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Analysis import ferrets
from Analysis import cf_plot as cfp
from Modelling import cf_simulate as csim


def draw_curve(ax, coefs, color='k'):


    theta = np.linspace(-180, 180, num=360)
    pResp = csim.run_matlab_mdl(theta, coefs)

    ax.plot(theta, pResp, c=color, zorder=1)

    return None


def get_models(file_path):
    """    
    Get performance predicting held-out animal behavior for each fold 
    of cross-validation

   Parameters:
   ----------
   file_path : pathlib posix path
       Directory containing multiple subdirectories, each of which contains
       results files from a single model of one ferret
   
   Returns:
   --------
   ~ : pandas dataframe
       Dataframe containing performance and ferret identifier
   """

    best_models, all_mdls = [], []

    for model_dir in file_path.glob('*_TestModel_*'):

        # Load data
        config = csim.load_config(model_dir)        
        df = pd.read_csv( model_dir / 'param_contrast.csv')
        
        # Format for later use
        df['Ferret'] = int(config['InputData'][1:5])
        df['predictor'] = config['stim_col']
        
        for x in df.columns:
            df.rename({x:x.replace('_Xfit','')}, axis=1, inplace=True)

        initial_columns = [x for x in df.columns if 'X0' in x]
        df.drop(initial_columns, axis=1, inplace=True)

        # Take all outcomes for scatter
        all_mdls.append(df)
        
        # Take the model with minimum negative log likelihood for simulation
        df = df[df['NegLogLik'] == df['NegLogLik'].min()]         
        best_models.append(df)
    
    return pd.concat(best_models), pd.concat(all_mdls)


class panel():


    def __init__(self, num, fig, h_pos):

        self.num = num
        self.parent = fig

        fig_size = tuple(fig.get_size_inches())

        self.positions = dict(            
            speaker_angle_platform = cfp.cm2norm([h_pos, 2, 1.75, 1.75], fig_size),       
            speaker_angle_world    = cfp.cm2norm([h_pos, 6, 1.75, 1.75], fig_size)
        )

        self.axs = dict()
        for (key, value) in self.positions.items():
            self.axs[key] = fig.add_axes(value)
        


def main():

    root_dir = Path('Modelling/matlab/logs/')
    
    bm1, _ = get_models( root_dir / 'CF8_FullAllo_Theta_Recoded')
    bm2, _ = get_models( root_dir / 'CF8_HeadCentred_Theta_Recoded')

    best_models = pd.concat([bm1, bm2])     
    

    # Create figure and assign axes to ferrets in a user-friendly dictionary
    fig_size = (7.5, 4)
    fig = plt.figure(figsize=fig_size)       

    panels = dict(
        Pendleton = panel(1701, fig, 2.285),
        Grainger  = panel(1703, fig, 4.3),
        Dory      = panel(1811, fig, 6.35),
        Eclair    = panel(1902, fig, 8.385),
        Ursula    = panel(1810, fig, 12.54),
        Crumble   = panel(1901, fig, 14.57),
        Sponge    = panel(1905, fig, 16.6),
    )

    # Plot model outcomes and fold performance
    rng = np.random.default_rng()       

    for ferret in ferrets:         

        ferret['panel'] = panels[ferret['name']]
        ferret['panel'].axs['speaker_angle_world'].set_title(f"F{ferret['num']}", fontsize=8, color=ferret['color'], fontweight='bold')        

        # Plot the model curve
        fData = best_models[best_models['Ferret'] == ferret['num']]
        fData.reset_index(inplace=True)

        for idx, mdl_info in fData.iterrows():
            
            mdl_sim = csim.create_stimuli() 
            mdl_info = mdl_info.to_dict()
            
            print(mdl_info)

            theta = mdl_sim[ mdl_info['predictor']]            
            mdl_sim['response_activation'] = csim.run_mdl( theta, mdl_info)      

            mdl_sim, rng = csim.get_response_probability(
                mdl_sim, 
                coldness = mdl_info['coldness'],
                nIterations = 1000, 
                generator = rng
                )

            ax = ferret['panel'].axs[mdl_info['predictor']]

            csim.draw_pivot_table( ax, mdl_sim, 'speaker_angle_world', 'speaker_angle_platform')
            
            if ferret['num'] > 1701:
                ax.set_xlabel('')
                ax.set_ylabel('')
                ax.set_yticklabels('')
    
    # plt.show()
    plt.savefig('Modelling/images/Ferret_Model_Sim.png', dpi=300)
    plt.close()




if __name__ == '__main__':
    main()