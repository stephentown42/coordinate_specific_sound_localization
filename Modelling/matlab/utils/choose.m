function a = choose(p)
%
% ST notes
% Essentially this function is equivalent to randperm( numel(p), 1)
% If p is [0.5 0.5], then a is either 1 or 2
% I find this function a bit weird for a simply random guess, but I may not
% know all its use cases yet
%
a = [-eps cumsum(p)]; % Create probability edges 
a = find(a < rand); % Fill probability bins at random
a = max(a); % Find the maximum number from that array
