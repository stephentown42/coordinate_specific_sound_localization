function [Xfit, X0, NegLL, BIC] = fit_CF7_FullAllo_Xpos(response, stim)
%
%
% Stephen Town: 20 August 2019

obFunc = @(x) lik_CF7_FullAllo_Xpos(response, stim, x(1), x(2), x(3));

X0 = [rand(1,2) exprnd(1)];   % Initial estimates
LB = [-1 -10 0];
UB = [+1 +20 20];

X0(1) = (X0(1) * (UB(1) - LB(1))) + LB(1);  % Extend random number into parameter range
X0(2) = (X0(2) * (UB(2) - LB(2))) + LB(2);  

[Xfit, NegLL] = fmincon(obFunc, X0, [], [], [], [], LB, UB);

LL = -NegLL;
BIC = length(X0) * log(length(response)) + 2*NegLL;