function [response, stim] = simulate_CF7_FullAllo_Xpos(nTrials, x0, k, beta)
% [response, stim] = simulate_CF7_FullyAllocentric(nTrials, bias, beta)
%
% INPUTS:
% T - number of trials
%
% x0 - logistic equation value, influences the midpoint of the curve (to
% avoid confusion, this has been renamed from b0)
%
% k - logistic equation value, influences the curve steepness (to avoid
% confusion, this has been renamed from b1)
%
% beta - inverse temperature for softmax argument (equivalent to level of
% stochastisticy in choice behavior: range from 0 [completely random] to inf [deterministic])
% 
%
% OUTPUTS:
%
% response - list of agent responses for each trial
% 
% stim - table of stimuli presented to the agent
%
%
%
% Stephen Town: 20 August 2019

% Define spatial tuning of agent (where x is position in North - South axis
% of test chamber, while east-west position (y) is irrelevant.
func = @(x) (1 ./ (1 + exp(-1 .* (x0 + k.*x))));

% Get number of stimuli and trials per stimulus
n_stim = 361;
stim_p = 1 / n_stim;
stim_n_trials = round(nTrials .* stim_p);

% Define stimulus parameters of speaker ring
stim = define_world_centered_stim( n_stim, stim_n_trials);

stim = replicate_at_platform_angles( stim);


% Define probability of response (2 possible actions)
% nActions = 2;
% response_idx = 1 : nActions;
p_response(:,1) = func(stim.x);
p_response(:,2) = 1 - p_response(:,1);


% Get response for each trial using softargmax
nTrials = size(stim, 1);
response = nan(nTrials, 1);

for trial = 1 : nTrials    
    
    Q = p_response(trial,:);
    
    trial_p = exp(beta.*Q) / sum(exp(beta.*Q));   % softmax
    
    response(trial) = choose(trial_p);    
end



function stim = define_world_centered_stim( n_stim, stim_n_trials)

stim.theta_d = linspace(-180, 180, n_stim)';
stim.rho = ones(size(stim.theta_d));
[stim.x, stim.y] = pol2cart( deg2rad(stim.theta_d), stim.rho);

stim = struct2table(stim);
stim = repmat( stim, stim_n_trials, 1);



function stim = replicate_at_platform_angles(stim)

n_platform_angles = 13;
CenterSpoutAngle = linspace(-180, 180, n_platform_angles)';

stim.CenterSpoutAngle = repmat( CenterSpoutAngle(1), size(stim.x));    
stim_template = stim; 

for i = 2 : n_platform_angles
    
    stim_i = stim_template;
    stim_i.CenterSpoutAngle = repmat( CenterSpoutAngle(i), size(stim_i.x));
    stim = [stim; stim_i];
end