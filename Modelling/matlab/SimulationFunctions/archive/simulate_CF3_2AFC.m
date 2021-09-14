function [response, stim] = simulate_CF3_2AFC(nTrials, bias, lapse_rate, beta)
% [response, stim] = simulate_CF3_2AFC(T, bias, lapse_rate)
%
% INPUTS:
% T - number of trials
% bias - value between 0 and inf (unlikely to be higher than 10)
% lapse_rate - how much the animal uses stimulus to respond (0 to 1). 
% beta - inverse temperature for softmax argument (equivalent to level of
% stochastisticy in choice behavior: range from 0 [completely random] to inf [deterministic])
% 
% OUTPUTS:
% response - list of agent responses for each trial
% stim - list of stimuli presented to the agent
%
% COMMENTS:
% There's a subtle distinction here between lapse rate and inverse
% temperature (beta) in that beta is random whereas lapse rate is directed.
% I.e. when the animal lapses, it's specifically not going to the location
% of the stimulus, whereas beta can result in spontaneously getting the
% trial right. We may thus want to consider models with and without lapse
% rates added as it might not add anything specific or helpful
%
% Stephen Town: 18 August 2019

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
p_response(:, 1) = p_response(:, 1) + bias;		% Assumes bias applies to first action
p_response(:, 2:end) = p_response(:, 2:end) - (bias / (nActions-1));	% Again spreading bias equally across all other actions

% For each trial
for trial = 1 : nTrials    
    
    Q = p_response(trial,:);
    
    trial_p = exp(beta.*Q) / sum(exp(beta.*Q));   % softmax
    
    response(trial) = choose(trial_p);    
end
