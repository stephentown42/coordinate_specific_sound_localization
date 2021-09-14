function [T, S] = simulate_CF1_random_v1(nTrials, b, angles)
%
% INPUT
% nTrials is number of trials 
% b is bias (e.g. no bias, b = 0.5)
% angles are the values of the central platform
%
% OUTPUT
% T is a simulation data as table with all the relevant data for tracking 
%   the model performance
% S is a summary of simulation performance vs. platform angle
%
% Based partly on simulate_M1random_v1.m (Wilson & Collins, 2019)
% Stephen Town (07 March 2019)
%
% ST: I moved the choose function into the main code for speed and
% vectorized the function (also for speed)
% Here, reward is determined by producing the target response, which needs
% to be defined (difference from the one-arm bandits). 
%
% Note that at some point, we're going to have to introduce the task
% structure in terms of correlations between platform angles across days.
% For the moment, we're assuming they are random, which isn't the case.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 1. Simulate experimental parameters

% Create table
T = table;

% Add Center Platform Angles
nAngle = numel(angles);
T.Platform_Angle = repmat( angles(:), nTrials / nAngle, 1);

% Add target response list (values of 1 or 2)
T.Target = ones(nTrials, 1);
T.Target(1:nTrials/2) = 2;

% Shuffle, just to be sure!
T = T( randperm(nTrials), :);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 2. Simulate agent responses

% Compute choice probabilities
p = [b 1-b];
cp = [-eps cumsum(p)]; % Create probability edges (response array)

% Create random numbers for each trial
rand_t = rand(nTrials, 1);

% Select response based on random number
sim_response = bsxfun(@lt, cp, rand_t);
T.Response = sum(sim_response, 2);  % Convert to single number (1 or 2)

% Generate reward based on choice
T.Reward = T.Response == T.Target; 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 3. Summarize performance across head direction

% Preassign
S = struct('Angles', transpose(angles),...
           'nTrials', nan(nAngle,1),...
           'nCorrect', nan(nAngle, 1));

% For each angle
for i = 1 : nAngle
    
    % Get index of all trials in simulation
    idx = T.Platform_Angle == angles(i);
    S.nTrials(i) = sum(idx);    % Number of trials (could be done elsewhere but whatever)
    S.nCorrect(i) = sum( T.Reward(idx));    % Number correct
end

% Format
S = struct2table(S);

% Calculate percent correct
S.pCorrect = S.nCorrect ./ S.nTrials .* 100;
