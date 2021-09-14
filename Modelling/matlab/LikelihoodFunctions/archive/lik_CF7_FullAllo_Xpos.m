function NegLL = lik_CF7_FullyAllocentric(response, stim, x0, k, beta)
%
% INPUTS
% response - the actions that model fit is assessed for
% 
% stim - vector of stimulus feature values for which the model is fit
%
% x0, k and beta - model parameter being fitted
%
%
% OUTPUTS
%
% NegLL is the negative log likelihood that indicates model error (to be
% minimized)
%
% Stephen Town: 18 August 2019


% Define spatial tuning of agent (where x is position in North - South axis
% of test chamber, while east-west position (y) is irrelevant.
func = @(x) (1 ./ (1 + exp(-1 .* (x0 + k.*x))));


% Define probability of response (2 possible actions)
% nActions = 2;
% response_idx = 1 : nActions;
p_response(:,1) = func(stim);
p_response(:,2) = 1 - p_response(:,1);


% Compute choice probabilities for each trial
nTrials = numel(stim);
choice_prob = nan(nTrials, 1);

for trial = 1 : nTrials

    Q = p_response(trial,:);
    
    trial_p = exp(beta.*Q) / sum(exp(beta.*Q));   % softmax
    
    choice_prob(trial) = trial_p( response( trial));          
end

% Compute negative log-likelihood
NegLL = -sum(log(choice_prob)); 
