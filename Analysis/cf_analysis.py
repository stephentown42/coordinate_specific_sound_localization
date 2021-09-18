"""

Created:
    2021-06-21 by Stephen Town

"""

import pandas as pd
import numpy as np
from scipy import stats

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


def get_joint_responseP(df, sample_size=3, nIterations=100):
    """
    Get the probability of making a response for each combination of 
    sound angles in head and world-centred space.

    Ensure that measurements are made using equal sample sizes and use
    bootstrap resampling to get a better estimate of the sample mean 
    (where sample sizes allow) and potentially estimate variability (though
    we're not really going to use that info here)
    
    Parameters:
    ----------
    df : pandas dataframe
        Dataframe containing sound angle in head and world coordinates, 
        platform angle in the world, and behavioral response on each trial
    sample_size : int
        Number of samples required for each combination of head and world coordinates
        (Note this is small because most data comes from probe tests)
    nIterations : int
        Number of bootstrap resamples
    
    Returns:
    --------
    stim_platf : numpy array
        1D array of sound angles relative to platform
    stim_world : numpy array
        1D array of sound angles in the world
    pResp : numpy array
        2D array of response probabilities for each combination of sound angles
    """

    # Group by stimulus angle and get performance
    n_response, n_trial, stim_platf, stim_world = [], [], [], []

    for angle_combo, group_data in df.groupby(['speaker_angle_world','speaker_angle_platform']):

        stim_world.append(angle_combo[0])
        stim_platf.append(angle_combo[1])
        
        response_count, trial_count = 0, 0

        for i in range(0, nIterations):
            sampled_data = group_data.sample(sample_size, replace=True)
            response_count = response_count + sampled_data['Response'].sum()
            trial_count = trial_count + sampled_data.shape[0]

        n_response.append(response_count)
        n_trial.append(trial_count)
        
    # Return as dataframe
    result = list(zip(stim_platf, stim_world, n_response, n_trial))
    result = pd.DataFrame( result, columns=['stim_platf','stim_world','nResp','nTrial'])

    result['pResp'] = result['nResp'] / result['nTrial']

    return result



def get_percent_correct(df, sample_size=400, nIterations=100):
    """
    Get task performance (% correct) for each platform angle, using 
    fixed sample sizes with bootstrap resampling.
    
    Parameters:
    ----------
    df : pandas dataframe
        Dataframe containing columns for correct scoring (0=error, 1=correct) and 
        platform orientation
    sample_size : int
        Number of trials over which to measure task performance at each platform angle
    nIterations : int
        Number of bootstrap iterations over which to ensure consistency of measurement

    TO DO:        
        Think about random state of sampling more critically

    Notes:
    ------
    Sample size is selected to maximise the available data    
    The confidence intervals across bootstrap resampling are very small, even when sample
    size and number of iterations are lower (e.g. 100 and 20 respectively)

    Returns:
    --------
    result : pandas dataframe
        Dataframe with performance (% correct) for each platform angle
    """

    # Remove probe sounds
    df = df[df.not_probe == 1]
   
    # Group by Platform Angle and get performance    
    angle_n = df['CenterSpoutRotation'].value_counts()
    n_angles = len(angle_n)

    pCorrect = np.zeros((n_angles, nIterations))
    platform_angles = []
    k = 0

    for cs_angle, group_data in df.groupby('CenterSpoutRotation'):

        nCorrect = np.zeros(nIterations)

        for i in range(0, nIterations):
            sampled_data = group_data.sample(sample_size)
            pCorrect[k,i] = sampled_data['Correct'].sum() / float(sample_size)
            nCorrect[i] = sampled_data['Correct'].sum()

        platform_angles.append(cs_angle)
        k += 1

        # Run binomial test on mean number of correct trials
        nCorrect = round(np.mean(nCorrect))
        pBinom = stats.binom_test(nCorrect, n=sample_size, p=0.5, alternative='two-sided')

        print(f"\t\tPlatform = {cs_angle}°, p = {pBinom}")


    mean_pCorrect = np.mean(pCorrect, axis=1) * 100
    std_pCorrect = np.std(pCorrect, axis=1)

    

    # Return as dataframe
    result = list(zip(platform_angles, mean_pCorrect, std_pCorrect))
    result = pd.DataFrame( result, columns=['PlatformAngle','mean', 'std_dev'])

    # Wrap around circle (i.e. make a datapoint at -180 that corresponds to +180)   
    result = wrap_data(result, 'PlatformAngle', filter_val=180, delta=-360)
    result.sort_values(by='PlatformAngle', inplace=True)
    result.set_index('PlatformAngle', inplace=True)
    
    return result


if __name__ == '__main__':
    
    import doctest
    doctest.testmod()