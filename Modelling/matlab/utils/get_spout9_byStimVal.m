function [uniq_x, p9] = get_spout9_byStimVal(response, stim)
%
% Get probability of responding at spout 9 (action 2) for each stimulus
% value presented (e.g. each stimulus angle)
    
uniq_x = unique(stim);
n_x = size( uniq_x, 1);
p9 = nan(n_x, 1);

for j = 1 : n_x    
    resp_i = response( stim == uniq_x(j), :);    
    p9(j) = mean( resp_i == 2);
end
