function [Xfit, X0, NegLL, BIC] = fit_CF9_PartEgo_theta(response, stim)
%
%
% Stephen Town: 23 August 2019

obFunc = @(x) lik_CF9_PartEgo_Theta(response, stim, x(1), x(2), x(3));

X0 = [rand(1,2) exprnd(1)];   % Initial estimates
LB = [0 -180 0.1];
UB = [10 +180 20];

X0(1) = (X0(1) * (UB(1) - LB(1))) + LB(1);  % Extend random number into parameter range
X0(2) = (X0(2) * (UB(2) - LB(2))) + LB(2);  

[Xfit, NegLL] = fmincon(obFunc, X0, [], [], [], [], LB, UB);

LL = -NegLL;
BIC = length(X0) * log(length(response)) + 2*NegLL;