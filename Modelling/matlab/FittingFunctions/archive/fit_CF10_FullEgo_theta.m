function [Xfit, X0, NegLL, BIC] = fit_CF10_FullEgo_theta(response, stim)
%
%
% Stephen Town: 24 August 2019

obFunc = @(x) lik_CF10_FullEgo_Theta(response, stim, x(1), x(2), x(3), x(4));

X0 = [rand(1,2) exprnd(1) rand(1)];   % Initial estimates
LB = [0 -180 0.1 -180];
UB = [10 180 20 180];

X0(1) = (X0(1) * (UB(1) - LB(1))) + LB(1);  % Extend random number into parameter range
X0(2) = (X0(2) * (UB(2) - LB(2))) + LB(2);  
X0(4) = (X0(4) * (UB(4) - LB(4))) + LB(4);  

[Xfit, NegLL] = fmincon(obFunc, X0, [], [], [], [], LB, UB);

LL = -NegLL;
BIC = length(X0) * log(length(response)) + 2*NegLL;