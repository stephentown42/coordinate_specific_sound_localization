"""
Create figure (5C in manuscript) showing how well the best fitting models
predict animal behavior in held-out validation data.

Data is plotted separately for each ferret in the project, and for models 
using sound angle relative to the head or world as predictors. In each
case, data is shown both as a scatter plot in which individual data
points show the performance on each fold, with the analysis being repeated
20 times (i.e. 20 fold cross-validation) and boxplots showing the median 
and interquartile range across folds.

Version History
    - 2021-08-31: Branched from plot_matlab_model.py
"""

import os, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

plt.style.use('seaborn')

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Analysis import ferrets
from Analysis import cf_plot as cfp
from Modelling import cf_simulate as csim


def get_fold_performance(file_path):
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

    fold_performance = []

    for model_dir in file_path.glob('*_TestModel_*'):

        config = csim.load_config(model_dir)
        
        pf = pd.read_csv( model_dir / 'fold_performance.csv')
        
        pf['Ferret'] = int(config['InputData'][1:5])
        pf['predictor'] = config['stim_col']

        fold_performance.append(pf)
    
    return pd.concat(fold_performance)


class panel():
    """
    Panels are objects that contain multiple axes within a figure
    and hold useful metadata. Here, each subject is expected to 
    have it's own panel, with mutliple axes in the same column.

    ...

    Attributes
    ----------
    num : int
        Subject ID (e.g. F1801)
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

    def __init__(self, num, fig, h_pos):
        """        
        Parameters:
        ----------
        num : int
            Subject ID (e.g. F1801)
        fig : matplotlib figure
            Parent figure in which to plot data
        h_pos : float
            Horizontal starting location of axis in cm
                              
        """
        self.num = num
        self.parent = fig

        fig_size = tuple(fig.get_size_inches())

        self.positions = dict(
            performance = cfp.cm2norm([h_pos, 2.5, 1.75, 3], fig_size),             
        )

        self.axs = dict()
        for (key, value) in self.positions.items():
            self.axs[key] = fig.add_axes(value)
        

def main():

    root_dir = Path('Modelling/matlab/logs/')
    
    fold_performance = pd.concat([                                          # Get performance predicting behavior for each ferret
        get_fold_performance( root_dir / 'CF8_FullAllo_Theta'),
        get_fold_performance( root_dir / 'CF8_HeadCentred_Theta')
        ])    

    
    # Create figure and assign axes to ferrets in a user-friendly dictionary
    fig_size = (7.5, 3)
    fig = plt.figure(figsize=fig_size)       

    panels = dict(
        Pendleton = panel(1701, fig, 2.93),
        Grainger  = panel(1703, fig, 4.95),
        Dory      = panel(1811, fig, 6.985),
        Eclair    = panel(1902, fig, 9.0),
        Ursula    = panel(1810, fig, 12.47),
        Crumble   = panel(1901, fig, 14.495),
        Sponge    = panel(1905, fig, 16.535),
    )

    # Plot cross-validated model performance for each ferret   
    for ferret in ferrets:         

        ferret['panel'] = panels[ferret['name']]       
        ax = ferret['panel'].axs['performance']
        print(ferret['name'])

        ax.set_title(f"F{ferret['num']}", fontsize=8, color=ferret['color'], fontweight='bold')

        fData = fold_performance[fold_performance['Ferret'] == ferret['num']]        

        x = -0.25                                                   # This is a dumb but quick way to get the order of items on the x axis to look like I want, x will increase through the loop so that each object moves progressively right
        for predictor, pData in fData.groupby(by='predictor'):            
            
            y = pData['pCorrect'].to_numpy()
            j = np.random.rand(y.shape[0]) / 4

            ax.boxplot(
                y, 
                boxprops = {'linewidth':1},
                medianprops = {'linewidth':1, 'color':ferret['color']},
                positions=np.arange(x, x+1), 
                showcaps=False,
                sym='', 
                widths=0.45,
                whiskerprops={'linewidth':1}
                )
            
            x += 0.35                                               # Move to the right

            ax.scatter(
                x=x+j,
                y=y,
                color = '.25',
                alpha=0.7,
                s=12,
                marker='.',
                edgecolors=None
            )
            
            x += 0.6                                               # Move to the right
            print(f"{predictor}: min = {min(y):.1f}, max = {max(y):.1f}")
  
        # Set general axes properties 
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Head','World'], fontsize=7.5, style='italic')        
        ax.set_xlabel('Model', fontsize=8)
        ax.set_xlim((-0.8, 1.7))
        ax.set_ylim((45, 75))

        # Add specific features for showing shared y axes
        if ferret['num'] == 1701 or ferret['num'] == 1810:
            ax.set_ylabel('% Correct', fontsize=8)
            ax.set_yticks([50, 60, 70])
            ax.set_yticklabels(['50','60','70'], fontsize=7.5)
        else:
            ax.set_ylabel('')
            ax.set_yticklabels('')
        

    # plt.show()
    plt.savefig('Modelling/images/Ferret_Model_Validation.png', dpi=300)
    plt.close()




if __name__ == '__main__':
    main()