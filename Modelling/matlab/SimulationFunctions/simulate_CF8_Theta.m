function [response, stim] = simulate_CF8_Theta(X, stim)
% function [response, stim] = simulate_CF8_FullAllo_Theta(nTrials, X, stim)
%
% Get model responses to stimuli in input
%
% INPUTS:
%   X - model parameters...
%       vert_offset - midpoint of the curve 
%       horiz_offset - midpoint of the curve 
%       amplitude - curve steepness (a.k.a. b1)
%       temperature - inverse temperature for softmax argument 
%              (equivalent to level of stochastisticy in choice behavior:
%               range from 0 [completely random] to inf [deterministic])
%   stim - Specific list of stimuli to get model responses for
%
% OUTPUTS:
%   response - list of agent responses for each trial
%   stim - table of stimuli presented to the agent
%
% Version History
%   2019-08-20: Created (Stephen Town)
%   2021-08-24: Branched from simulate_CF8_FullAllo_Theta.m (ST)


% Define spatial tuning of agent 
func = @(x) X.vert_offset + (cosd(x - X.horiz_offset) * X.amplitude);

% Define probability of response (2 possible actions)
% nActions = 2;
% response_idx = 1 : nActions;
p_response(:,1) = func(stim.theta_d);
p_response(:,2) = 1 - p_response(:,1);

% Get response for each trial using softargmax
nTrials = size(p_response, 1);
response = nan(nTrials, 1);

for trial = 1 : nTrials    
    
    Q = p_response(trial,:);
    
    trial_p = exp(X.coldness.*Q) / sum(exp(X.coldness.*Q));   % softmax
    
    response(trial) = choose(trial_p);    
end



function stim = define_world_centered_stim( n_stim, stim_n_trials)

stim.theta_d = linspace(-180, 180, n_stim)';
stim.rho = ones(size(stim.theta_d));
[stim.x, stim.y] = pol2cart( deg2rad(stim.theta_d), stim.rho);

stim = struct2table(stim);
stim = repmat( stim, stim_n_trials, 1);



function stim = replicate_at_platform_angles(stim)

n_platform_angles = 73;
center_spout_angle = linspace(-180, 180, n_platform_angles)';

stim.center_spout_angle = repmat( center_spout_angle(1), size(stim.x));    
stim_template = stim; 

for i = 2 : n_platform_angles
    
    stim_i = stim_template;
    stim_i.center_spout_angle = repmat( center_spout_angle(i), size(stim_i.x));
    stim = [stim; stim_i];
end


stim.head_stim_angle = stim.theta_d - stim.center_spout_angle;

idx = stim.head_stim_angle < -180;
stim.head_stim_angle(idx) = stim.head_stim_angle(idx) + 360;

idx = stim.head_stim_angle >= 180;
stim.head_stim_angle(idx) = stim.head_stim_angle(idx) - 360;