% Batch model fitting
%
% Fits multiple models to data from each ferret in the project
%
% Version History:
%   2021-08-??: Created
%   2022-01-14: Branched from Batch_test_CF8.m

% Define paths
modelling_dir = fileparts( pwd());
repo_dir = fileparts(modelling_dir);
addpath( genpath( modelling_dir))

rng(1)

% List files for each ferret
file_path = fullfile(repo_dir, 'Analysis\Main\Data\Formatted');
files = dir( fullfile( file_path, '*.csv'));

combined_files = {'F1701_Pendleton.csv','F1703_Grainger.csv','F1811_Dory.csv'};

% Fit model that falls back to guessing
% for i = 1 : numel(files)
%     TestModel_Alt01_Guess(file_path, files(i).name)
% end

% Fit model that falls back to guessing
% for i = 1 : numel(files)
%     TestModel_Alt02_Round(file_path, files(i).name)
% end

% Fit model that guesses based on proximity
% for i = 1 : numel(files)
%     TestModel_Alt03_Nearest(file_path, files(i).name)
% end

TestModel_Alt01_Guess(file_path, combined_files)
TestModel_Alt02_Round(file_path, combined_files)
% TestModel_Alt03_Nearest(file_path, combined_files)
