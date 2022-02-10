function NegLL = lik_CF8_Theta(response, stim, vert_offset, horiz_offset, amplitude, coldness)
%
% INPUTS
%   response - the actions that model fit is assessed for
%   stim - vector of stimulus feature values for which the model is fit
%
%   coldness - inverse temperature of softmax (also known as beta)
%
%
% OUTPUTS
%
% NegLL is the negative log likelihood that indicates model error (to be
% minimized)
%
% Stephen Town: 18 August 2019


% Define spatial tuning of agent (where x is sound angle in relevant coordinate frame).
func = @(x) vert_offset + (cosd(x - horiz_offset) * amplitude);

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
    
    trial_p = exp(coldness.*Q) / sum(exp(coldness.*Q));   % softmax
    
    choice_prob(trial) = trial_p( response( trial));          
end

% Compute negative log-likelihood
NegLL = -sum(log(choice_prob)); 
