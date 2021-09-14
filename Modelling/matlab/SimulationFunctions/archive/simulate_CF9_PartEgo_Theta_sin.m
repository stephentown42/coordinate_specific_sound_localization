function [response, stim] = simulate_CF9_PartEgo_Theta_sin(nTrials, params, stim)
% [response, stim] = simulate_CF9_PartEgo_Theta(nTrials, params, stim)
%
% INPUTS:
% T - number of trials
%
% Params - vector of model parameters
%
% Stimuli - optional specification of stimuli (e.g. that were used in a
% particular experiment)
%
% OUTPUTS:
%
% response - list of agent responses for each trial
% 
% stim - table of stimuli presented to the agent
%
%
% Stephen Town: 24 August 2019

alpha = params(1);
x0 = params(2);
invT = params(3);
y0 = params(4);


generate_stim = nargin < 3;

% Define spatial tuning of agent 
func = @(x) (alpha .* sind(x - x0)) + y0;

% Get number of stimuli and trials per stimulus
n_stim = 361;
stim_p = 1 / n_stim;
stim_n_trials = round(nTrials .* stim_p);

% Define stimulus parameters of speaker ring
if generate_stim
    
    stim = define_world_centered_stim( n_stim, stim_n_trials);

    stim = replicate_at_platform_angles( stim);
end

% Define probability of response (2 possible actions)
% nActions = 2;
% response_idx = 1 : nActions;
p_response(:,1) = func(stim.head_stim_angle);  % <===== line to change between allo/ego
p_response(:,2) = 1 - p_response(:,1);


% Get response for each trial using softargmax
nTrials = size(p_response, 1);
response = nan(nTrials, 1);

for trial = 1 : nTrials    
    
    Q = p_response(trial,:);
    
    trial_p = exp(invT.*Q) / sum(exp(invT.*Q));   % softmax
    
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