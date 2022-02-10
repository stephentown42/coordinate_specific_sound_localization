function [Xfit, X0, NegLL, BIC] = fit_CF8_theta(response, stim)
%
% Coefficients:
%   1: vert_offset
%   2: horiz_offset
%   3: amplitude (0-0.5)
%   4: coldness
%
% Version History
%   2019-08-20: Created (Stephen Town)
%   2021-08-23: Modified for Github: 

obFunc = @(x) lik_CF8_Theta(response, stim, x(1), x(2), x(3), x(4));

% Define parameter limits and initial values
min_v_offset = 0.5;
fst_v_offset = rand(1)/2 + 0.5;
max_v_offset = 1.0;

min_h_offset = -180;
fst_h_offset = (rand(1) * 360) - 180;
max_h_offset = 180;

min_amplitude = 0;
fst_amplitude = rand(1) / 2;
max_amplitude = 0.5;

min_coldness = 0.0001;
fst_coldness = exprnd(1);
max_coldness = 20;

parameter_names = {'vert_offset','horiz_offset','amplitude','coldness'};   % Can be confirmed by checking the likelihood function
X0 = [fst_v_offset, fst_h_offset, fst_amplitude, fst_coldness];
LB = [min_v_offset, min_h_offset, min_amplitude, min_coldness];
UB = [max_v_offset, max_h_offset, max_amplitude, max_coldness];

% Optimize
[Xfit, NegLL] = fmincon(obFunc, X0, [], [], [], [], LB, UB);

LL = -NegLL;
BIC = length(X0) * log(length(response)) + 2*NegLL;

% Return as tables with column names
X0 = array2table(X0, 'VariableNames', parameter_names);
Xfit = array2table(Xfit, 'VariableNames', parameter_names);