function [response, stim] = simulate_CF3_SpeakerID(nTrials, bias, lapse_rate)
% [response, stim] = simulate_CF3_SpeakerID(T, bias, lapse_rate)
%
% INPUTS
% T - number of trials
% bias - value between 0 and 1
% lapse_rate - how much the animal uses stimulus to respond (0 to 1). 
% 
% 
% OUTPUTS
% response - list of agent responses for each trial
% stim - list of stimuli presented to the agent
%
% Stephen Town: 17 August 2019

% Define the probability of each stimulus occuring
stim_p = [0.5 0.5];

% Preassign
n_stim = numel(stim_p);
stim_n_trials = round(nTrials .* stim_p);
trial_idx = [0 cumsum(stim_n_trials)];

nTrials = sum(stim_n_trials);
[stim, response] = deal( nan(nTrials, 1));

% Define probability of response (2 possible actions)
nActions = 2;
response_idx = 1 : nActions;
p_response = nan(nTrials, nActions);

% Define probability of making correct response (1 = correct, 2 = error)
% (spread lapses equally over all options - could be modified later to create specific patterns of errors for localization)
p_correct = [1-lapse_rate lapse_rate/(nActions-1)];

% For each stimulus
for i = 1 : n_stim
    
    i_idx = trial_idx(i)+1 : trial_idx(i+1);    % Trial index 
    
    stim(i_idx) = i;    % Assign stimulus identity

	col = response_idx == i; 	% Assumes stim_1 corresponds to action 1, stim 2 to action 2 etc
    p_response(i_idx, col) = p_correct(1);
	p_response(i_idx, ~col) = p_correct(2);
end

% Apply bias
% (What do we do if bias is larger than lapse_rate? - TO BE SOLVED)
if bias > lapse_rate
	keyboard
end

p_response(:, 1) = p_response(:, 1) + bias;		% Assumes bias applies to first action
p_response(:, 2:end) = p_response(:, 2:end) - (bias / nActions-1);	% Again spreading bias equally across all other actions

% For each trial
for trial = 1 : nTrials     
    response(trial) = choose(p_response(trial,:));    
end

