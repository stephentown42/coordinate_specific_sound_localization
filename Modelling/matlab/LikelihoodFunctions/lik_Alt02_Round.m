function NegLL = lik_Alt02_Round(response, stim, resp_offset, coldness)
%
% INPUTS
%   response - the actions that model fit is assessed for
%   stim - vector of stimulus feature values for which the model is fit
%       - (:,1): stimulus angle 
%       - (:,2): platform angle
%   response_offset: rotation to make to respond
%   coldness - inverse temperature of softmax (also known as beta)
%
%
% OUTPUTS
%
% NegLL is the negative log likelihood that indicates model error (to be
% minimized)
%
% Version History:
% ----------------
%   2019-08-18: Created by Stephen Town
%   2022-01-14: Branced from lik_CF8_Theta.m

% Get response probability 
response_angle_platform = stim(:,1) - resp_offset;
response_angle_world = response_angle_platform + stim(:,2);

idx = response_angle_world  < -180;             % wrap to +/- 180 deg
response_angle_world(idx) = response_angle_world(idx) + 360;

idx = response_angle_world  >= 180;
response_angle_world(idx) = response_angle_world(idx) - 360;
    
r_port = (response_angle_world - 180) / -30;

r_dist = [abs(9 - r_port), abs(3 - r_port)];
p_response = r_dist ./ sum(r_dist, 2);

p_response(p_response < 0.5) = 0;
p_response(p_response > 0.5) = 1;

% Define probability of response (2 possible actions)
% p_response = zeros(size(r_port,1), 2);

% p_response( r_port == 9, 1) = 1;            % Guided responses
% p_response( r_port == 3, 2) = 1;
% 
% idx = ismember(r_port, [0,1,2,4,5,6,7,8,10,11,12]);     % Guess otherwise
% p_response(idx, :) = 0.5;

% Compute choice probabilities for each trial
nTrials = size(stim, 1);
choice_prob = nan(nTrials, 1);

for trial = 1 : nTrials

    Q = p_response(trial,:);
    
    trial_p = exp(coldness.*Q) / sum(exp(coldness.*Q));   % softmax
    
    choice_prob(trial) = trial_p( response( trial));          
end

% Compute negative log-likelihood
NegLL = -sum(log(choice_prob)); 
