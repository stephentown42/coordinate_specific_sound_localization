'''

Demonstrates the role played by parameters in circular models of behavior.

Specifically:

    - Vertical Shift (bias):
        The probability of making the specific response, independent of sound 
        angle. (NB: This might be equivalent to a prior in Bayes)
    
    - Horizonal Shift (preferred location): 
        The sound angle for which a response is most likely
    
    - Amplitude (spatial modulation)
        The extent to which response probability is modulated by sound angle

Output:
    Matplotlib figure with 3x1 axes showing curves for various models with
    set values.

Created:
    2020-10-?? (ST)
Updated:
    2020-10-?? : Branced from basic_curves.py
    2021-08-08 : Added documentation

'''

import matplotlib.pyplot as plt
import numpy as np
import os

fig_name = 'parameter_changes.png'

# Define range and coefficients
theta = np.arange(-180, 181, step=1)
radians = theta / 180 * np.pi   # Deg 2 rad

# Create figure
plt.style.use("seaborn")
fig, axs = plt.subplots(1, 3, figsize=(14, 4))

t_str = ['B0','B1','B2']
text_color = '#4d4d4d'

# Change shift parameter
beta = [0, 4]
shift = np.arange(0, 90, 15)

shift = shift / 180 * np.pi

for c in np.nditer(shift):
    exponent = beta[0] + np.sin(radians + c) * beta[1]
    q = 1 / (1 + np.exp(-exponent))
    d = np.round(c / np.pi * 180)
    axs[2].plot(theta, q, label=np.array2string(d, precision=0))

# Change amplitude
beta_1 = np.arange(0, 11, 2)

for b1 in np.nditer(beta_1):
    exponent = np.sin(radians) * b1
    q = 1 / (1 + np.exp(-exponent))
    axs[1].plot(theta, q, label=str(b1))

# Change bias
beta_0 = np.arange(-0.3, 0.6, 0.2)

for b0 in np.nditer(beta_0):
    exponent = np.sin(radians) + b0
    q = 1 / (1 + np.exp(-exponent))
    axs[0].plot(theta, q, label=np.array2string(b0, precision=2))


# Format axes
for i, ax in enumerate(axs):

    ax.legend()
    ax.set_xlim([-180, 180])
    ax.set_xlabel('x', fontsize=15, color=text_color)
    ax.set_xticks(np.arange(-180, 181, 90))
    ax.set_ylabel('p', fontsize=15, color=text_color)
    ax.set_ylim([0, 1])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
    # ax.set_title(t_str[i], fontsize=15, color=text_color)
    ax.tick_params(axis='both', labelsize=13, labelcolor=text_color)

plt.tight_layout()
plt.show()

# fig_path = '/home/stephen/Documents/CoordinateFrames/Modelling'
# plt.savefig(os.path.join(fig_path, fig_name), dpi=300)
