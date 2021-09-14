function [center_angles, S_out] = get_pCorrect_by_center_angle(stim, response, contingency)

% Determine correct trials using stimulus contingency
stim.correct = zeros(size(stim.center_spout_angle));

for i = 1 : size(contingency, 1)
   
    idx = stim.speaker == contingency.speaker(i) &...
            response == contingency.response(i);
        
    stim.correct(idx) = 1;    
end

% Remove probe trials
if ismember('not_probe', stim.Properties.VariableNames)
    stim = stim( stim.not_probe, :);
end

% Get performance for each center spout angle
[n_angles, center_angles, ~] = nUnique(stim.center_spout_angle);
[nTrials, nCorrect] = deal(nan(n_angles, 1));

for i = 1 : n_angles
   
    angle_idx = stim.center_spout_angle == center_angles(i);
    angle_correct = stim.correct(angle_idx);    
        
    nTrials(i) = sum(angle_idx);
    nCorrect(i) = sum( angle_correct);  
end

pCorrect = nCorrect ./ nTrials;
pCorrect = pCorrect .* 100;

pCorrect_over_angles = sum(nCorrect) / sum(nTrials);

S_out = v2struct(nTrials, nCorrect, pCorrect, pCorrect_over_angles );
