"""
The goal of this module is to organize primary data
into something convenient to analyse.

Background:
----------
Experiments in the project were conducted over several
years, with changes made to improve data collection or 
correct minor deficiencies. This results in some 
differences in the structure of data files that we 
want to manage here, so we don't have to manage them 
later on when we're focussing on analysis.

Created
    2019: Stephen Town
Updated
    2021 June (ST): 
        Added documentation
        Removed unnecessary functions
            
"""

from datetime import datetime

import numpy as np
import pandas as pd
from pathlib import Path


def list_files(file_path):
    """
    Gets a list of text files that include the relevant task
    levels in the file name
    
    Parameters:
    ----------
    file_path : pathlib Path
        Directory containing subdirectories for each ferret
    ferret : str
        Full name of subject (e.g. "F1701_Pendleton")
    
    Returns:
    --------
    all_files : list
        List of text files for ferret
    """

    # file_path = file_path / ferret
    types = ('*level53*.txt', '*level54*.txt', '*level55*.txt')
    all_files = []

    for files in types:
        all_files.extend(file_path.rglob(files))

    return all_files


def append_session_datetime(file, df=None):
    """
    Strips datetime information from file name and adds
    it to dataframe as 'SessionDate'
    
    Parameters:
    ----------
    file : path or str
        Path to behavioral file
    df : pandas dataframe, optional
        Dataframe containing behavioral trials
    
    Returns:
    --------
    df : pandas dataframe
        Dataframe now with session datetime added

    >>> append_session_datetime('02_03_2018 level53_Pendleton 14_12_10.516 Block_J5-90.txt')
    datetime.datetime(2018, 3, 2, 14, 12, 10)
    """

    if isinstance(file, Path):
        file = file.stem

    [f_date, level, f_time, block] = file.split()
    date_string = f_date + ' ' + f_time[0:8]
    session_dt = datetime.strptime(date_string, '%d_%m_%Y %H_%M_%S')

    if df is None:
        return session_dt
    else:
        df['SessionDate'] = session_dt
        return df


def load_behavioral_files(all_files):
    """
    Loads many behavioral files (usually)
    
    Accommodates changes in data collection methods over the course of the project
    (e.g. updates to column names to remove white space, addition of center pixel
    values)

    Parameters:
    ----------
    all_files : list
        List containing strings of paths to behavioral files

    Notes:
    -----
    Behavioral files here are the original tab-delimited text files recorded during  
    experiments, rather than any formatted or concatenated version generated later.

    Returns:
    --------
    unnamed : pandas dataframe
        Concatenated dataframe containing rows (trials) from multiple test sessions
    """


    # Preassign
    list_ = []
    count = 0

    # For each file
    for file in all_files:

        # Read file in
        try:
            df = pd.read_csv(file, sep='\t', encoding='latin1', index_col='Trial')
        except:
            print(f"Could not load {file}")
            break

        # If the file includes data about the center spout (we don't care about old data lacking this)
        if 'CenterSpoutRotation' in df.columns:

            # Pad Center Pixel Value if not included (only started late in project) -  do this first
            if 'CenterPixelVal' in df:
                df.drop(columns=['CenterPixelVal'], inplace=True)

            # Drop unnamed columns (occurs when each line terminates with tab, which can be read as the start of a new column)            
            df.drop(columns=[x for x in df.columns if 'Unnamed' in x], inplace=True)

            # Correct for early column headers that included "?"
            df = df.rename(columns={'CorrectionTrial?': 'CorrectionTrial',
                                    'CenterReward?': 'CenterReward',
                                    'Speaker_Location': 'Speaker Location',                                    
                                    'LED_Location': 'LED Location'})

            # Get datetime for this file from file name                
            [f_date, level, f_time, block] = file.stem.split()
            date_string = f_date + ' ' + f_time[0:8]
            session_dt = datetime.strptime(date_string, '%d_%m_%Y %H_%M_%S')
            df['SessionDate'] = session_dt

            # Add session number
            count = count + 1
            df['SessionID'] = count

            # if count > 100:
                # print('s')

            # Add to list
            list_.append(df)

    return pd.concat(list_, sort=False)     


def add_timing_columns(frame):
    """
    Adds some useful temporal information to a dataframe, including the total duration
    of all stimuli within a trial (to look at data with multiple stimulus repeats), and 
    the unique time of each time (which is helpful to distinguish data points when 
    plotting trial values vs time). 

    The function also sorts trials by start datetime, ensuring that dataframes containing
    results from multiple sessions have a meaningful order.
    
    Parameters:
    ----------
    frame : pandas dataframe
        Dataframe containing session datetime, trial start time, stimulus duration and 
        number of stimulus repeats
    
    Returns:
    --------
    frame : pandas dataframe
        Dataframe sorted by trial datetime, with total stimulus duration added
    """

    # if isinstance(frame.SessionDate[0], str):   # Ensure correct datatype
    #     frame.SessionDate = pd.to_datetime(frame.SessionDate)

    frame['StartDateTime'] = frame['SessionDate'] + pd.to_timedelta(frame['StartTime'], unit='s')

    frame = frame.sort_values(by='StartDateTime')

    frame['StimulusTotalDuration'] = frame['Duration'] * frame['nStimReps']

    return frame


def wrap_to_180(x):
    """
    Wraps value to between -180 and 180 degrees
    
    Parameters:
    ----------
    x : float
        Angular value in degrees
    
    Returns:
    --------
    x : float
        Angle wrapped to -180 <= x < 180

    >>> wrap_to_180(-270)
    90
    >>> wrap_to_180(335)
    -25
    >>> wrap_to_180(180)
    -180
    >>> wrap_to_180(-180)
    -180

    """
    if x < -180:
        x += 360
    elif x >= 180:
        x -= 360
    return x


def format_angular_values(frame):
    """
    Convert world-centred clock notation to angular format and map 
    speaker and response angles from world-centred to platform centred
    coordinates. 

    Map is from clock-face indices (1 to 12) to angles (150 to -180°). 
    
    Parameters:
    ----------
    frame : pandas dataframe
        Dataframe with spatial variables in clock (1-12) format
    
    Returns:
    --------
    frame : pandas dataframe
        Dataframe with spatial variables also in degrees
    """
    
    frame['response_angle_world'] = [180 + (i * -30) for i in frame['Response']]
    frame['speaker_angle_world'] = [180 + (i * -30) for i in frame['Speaker Location']]

    # Calculate speaker angle relative to platform (putative head) coordinate frame
    frame['speaker_angle_platform'] = frame['speaker_angle_world'] - frame['CenterSpoutRotation']
    frame['speaker_angle_platform'] = frame['speaker_angle_platform'].apply(wrap_to_180)

    # Calculate response angle relative to platform
    frame['response_angle_platform'] = frame['response_angle_world'] - frame['CenterSpoutRotation']
    frame['response_angle_platform'] = frame['response_angle_platform'].apply(wrap_to_180)

    return frame


def remove_correction_trials(frame):
    # TO DO: Remove this function

    idx = frame['CorrectionTrial'] == 0
    frame = frame[idx]

    return frame


def remove_repeatStim_trials(frame):
    # TO DO: Remove this function

    idx = frame['nStimReps'] == 1
    frame = frame[idx]

    return frame


def flag_probe_trials(df, task, valid_locations):
    """
    Add a boolean variable to a dataframe indicating whether sounds are from probe or 
    test locations

    Parameters:
    ----------
    df : pandas dataframe
        Dataframe containing sound locations on all trials in relevant coordinate frame
    task : str
        Allocentric / Egocentric
    valid_locations : List
        List of speaker locations in relevant coordinate system or nomenclature

    Returns:
    --------
    df : pandas dataframe
        Dataframe with added column
    """

    if task == 'World':
        df['not_probe'] = df['Speaker Location'].isin(valid_locations)     # Speaker location = 1 to 12 o'clock

    elif task == 'Head':
        df['not_probe'] = df['speaker_angle_platform'].isin(valid_locations)   # Angle = -180 : 30 : 180°

    return df


def report_by_angle(test_data):

    # TO DO: Replace this function with groupby (much neater)
    # by_CSR = test_data.groupby(by='CenterSpoutRotation')

    # Get unique values and ignore nan
    angles = test_data.CenterSpoutRotation.unique()
    # angles = angles[~np.isnan(angles)]
    angles.sort()

    # For each angle
    for i in range(0, angles.size):

        # Filter for data
        angle_data = test_data[test_data['CenterSpoutRotation'] == angles[i]]

        # Get percent correct
        nTrials = angle_data.shape[0]
        nCorrect = sum(angle_data.Correct)

        # Report to user
        print('\t%d°: ' % angles[i], end='')
        # print(repr(angles[i]) + '%d°:', end=' ')
        print('{0[0]} / {0[1]} trials, '.format((nCorrect, nTrials)), end=' ')
        print('{:.1%}'.format(nCorrect / nTrials))



def id_center_spout_changes(test_data):
    """
    Get the number of times the center platform has changed position between 
    two angles, while ignoring times that the platform remained in a constant
    direction.
    
    Parameters:
    ----------
    test_data : pandas dataframe
        Dataframe containing center platform angles (CenterSpoutRotation),
        animal behavior (Correct) and a column to order test sessions
        (SessionID)
    
    Returns:
    --------
    ~ : dict
        Dictionary with the number of trials as a 2D numpy array, with the 
        previous angle as column (x) and the next angle as row (y). Also 
        includes whether the first trial was performed correctly.
    """


    # Get unique angles
    angles = test_data.CenterSpoutRotation.unique()
    angles = angles.tolist()
    angles.sort()

    # Preassign matrix in which we will count each change in rotation
    nAngles = len(angles)
    nTrials = np.zeros((nAngles, nAngles), dtype=int)
    nCorrect = np.zeros((nAngles, nAngles), dtype=int)

    # # Intialize
    rotation_value = test_data['CenterSpoutRotation'][0:1].values
    rotation_value = rotation_value[0]

    session_id = test_data['SessionID'][0:1].values
    session_id = session_id[0]

    # For each row
    for index, row in test_data.iterrows():

        # If the current value has changed
        if rotation_value != row['CenterSpoutRotation'] or session_id != row['SessionID']:

            # Get row and column indices for count matrix
            row_index = angles.index(row['CenterSpoutRotation'])
            col_index = angles.index(rotation_value)

            # Add one to count value
            nTrials[row_index, col_index] += 1

            # Add an additional trial if the animal performed correctly
            nCorrect[row_index, col_index] = nCorrect[row_index, col_index] + row['Correct']

            # Update rotation and session id
            rotation_value = row['CenterSpoutRotation']
            session_id = row['SessionID']   

    return {'nTrials': nTrials, 'nCorrect':nCorrect, 'x': angles, 'y': angles}


def get_angle_changes(angles):
    """
    Creates a difference matrix for a list of angles
    
    Parameters:
    ----------
    angles : list or numpy array
        List of angles with n elements
    
    To Do:
    -----
    This function may be defunct - check if can be removed

    Returns:
    --------
    delta_angle : numpy array
        2D array of distances with n-by-n elements
    """

    # Create angle difference map
    nAngles = len(angles)
    delta_angle = np.zeros((nAngles, nAngles), dtype=int)

    for i in range(0, nAngles):  # For each index of angle
        for j in range(0, nAngles):
            delta_ij = abs(angles[i] - angles[j])   # Get the unsigned difference

            if delta_ij > 180:  # Wrap around circle (if required)
                delta_ij = 360 - delta_ij

            delta_angle[i, j] = delta_ij

    return delta_angle


def get_pCorrect_with_angle_changes(nTrials, nCorrect, delta_angles):
    """
    Description
    
    This data should be collected from the first trial after rotation

    
    Parameters:
    ----------
    nTrials : 2D numpy array 
        Matrix with the number of *total* trials for each change in center
        spout rotation from angle x to angle y
    nCorrect : 2D numpy array
        Matrix with the number of *correct* trials for each change in center
        spout rotation from angle x to angle y
    delta_angles : 2D numpy array
        Matrix with the angular distance for each change in center
        spout rotation from angle x to angle y
    
    TO DO:
    Split the analysis and plotting aspects of this function into two
    
    
    Returns:
    --------
    data : List
        List of plotly graphics objects containing:
        - scatter plot of unique changes in angle vs. percentage correct
        - bar plot of trial number
        - bar plot of number of trials correct
    """

    # Check the input sizes are the same
    assert nTrials.shape == nCorrect.shape
    assert nTrials.shape == delta_angles.shape
    
    # Flatten arrays
    nTrials = nTrials.flatten()
    nCorrect = nCorrect.flatten()
    delta_angles = delta_angles.flatten()

    # Get unique changes in angle value
    unique_changes = np.unique(delta_angles)
    unique_changes = unique_changes.tolist()
    unique_changes.sort()

    # Preassign list of
    nChanges = len(unique_changes)
    nTrials_total = np.zeros(nChanges, dtype=int)
    nCorrect_total = np.zeros(nChanges, dtype=int)

    # For each cell in the matrix
    for input_idx, angle_delta in np.ndenumerate(delta_angles):

        # Get index of change
        output_idx = unique_changes.index(angle_delta)

        # Add numbers to vectors
        nTrials_total[output_idx] = nTrials_total[output_idx] + nTrials[input_idx]
        nCorrect_total[output_idx] = nCorrect_total[output_idx] + nCorrect[input_idx]

    # Get percent correct
    pCorrect_total = nCorrect_total / nTrials_total * 100

    # Create graphics objects
    # Generate line plot of performance vs angle
    trace0 = go.Scatter(x=unique_changes, y=pCorrect_total, name='pCorrect',
                        line=dict(color='rgb(0,0,0)', width=2))

    # Create bar object showing total number of trials
    trace1 = go.Bar(x=unique_changes, y=nTrials_total,
                    text=nTrials_total,   # this puts the actual numbers on the bars
                    textfont=dict(color='rgb(0,0,0)'),
                    name='Total',   # this is the name used in the legend
                    yaxis='y2',
                    textposition='auto',
                    marker=dict(
                        color='rgb(145,29,183)',
                        line=dict(
                            color='rgb(103,0,137)',
                            width=1.5),
                    ), opacity=0.6)

    # Create bar object showing number of trials correct
    trace2 = go.Bar(x=unique_changes, y=nCorrect_total, text=nCorrect_total, name='Correct',
                    textposition='auto', opacity=0.6, yaxis='y2',
                    marker=dict(color='rgb(255,238,0)',
                                line=dict(color='rgb(168,157,3)', width=1.5)))

    # Bring those objects together
    data = [trace0, trace1, trace2]

    return data


def get_probe_performance(test_data, np, pd, ferret):

    from math import pi

    # Get rid of white space in column names
    test_data.columns = test_data.columns.str.replace(' ', '')

    # # Get unique center spout and speaker angles
    speakers = test_data.SpeakerLocation.unique()   # e.g. speakers 1-12
    CS_angles = test_data.CenterSpoutRotation.unique()  # e.g. -150 to 180 in 30° steps

    # Convert speaker index into angle
    speaker_angle = -30 * speakers
    speaker_angle = speaker_angle + 180

    # Preassign
    my_list = list()

    # For each speaker location (i.e. world angle)
    for speaker in speakers:

        # Filter for data
        speaker_data = test_data[test_data['SpeakerLocation'] == speaker]

        # For each center spout angle
        for CS_angle in CS_angles:

            # Filter for data
            flt_data = speaker_data[speaker_data['CenterSpoutRotation'] == CS_angle]

            # Get number of trials
            nTrials = sum(flt_data['Response'] == 3) + sum(flt_data['Response'] == 9)

            # If this combination of speaker index and center spout angle was tested
            if flt_data.shape[0] > 0:
                nResponse = sum(flt_data['Response'] == 3)  # Get number of instances of each response type
            else:
                nResponse = 0

            # Write results to text file
            my_list.append({'Speaker_Idx': speaker, 'Platform_Angle': CS_angle, 'nTrials': nTrials, 'nSpout3': nResponse})

    # Convert to pandas dataframe
    df = pd.DataFrame(my_list)

    # Convert platform angles from degrees to radians
    df.Platform_Angle = df.Platform_Angle / 180 * pi     # Convert to radians

    # Add Speaker Location in the world (in radians)
    def index2world(idx):
        return pi + idx * -(pi / 6)

    df['SpeakerAngleWorld'] = index2world(df['Speaker_Idx'])

    # Calculate Speaker angles relative to platform
    df['platform_speaker_angle'] = df['SpeakerAngleWorld'] - df['Platform_Angle']
    df['platform_speaker_angle'] = df['platform_speaker_angle'].apply(lambda x: x - (2 * pi) if x > pi else x)  # Wrap to ± pi
    df['platform_speaker_angle'] = df['platform_speaker_angle'].apply(lambda x: x + (2 * pi) if x <= (0.01 - pi) else x)

    # Return data frame
    return df


def draw_probe_performance(test_data, np, go, py, ferret, notebook=False):

    # Get rid of white space in column names
    test_data.columns = test_data.columns.str.replace(' ', '')

    # # Get unique center spout and speaker angles
    speakers = test_data.SpeakerLocation.unique()   # e.g. speakers 1-12
    CS_angles = test_data.CenterSpoutRotation.unique()  # e.g. -150 to 180 in 30° steps

    # Sort
    CS_angles.sort()
    speakers.sort()

    # Convert speaker index into angle
    speaker_angle = -30 * speakers
    speaker_angle = speaker_angle + 180

    # Count unique cases
    nSpeakers = len(speakers)
    nCS_Angles = len(CS_angles)

    # Create results space
    nRight = np.zeros((nSpeakers, nCS_Angles), dtype=int)
    nTrials = np.zeros((nSpeakers, nCS_Angles), dtype=int)

    # For each speaker location (i.e. world angle)
    for spkr_idx, speaker in enumerate(speakers):

        # Filter for data
        speaker_data = test_data[test_data['SpeakerLocation'] == speaker]

        # For each center spout angle
        for CS_idx, CS_angle in enumerate(CS_angles):

            # Filter for data
            flt_data = speaker_data[speaker_data['CenterSpoutRotation'] == CS_angle]

            # Get number of trials
            nTrials[spkr_idx, CS_idx] = sum(flt_data['Response'] == 3) + sum(flt_data['Response'] == 9)

            # If data exists for this combination of speaker index and center spout angle
            if flt_data.shape[0] > 0:

                # Get number of instances of each response type
                nResponses = sum(flt_data['Response'] == 3)

                # Append to lists
                nRight[spkr_idx, CS_idx] = nResponses

            else:
                f'No data: Platform @ {CS_angle}, Speaker {speaker}'

    # Calculate percent correct in each cell
    np.seterr(divide='ignore', invalid='ignore')  # ignore divide by zero (data still being collected for these areas)
    pRight = nRight / nTrials

    ####################################################################
    # Analyze marginals

    ####################################################################
    # Create graphics objects

    trial_n_map = go.Heatmap(x=CS_angles, y=speakers, z=nTrials,    # Trial number
                             colorscale='Greys',
                             xaxis='x1', yaxis='y1')

    trace1 = go.Heatmap(x=CS_angles, y=speakers, z=nRight,  # Number of trial correct
                        colorscale='Greys',
                        xaxis='x2', yaxis='y2')

    trace2 = go.Heatmap(x=CS_angles, y=speakers, z=pRight,  # Trial number
                        colorscale='Greys',
                        xaxis='x3', yaxis='y3')

    layout = go.Layout(title=ferret,
                       xaxis=dict(title='Center Spout Angle (°)',  # bottom left
                                  domain=[0, 0.3]),
                       yaxis=dict(title='World Angle (°)',
                                  domain=[0, 1]),
                       xaxis2=dict(title='Center Spout Angle (°)', anchor='x2',  # bottom right
                                   domain=[0.35, 0.65]),
                       yaxis2=dict(domain=[0, 1],
                                   anchor='y2'),
                       xaxis3=dict(title='Center Spout Angle (°)', anchor='x3',  # top left
                                   domain=[0.7, 1]),
                       yaxis3=dict(domain=[0, 1],
                                   anchor='y3'))

    fig = go.Figure(data=[trial_n_map, trace1, trace2], layout=layout)

    # Plot to file or notebook
    if notebook:
        py.iplot(fig, filename='jupyter_' + ferret)
    else:
        html_name = ferret + '_probe_count.html'
        py.plot(fig, filename=html_name)


if __name__ == "__main__":
    import doctest
    doctest.testmod()