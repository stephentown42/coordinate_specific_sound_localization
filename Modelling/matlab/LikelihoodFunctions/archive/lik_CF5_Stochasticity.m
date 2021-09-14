function NegLL = lik_CF5_Stochasticity(response, stim, bias, beta)
%
%
% response, stim is the data that model fit is assessed for
% bias, beta is model parameter being fitted
%
% NegLL is the negative log likelihood that indicates model error (to be
% minimized)
%
% Stephen Town: 18 August 2019

% Preassign
nActions = numel( unique( response));
nStim = numel( unique( stim));
nTrials = numel(stim);

% For each stimulus class, response probabilitiy linked to 
p_response = nan( nTrials, nActions);

for i = 1 : nStim
   
    trial_idx = stim == i;       
    act_idx = (1 : nStim) == i; % action index
        
    p_response( trial_idx, act_idx) = 1;
    p_response( trial_idx, ~act_idx) = 0;    
end

% Superimpose stimulus-independent bias for action 1
p_response(:, 1) = p_response(:, 1) + bias;		% Assumes bias applies to first action
p_response(:, 2:end) = p_response(:, 2:end) - (bias / (nActions-1));	% Again spreading bias equally across all other actions


% Compute choice probabilities for each trial
choice_prob = nan(nTrials, 1);

for trial = 1 : nTrials

    Q = p_response(trial,:);
    
    trial_p = exp(beta.*Q) / sum(exp(beta.*Q));   % softmax
    
    choice_prob(trial) = trial_p( response( trial));          
end

% Compute negative log-likelihood
NegLL = -sum(log(choice_prob)); 
