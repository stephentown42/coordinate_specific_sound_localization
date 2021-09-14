function NegLL = lik_CF2_bias(a, bias)
%
%
% a is the data that model fit is assessed for
% bias is model parameter being fitted
%
% NegLL is the negative log likelihood that indicates model error (to be
% minimized)
%
% Stephen Town: 17 August 2019

p = [bias 1-bias];
choiceProb = p(a);
NegLL = -sum(log(choiceProb));  % compute negative log-likelihood
