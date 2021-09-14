function fit_data = load_data( file_path, file_name, stim_col, inc_probe)
%function [test_data, data] = load_data( file_path, file_name)
%
% Loads data from a csv file that was generated using Jupyter notebooks
% (see ~\CoordinateFrames\BehavioralAnalysis\Notebooks\F1703_Grainger_Analysis.ipynb)
%
%
% Note that response is conveted from spout indices (3 or 9) to actions (1 or 2) 
%
% Inputs:
%   - file_path: directory containing data
%   - file_name: name of csv file 
%   - stim_col: name of column containing predictor values
%   - inc_probe: boolean, whether to include probe trials in output
%
% Return:
%   tables containing speaker index, behavioral response,
%    speaker position in the world in both polar and cartesian
%    space, correct, platform angle and speaker angle relative 
%    to head
%   - test_data: Includes test sounds, excludes probe trials
%   - data: Includes both probe and test sounds
%
% Notes:
%   Properties of test_data include response contingency for task
%
% Version History:
%   - 2021-08-24: Extracted from TestModel_CF8_FullAllo_Theta.m

% Load it
data = readtable( fullfile( file_path, file_name), 'delimiter',',');

% Keep only selected variables
vs = {'SpeakerLocation','Response','CenterSpoutRotation','not_probe',...
    'speaker_angle_world','speaker_angle_platform', 'Correct'};

data = data(:, vs);

% Convert responses into action indices 
% (response 3 = action 2, response 9 == action 1)
% (Note that here the order is critical, as the model is fit to probability
% of making action 1, with action 2 being the alternative
data.Response(data.Response == 0) = 2;

% Convert speaker angle into cartesian coordinates, using assumed rho value
% from model (rho = 1)
eval( sprintf('data.theta_d = data.%s;', stim_col))
% rho = ones(size(data.theta_d));
% [data.x, data.y] = pol2cart( deg2rad(data.theta_d), rho);

% Optional pplit test trials (no probe sounds)
test_data = data(data.not_probe == 1, :);

% Get response contingency from test data
correct_data = test_data(test_data.Correct == 1, {stim_col,'Response'});
contingency = unique(correct_data, 'rows');
contingency.Properties.Description = 'Contingency';

% Direct output based on use or exclusion of probe trials
if inc_probe
    fit_data = data;
else
    fit_data = test_data;
end

fit_data.Properties.UserData = contingency;

% Report to user to ensure source data is correct
fprintf('Response = %d\n', unique(fit_data.Response))
fprintf('Speaker = %d\n', unique(fit_data.theta_d))

