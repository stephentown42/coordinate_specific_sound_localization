"""
Plot the performance (% correct) that a ferret performs before and after
swapping the speakers used to present test stimuli.

These results reflect the outcome of control experiments to rule out the 
possibility that animals performing world-centred discrimination of sounds
are doing so using some unique property of the specific sound source that
is unknown to us as observers.

Plot is formatted as two axes, one for each task. Here, the effect of 
swapping speakers on head-centred behavior is used as a standard with 
which we can estimate the general variability in behavior with time.

On each axes, lines show the results from individual swaps, with multiple 
swaps being performed on most animals. Animal identity is denoted by color.

Created:
    2021-07-05 by Stephen Town
Modified
    2021-07-13: Formatted for publication quality images


"""


import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Analysis import ferrets
from Analysis import cf_plot as cfp


file_path = Path('Analysis/Speaker_swaps/Data/Speaker_Summary.csv')
save_path = Path('Analysis/Speaker_swaps/images/')

# Load summary data
df = pd.read_csv(file_path)

df['pCorrect'] = df['nCorrect'] / df['nTrials'] * 100
df.sort_values(by=['ferret','swap','datetime'], inplace=True)

# Create and format plotting objects (two axes, one for each task)
plt.style.use('seaborn')
fig_size = (4, 3)
fig = plt.figure(figsize=fig_size)       

axs = [
    fig.add_axes( cfp.cm2norm([1.5, 3, 2.5, 4], fig_size)), 
    fig.add_axes( cfp.cm2norm([5, 3, 2.5, 4], fig_size))
    ]        

for ax in axs:
    ax.plot([0, 3], [50, 50], linestyle='--', c='#888888', lw=1)
    
    ax.tick_params(labelsize=7)
    
    ax.set_xlim(0.5, 2.5)
    ax.set_xticks([1, 2])
    ax.set_xticklabels(['Before','After'], rotation=45)
    
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

# Report results of each swap as line on relevant axes, together with
# predictions for what should happen based on speaker identity or previous location
delta = dict(World=[], Head=[])

for ferret in ferrets:

    f_name = f"F{ferret['num']}_{ferret['name']}"
    ferret_data = df[df['ferret'] == f_name]

    if ferret['task'] == 'World':
        ax = axs[0]        
    elif ferret['task'] == 'Head':
        ax = axs[1]

    for swap, swap_data in ferret_data.groupby(by='swap'):

        assert swap_data.shape[0] == 2

        before = swap_data[swap_data['datetime'] == swap_data['datetime'].min()]
        after = swap_data[swap_data['datetime'] == swap_data['datetime'].max()]

        before = before['pCorrect'].to_numpy()
        after = after['pCorrect'].to_numpy()

        h1 = ax.plot([1, 2], [before, after], linestyle='-', marker='.', c=ferret['color'], label="Observed", lw=1, zorder=10)
        h2 = ax.plot([1, 2], [before, 100 - before], linestyle='--', marker='.', c=ferret['color'], alpha=0.3, label="Predicted by Identity", lw=1, zorder=5)
        h3 = ax.plot([1, 2], [before, before], linestyle=':', marker='.', c='#404040', alpha=0.4, label="Predicted by Location", lw=1, zorder=1)

        delta[ferret['task']].append(after[0] - before[0])

    if ferret['name'] == 'Grainger' or ferret['name'] == 'Sponge':
        ax.legend([h1[0], h2[0], h3[0]], ['Observed','Predict by Identity','Predict by Location'], fontsize=8, loc=(-0.1, -0.6))

# Report summary stats to user
print(f"World-centred animals: N = {len(delta['World'])} swaps, Mean = {np.mean(delta['World'])}, Std. Dev = {np.std(delta['World'])}")
print(f"Head-centred animals: N = {len(delta['Head'])} swaps, Mean = {np.mean(delta['Head'])}, Std. Dev = {np.std(delta['Head'])}")

# Format axes and save plots
axs[0].set_ylabel('% Correct', fontsize=8)
axs[0].set_title('World-centred', fontsize=8)
axs[1].set_title('Head-centred', fontsize=8)

save_name = 'Speaker_Swap.png'
plt.savefig( os.path.join(save_path, save_name), dpi=300)
plt.close()

# plt.show()
