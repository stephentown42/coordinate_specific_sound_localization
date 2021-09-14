function TestModel_CF8_HeadCentred_Theta(file_path, file_name)
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
nParams = 4;               % Number of parameters in model

stim_col = 'speaker_angle_platform';      % Variable used as predictor
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

