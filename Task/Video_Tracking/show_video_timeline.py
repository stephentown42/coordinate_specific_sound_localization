'''
1. Lists all the videos in the project, labelled according to subject and date, with additional metadata (e.g. frame size).
2. Draw timeline of videos



Stephen Town - 18 Oct 2020
'''

import cv2
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


# Note time of implants
implant_dates = {
    'F1701_Pendleton': np.datetime64('2019-07-31'),
    'F1703_Grainger': np.datetime64('2019-02-14'),
    'F1810_Ursula': np.datetime64('2019-11-18'),
    'F1905_Sponge': np.datetime64('2020-08-10'),
    'F1901_Crumble': np.datetime64('2020-08-24'),
    'F1811_Dory': np.datetime64('2020-07-31'),
}


def list_videos(file_path):

    # Define parent directory within which to search
    p = Path(file_path)

    # Create output path
    csv_path = p.joinpath('Video_Table.csv')

    with open(csv_path, 'w+') as fid:

        fid.write('Ferret,Block,Name,Date,Height,Width,FPS\n')

        # For each avi file
        for file in p.glob('**/*_Track_*.avi'):

            # Skip any files that aren't in blocks
            if len(file.parts) < 5:
                continue

            # Parse the file path
            fid.write(file.parts[2] + ',')  # Ferret
            fid.write(file.parts[3] + ',')  # Block
            fid.write(file.name + ',')  # File Name

            # Get datetime by removing extra text from name
            file_date = remove_AT_suffix(file.name)
            fid.write(file_date + ',')

            # Get image statistics
            vCap = cv2.VideoCapture(str(file))

            if vCap.isOpened:
                width = vCap.get(3)
                height = vCap.get(4)
                fps = vCap.get(5)
            else:
                width, height, fps = (-1 for i in range(3))

            fid.write(f"{height:.0f},{width:.0f},{fps}\n")

    return csv_path


def remove_AT_suffix(file_name):

    file_name = file_name.replace('_AT1', '')
    file_name = file_name.replace('_AT2', '')
    file_name = file_name.replace('_AT', '')
    file_name = file_name.replace('_tagged', '')
    file_name = file_name.replace('_C1', '')
    file_name = file_name.replace('_C2', '')
    file_name = file_name.replace('_Track_', ' ')
    file_name = file_name.replace('.avi', '')

    return file_name


def plot_vid_metadata(csv_path):

     # Load in data and sort
    df = pd.read_csv(csv_path)
    df['Datetime'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H-%M-%S')
    df = df.sort_values(by=['Ferret', 'Datetime'])

    df['nPix'] = df['Height'] * df['Width']

    # Get min and max times
    dt = df['Datetime'].to_numpy()
    xlim = (min(dt), max(dt))

    # Convert file names to dates
    plt.style.use('ggplot')
    years = mdates.YearLocator()   # every year
    months = mdates.MonthLocator()  # every month
    years_fmt = mdates.DateFormatter('%Y')

    # Create figure for values vs. time
    fig, axs = plt.subplots(2, 2, sharex=True)
    axs = axs.ravel()

    for ferret, fdata in df.groupby('Ferret'):

        x = fdata['Datetime'].to_numpy()

        axs[0].scatter(x, fdata['Height'], label=ferret)
        axs[1].scatter(x, fdata['Width'], label=ferret)
        axs[2].scatter(x, fdata['nPix'], label=ferret)
        axs[3].scatter(x, fdata['FPS'], label=ferret)

        # if ferret in implant_dates:
            # axs[0].axvline()

    for ax in axs:
        ax.set_xlim(xlim)
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(years_fmt)
        ax.xaxis.set_minor_locator(months)
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

    axs[0].set_ylabel('Height (px)')
    axs[1].set_ylabel('Width (px)')
    axs[2].set_ylabel('Pixels')
    axs[3].set_ylabel('FPS')

    plt.legend()
    plt.tight_layout()
    fig.show()

    # Create histograms
    g, gxs = plt.subplots(2, 2)
    gxs = gxs.ravel()

    df['Height'].hist(ax=gxs[0])
    df['Width'].hist(ax=gxs[1])
    df['nPix'].hist(ax=gxs[2])
    df['FPS'].hist(ax=gxs[3])

    gxs[0].set_xlabel('Height (px)')
    gxs[1].set_xlabel('Width (px)')
    gxs[2].set_xlabel('Pixels')
    gxs[3].set_xlabel('FPS')

    plt.tight_layout()
    g.show()

    input()


def main():

    csv_path = list_videos('E:/UCL_Behaving')

    plot_vid_metadata(csv_path)


if __name__ == '__main__':
    main()
