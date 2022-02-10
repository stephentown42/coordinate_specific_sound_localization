function [Xfit, X0, NegLL, BIC] = fit_Alt02_Round(response, stim)
%
% Coefficients:
%   1: Response offset
%   2: coldness
%
% Version History:
% ---------------
%   2019-08-20: Created (Stephen Town)
%   2021-08-23: Modified for Github
%   2022-01-14: Branched from fit_CF8_theta.m

obFunc = @(x) lik_Alt02_Round(response, stim, x(1), x(2));

% Define parameter limits and initial values
min_r_offset = -180;
max_r_offset = 180;
fst_r_offset = (rand(1) * (max_r_offset - min_r_offset)) + min_r_offset;

min_coldness = 0.0001;
fst_coldness = exprnd(1);
max_coldness = 20;

parameter_names = {'response_offset','coldness'};   % Can be confirmed by checking the likelihood function
X0 = [fst_r_offset, fst_coldness];
LB = [min_r_offset, min_coldness];
UB = [max_r_offset, max_coldness];

% Optimize
[Xfit, NegLL] = fmincon(obFunc, X0, [], [], [], [], LB, UB);

LL = -NegLL;
BIC = length(X0) * log(length(response)) + 2*NegLL;

% Return as tables with column names
X0 = array2table(X0, 'VariableNames', parameter_names);
Xfit = array2table(Xfit, 'VariableNames', parameter_names);