function TestModel_CF9_PartialEgo_Theta_Ursula


% ST: 6th Oct 2019 - Split probe data out from training data

% Options
nFolds = 20;
nFit = 20;
nSim = 50;

% Load behavioral data
file_path = Cloudstation('CoordinateFrames\BehavioralModels\Ferret_Behavior');
ferret = 'F1810_Ursula_test_data'; %'F1701_Pendleton';  % 'F1703_Grainger';

[test_data, all_data] = load_data( file_path, ferret);

% Create figure and axes for plotting intial vs. final parameters
figure('Name', ferret)

colormap('jet')
ax(1) = axes('position', [0.1 0.76 0.15 0.2]);  title('Alpha')
ax(2) = axes('position', [0.35 0.76 0.15 0.2]); title('x0')
ax(3) = axes('position', [0.6 0.76 0.15 0.2]);  title('Inverse Temperature')
ax(4) = axes('position', [0.8 0.76 0.15 0.2]);  title('y0')
set(ax,'nextplot','add')
xlabels(ax, 'Initial')
ylabels(ax, 'Final')

% Split data into training and testing subsets 
cvIndices = crossvalind('Kfold', size(test_data,1), nFolds);

Xfit = nan(nFolds, 4);
[fold_performance, NLL] = deal( nan(nFolds,1));

for i = 1 : nFolds  % For each fold
        
    train_folds = test_data(cvIndices ~= i, :);
    test_fold = test_data(cvIndices == i, :);          
    
    [Xfit(i,:), NLL(i)] = fit_data_multiple_runs(nFit, train_folds, 'head_stim_angle', ax);
    
    fold_performance(i) = test_model_performance( test_fold, Xfit(i,:));
end

% Plot cross validation performance
axes('position', [0.85 0.06 0.1 0.2]);       
title('Predicting behavior')
boxANDscatter(1, fold_performance, 'k', 'r')
plotXLine(50)
ylabel('% Correct')
box off
set(gca,'xcolor','none')

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

plot_stim_vs_pSpout9(nSim, Xfit, test_data, ax, true)


ax(1) = axes('nextplot','add','position',[0.37 0.48 0.22 0.14]);
ax(2) = axes('nextplot','add','position',[0.37 0.27 0.22 0.14]);
ax(3) = axes('nextplot','add','position',[0.73 0.07 0.14 0.15]);
ax(4) = axes('nextplot','add','position',[0.37 0.07 0.22 0.14]);

title(ax(1), 'Experimental Stimuli')
title(ax(3), 'Probe (Experimental) Stimuli: Model')
title(ax(4), 'Experimental Stimuli')

plot_stim_vs_pSpout9(nSim, Xfit, test_data, ax, false)


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

xlabel('Platform Angle (°)')
ylabel('Speaker Angle (°)')


function [response, stim] = sim_table_to_struct( response, stim, contingency)
% 
% Helper function because this code is so bad and tied up with different
% object types - much streamlining can be done if required... <sigh> not
% that I ever have time for that

% Remove sounds that aren't at test locations
idx = bsxfun(@eq, stim.head_stim_angle, transpose(contingency.head_stim_angle));
stim.not_probe = any(idx, 2);




function [center_angles, S_out] = get_pCorrect_by_center_angle(stim, response, contingency)

% Determine correct trials using stimulus contingency
stim.correct = zeros(size(stim.center_spout_angle));

for i = 1 : size( contingency, 1)
   
    idx = stim.head_stim_angle == contingency.head_stim_angle(i) &...
            response == contingency.response(i);
        
    stim.correct(idx) = 1;    
end

% Remove probe trials
if ismember('not_probe', stim.Properties.VariableNames)
    stim = stim( stim.not_probe, :);
end

% Get performance for each center spout angle
[n_angles, center_angles, ~] = nUnique(stim.center_spout_angle);
[nTrials, nCorrect] = deal(nan(n_angles, 1));

for i = 1 : n_angles
   
    angle_idx = stim.center_spout_angle == center_angles(i);
    angle_correct = stim.correct(angle_idx);  
    
    nTrials(i) = sum(angle_idx);
    nCorrect(i) = sum( angle_correct);    
end

pCorrect = nCorrect ./ nTrials;
pCorrect = pCorrect .* 100;

pCorrect_over_angles = sum(nCorrect) / sum(nTrials);

S_out = v2struct(nTrials, nCorrect, pCorrect, pCorrect_over_angles );




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
        [sim_resp, sim_stim] = simulate_CF9_PartEgo_Theta_sin( nTrials, X);
    else
        [sim_resp, sim_stim] = simulate_CF9_PartEgo_Theta_sin( nTrials, X, obs_data);
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
xlabel('Angle w.r.t World (°)')
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
xlabel('Angle w.r.t Head (°)')
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


function [uniq_x, p9] = get_spout9_byStimVal(response, stim)
%
% Get probability of responding at spout 9 (action 2) for each stimulus
% value presented (e.g. each stimulus angle)
    
uniq_x = unique(stim);
n_x = size( uniq_x, 1);
p9 = nan(n_x, 1);

for j = 1 : n_x    
    resp_i = response( stim == uniq_x(j), :);    
    p9(j) = mean( resp_i == 2);
end



function [params, minNLL] = fit_data_multiple_runs(nRuns,  obs_data, str, ax)
%
% Fit the data many times to see how reliable the resulting parameters are,
% and if/how they depend on starting values

% Parse inputs
response = obs_data.response;
eval( sprintf( 'stim = obs_data.%s;', str))

[Xfit, X0] = deal(nan(nRuns, 4));
NegLL = nan(nRuns, 1);

for i = 1 : nRuns
    [Xfit(i,:), X0(i,:), NegLL(i), ~] = fit_CF9_PartEgo_theta_sin( response, stim);
end

% Get best fitting parameters
[minNLL, idx] = min(NegLL);
params = Xfit(idx,:);


% Show comparison as colored scatter plot
for i = 1 : size(Xfit, 2)
    scatter(X0(:,i), Xfit(:,i), [], NegLL, 'filled', 'parent', ax(i))
end


function performance = test_model_performance( test_fold, X)
%
% Runs simulation with fitted parameters and then measure how many
% responses you were able to match to the animals

[predicted_response, ~] = simulate_CF9_PartEgo_Theta_sin(0, X, test_fold);

correct = predicted_response == test_fold.response;
performance = mean(correct) * 100;



function [test_data, all_data] = load_data( file_path, ferret)
%
% Loads data from a csv file that was generated using Jupyter notebooks
% (see ~\CoordinateFrames\BehavioralAnalysis\Notebooks\F1703_Grainger_Analysis.ipynb)
%
% Note that response is conveted from spout indices (3 or 9) to actions (1 or 2) 

[data, header] = xlsread( fullfile( file_path, [ferret '.xlsx']));

% Get column indices
col = struct('SpoutRotation', strcmp( header, 'CenterSpoutRotation'),...
             'Speaker', strcmp( header, 'Speaker Location'),...
             'SpeakerAngle', strcmp( header, 'speaker_angle'),...
             'HeadStimAngle', strcmp( header, 'speaker_platform_angle'),...
             'Response', strcmp(header, 'Response'),...
             'Correct', strcmp( header, 'Correct'));

% Identify probe trals
head_stim_angle = data(:, col.HeadStimAngle);
not_probe = abs(head_stim_angle) == 90;

% Convert responses into action indices 
% (response 3 = action 1, response 9 == action 2)
response = data(:, col.Response);
response = double(response == 9) + 1;

% Convert speaker angle into cartesian coordinates, using assumed rho value
% from model (rho = 1)
theta_d = data(:, col.SpeakerAngle);
rho = ones(size(theta_d));
[x, y] = pol2cart( deg2rad(theta_d), rho);

% Split data into probe and test trials
all_data = table(head_stim_angle, response, theta_d, rho, x, y);
all_data.Correct = data(:, col.Correct);
all_data.center_spout_angle = data(:, col.SpoutRotation);
all_data.speaker = data(:, col.Speaker);

test_data = all_data(not_probe, :);

% Get response contingency from test data
correct_data = test_data(test_data.Correct == 1, {'head_stim_angle','response'});
contingency = unique(correct_data, 'rows');

contingency.Properties.Description = 'Contingency';
test_data.Properties.UserData = contingency;

% Report to user to ensure source data is correct
fprintf('Response = %d\n', unique(test_data.response))
fprintf('Speaker = %d\n', unique(all_data.theta_d))
