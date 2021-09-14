function [response, stim] = simulate_CF10_FullEgo_Theta(nTrials, X, stim)
% [response, stim] = simulate_CF10_FullEgo_Theta(nTrials, param, stim)
%
% INPUTS:
% T - number of trials
%
% Params - structure containing parameters to simulate:
%
%   x0 - offset for peak likilhood of spatial tuning
%
%   alpha - strength of spatial modulation
%
%   beta - inverse temperature for softmax argument (equivalent to level of
%           stochastisticy in choice behavior: range from 0 [completely random] to inf [deterministic])
%
%   critical angle - value above which to distinguish action 1 or 2
% 
% stim - (Optional) specific list of stimuli to get model responses for
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

try

    % Swtich to generate stimuli or use predefined input (e.g. stimuli actually
    % presented to ferrets)
    generate_stim = nargin < 3;

    alpha = X(1);
    x0 = X(2);
    inv_temp = X(3);
    critical_angle = X(4);
    

    % Define spatial tuning of agent 
    func = @(x) alpha .* cosd(x - x0);

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
    [action, response] = deal( nan(nTrials, 1));

    for trial = 1 : nTrials    

        Q = p_response(trial,:);

        trial_p = exp(inv_temp.*Q) / sum(exp(inv_temp.*Q));   % softmax

        action(trial) = choose(trial_p);    
    end
    
    % Convert response actions into response angles
%     is_left = @(x, lb)  x >= lb & x < (lb+180);
    left_val = mean([0 180] + critical_angle);    
    response( action == 2) = left_val;
    response( action == 1) = left_val + 180;
        
    response( response >= 180) = response( response >= 180) - 360;
    response( response < -180) = response( response < -180) + 360;
    
catch err
    err
    keyboard
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