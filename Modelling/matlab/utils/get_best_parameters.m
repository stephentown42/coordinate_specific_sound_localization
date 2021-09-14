function [Xfit, NLL] = get_best_parameters(Xfit, NLL)
% function [Xfit, NLL] = get_best_parameters(Xfit, NLL)
%
% Get best fitting parameters
[NLL, idx] = min(NLL);
Xfit = Xfit(idx,:);