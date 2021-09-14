function [Xfit, NegLL, BIC] = fit_CF5_Stochasticity(response, stim)
%
%
% Stephen Town: 18 August 2019

obFunc = @(x) lik_CF5_Stochasticity(response, stim, x(1), x(2));

X0 = [rand exprnd(1)];   % Initial estimates
LB = [0 0];
UB = [1 100];

[Xfit, NegLL] = fmincon(obFunc, X0, [], [], [], [], LB, UB);

LL = -NegLL;
BIC = length(X0) * log(length(response)) + 2*NegLL;