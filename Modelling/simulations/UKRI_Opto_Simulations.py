
import numpy as np
import matplotlib.pyplot as plt
import cf_simulate as csim


def introduce_head_centred_deficit(df, deficit_type='bilateral'):

    print(f"Simulating {deficit_type} impairment")

    # Create noise
    df['x_angle_platform'] = np.random.uniform(-180, 180, df['speaker_angle_platform'].shape)

    # Restore hearing for one hemisphere if requried
    if deficit_type == 'left':
        df.loc[df['speaker_angle_platform'] >= 0, 'x_angle_platform'] = df['speaker_angle_platform'] 
        df.loc[df['speaker_angle_platform'] == -180, 'x_angle_platform'] = df['speaker_angle_platform'] 

    elif deficit_type == 'right':
        df.loc[df['speaker_angle_platform'] <= 0, 'x_angle_platform'] = df['speaker_angle_platform'] 

    # Project deficit in head-centred localisation onto world-centred estimates
    df['inherited_angle_world'] = df['CenterSpoutRotation'] + df['x_angle_platform']

    # Wrap angles
    df['inherited_angle_world'] = df['inherited_angle_world'].apply(lambda x: x - (360) if x > 180 else x)  # Wrap to ± 180
    df['inherited_angle_world'] = df['inherited_angle_world'].apply(lambda x: x + (360) if x <= -179.99 else x)

    return df


def introduce_world_centred_deficit(df, deficit_type='bilateral'):

    print(f"Simulating {deficit_type} impairment")

    # Create noise
    df['x_angle_world'] = np.random.uniform(-180, 180, df['speaker_angle_world'].shape)

    # Restore hearing for one hemisphere if requried
    if deficit_type == 'west':
        df.loc[df['speaker_angle_world'] >= 0, 'x_angle_world'] = df['speaker_angle_world'] 
        df.loc[df['speaker_angle_world'] == -180, 'x_angle_world'] = df['speaker_angle_world'] 

    elif deficit_type == 'east':
        df.loc[df['speaker_angle_world'] <= 0, 'x_angle_world'] = df['speaker_angle_world'] 

    # Here, these is no transfer of world-centred location back into head-centred space
    # (I.e. the calculation goes one way, the listener goes head->world, while we as the experimenter go world->head)
    df['inherited_angle_head'] = df['speaker_angle_platform']

    return df


def add_world_centred_deficit(df, deficit_type='bilateral'):

    print(f"Simulating {deficit_type} impairment")

    # Create noise
    df['x_angle_world'] = np.random.uniform(-180, 180, df['inherited_angle_world'].shape)

    # Restore hearing for one hemisphere if requried
    if deficit_type == 'west':
        df.loc[df['inherited_angle_world'] >= 0, 'x_angle_world'] = df['inherited_angle_world'] 
        df.loc[df['inherited_angle_world'] == -180, 'x_angle_world'] = df['inherited_angle_world'] 

    elif deficit_type == 'east':
        df.loc[df['inherited_angle_world'] <= 0, 'x_angle_world'] = df['inherited_angle_world'] 

    # Here, these is no transfer of world-centred location back into head-centred space
    # (I.e. the calculation goes one way, the listener goes head->world, while we as the experimenter go world->head)
    df['inherited_angle_head'] = df['x_angle_platform']

    return df

    
def main():

    # Create basics needed to test and draw models
    df = csim.create_stimuli()

    fig, axs = plt.subplots(2, 4, figsize=(14, 8))
    # axs = np.ravel(ax)

    # 1. Control models (no deficits)
    csim.run_head_centred_mdl(axs[0, 0], df, 'speaker_angle_platform')    
    csim.run_world_centred_mdl(axs[0, 2], df, 'speaker_angle_world')

    # 2. Bilateral inactivation - head-centred deficit
    # bf = introduce_head_centred_deficit(df, 'left')
    # 
    # run_head_centred_mdl(axs[0], bf, 'x_angle_platform')        
    # run_world_centred_mdl(axs[1], bf, 'inherited_angle_world')

    # 3. Unilateral inactivation - head-centred deficit for localising sounds on the left
    lf = introduce_head_centred_deficit(df, 'left')

    csim.run_head_centred_mdl(axs[0, 1], lf, 'x_angle_platform')        
    csim.run_world_centred_mdl(axs[0, 3], lf, 'inherited_angle_world')

    # 4. Bilateral inactivation - world-centred deficit
    # wf = introduce_world_centred_deficit(df)
    #
    # run_head_centred_mdl(axs[0], wf, 'inherited_angle_head')        
    # run_world_centred_mdl(axs[1], wf, 'x_angle_world')

    # 5. Unilateral inactivation - world-centred deficit for localising sounds in the west
    xf = introduce_world_centred_deficit(df, 'west')

    csim.run_head_centred_mdl(axs[1, 0], xf, 'inherited_angle_head')        
    csim.run_world_centred_mdl(axs[1, 2], xf, 'x_angle_world')

    # 6. Unilateral inactivation - double deficit for localising sounds in the west and on the left
    jf = add_world_centred_deficit(lf, 'west')

    csim.run_head_centred_mdl(axs[1, 1], jf, 'x_angle_platform')        
    csim.run_world_centred_mdl(axs[1, 3], jf, 'x_angle_world')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
