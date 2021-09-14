function [Xfit, NegLL, BIC] = fit_CF2_bias(a)
%
%
% Stephen Town: 17 August 2019

obFunc = @(x) lik_CF2_bias(a, x);

X0 = rand(1);
LB = 0;
UB = 1;

[Xfit, NegLL] = fmincon(obFunc, X0, [], [], [], [], LB, UB);

LL = -NegLL;
BIC = length(X0) * log(length(a)) + 2*NegLL;