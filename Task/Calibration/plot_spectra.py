"""


Nested file structure in which there are multiple speakers, which can be tested multiple times
(one block per test) and there are multiple snippets per block

Spectrograms might work better here...

"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path


data_dir = Path('/home/stephen/Documents/CoordinateFrames/Data/Speaker_Spectra')

# Load metadata
meta = pd.read_csv( data_dir / 'Metadata.csv')

meta = meta[ meta['Speaker'] % 6 == 0]


# Create figure
fig, axs = plt.subplots(1,2, sharey=True)
count = 0

# For each speaker
for speaker, sBlocks in meta.groupby(by='Speaker'):

    # fig, axs = plt.subplots(4,8)
    # axs = np.ravel(axs)

    # Get stimulus spectra after subtracting baseline
    delta = []
    # count = 0

    for _, block in sBlocks.iterrows():             # For each block

        for snip_file in data_dir.glob('*' + str(block['Block']) + '*.csv'):    # For each snippet within the block
                    
            df = pd.read_csv(str(snip_file), index_col='Frequency')

            delta_name = snip_file.stem
            df[delta_name] = df['Stimulus_dB'] - df['Baseline_dB']
            delta.append(df[delta_name])

            # axs[count].plot(df.index, df[delta_name])
            # axs[count].set_title(delta_name)
            # count += 1

    # plt.show()

    delta = pd.concat(delta, axis=1)

    # Average across snippets
    m = delta.median(axis=1)

    axs[count].plot(m.index, m.values)    
    count += 1


# plt.xscale('log')
plt.show()

    