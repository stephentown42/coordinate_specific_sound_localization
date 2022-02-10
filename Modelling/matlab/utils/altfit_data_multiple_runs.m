function [Xfit, X0, NegLL] = altfit_data_multiple_runs(fitfunc, nRuns, obs_data, str)
% function [Xfit, X0, NegLL] = altfit_data_multiple_runs(fitfunc, nRuns, obs_data, str)
%
% Fit the data many times to see how reliable the resulting parameters are,
% and if/how they depend on starting values
% 
% Arguments:
%   - fitfunc: handle to fitting function
%   - nRuns: number of times to rerun fitting on same data
%   - obs_data: table containing stimulus and response
%   - str: name of stimulus column
%
% Returns:
%   - Xfit: table of parameter values after fitting for each run
%   - X0:  table of parameter values *before* fitting
%   - NegLL: nRuns x 1 vector of negative log likelihoods for each set of
%   fitted parameters
%
% Version History
%   - 2021-08-23: Pulled from TestModel_CF8_FullAllo_Theta.m
%   - 2021-08-24: Added parameter labels  
%   - 2022-01-14: Branched from fit_data_multiple_runs to include center
%   spout angle and remove redundant input variables

% Parse inputs
response = obs_data.Response;
eval( sprintf( 'stim = obs_data.%s;', str))
stim(:,2) = obs_data.CenterSpoutRotation;       % Add center spout rotation

% Preassign
[Xfit, X0] = deal([]);
NegLL = nan(nRuns, 1);

% For each run
for i = 1 : nRuns
    
    [Xfit_i, X0_i, NegLL(i), ~] = fitfunc( response, stim);        
    
    X0_i.Run = i;     % Ensure consistency across rows
    Xfit_i.Run = i;
    
    X0 = [X0; X0_i];
    Xfit = [Xfit; Xfit_i];
end
