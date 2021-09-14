function TestModel_CF9_PartialEgo_Theta_Ursula


% Load behavioral data
file_path = Cloudstation('CoordinateFrames\BehavioralModels\Ferret_Behavior');

if nargin == 0
    ferret = 'F1810_Ursula'; %'F1701_Pendleton';  % 'F1703_Grainger';
end

[stim, response] = load_data( file_path, ferret);

% Create figure
figure('Name', ferret)

% Fit data, with check for reliability
nRuns = 10;
[Xfit, ~] = fit_data_multiple_runs(nRuns, response, stim.head_stim_angle);

% Simulate data with the fitted parameters
nSim = 10;

ax(1) = axes('nextplot','add','position',[0.08 0.48 0.22 0.14]);
ax(2) = axes('nextplot','add','position',[0.08 0.27 0.22 0.14]);
ax(3) = axes('nextplot','add','position',[0.73 0.285 0.14 0.15]);
ax(4) = axes('nextplot','add','position',[0.08 0.07 0.22 0.14]);

title(ax(1), 'Simulated Stimuli')
title(ax(3), 'Probe (Simulation) Stimuli: Model')
title(ax(4), 'Simulated Stimuli')

plot_stim_vs_pSpout9(nSim, Xfit, stim, response, ax, true)


ax(1) = axes('nextplot','add','position',[0.37 0.48 0.22 0.14]);
ax(2) = axes('nextplot','add','position',[0.37 0.27 0.22 0.14]);
ax(3) = axes('nextplot','add','position',[0.73 0.07 0.14 0.15]);
ax(4) = axes('nextplot','add','position',[0.37 0.07 0.22 0.14]);

title(ax(1), 'Experimental Stimuli')
title(ax(3), 'Probe (Experimental) Stimuli: Model')
title(ax(4), 'Experimental Stimuli')

plot_stim_vs_pSpout9(nSim, Xfit, stim, response, ax, false)


% Plot probe data
axes('nextplot','add','position',[0.73 0.5 0.14 0.15]);
title('Probe Stimuli: Ferret')
get_probe_data( response, stim, 1);



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


function [response, stim_out] = sim_table_to_struct( response, stim_in, contingency)
% 
% Helper function because this code is so bad and tied up with different
% object types - much streamlining can be done if required... <sigh> not
% that I ever have time for that

% Remove sounds that aren't at test locations
idx = bsxfun(@eq, stim_in.head_stim_angle, transpose(contingency.head_stim_angle));
stim_in.not_probe = any(idx, 2);

% Convert to struct
stim_out = struct('center_spout_angle', stim_in.center_spout_angle,...
                  'head_stim_angle', stim_in.head_stim_angle,...
                  'not_probe', stim_in.not_probe,...
                  'contingency', contingency);


function [center_angles, S_out] = get_pCorrect_by_center_angle(stim, response)

% Determine correct trials using stimulus contingency
stim.correct = zeros(size(stim.center_spout_angle));

for i = 1 : size( stim.contingency, 1)
   
    idx = stim.head_stim_angle == stim.contingency.head_stim_angle(i) &...
            response == stim.contingency.Action(i);
        
    stim.correct(idx) = 1;    
end

% Remove probe trials
stim = rmfield(stim, 'contingency');
stim = struct2table(stim);
stim = stim( stim.not_probe, :);

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




function plot_stim_vs_pSpout9(nSim, X, true_stim, true_response, ax, create_stim)
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

% Get simulation performance across many runs
[p9_byWorld_sim, p9_byHead_sim, p9probe, sim_pCorrect] = deal([]);
sim_pCorrect_overAngle = nan( nSim, 1);

for i = 1 : nSim
    
    fprintf('Simulation %d / %d\n', i, nSim)
    
    % Simulate responses from either new stimuli or input stimuli
    if create_stim
        [sim_resp, sim_stim] = simulate_CF9_PartEgo_Theta_sin( nTrials, X);
    else
        [sim_resp, sim_stim] = simulate_CF9_PartEgo_Theta_sin( nTrials, X, true_stim);
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
        [sim_resp, sim_stim] = sim_table_to_struct( sim_resp, sim_stim, true_stim.contingency);                  
    end
    
    [sim_angle, sim_performance] = get_pCorrect_by_center_angle(sim_stim, sim_resp);    
    
    sim_pCorrect(:,i) = sim_performance.pCorrect;
    sim_pCorrect_overAngle(i) = sim_performance.pCorrect_over_angles;
end

% Get ferret performance
[world_stim_true, p9_byWorld_true] = get_spout9_byStimVal(true_response, true_stim.theta_d);      
[head_stim_true,  p9_byHead_true]  = get_spout9_byStimVal(true_response, true_stim.head_stim_angle);
[true_angles, tru_performance] = get_pCorrect_by_center_angle(true_stim, true_response);

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




function [params, minNLL] = fit_data_multiple_runs(nRuns, response, stim)
%
% Fit the data many times to see how reliable the resulting parameters are,
% and if/how they depend on starting values

[Xfit, X0] = deal(nan(nRuns, 4));
NegLL = nan(nRuns, 1);

for i = 1 : nRuns
    [Xfit(i,:), X0(i,:), NegLL(i), ~] = fit_CF9_PartEgo_theta_sin( response, stim);
end

% Get best fitting parameters
[minNLL, idx] = min(NegLL);
params = Xfit(idx,:);


% Show comparison as colored scatter plot
colormap('jet')

ax(1) = axes('position', [0.1 0.76 0.15 0.2]);
scatter(X0(:,1), Xfit(:,1), [], NegLL,'filled')
title('Alpha')

ax(2) = axes('position', [0.35 0.76 0.15 0.2]);
scatter(X0(:,2), Xfit(:,2), [], NegLL,'filled')
title('x0')

ax(3) = axes('position', [0.6 0.76 0.15 0.2]);
scatter(X0(:,3), Xfit(:,3), [], NegLL,'filled')
title('Inverse Temperature')

ax(4) = axes('position', [0.8 0.76 0.15 0.2]);
scatter(X0(:,4), Xfit(:,4), [], NegLL,'filled')
title('y0')


xlabels(ax, 'Initial')
ylabels(ax, 'Final')


function [stim, response] = load_data( file_path, ferret)
%
% Loads data from a csv file that was generated using Jupyter notebooks
% (see ~\CoordinateFrames\BehavioralAnalysis\Notebooks\F1703_Grainger_Analysis.ipynb)
%
% Note that response is conveted from spout indices (3 or 9) to actions (1 or 2) 

[data, header] = xlsread( fullfile( file_path, [ferret '.xlsx']));

stim.center_spout_angle = data(:, strcmp( header, 'CenterSpoutRotation'));
stim.speaker = data(:, strcmp( header, 'Speaker Location'));
stim.theta_d = data(:, strcmp( header, 'speaker_angle'));
stim.head_stim_angle = data(:, strcmp( header, 'speaker_platform_angle'));
response = data(:, strcmp(header, 'Response'));

% Separate probe and test speakers
stim.not_probe = abs(stim.head_stim_angle) == 90;

% Report to user to ensure source data is correct
fprintf('Response = %d\n', unique(response))
fprintf('Speaker = %d\n', unique(stim.theta_d))

% Convert speaker angle into cartesian coordinates, using assumed rho value
% from model (rho = 1)
stim.rho = ones(size(stim.theta_d));
[stim.x, stim.y] = pol2cart( deg2rad(stim.theta_d), stim.rho);

% Convert responses into action indices (response 3 = action 1, response 9
% == action 2)
response = double(response == 9) + 1;

% Get Response contingency
test_data = data(stim.not_probe, :);

correct_idx = test_data(:, strcmp( header, 'Correct')) == 1;
correct_stim = test_data(correct_idx, strcmp( header, 'speaker_platform_angle'));
correct_resp = test_data(correct_idx, strcmp( header, 'Response'));

contingency = unique([correct_stim, correct_resp], 'rows');
contingency = array2table(contingency,'VariableNames',{'head_stim_angle','Spout'});
contingency.Action = double(contingency.Spout == 9) + 1;

stim.contingency = contingency;

