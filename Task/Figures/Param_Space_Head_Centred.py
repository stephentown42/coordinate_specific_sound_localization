"""


This function also serves to help me understand the horror
that is saving figures in matplotlib.

The default resolution of the figure is 100ppi. It is recommended
to stick with this and scale any images by the relevant amount 
(i.e. if you want 300 ppi, make a figure three times as big, 
because matplotlib won't save corr)
"""

import os, sys

from matplotlib import cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Analysis import cf_plot as cfp


def main():

    fig_size = (2, 2)    # In inches, - make this big, I don't care how big as long as it can fit the axes in

    ax_rect = [2, 2, 2.3, 2.3] # cm
    ax_rect = cfp.cm2norm(ax_rect, fig_size)

    plt.style.use('seaborn')

    fig = plt.figure(figsize=fig_size)
    ax = fig.add_axes(ax_rect)
                          

    sound_angle_world = np.arange(-180, 210, 30) 

    # Plot probe speakers
    for probe_angle in range(30, 180, 30):
        sound_angle_head = np.full_like(sound_angle_world, probe_angle)

        ax.plot(sound_angle_head, sound_angle_world, c='#bdbdbd', linestyle='none', marker='.')
        ax.plot(-sound_angle_head, sound_angle_world, c='#bdbdbd', linestyle='none', marker='.')


    # Plot platform angles
    x = np.arange(-180, 181, 1)

    for platform_angle in range(-180, 360, 180):

        if abs(platform_angle) == 180:
            ls = ':'
        else:
            ls = '--'

        if platform_angle > 180:
            platform_wrap = platform_angle - 360
        elif platform_angle < -180:
            platform_wrap = platform_angle + 360
        else:
            platform_wrap = platform_angle
                    
        y = x + platform_angle

        ax.plot(x, y, c='#7b7b7b', lw=1, linestyle=ls)

    # Plot front speaker    
    sound_angle_head = np.full_like(sound_angle_world, 180)

    ax.plot(sound_angle_head, sound_angle_world, c='#ff9364', linestyle='-', marker='.')
    ax.plot(-sound_angle_head, sound_angle_world, c='#ff9364', linestyle='-', marker='.')


    # Plot behind speaker
    sound_angle_head = np.full_like(sound_angle_head, 0)

    ax.plot(sound_angle_head, sound_angle_world, c='#479093', linestyle='-', marker='.')




    ax.tick_params(labelsize=7)

    ax.set_xlim((-200, 200))
    ax.set_ylim((-200, 200))

    ax.set_xticks([-180, -90, 0, 90, 180])
    ax.set_yticks([-180, -90, 0, 90, 180])

    ax.set_xlabel('Head (°)', fontsize=8)
    ax.set_ylabel('World (°)', fontsize=8)
    ax.set_title('Sound Angle w.r.t. (°)', fontsize=8)

    # plt.show()
    plt.savefig('Task/Figures/ParamSpace_HeadCentred.png', dpi=600)
    plt.close()




if __name__ == '__main__':
    main()