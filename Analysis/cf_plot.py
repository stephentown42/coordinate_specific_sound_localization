"""


Created - 2019, Stephen Town
Updated
    2021 June 07 (ST): 
        Added documentation
        Removed 
            
"""

from collections.abc import Iterable

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns

########################################################################################
# Matplotlib functions
#   - Developed for publications
#   - Intended for use with balanced datasets
#   - Designed with little / no analysis in functions
#   - Designed for use with stylesheet-like dictionary for consistency


def inch2cm(inches):
    """
    Designed for use with matplotlib
    
    Parameters:
    ----------
    cm : int, float or list/tuple of ints/floats
        Values in cm that need converting
    
    Returns:
    --------
    y : float or list/tuple of floats
        Values in inches

    >>> cm2inch(2.54)
    1

    >>> cm2inch((25.4, 25.4))
    (10,10)

    >>> cm2inch([254.0, 254.0])
    [100,100]
    """

    if isinstance(inches, float) or isinstance(inches, int):
            return float(inches) * 2.54
    else:
        y = [float(x) * 2.54 for x in inches]

        if isinstance(inches, tuple):
            y = tuple(y)    
        
        return y



def cm2norm(x, fig_size):
    """
    Converts the desired size of an axis in centimeters into the required 
    normalized values, given a set figure size.

    The idea here is usually to generate a canvas big enough to show the axes, 
    and then cut the figure out in the figure design software (e.g. illustrator / gimp)
    
    
    Parameters:
    ----------
    x : list
        4-element vector containing the position of an object (usually axes) required in cm
    fig_size : tuple
        2-element tuple containing figure width and height in inches
    
    Returns:
    --------
    y : list
        4-element vector for position in units normalized for figure shape

    >>> cm2norm([0, 0, 5.08, 5.08], (2, 2))
    [0.0, 0.0, 1.0, 1.0]
    """

    assert len(x) == 4
    assert len(fig_size) == 2
    assert isinstance(fig_size, tuple)

    fig_width_cm, fig_height_cm = inch2cm(fig_size)
    
    return [
        x[0] / fig_width_cm,
        x[1] / fig_height_cm,
        x[2] / fig_width_cm, 
        x[3] / fig_height_cm
    ]
        

def cm2inch(cm):
    """
    Designed for use with matplotlib
    
    Parameters:
    ----------
    cm : int, float or list/tuple of ints/floats
        Values in cm that need converting
    
    Returns:
    --------
    y : float or list/tuple of floats
        Values in inches

    >>> cm2inch(2.54)
    1

    >>> cm2inch((25.4, 25.4))
    (10,10)

    >>> cm2inch([254.0, 254.0])
    [100,100]
    """

    if isinstance(cm, float) or isinstance(cm, int):
            return float(cm) / 2.54
    else:
        y = [float(x) / 2.54 for x in cm]

        if isinstance(cm, tuple):
            y = tuple(y)    
        
        return y


def get_ax_offset(ax_size, margin):
    """
    Description
    
    Parameters:
    ----------
    ax_size : tuple
        2-element tuple containing the width and height of a single axis
    margin : tuple
        2-
    
    Returns:
    --------
    a : var_type
        Description
    """


def get_fig_style(output_type='talk'):
    """
    Work in progress
    
    Parameters:
    ----------
    output_type : str
        Whether to create a figure for a paper (small but high res) or 
        for a talk (large but low res)

    Notes:
    -----
    Because of challenges getting Matplotlib to do what I want re 
    saving in the correct resolution and figure size at the same time
    it may be that the values here look odd. 
    
    Returns:
    --------
    fss : dict
        Dictionary defining style for figure (cheapo css)
    """

    if output_type == 'paper':      
        fss = dict(        
            format ='paper',
            font_size = 8,
            axis_label_size = 7,
            fig_size = (7, 4),
            ax_size = (2.5, 2),
            ax_margin = (0.2, 0.3)
        )

    else:                      
        fss = dict(
            format = 'talk',
            font_size = 15,
            axis_label_size = 13,
            fig_size = (16, 9)
        )

    fss['axis_font_color'] = '#4d4d4d'

    return fss


def make_ticks_integers(ax, dim):
    """
    Sets the values on a matplotlib axis to be shown as integers
    
    Parameters:
    ----------
    ax : matplotlib axes
        Axis object to modify
    dim : str
        Axes / Axis object to change ('x','y' or 'xy') 
    
    Returns:
    --------
    None
    """

    if dim == 'x':
        ax.set_xticklabels(['{:.0f}'.format(float(t.get_text())) for t in ax.get_xticklabels()])
    elif dim == 'y':
        ax.set_yticklabels(['{:.0f}'.format(float(t.get_text())) for t in ax.get_yticklabels()])
    elif dim == 'xy':
        ax.set_yticklabels(['{:.0f}'.format(float(t.get_text())) for t in ax.get_yticklabels()])
        ax.set_xticklabels(['{:.0f}'.format(float(t.get_text())) for t in ax.get_xticklabels()])


def wrap_data(df, colname, filter_val=-180, delta=360):
    """
    Description
    
    Parameters:
    ----------
    df : pandas dataframe
        Description
    colname : str
        Name of column containing values to wrap (e.g. platform angle)
    filter_value : float
        Value to identify data to be wrapped (e.g. -180)
    delta : float
        Change to create new value (e.g. -180 + 360 = 180)
    
    Returns:
    --------
    df : pandas dataframe
        Dataframe with wrapped value
    """

    wrap_data = df[df[colname] == filter_val].copy()
    wrap_data[colname] = wrap_data[colname] + delta
        
    return pd.concat([df, wrap_data])


def rotate_tick_labels(ax, dim, angle=45):

    if dim == 'x':
        labels = ax.get_xticklabels()
        ax.set_xticklabels(labels, rotation=angle)
    
    elif dim == 'y':
        labels = ax.get_yticklabels()
        ax.set_yticklabels(labels, rotation=angle)

    return labels


def plot_y_vs_theta(fss, ax, y, error=None, chance=0.5, xlabelstr='x', ylabelstr='y', ytix=[0, 1], wrapOn=None):
    """
    Plot mean and standard deviation of performance (% correct) vs. platform 
    angle in the world. Fill area between line and chance performance to 
    emphasize non-trivial behavior.
    
    Parameters:
    ----------
    fss : dict
        Style info for plotting 
    ax : matplotlib axes
        Axes for plotting
    df : pandas dataframe
        Dataframe with values to plot on x and y axes
    chance : float, optional
        Value for chance performance
    xlabelstr : str, optional
        String for x axis label
    ylabelstr : str, optional
        String for y axis label
    ytix : list
        Values for y tick marks
        
    TO DO:
        Make this more general so that can be used for response probability

    Returns:
    --------
    ax : matplotlib axes 
        Object on which plots have been added
    """

    # Apply wrap to data (optional)
    if wrapOn is not None:
        w = y[y.index == wrapOn]
        w.index += 360
        y = y.append(w)        

        if error is not None:
            f = error[error.index == wrapOn]
            f.index += 360
            error = error.append(f) 

    # Plot mean and (optionally) standard deviation
    if error is None:
        ax.plot(y.index, y, c=fss['fcolor'], lw=1)
    else:
        ax.errorbar(y.index, y, error, c=fss['fcolor'], label=fss['fNum'], lw=1)
        
    # Label subject
    if fss['format'] == 'talk':
        ax.plot(120, 15, marker='o', ms=56, mfc=fss['fcolor'], lw=2)     # Circles for ferret images
    # elif fss['format'] == 'paper':
    #     ax.text(-170, 90, fss['fNum'], fontsize=fss['font_size'], color=fss['fcolor'], fontweight='bold')     # Numbers 

    # Plot chance performance and fill area between chance and observed performance
    if chance is not None:
        chance_y = np.full_like(y, chance)
        ax.plot(y.index, chance_y, c="#888888", linestyle='--', lw=1)
        ax.fill_between(y.index, chance_y, y, alpha=0.2, color=fss['fcolor'])

    # Make axes pretty
    ax.set_xlabel(xlabelstr, fontsize=fss['font_size'], color=fss['axis_font_color'])
    ax.set_xlim(-180, 180)
    ax.set_xticks(y.index)
    ax.set_xticklabels(['-180', '', '', '-90', '', '', '0', '', '', '90', '', '', '180'], rotation=45)

    ax.set_ylabel(ylabelstr, fontsize=fss['font_size'], color=fss['axis_font_color'])
    ax.set_yticks(ytix)
    ax.set_ylim(min(ytix), max(ytix))    
    
    ax.tick_params(axis='both', labelsize=fss['axis_label_size'], labelcolor=fss['axis_font_color'])

    return ax


def make_heatmap_tick_labels(x_val):

    x_str = []
    for x in x_val:
        if x % 90 == 0:
            x_str.append(str(x))
        else: 
            x_str.append('')

    return x_str


def plot_joint_responseP(fss, ax, df):
    """
    Plot response probability as a function of sound angle in two coordinate
    systems.
    
    Parameters:
    ----------
    fss: dict
        Figure style sheet
    ax : matplotlib axes
        Axes to plot data
    df : pandas dataframe
        Dataframe containing sound angles in world and relative to platform,
        as well as response probability
    Returns:
    --------
    None
    """

    # Wrap to 180 degrees (i.e. have two datapoints for 180 and -180)    
    df = wrap_data(df, 'stim_platf', filter_val=-180, delta=360)
    df = wrap_data(df, 'stim_world', filter_val=-180, delta=360)

    # Reformat data
    df.sort_values(by=['stim_world','stim_platf'], inplace=True)

    y_val = df['stim_world'].unique()
    x_val = df['stim_platf'].unique()
    
    y_str = make_heatmap_tick_labels(y_val)
    x_str = make_heatmap_tick_labels(x_val)

    ny = len(y_val)
    nx = len(x_val)

    z = df['pResp'].to_numpy()   
    assert (nx * ny) == len(z)
    
    z = np.reshape(z, (ny, nx))    

    cb_opt = {'label': 'p(Response)'}

    sns.heatmap(z, ax=ax, cmap='vlag', vmin=0, vmax=1, xticklabels=x_str, yticklabels=y_str, cbar=False)

    # cbar = ax.collections[0].colorbar
    # cbar.ax.tick_params(labelsize=fss['axis_label_size'])

    ax.set_xlim(0, nx)
    ax.set_ylim(0, ny)

    # ax.set_xticks(np.where(x_val % 90 == 0))
    # ax.set_yticks(np.where(y_val % 90 == 0))
    
    # ax.set_xticklabels([str(x) for x in x_val if x % 90 == 0])
    # ax.set_yticklabels([str(y) for y in y_val if y % 90 == 0])

    ax.set_xlabel('Speaker Angle: Head (°)', fontsize=fss['font_size'], color=fss['axis_font_color'])
    ax.set_ylabel('Speaker Angle: World (°)', fontsize=fss['font_size'], color=fss['axis_font_color'])

    # ax.set_title(fss['fNum'])
    
    ax.tick_params(axis='both', labelsize=fss['axis_label_size'], labelcolor=fss['axis_font_color'])


def remove_spines(axs, spines=['top','right']):
    """
    Remove spines (box lines surrounding axes) from axis
    
    Parameters:
    ----------
    axs : matplotlib axes, or list of axes
        Axes to remove spines from
    spines : str or  list of str, optional
        List of spines to remove (from 'top','left','right','bottom')
    
    Returns:
    --------
    None
    """
    
    if not isinstance(axs, Iterable):
        axs = [axs]

    for ax in axs:

        if isinstance(spines, str):
            ax.spines[spines].set_visible(False)
        else:
            for spine in spines:
                ax.spines[spine].set_visible(False)


##########################################################################################
# Older Plotly functions
#   - Created for use monitorring performance during experiments
#   - Not designed specifically for use with balanced datasets
#   - May include some analysis with plotting functionality
#   - Candidates for deletion


def draw_performance_by_angle(test_data, py, ferret, notebook=False):

    # Get unique values and ignore nan
    angles = test_data.CenterSpoutRotation.unique()
    angles.sort()

    # Initialize lists
    nTrials = list()
    nCorrect = list()

    # For each angle
    for angle in angles:

        # Filter for data
        angle_data = test_data[test_data['CenterSpoutRotation'] == angle]
        # Add values to data frame
        nTrials.append(angle_data.shape[0])
        nCorrect.append(sum(angle_data.Correct))

    # Calculate performance
    pCorrect = (np.asarray(nCorrect) / np.asarray(nTrials)) * 100

    # Create graphics objects
    # Generate line plot of performance vs angle
    trace0 = go.Scatter(x=angles, y=pCorrect, name='pCorrect')

    # Create bar object showing total number of trials
    trace1 = go.Bar(x=angles, y=nTrials,
                    text=nTrials,   # this puts the actual numbers on the bars
                    name='Total',   # this is the name used in the legend
                    yaxis='y2',
                    textposition='auto',
                    marker=dict(
                        color='rgb(178,178,178)',
                        line=dict(
                            color='rgb(8,48,107)',
                            width=1.5),
                    ), opacity=0.6)

    # Create bar object showing number of trials correct
    trace2 = go.Bar(x=angles, y=nCorrect, text=nCorrect, name='Correct',
                    textposition='auto', opacity=0.6, yaxis='y2',
                    marker=dict(color='rgb(58,200,225)',
                                line=dict(color='rgb(8,48,107)', width=1.5)))

    # Bring those objects together
    data = [trace0, trace1, trace2]

    show_performance_vs_trial_count(go, py, data, ferret, notebook)


def draw_pSpout9_by_angle(test_data, np, go, py, ferret, notebook=False):

    # Get unique values and ignore nan
    angles = test_data.CenterSpoutRotation.unique()
    angles.sort()

    # Initialize lists
    nTrials = list()
    nSpout9 = list()

    # For each angle
    for angle in angles:

        # Filter for data
        angle_data = test_data[test_data['CenterSpoutRotation'] == angle]
        # Add values to data frame
        nTrials.append(angle_data.shape[0])
        nSpout9.append(sum(angle_data.Response == 9))

    # Calculate performance
    pSpout9 = (np.asarray(nSpout9) / np.asarray(nTrials)) * 100

    # Create graphics objects
    # Generate line plot of performance vs angle
    trace0 = go.Scatter(x=angles, y=pSpout9, name='pSpout9')

    # Create bar object showing total number of trials
    trace1 = go.Bar(x=angles, y=nTrials,
                    text=nTrials,   # this puts the actual numbers on the bars
                    name='Total',   # this is the name used in the legend
                    yaxis='y2',
                    textposition='auto',
                    marker=dict(
                        color='rgb(178,178,178)',
                        line=dict(
                            color='rgb(8,48,107)',
                            width=1.5),
                    ), opacity=0.6)

    # Create bar object showing number of trials correct
    trace2 = go.Bar(x=angles, y=nSpout9, text=nSpout9, name='Correct',
                    textposition='auto', opacity=0.6, yaxis='y2',
                    marker=dict(color='rgb(58,200,225)',
                                line=dict(color='rgb(108,48,98)', width=1.5)))

    # Bring those objects together
    data = [trace0, trace1, trace2]

    show_performance_vs_trial_count(go, py, data, ferret, notebook)


def show_performance_vs_trial_count(go, py, data, ferret, notebook):

    # Generate file name for plotting
    html_name = ferret + '.html'

    # Setup an overlay plot with two y axes
    layout = go.Layout(
        title=ferret,
        yaxis=dict(range=[40, 100],
                   title='(% Correct)'
                   ),
        yaxis2=dict(
            title='Number of trials',
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            overlaying='y',
            side='right'
        )
    )

    # Generate that figure
    fig = go.Figure(data=data, layout=layout)

    # Save and show as html in file browser
    if notebook:
        py.iplot(fig, filename='jupyter_' + ferret)
    else:
        py.plot(fig, filename=html_name)


def draw_angle_by_date(test_data, go, plotly, ferret):

    # Generate line plot of performance vs angle
    trace0 = go.Scatter(x=test_data['StartDateTime'], y=test_data['CenterSpoutRotation'],
                        mode='lines+markers')

    # specify layout
    layout = go.Layout(title=ferret, yaxis=dict(title='Center Spout Angle (°)'))

    # Generate that figure
    fig = go.Figure(data=[trace0], layout=layout)

    # Save and show as html in file browser
    plotly.offline.plot(fig, filename=ferret + '_CSA_vs_datetime.html')


def id_center_spout_changes(test_data):
    """
    Get the number of rotations from one platform angle to another
    
    Parameters:
    ----------
    test_data : pandas dataframe
        Dataframe containing platform angles and sessionID (filename?)
    
    Notes:
    -----
    Assumes that input data is correctly ordered by date

    Returns:
    --------
    output : dict
        Dictionary containing the number of switches from one platform angle (column x) 
        to another(row y)
    """

    # Get unique angles
    angles = test_data.CenterSpoutRotation.unique()
    angles = angles.tolist()
    angles.sort()

    # Preassign matrix in which we will count each change in rotation
    nAngles = len(angles)
    nTrials = np.zeros((nAngles, nAngles), dtype=int)
    nCorrect = np.zeros((nAngles, nAngles), dtype=int)

    # Intialize
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

    output = {
    'nTrials': nTrials, 'x': angles, 'y': angles}

    return output




def get_angle_changes(np, angles):

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


def plot_pCorrect_with_angle_changes(angle_change, nTrials, nCorrect, Fig=None):
    """
    This data should be collected from the first trial after rotation
    
    Parameters:
    ----------
    angle_changes : numpy array 
        Array of angular distances
    nTrials : numpy array
        Array of sample sizes
    nCorrect : 2D numpy array
        Array containing number of trials solved correctly
        
    Returns:
    --------
    data : List
        List of plotly graphics objects containing:
        - scatter plot of unique changes in angle vs. percentage correct
        - bar plot of trial number
        - bar plot of number of trials correct

    INSERT TEST HERE

    """
    
    pCorrect = nCorrect / nTrials * 100
    
    scat_obj = go.Scatter(            # Line plot of performance vs angle
        x = angle_change,
        y = pCorrect,
        name = 'pCorrect',
        line = dict(
            color = 'rgb(0,0,0)',
            width=2
            ),
        )
    
    bar_nT = go.Bar(                # Bar plot of total number of trials
        x = angle_change, 
        y = nTrials,
        text = nTrials,   
        textfont = dict(
            color='rgb(0,0,0)'
            ),
        name = 'Total',   
        yaxis = 'y2',
        textposition = 'auto',
        marker = dict(
            color = 'rgb(145,29,183)',
            line = dict(
                color = 'rgb(103,0,137)',
                width = 1.5
                )
            ), 
        opacity=0.6
        )

    bar_nC = go.Bar(                    # bar plot of number of trials correct
        x = angle_change,
        y = nCorrect,
        text = nCorrect,
        name = 'Correct',
        textposition = 'auto',
        opacity = 0.6,
        yaxis = 'y2',
        marker = dict(
            color = 'rgb(255,238,0)',
            line = dict(
                color = 'rgb(168,157,3)',
                width = 1.5
                ),
            ),
        )

    if fig is None:
        fig = make_subplots(rows=2,cols=1, shared_xaxes=True)
        fig.add_trace(scat_obj, row=1, col=1)
        fig.add_trace(bar_nT, row=2, col=1)
        fig.add_trace(bar_nC, row=2, col=1)
        fig.show()
    else:
        return [scat_obj, bar_nT, bar_nC]


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
