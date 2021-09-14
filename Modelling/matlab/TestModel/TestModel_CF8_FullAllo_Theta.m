function TestModel_CF8_FullAllo_Theta(file_path, file_name)
%
% Best run from Modelling/matlab
%
% TO DO: 
%   - Fix contingency calculations in load_data for head-centered task
%   - Balance sample sizes in input data to model

% ST: 11 Oct 2020 - Split probe data out from training data
% ST: 23 Aug 2021 - Adapted for Github

% Options
nFolds = 20;
nRuns = 20;  
train_trials = 10;
%nSim = 50;
nParams = 4;               % Number of parameters in model

stim_col = 'speaker_angle_world';      % Variable used as predictor
include_probe_data = true;             % All_data (includes probe locations)

fitfunc = @fit_CF8_theta;
simfunc = @simulate_CF8_Theta;

C = who();                 % Record config variables before expanding workspace

% Select input data if not specified
if nargin == 0
    modelling_dir = fileparts( pwd());
    repo_dir = fileparts(modelling_dir);
    addpath( genpath( modelling_dir))
    
    file_path = fullfile(repo_dir, 'Analysis\Main\Data\Formatted');
    [file_name, file_path, ~] = uigetfile(fullfile(file_path, '*.csv'), 'Select subject:');
end

data = load_data( file_path, file_name, stim_col, include_probe_data);

% Split data into training and testing subsets 
cvIndices = crossvalind('Kfold', size(data,1), nFolds);

% Log config file and start recording results
config = struct('InputData', file_name); 
for i = 1 : numel(C)
    eval(sprintf('config.%s = %s;', C{i}, C{i}));
end

log_path = logging(dbstack, config);    % Create save folder with date tag, and store config info

fold_performance = [];
parameters = [];

for i = 1 : nFolds  % For each fold

    test_fold = data(cvIndices == i, :);          
    train_folds = data(cvIndices ~= i, :);

    train_folds = flatten_sample_sizes(train_folds, train_trials);
    
    [Xfit, X0, NegLL] = fit_data_multiple_runs(fitfunc, nRuns, nParams, train_folds, stim_col);
    
    param_i = innerjoin(X0, Xfit, 'Keys','Run');    
    param_i.NegLogLik = NegLL;
    param_i.Fold = repmat(i, nRuns, 1);
    parameters = [parameters; param_i];                     % Append to tables   
    
    [Xfit, ~] = get_best_parameters(Xfit, NegLL);
    
    fold_i_perf = test_model_performance(simfunc, test_fold, Xfit);
    
    fold_performance = [fold_performance; fold_i_perf];        
end

fold_performance.Fold = transpose(1 : nFolds);
writetable( fold_performance, fullfile(log_path, 'fold_performance.csv'))
writetable( parameters, fullfile(log_path, 'param_contrast.csv'))

return

% Get best parameters
[~, min_idx] = min(NLL);
Xfit = Xfit(min_idx, :);

% Simulate data with the fitted parameters
ax(1) = axes('nextplot','add','position',[0.08 0.48 0.22 0.14]);
ax(2) = axes('nextplot','add','position',[0.08 0.27 0.22 0.14]);
ax(3) = axes('nextplot','add','position',[0.73 0.285 0.14 0.15]);
ax(4) = axes('nextplot','add','position',[0.08 0.07 0.22 0.14]);

title(ax(1), 'Simulated Stimuli')
title(ax(3), 'Probe (Simulation) Stimuli: Model')
title(ax(4), 'Simulated Stimuli')

plot_stim_vs_pSpout9(nSim, Xfit, all_data, ax, true)

ax(1) = axes('nextplot','add','position',[0.37 0.48 0.22 0.14]);
ax(2) = axes('nextplot','add','position',[0.37 0.27 0.22 0.14]);
ax(3) = axes('nextplot','add','position',[0.73 0.07 0.14 0.15]);
ax(4) = axes('nextplot','add','position',[0.37 0.07 0.22 0.14]);

title(ax(1), 'Experimental Stimuli')
title(ax(3), 'Probe (Experimental) Stimuli: Model')
title(ax(4), 'Experimental Stimuli')

plot_stim_vs_pSpout9(nSim, Xfit, all_data, ax, false)

% Plot probe data
axes('nextplot','add','position',[0.73 0.5 0.14 0.15]);
title('Probe Stimuli: Ferret')
get_probe_data( all_data.response, all_data, 1);



function [platform_ang, stim_ang, pSpout9] = get_probe_data( response, stim, qDraw)

% Convert from action (1-2) to refer to spout index (is spout 9*)
% (Action 1 = spout 3, Action 2 = spout 9)
response = response == 2;

% Get unique platform and stimulus angles
[n_platform, platform_ang, ~] = nUnique( stim.center_spout_angle);
[n_stim_ang, stim_ang, ~] = nUnique( stim.theta_d);

% Get probability of response at each combination of stim and platform angle
pSpout9 = nan(n_stim_ang, n_platform);

for i = 1 : n_platform
    
    platform_theta_d = stim.theta_d( stim.center_spout_angle == platform_ang(i), :);
    platform_resp = response( stim.center_spout_angle == platform_ang(i));
    
    for j = 1 : n_stim_ang
   
        pSpout9(j,i) = mean( platform_resp( platform_theta_d == stim_ang(j)));                               
    end
end

% Quick draw arg for plotting ferret data
if qDraw == 1
    plot_probe_data( platform_ang, stim_ang, pSpout9)
end


function plot_probe_data( platform_ang, stim_ang, pSpout9)

imagesc( platform_ang, stim_ang, pSpout9)
axis tight
colormap(gca, inferno)

xlabel('Platform Angle (�)')
ylabel('Speaker Angle (�)')



function [response, stim] = sim_table_to_struct( response, stim, contingency)
% 
% Helper function because this code is so bad and tied up with different
% object types - much streamlining can be done if required... <sigh> not
% that I ever have time for that

% Remove sounds that aren't at test locations
idx = bsxfun(@eq, stim.theta_d, transpose(contingency.theta_d));
stim.not_probe = any(idx, 2);

% Create speaker index
stim.speaker = nan(size(stim.theta_d));
for i = 1 : size(contingency, 1)   
    stim.speaker( stim.theta_d == contingency.theta_d(i)) = contingency.speaker(i);
end



function plot_stim_vs_pSpout9(nSim, X, obs_data, ax, create_stim)
%
% Plots probability of ferrets and simulations responding at spout 9 as a
% function of stimulus angle (theta). Simulations are repeated a number of
% times in order to estimate variability of performance, drawn as the
% standard deviation around the mean
% 
% INPUTS:
%
% nSim - Number of simulations to perform
% 
% X - The best parameters resulting from fitting
% 
% true_stim, true_response - Ferret behavior
% 
% ax - Two element array containing axes for plotting world centered and
%      head-centered results
% 
% create_stim - Logical option to create simulated stimulus sets (True) or
%               use the input stimuli that were presented during experiments (False)

nTrials = 20000;

contingency = obs_data.Properties.UserData;

% Get simulation performance across many runs
[p9_byWorld_sim, p9_byHead_sim, p9probe, sim_pCorrect] = deal([]);
sim_pCorrect_overAngle = nan( nSim, 1);

for i = 1 : nSim
    
    fprintf('Simulation %d / %d\n', i, nSim)
    
    % Simulate responses from either new stimuli or input stimuli
    if create_stim
        [sim_resp, sim_stim] = simulate_CF8_FullAllo_Theta( nTrials, X);
    else
        [sim_resp, sim_stim] = simulate_CF8_FullAllo_Theta( nTrials, X, obs_data);
    end
        
    fprintf('\tData generated\n')
    
    % Get probability of responding at spout 9 for sim
    fprintf('\tQuantifying response by angle\n')
    [world_stim_sim, p9_byWorld_sim(:,i)] = get_spout9_byStimVal(sim_resp, sim_stim.theta_d);    
    [head_stim_sim,  p9_byHead_sim(:,i)]  = get_spout9_byStimVal(sim_resp, sim_stim.head_stim_angle);    
    
    fprintf('\tAnalysing probe data\n')
    [platform_ang, stim_ang, p9probe(:,:,i)] = get_probe_data( sim_resp, sim_stim, 0);
    
    % Get sim performance across sound 
    fprintf('\tGetting percent correct\n')
    if create_stim
        [sim_resp, sim_stim] = sim_table_to_struct( sim_resp, sim_stim, contingency);                  
    end
    
    [sim_angle, sim_performance] = get_pCorrect_by_center_angle(sim_stim, sim_resp, contingency);    
    
    sim_pCorrect(:,i) = sim_performance.pCorrect;
    sim_pCorrect_overAngle(i) = sim_performance.pCorrect_over_angles;
end

% Get ferret performance
[world_stim_true, p9_byWorld_true] = get_spout9_byStimVal(obs_data.response, obs_data.theta_d);      
[head_stim_true,  p9_byHead_true]  = get_spout9_byStimVal(obs_data.response, obs_data.head_stim_angle);
[true_angles, tru_performance] = get_pCorrect_by_center_angle(obs_data, obs_data.response, contingency);

% Draw performance relative to the world
axes(ax(1))

[h(1), ~] = plotStd_patch( world_stim_sim, transpose(p9_byWorld_sim), 'x', gca, [1 0.5 0]);

h(2) = plot( world_stim_true, p9_byWorld_true,...
            'color',[0 0.4 0.8],...
            'LineWidth', 2,...
            'Marker','.',...
            'MarkerSize',12);

plotXLine(0.5);
xlabel('Angle w.r.t World (�)')
ylabel('p(Spout9)')
legend( h, 'Model', 'Ferret')

% Draw performance relative to the head
axes(ax(2))

[h(1), ~] = plotStd_patch( head_stim_sim, transpose(p9_byHead_sim), 'x', gca, [1 0.5 0]);

h(2) = plot( head_stim_true, p9_byHead_true,...
            'color',[0 0.4 0.8],...
            'LineWidth', 2,...
            'Marker','.',...
            'MarkerSize',12);

plotXLine(0.5);
xlabel('Angle w.r.t Head (�)')
ylabel('p(Spout9)')
set(ax(1:2),'ylim',[0.1 0.9])
legend( h, 'Model', 'Ferret')


% Plot probe data
axes(ax(3))
plot_probe_data(platform_ang, stim_ang, mean(p9probe, 3))


% Draw performance vs. center spout angle
axes(ax(4))

[h(1), ~] = plotStd_patch( sim_angle, transpose(sim_pCorrect), 'x', gca, [1 0.5 0]);
 
h(2) = plot(true_angles, tru_performance.pCorrect,...
            'color',[0 0.4 0.8],...
            'LineWidth', 2,...
            'Marker','.',...
            'MarkerSize',12);

xlabel('Center Spout Angle')
ylabel('% Correct')
legend( h, 'Model', 'Ferret')
ylim([10 90])









