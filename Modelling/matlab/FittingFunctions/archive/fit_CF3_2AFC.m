function [Xfit, NegLL, BIC] = fit_CF3_2AFC(response, stim)
%
%
% Stephen Town: 17 August 2019

obFunc = @(x) lik_CF3_2AFC(response, stim, x(1), x(2), x(3));

X0 = [exprnd(1) rand(1) exprnd(1)];   % Initial estimates
LB = [0 0 0];
UB = [10 1 100];

[Xfit, NegLL] = fmincon(obFunc, X0, [], [], [], [], LB, UB);

LL = -NegLL;
BIC = length(X0) * log(length(response)) + 2*NegLL;