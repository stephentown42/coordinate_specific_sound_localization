function [response, stim] = simulate_CF6_ParametricFeatures_Softmax(nTrials, bias, beta)
% [response, stim] = simulate_CF6_ParametricFeatures_Softmax(nTrials, bias, beta)
%
% INPUTS:
% T - number of trials
% bias - value between 0 and inf (unlikely to be higher than 10)
% beta - inverse temperature for softmax argument (equivalent to level of
% stochastisticy in choice behavior: range from 0 [completely random] to inf [deterministic])
% 
% OUTPUTS:
% response - list of agent responses for each trial
% stim - list of stimuli presented to the agent
%
% COMMENTS:
% Limited to two actions
%
% Stephen Town: 18 August 2019

% Define response probability as function of stimulus
% NB: You can make these values parameters to fit
b0 = 1;
b1 = 2;
transfer_fun = @(x) (b1.*x) + b0; 

% Randomly generate stimuli from a uniform distribution (can change later)
stim_limits = [-180 180];
stim = (rand(nTrials, 1) .* diff(stim_limits)) + min(stim_limits); % <=Change distribution of stimuli here

p_response(:,1) = transfer_fun(stim);
p_response(:,2) = -p_response(:,1);  
% The line above is a key assumption that the response likelihoods are opposite
% for two actions, but I'm not sure whether this is correct or what it's
% implication are

% Apply bias
nActions = size(p_response, 2);
p_response(:, 1) = p_response(:, 1) + bias;		% Assumes bias applies to first action
p_response(:, 2:end) = p_response(:, 2:end) - (bias / (nActions-1));	% Again spreading bias equally across all other actions

% Get response for each trial
response = nan(nTrials, 1);

for trial = 1 : nTrials    
    
    Q = p_response(trial,:);
    
    trial_p = exp(beta.*Q) / sum(exp(beta.*Q));   % softmax
    
    response(trial) = choose(trial_p);    
end
