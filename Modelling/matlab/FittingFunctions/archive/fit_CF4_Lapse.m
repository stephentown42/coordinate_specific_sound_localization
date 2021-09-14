function [Xfit, NegLL, BIC] = fit_CF4_Lapse(response, stim)
%
%
% Stephen Town: 18 August 2019

obFunc = @(x) lik_CF4_Lapse(response, stim, x(1), x(2));

X0 = rand(1,2);   % Initial estimates
LB = [0 -inf];
UB = [1 inf];

[Xfit, NegLL] = fmincon(obFunc, X0, [], [], [], [], LB, UB);

LL = -NegLL;
BIC = length(X0) * log(length(response)) + 2*NegLL;