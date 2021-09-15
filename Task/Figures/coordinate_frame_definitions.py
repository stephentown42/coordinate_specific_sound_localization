"""
This script creates a simple plot in which the coordinates 
and angular values of the head are explicitly stated.

Here we will use the functions from cf_behavior, so that
the definitions used in the analysis are the ones being made 
explicit.
"""

import os, sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mpc

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Analysis import cf_behavior as cf


def deg2rad(x):
    return (x / 180) * np.pi

def main():

    # Define speaker and response locations in the world
    df = []
    for speaker in range(1, 13):
        for response in range(3, 15, 6):
            for ax_idx, platform_angle in enumerate(range(-180, 180, 30)):
                df.append({
                    'CenterSpoutRotation': platform_angle,
                    'Speaker Location': speaker, 
                    'Response': response,
                    'ax_idx': ax_idx
                    })

    df = pd.DataFrame(df)
    df = cf.format_angular_values(df)

    # Convert to radians 
    df['speaker_angle_world'] = df['speaker_angle_world'].apply(deg2rad)
    df['response_angle_world'] = df['response_angle_world'].apply(deg2rad)
    df['speaker_angle_platform'] = df['speaker_angle_platform'].apply(deg2rad)
    df['response_angle_platform'] = df['response_angle_platform'].apply(deg2rad)

    # Convert speaker locations into cartesian coordinates (with unit distance)
    df['speaker_world_x'] = df['speaker_angle_world'].apply( np.cos)
    df['speaker_world_y'] = df['speaker_angle_world'].apply( np.sin)

    # Plot6
    fig, axs = plt.subplots(3,4)
    axs = np.ravel(axs)    

    for platform_angle, pa in df.groupby(by='CenterSpoutRotation'):

        ax = axs[pa['ax_idx'].iloc[0]]
        
        platform_radians = (platform_angle / 180) * np.pi
        platform_x = np.cos(platform_radians) * 0.5
        platform_y = np.sin(platform_radians) * 0.5

        ax.plot(0, 0, marker='o', mfc='k', mec='k', markersize=30)
        ax.plot([0, platform_x], [0, platform_y], linewidth=2, c='k')
        ax.text(0, 0, f"{platform_angle}°", c='w', ha='center', va='center')

        # Plot speakers               
        ax.scatter(x=pa['speaker_world_x'], y=pa['speaker_world_y'], c=pa['speaker_angle_world'], cmap=plt.cm.turbo)

        for speaker, spk in pa.groupby(by='Speaker Location'):            
            s = spk.iloc[0]
            ax.text(s['speaker_world_x']*1.2, s['speaker_world_y']*1.2, f"S{speaker:02d}", ha='center', va='center')

        # Set axes properties
        ax.set_xticks([])
        ax.set_yticks([])
        
        ax.set_xlim(-1.4, 1.4)
        ax.set_ylim(-1.4, 1.4)

        ax.set_aspect(1)

        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        

    plt.show()



if __name__ == '__main__':
    main()