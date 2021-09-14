function a = simulate_CF2_bias(T, bias)
% function [a, r] = simulate_M3RescorlaWagner_v1(T, mu, alpha, beta)
%
% INPUTS
% T - number of trials
% bias - value between 0 and 1
% 
% OUTPUTS
% a - list of model responses for each trial
%
% Stephen Town: 17 August 2019

p = [bias 1-bias];
a = deal(nan(T, 1));

for t = 1 : T      
    a(t) = choose(p);    
end

