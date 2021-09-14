function new_T = flatten_sample_sizes(T, k)
% function T = flatten_sample_sizes(T, k)
% 
% Samples equal numbers of sound angles in each combination of head and
% world-centered space. 
% 
% Equal sample sizes are important before model fitting as otherwise
% the model will fit better to some combinations than others. During 
% testing, this can lead to overestimates in performance as the bias 
% in sampling is present in both train and test datasets, but reflects
% the specific properties of the experiment, rather than general properties
% of the biological system.
% 
% Resampling here is performed with replacement unless specified by setting 
% n to 0 or nan.
% 
% Arguments
%     - T: table with columns for sound angle in head and world-centered space
%     - k: required sample size (or min available if zero)
%     
%     
% Returns
%     - T: table containing subset of rows from input data 
%     (Note that if replacement is true, rows may be repeated)
% 
% Version History
%     - 2021-08-25: Created (Stephen Town)

try

    % Pass all data if k is not a number
    if isnan(k)
        new_T = T;
        return
    end
    
    % Get unique combinations of sound angle in head and world-centered space
    sloc = T(:, {'speaker_angle_world','speaker_angle_platform'});
    unique_combos = unique(sloc, 'rows');
    n_combo = size(unique_combos, 1);

    n_trials = nan(n_combo, 1);
    for i = 1 : n_combo
        idx = ismember(sloc, unique_combos(i,:), 'rows');
        n_trials(i) = sum(idx);
    end

    % If no replacement, use min sample size
    if k == 0
        k = min(n_trials); 
        with_replacement = false;
    else
        with_replacement = true;
    end

    % Resample new data
    new_T = [];

    for i = 1 : n_combo

        idx = ismember(sloc, unique_combos(i,:), 'rows');
        combo_data = T(idx, :);

        if with_replacement
            combo_data = datasample(combo_data, k, 1);
            new_T = [new_T; combo_data];
        else
            new_idx = randperm( n_trials(i), k);
            new_T = [new_T; combo_data(new_idx,:)];
        end
    end

catch err
    err
    keyboard
end

    