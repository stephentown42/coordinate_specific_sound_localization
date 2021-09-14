"""
Create figure (5B in manuscript) showing parameter estimates for all models
vs. negative log likelihood, colored by ferret

Separate columns show each parameter, whereas rows show models using different
predictors (e.g. sound angle w.r.t head or world). Data on each plot is shown 
as a scatter, with each point showing one run of the model fitting procedure.
We repeated the fitting 20 times for each fold, such that, with 20 folds, each 
ferret has 400 datapoints. 

The figure illustrates how parameters nearly always have a single trough in
the loss function that is straightforward to identify.

Version History
    - 2021-08-31: Branched from plot_matlab_model.py
"""

import os, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Analysis import ferrets
from Analysis import cf_plot as cfp
from Modelling import cf_simulate as csim

plt.style.use('seaborn')


def plot_param_contrasts(file_path, axs):
        
    df = pd.read_csv( file_path / 'param_contrast.csv')

    initial_cols = [x for x in df.columns if 'X0' in x]
    fitted_cols = [x for x in df.columns if 'Xfit' in x]

    for (iCol, fCol, ax) in zip(initial_cols, fitted_cols, axs):

        x = df[iCol].to_numpy()
        y = df[fCol].to_numpy()
        c = df['NegLogLik'].to_numpy()

        ax.scatter(x, y, c=c)      

        ax.set_xlabel('Initial')
        ax.set_ylabel('Fitted')
        ax.set_title(fCol.replace('_Xfit',''))


        # v_max = max(np.append(x,y))
        # v_min = min(np.append(x,y))

        # ax.set_xlim((v_min, v_max))
        # ax.set_ylim((v_min, v_max))
        # ax.set_aspect(1)   

    best_mdl = df[df['NegLogLik'] == df['NegLogLik'].min()]                                                                 # Take the model with minimum negative log likelihood
    best_mdl = best_mdl[[x for x in best_mdl.columns if 'Xfit' in x]]                   
    
    name_map = {best_mdl.columns[i]: best_mdl.columns[i].replace('_Xfit', '') for i in range(len(best_mdl.columns))}        # Remove 'Xfit' from column names (aesthetics)
    best_mdl.rename(name_map, axis=1, inplace=True)

    return best_mdl


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
    best_mdls : pandas dataframe
        Dataframe containing performance of best model across folds for each ferret
    all_mdls : pandas dataframe
        Dataframe containing performance of all models for each ferret
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
    
    best_models = pd.concat(best_models)
    all_mdls = pd.concat(all_mdls)

    return best_models, all_mdls


class panel():
    """
    Panels are objects that contain multiple axes within a figure
    and hold useful metadata. Here, each subject is expected to 
    have it's own panel, with mutliple axes in the same column.

    ...

    Attributes
    ----------
    name : str
        Parameter name
    fig : matplotlib figure
        Parent figure in which to plot data
    axs : dict
        Dictionary containing multiple matplotlib axes, keyed by 
        variable being plotted (here only 'performance')
    h_pos : float
        Horizontal starting location of axis in cm
    positions : dict
        Dictionary of positions for each axis in normalized units
        consistent with matplotlib plotting, keyed by variable
        being plotted ('performance')
    """

    def __init__(self, name, fig, h_pos):
        """        
        Parameters:
        ----------
        name : str
            Parameter name
        fig : matplotlib figure
            Parent figure in which to plot data
        h_pos : float
            Horizontal starting location of axis in cm
                              
        """
        self.name = name
        self.parent = fig

        fig_size = tuple(fig.get_size_inches())

        self.positions = dict(            
            speaker_angle_platform = cfp.cm2norm([h_pos, 2, 1.75, 1.75], fig_size),       
            speaker_angle_world    = cfp.cm2norm([h_pos, 4.6, 1.75, 1.75], fig_size)
        )

        self.axs = dict()
        for (key, value) in self.positions.items():
            self.axs[key] = fig.add_axes(value)
        
    def set_xlabel(self, axname):

        ax = self.axs[axname]        
        ax.set_xlabel(self.name, fontsize=8)


def main():

    # Load data
    root_dir = Path('Modelling/matlab/logs/')
    
    _, am1 = get_models( root_dir / 'CF8_FullAllo_Theta_Recoded')
    _, am2 = get_models( root_dir / 'CF8_HeadCentred_Theta_Recoded')
                                             
    all_models = pd.concat([am1, am2])
    
    # Create plotting objects
    fig_size = (5, 3)
    fig = plt.figure(figsize=fig_size)     

    param_ax = dict(                                            # Separate panels (columns of axes) for each model parameter
        vert_offset  = panel(r"$\beta_0$", fig, 2),
        horiz_offset = panel(r"$\beta_1$", fig, 4.1),
        amplitude    = panel(r"$\beta_2$", fig, 6.2),
        coldness     = panel(r"$\beta_{inv. temp}$", fig, 8.3),
    )

    titles = dict(
        speaker_angle_world = 'World-Centered Model',
        speaker_angle_platform = 'Head-Centered Model',
    )

    # Plot parameter data for each ferret
    for ferret in ferrets:                
        fData = all_models[all_models['Ferret'] == ferret['num']]

        for predictor, pData in fData.groupby('predictor'):

            # for col_idx, param in enumerate(params):
            for (param, param_pan) in param_ax.items():
            
                x = pData[param].to_numpy()
                y = pData['NegLogLik'].to_numpy()
                ax = param_pan.axs[predictor]

                ax.scatter(x, y, s=16, marker='.', c=ferret['color'], alpha=0.5)                

                if param == 'coldness':                                                 # a.k.a. Inverse temperature
                    ax.set_title(titles[predictor], fontsize=8, fontweight='bold')       
                    ax.set_xscale('log')                                                            
    

    # Format axes            
    param_ax['vert_offset'].axs['speaker_angle_world'].set_ylabel('Neg. Log Likelihood', fontsize=8)     
    
    xlims = dict(                                               # Define axes properties by parameter 
        vert_offset  = [0.45, 1.05],
        horiz_offset = [-200, 200],
        amplitude    = [-0.05, 0.55],
        coldness     = [0.01, 21],
    )

    xticks = dict(
        vert_offset  = [0.5, 0.75, 1],
        horiz_offset = [-180, 0, 180],
        amplitude    = [0, 0.25, 0.5],
        coldness     = [0.1, 1, 10],
    )

    y_max = all_models['NegLogLik'].max()                       # For this dataset a scale based on 500 works, but this will vary if the training dataset was made larger
    y_min = all_models['NegLogLik'].min()

    y_max = (np.ceil(y_max / 500) * 500) + 25
    y_min = (np.floor(y_min / 500) * 500) - 25


    for param, param_pan in param_ax.items():                       # For each model parameter
        
        param_pan.set_xlabel(axname='speaker_angle_platform')       # i.e. xlabel(parameter_name) on the bottom row

        for predictor, ax in param_pan.axs.items():
                            
            ax.set_xlim(xlims[param])
            ax.set_xticks(xticks[param])

            if predictor == 'speaker_angle_platform':               # Include tick labels for bottom row
                ax.set_xticklabels([str(x) for x in xticks[param]], fontsize=7)
            else:
                ax.set_xticklabels('')                              # Exclude tick labels on top row
                        
            ax.set_ylim((y_min, y_max))                                
            ax.set_yticks([500, 750, 1000])                         # This is bad practice, but I don't have time to deal with Matplotlib being difficult

            if param == 'vert_offset':
                ax.set_yticklabels(['500', '750', '1000'], fontsize=7)
            else:
                ax.set_yticklabels('')


    # plt.show()
    plt.savefig('Modelling/images/Ferret_Params_vs_NLL.png', dpi=300)
    plt.close()

    




if __name__ == '__main__':
    main()