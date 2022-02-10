function TestModel_Alt03_Nearest(file_path, file_name)
% function TestModel_Alt03_Nearest(file_path, file_name)
%
% Model behavior in the world-centered task as a response 90-deg CCW from
% head-centered sound location
%
% Arguments:
% ---------
%   - file_path: str to path containing formatted behavioral files
%   - file_name: str of csv file containing data for one ferret
%
% Outputs:
% --------
%   - fold_performance.csv: file containing performance predicting animal
%       behavior on each fold
%   - param_contrast.csv: file containing negative log-likelihood values
%   for each model fitted (nRuns * nFolds)
%   - config.txt: log file containing information about fitting parameters
%
% Notes:
% -----
%   - Best run from Modelling/matlab
%
% TO DO: 
%   - Fix contingency calculations in load_data for head-centered task
%   - Balance sample sizes in input data to model
%
% Version History:
% -----------------
%   ST: 14 Jan 2022 - Branched from TestModel_Alt01_90CCW_Guess
%   ST: 23 Aug 2021 - Adapted for Github
%   ST: 11 Oct 2020 - Split probe data out from training data
%   

% Options
nFolds = 20;
nRuns = 20;  
train_trials = 10;
nParams = 2;               % Number of parameters in model


stim_col = 'speaker_angle_platform';      % Variable used as predictor
train_probe = false;             % All_data (includes probe locations)
test_probe = true;             % All_data (includes probe locations)

fitfunc = @fit_Alt03_Nearest;
simfunc = @simulate_Alt03_Nearest;

C = who();                 % Record config variables before expanding workspace

% Select input data if not specified
if nargin == 0
    modelling_dir = fileparts( pwd());
    repo_dir = fileparts(modelling_dir);
    addpath( genpath( modelling_dir))
    
    file_path = fullfile(repo_dir, 'Analysis\Main\Data\Formatted');
    [file_name, file_path, ~] = uigetfile(fullfile(file_path, '*.csv'), 'Select subject:');
end

data = load_data( file_path, file_name, stim_col, test_probe);

% Split data into training and testing subsets 
cvIndices = crossvalind('Kfold', size(data,1), nFolds);

% Log config file and start recording results
if iscell(file_name), file_name = cell2mat(file_name); end
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

    % Have the potential to selectively remove probe data from training but not test set
    if ~train_probe     
       train_folds = train_folds(train_folds.not_probe == 1, :); 
    end
    
    train_folds = flatten_sample_sizes(train_folds, train_trials);    
    
    [Xfit, X0, NegLL] = altfit_data_multiple_runs(fitfunc, nRuns, train_folds, stim_col);
    
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

