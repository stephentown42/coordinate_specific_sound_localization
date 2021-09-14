function TestModel_CF10_FullEgo_Theta_Grendleton_FixedParams
%
% Stephen Town - 25th August 2019


% Load behavioral data
file_path = Cloudstation('CoordinateFrames\BehavioralModels\Ferret_Behavior');
ferret = 'F1731_Grendleton'; %'F1701_Pendleton';  % 'F1703_Grainger';

[stim, response] = load_data( file_path, ferret);

% Create figure
figure('Name', ferret)


X_chosen = [100, 0, 0.5, 15];


% Simulate data with the fitted parameters
nSim = 1;

ax(1) = axes('nextplot','add','position',[0.08 0.48 0.22 0.14]);
ax(2) = axes('nextplot','add','position',[0.08 0.27 0.22 0.14]);
ax(3) = axes('nextplot','add','position',[0.73 0.285 0.14 0.15]);
ax(4) = axes('nextplot','add','position',[0.08 0.07 0.22 0.14]);

title(ax(1), 'Simulated Stimuli')
title(ax(3), 'Probe (Simulation) Stimuli: Model')
title(ax(4), 'Simulated Stimuli')

plot_stim_vs_pLeft(nSim, X_chosen, stim, response, ax, true)


ax(1) = axes('nextplot','add','position',[0.37 0.48 0.22 0.14]);
ax(2) = axes('nextplot','add','position',[0.37 0.27 0.22 0.14]);
ax(3) = axes('nextplot','add','position',[0.73 0.07 0.14 0.15]);
ax(4) = axes('nextplot','add','position',[0.37 0.07 0.22 0.14]);

title(ax(1), 'Experimental Stimuli')
title(ax(3), 'Probe (Experimental) Stimuli: Model')
title(ax(4), 'Experimental Stimuli')

plot_stim_vs_pLeft(nSim, X_chosen, stim, response, ax, false)


% Plot probe data
axes('nextplot','add','position',[0.73 0.5 0.14 0.15]);
title('Probe Stimuli: Ferret')
get_probe_data( response, stim, X_chosen(4), 1);



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
idx = bsxfun(@eq, stim_in.theta_d, [0 -180]);
stim_in.not_probe = any(idx, 2);

% Convert to struct
stim_out = struct('center_spout_angle', stim_in.center_spout_angle,...
                  'head_stim_angle', stim_in.head_stim_angle,...
                  'theta_d', stim_in.theta_d,...
                  'not_probe', stim_in.not_probe,...
                  'contingency', contingency);


function [center_angles, pCorrect] = get_pCorrect_by_center_angle(stim, response, critical_angle)

% Map responses to actions
is_left = @(x, lb)  x >= lb & x < (lb+180);
response = is_left(response, critical_angle) + 1; 

action(:,1) = is_left( stim.contingency.Response_Angle, critical_angle);

if critical_angle > 0
   action(:,2) = is_left( stim.contingency.Response_Angle, critical_angle-360); 

elseif critical_angle < 0
    action(:,2) = is_left( stim.contingency.Response_Angle, critical_angle+360); 
end
    
stim.contingency.Action = any(action, 2) + 1;

    
% Get correct action to take if within ± 90 of critical angle (allows for
% use of simulation data outside experiment)
in_range = @(x, c) x >= (c-90) & x < (c+90);
in_range_idx = in_range(stim.contingency.Speaker_Angle, critical_angle);
in_range_act = stim.contingency.Action( in_range_idx);
in_range_act = unique( in_range_act);
out_range_act = setdiff([1 2], in_range_act);

if numel(in_range_act) > 1, keyboard; end

% Create template from which to adjust contingencies
zero_contingency = stim.contingency( stim.contingency.Platform == 0, :);

% Determine correct trials using stimulus contingency
stim.correct = zeros(size(stim.center_spout_angle));
conditions = unique([stim.center_spout_angle stim.head_stim_angle],'rows');

for i = 1 : size(conditions, 1)
    
    c_idx = stim.contingency.Platform == conditions(i,1) &...
            stim.contingency.Speaker_Angle == conditions(i,2);
        
    if any(c_idx)    
        
        % Based on experimental records
        contingency = stim.contingency( c_idx, :);        
        
        idx = stim.center_spout_angle == contingency.Platform &...
              stim.head_stim_angle == contingency.Speaker_Angle &...
              response == contingency.Action;
        
        stim.correct(idx) = 1;
    else
                
        % Map what the contingency should be from zero spout rotation
        local_contingency = zero_contingency;
        local_contingency.Speaker_Angle = local_contingency.Speaker_Angle - conditions(i,1); 
        local_contingency.Response_Angle = local_contingency.Response_Angle - conditions(i,1); 
        local_contingency.Platform = repmat(conditions(i,1), size(local_contingency.Platform));
        
        local_contingency.Speaker_Angle = wrap_angles(local_contingency.Speaker_Angle, -180, 180);
        local_contingency.Response_Angle = wrap_angles(local_contingency.Response_Angle, -180, 180);
        
        % Adjust correct action according to sound angle relative to head
        in_range_idx = in_range(local_contingency.Speaker_Angle, critical_angle);
        local_contingency.Action( in_range_idx) = in_range_act;
        local_contingency.Action( ~in_range_idx) = out_range_act;
        
        c_idx = local_contingency.Speaker_Angle == conditions(i,2);
        
        if any(c_idx)          
            
            contingency = local_contingency( c_idx, :);        
        
            idx = stim.center_spout_angle == contingency.Platform &...
                stim.head_stim_angle == contingency.Speaker_Angle &...
                response == contingency.Action;

            stim.correct(idx) = 1;                                  
        end       
    end    
end

% for i = 1 : size( stim.contingency, 1)
%    
%     idx = stim.center_spout_angle == stim.contingency.Platform(i) &...
%           stim.head_stim_angle == stim.contingency.Speaker_Angle(i) &...          
%           response == stim.contingency.Action(i);
%         
%     stim.correct(idx) = 1;    
% end

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
ylabel('p(Left?)')
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
ylabel('p(Left?)')

set(ax(1:2),'ylim',[0 1])
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
ylim([0 100])


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
response = data(:, strcmp(header, 'response_angle_alt'));

% Separate probe and test speakers
stim.not_probe = stim.speaker == 6 | stim.speaker == 12;

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
test_data = test_data( correct_idx, :);

c_stim_idx = test_data(:, strcmp( header, 'Speaker Location'));
c_stim_ang = test_data(:, strcmp( header, 'speaker_platform_angle'));
c_platform = test_data(:, strcmp( header, 'CenterSpoutRotation'));
c_resp_ang = test_data(:, strcmp( header, 'response_angle_alt'));
c_resp_idx = test_data(:, strcmp( header, 'Response'));

contingency = unique([c_stim_idx, c_stim_ang, c_platform c_resp_idx c_resp_ang], 'rows');
contingency = array2table(contingency,'VariableNames',{'Speaker_Idx','Speaker_Angle','Platform','Response_Idx','Response_Angle'});

stim.contingency = contingency;

