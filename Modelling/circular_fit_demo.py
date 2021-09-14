'''
Plots performance (% correct) for animals in egocentric (reds) and allocentric

Uses bootstrap resampling to estimate percent correct at each platform angle.
Resampling is required because of the unequal sample sizes in the source data,
where subjects are more commonly tested at some platform angles than others
(particularly the initial first trained angle)

Stephen Town - October 2020
'''

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# Settings
nIterations = 10
sample_size = 3

# Create demo fit
beta = [-0.25, 3, 145]
theta = np.arange(-180, 181, step=1)
radians = theta / 180 * np.pi   # Deg 2 rad
beta[2] = beta[2] / 180 * np.pi   # Deg 2 rad
exponent = beta[0] + np.sin(radians + beta[2]) * beta[1]
model_p = 1 / (1 + np.exp(-exponent))

fig_name = 'Sponge_demo_curve_fit.png'
stim_var = 'speaker_angle_platform'
xlabel_str = 'Speaker Angle: Head (°)'
text_color = '#4d4d4d'

# Define paths and files
file_path = '/home/stephen/Documents/CoordinateFrames'
ferret = 'F1905_Sponge'
color = "#d5462c"

df = pd.read_csv(os.path.join(file_path, ferret + '.csv'))

# Group by stimulus angle and get performance
n_response = []
platform_angles = []
stim_angles = []

for cs_angle, group_data in df.groupby([stim_var, 'CenterSpoutRotation']):

    stim_angles.append(cs_angle[0])
    platform_angles.append(cs_angle[1])
    response_count = 0

    for i in range(0, nIterations):
        sampled_data = group_data.sample(sample_size, replace=True)
        response_count = response_count + sampled_data['Response'].sum()

    n_response.append(response_count)

# Get sum of responses for each stimulus variable
# now that the number of platform angles has been equated
rf = pd.DataFrame(list(zip(stim_angles, platform_angles, n_response)), columns=[stim_var, 'CenterSpoutRotation', 'ResponseCount'])

response_sum = rf.groupby(stim_var).sum()
stim_angles = response_sum.index.to_numpy()
response_sum = response_sum['ResponseCount'].to_numpy()

nTrials = sample_size * nIterations * len(set(platform_angles))
pResp = np.true_divide(response_sum, nTrials)

# Wrap to 180
pResp = np.append(pResp, pResp[stim_angles == -180])
stim_angles = np.append(stim_angles, 180)

# Create figure
plt.style.use("seaborn")
fig, ax = plt.subplots(1, 1, figsize=(6, 4))

ax.plot(theta, model_p, c='k', linestyle='--', label='Fitted', zorder=-1)
# ax.plot([-180, 180], [0.5, 0.5], c="#888888", linestyle='--')
ax.scatter(stim_angles, pResp, 48, c=color, label='Observed', zorder=1)

ax.legend(prop={'size': 13})

ax.set_xlabel(xlabel_str, fontsize=15, color=text_color)
ax.set_xlim(-180, 180)
ax.set_xticks(stim_angles)
ax.set_xticklabels(['-180', '', '', '-90', '', '', '0', '', '', '90', '', '', '180'])

ax.set_ylabel('p(Response)', fontsize=15, color=text_color)
ax.set_ylim(0, 1)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1])

ax.tick_params(axis='both', labelsize=13, labelcolor=text_color)

plt.tight_layout()
# plt.show()
fig_path = '/home/stephen/Documents/CoordinateFrames/Modelling'
plt.savefig(os.path.join(fig_path, fig_name), dpi=300)
