function [response, stim] = simulate_Alt03_Nearest(X, stim)
% function [response, stim] = simulate_Alt03_Nearest(X, stim)
%
% Get model responses to stimuli in input
%
% INPUTS:
%   X - model parameters...
%       response_offset: how far to rotate in head-centered space to
%       respond
%       coldness: Inverse temperature softmax
%   stim - Specific list of stimuli to get model responses for
%
% OUTPUTS:
%   response - list of agent responses for each trial
%   stim - table of stimuli presented to the agent
%
% Version History
%   2019-08-20: Created (Stephen Town)
%   2021-08-24: Branched from simulate_CF8_FullAllo_Theta.m (ST)
%   2022-01-14: Branched from simulate_CF8_Theta.m (ST)


% Get response probability 
response_angle_platform = stim.theta_d - X.response_offset;
response_angle_world = response_angle_platform + stim.CenterSpoutRotation;

idx = response_angle_world  < -180;             % wrap to +/- 180 deg
response_angle_world(idx) = response_angle_world(idx) + 360;

idx = response_angle_world  >= 180;
response_angle_world(idx) = response_angle_world(idx) - 360;
    
r_port = (response_angle_world - 180) / -30;

r_dist = [abs(9 - r_port), abs(3 - r_port)];
p_response = r_dist ./ sum(r_dist, 2);

% Define probability of response (2 possible actions)
% p_response = zeros(size(r_port,1), 2);
% 
% p_response( r_port == 9, 1) = 1;            % Guided responses
% p_response( r_port == 3, 2) = 1;
% 
% idx = ismember(r_port, [0,1,2,4,5,6,7,8,10,11,12]);     % Guess otherwise
% p_response(idx, :) = 0.5;

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