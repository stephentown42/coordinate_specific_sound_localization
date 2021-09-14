function TestModel_CF10_FullEgo_Theta_Ursula
%
% Stephen Town - 25th August 2019


% ferrets = {'F1701_Pendleton', 'F1703_Grainger', 'F1731_Grendleton',...
%     'F1810_Ursula'};
% 
% for i = 1 : 1 %numel(ferrets)    
%     main(ferrets{i})
% end
% 
% 
% function main(ferret)

% Load behavioral data
file_path = Cloudstation('CoordinateFrames\BehavioralModels\Ferret_Behavior');

if nargin == 0
    ferret = 'F1810_Ursula'; %'F1701_Pendleton';  % 'F1703_Grainger';
end

[stim, response] = load_data( file_path, ferret);

% Create figure
figure('Name', ferret)

% Fit data, with check for reliability
nRuns = 20;
[Xfit, ~] = fit_data_multiple_runs(nRuns, response, stim.head_stim_angle);

% Simulate data with the fitted parameters
nSim = 50;

ax(1) = axes('nextplot','add','position',[0.08 0.48 0.22 0.14]);
ax(2) = axes('nextplot','add','position',[0.08 0.27 0.22 0.14]);
ax(3) = axes('nextplot','add','position',[0.73 0.285 0.14 0.15]);
ax(4) = axes('nextplot','add','position',[0.08 0.07 0.22 0.14]);

title(ax(1), 'Simulated Stimuli')
title(ax(3), 'Probe (Simulation) Stimuli: Model')
title(ax(4), 'Simulated Stimuli')

plot_stim_vs_pLeft(nSim, Xfit, stim, response, ax, true)


ax(1) = axes('nextplot','add','position',[0.37 0.48 0.22 0.14]);
ax(2) = axes('nextplot','add','position',[0.37 0.27 0.22 0.14]);
ax(3) = axes('nextplot','add','position',[0.73 0.07 0.14 0.15]);
ax(4) = axes('nextplot','add','position',[0.37 0.07 0.22 0.14]);

title(ax(1), 'Experimental Stimuli')
title(ax(3), 'Probe (Experimental) Stimuli: Model')
title(ax(4), 'Experimental Stimuli')

plot_stim_vs_pLeft(nSim, Xfit, stim, response, ax, false)


% Plot probe data
axes('nextplot','add','position',[0.73 0.5 0.14 0.15]);
title('Probe Stimuli: Ferret')
get_probe_data( response, stim, Xfit(4), 1);



function [platform_ang, stim_ang, pSpoutL] = get_probe_data( response, stim, critical_angle, qDraw)

% Convert from action (1-2) to refer to spout index (is spout 9*)
% (Action 1 = spout 3, Action 2 = spout 9)
is_left = @(x, lb)  x >= lb & x < (lb+180);
response = is_left(response, critical_angle); 

% Get unique platform and stimulus angles
[n_platform, platform_ang, ~] = nUnique( stim.center_spout_angle);
[n_stim_ang, stim_ang, ~] = nUnique( stim.theta_d);

% Get probability of response at each combination of stim and platform angle
pSpoutL = nan(n_stim_ang, n_platform);

for i = 1 : n_platform
    
    platform_theta_d = stim.theta_d( stim.center_spout_angle == platform_ang(i), :);
    platform_resp = response( stim.center_spout_angle == platform_ang(i));
    
    for j = 1 : n_stim_ang
   
        pSpoutL(j,i) = mean( platform_resp( platform_theta_d == stim_ang(j)));                               
    end
end

% Quick draw arg for plotting ferret data
if qDraw == 1
    plot_probe_data( platform_ang, stim_ang, pSpoutL)
end

function plot_probe_data( platform_ang, stim_ang, pSpoutL)

imagesc( platform_ang, stim_ang, pSpoutL)
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
                  'world_stim_angle', stim_in.theta_d,...
                  'not_probe', stim_in.not_probe,...
                  'contingency', contingency);


function [center_angles, pCorrect] = get_pCorrect_by_center_angle(stim, response, critical_angle)

% Map responses to actions
is_left = @(x, lb)  x >= lb & x < (lb+180);
response = is_left(response, critical_angle) + 1; 

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
pCorrect = nan(n_angles, 1);

for i = 1 : n_angles
   
    angle_idx = stim.center_spout_angle == center_angles(i);
    angle_correct = stim.correct(angle_idx);    
    pCorrect(i) = mean(angle_correct);    
end

pCorrect = pCorrect .* 100;




function plot_stim_vs_pLeft(nSim, X, true_stim, true_response, ax, create_stim)
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
critical_angle = X(4);

% Get simulation performance across many runs
[pL_byWorld_sim, pL_byHead_sim, pLprobe, sim_pCorrect] = deal([]);

for i = 1 : nSim
    
    fprintf('Simulation %d / %d\n', i, nSim)
    
    % Simulate responses from either new stimuli or input stimuli
    if create_stim
        [sim_resp, sim_stim] = simulate_CF10_FullEgo_Theta( nTrials, X);
    else
        [sim_resp, sim_stim] = simulate_CF10_FullEgo_Theta( nTrials, X, true_stim);
    end
        
    fprintf('\tData generated\n')
    
    % Get probability of responding at spout 9 for sim
    fprintf('\tQuantifying response by angle\n')
    [world_stim_sim, pL_byWorld_sim(:,i)] = get_pLeft_byStimVal(sim_resp, sim_stim.theta_d, critical_angle);    
    [head_stim_sim,  pL_byHead_sim(:,i)]  = get_pLeft_byStimVal(sim_resp, sim_stim.head_stim_angle, critical_angle);    
    
    fprintf('\tAnalysing probe data\n')
    [platform_ang, stim_ang, pLprobe(:,:,i)] = get_probe_data( sim_resp, sim_stim, critical_angle, 0);
    
    % Get sim performance across sound 
    fprintf('\tGetting percent correct\n')
    if create_stim
        [sim_resp, sim_stim] = sim_table_to_struct( sim_resp, sim_stim, true_stim.contingency);                  
    end
    
    [sim_angle, sim_pCorrect(:,i)] = get_pCorrect_by_center_angle(sim_stim, sim_resp, critical_angle);    
end

% Get ferret performance
[world_stim_true, pL_byWorld_true] = get_pLeft_byStimVal(true_response, true_stim.theta_d, critical_angle);      
[head_stim_true,  pL_byHead_true]  = get_pLeft_byStimVal(true_response, true_stim.head_stim_angle, critical_angle);
[true_angles, tru_pCorrect] = get_pCorrect_by_center_angle(true_stim, true_response, critical_angle);

% Draw performance relative to the world
axes(ax(1))

[h(1), ~] = plotStd_patch( world_stim_sim, transpose(pL_byWorld_sim), 'x', gca, [1 0.5 0]);

h(2) = plot( world_stim_true, pL_byWorld_true,...
            'color',[0 0.4 0.8],...
            'LineWidth', 2,...
            'Marker','.',...
            'MarkerSize',12);

plotXLine(0.5);
xlabel('Angle w.r.t World (°)')
ylabel('p(Left)')
legend( h, 'Model', 'Ferret')

% Draw performance relative to the head
axes(ax(2))

[h(1), ~] = plotStd_patch( head_stim_sim, transpose(pL_byHead_sim), 'x', gca, [1 0.5 0]);

h(2) = plot( head_stim_true, pL_byHead_true,...
            'color',[0 0.4 0.8],...
            'LineWidth', 2,...
            'Marker','.',...
            'MarkerSize',12);

plotXLine(0.5);
xlabel('Angle w.r.t Head (°)')
ylabel('p(Left)')

set(ax(1:2),'ylim',[0.1 0.9])
legend( h, 'Model', 'Ferret')


% Plot probe data
axes(ax(3))
plot_probe_data(platform_ang, stim_ang, mean(pLprobe, 3))


% Draw performance vs. center spout angle
axes(ax(4))

[h(1), ~] = plotStd_patch( sim_angle, transpose(sim_pCorrect), 'x', gca, [1 0.5 0]);
 
h(2) = plot(true_angles, tru_pCorrect,...
            'color',[0 0.4 0.8],...
            'LineWidth', 2,...
            'Marker','.',...
            'MarkerSize',12);

xlabel('Center Spout Angle')
ylabel('% Correct')
legend( h, 'Model', 'Ferret')
ylim([10 90])


function [uniq_x, pLeft] = get_pLeft_byStimVal(response, stim, critical_angle)
%
% Get probability of responding at left spout (action 1) for each stimulus
% value presented (e.g. each stimulus angle)

is_left = @(x, lb)  x >= lb & x < (lb+180);
response = is_left(response, critical_angle); 
    
uniq_x = unique(stim);
n_x = size( uniq_x, 1);
pLeft = nan(n_x, 1);

for j = 1 : n_x    
    resp_i = response( stim == uniq_x(j), :);    
    pLeft(j) = mean( resp_i == 1);
end




function [params, minNLL] = fit_data_multiple_runs(nRuns, response, stim)
%
% Fit the data many times to see how reliable the resulting parameters are,
% and if/how they depend on starting values

[Xfit, X0] = deal(nan(nRuns, 4));
NegLL = nan(nRuns, 1);

for i = 1 : nRuns
    [Xfit(i,:), X0(i,:), NegLL(i), ~] = fit_CF10_FullEgo_theta( response, stim);
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
title('Critical Angle')

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
response = data(:, strcmp(header, 'response_angle_task'));

% Separate probe and test speakers
stim.not_probe = abs(stim.head_stim_angle) == 90;

% Report to user to ensure source data is correct
fprintf('Response = %d\n', unique(response))
fprintf('Speaker = %d\n', unique(stim.theta_d))

% Convert speaker angle into cartesian coordinates, using assumed rho value
% from model (rho = 1)
stim.rho = ones(size(stim.theta_d));
[stim.x, stim.y] = pol2cart( deg2rad(stim.theta_d), stim.rho);

%% Get Response contingency

% Remove probe trials
test_data = data(stim.not_probe, :);

% Filter for only correct trials
correct_idx = test_data(:, strcmp( header, 'Correct')) == 1;
correct_stim = test_data(correct_idx, strcmp( header, 'speaker_platform_angle'));
correct_resp = test_data(correct_idx, strcmp( header, 'Response'));

% (nb, change the following line to 'response_angle_alt' for allocentric
% animals')
c_resp_ang = test_data(correct_idx, strcmp( header, 'response_angle_task'));    

% Generate contingency table
contingency = unique([correct_stim, correct_resp c_resp_ang], 'rows');
var_names = {'head_stim_angle','Spout','head_resp_ang'};
contingency = array2table(contingency,'VariableNames', var_names);

% This discretization step is key and needs to be moved into the modelling
% section
critical_angle = 0;

is_right = @(x, lb)  x >= lb & x < (lb+180);

contingency.Action = is_right(contingency.head_resp_ang, critical_angle) + 1;

stim.contingency = contingency;

