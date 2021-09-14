function S = test_model_performance( simfun, test_fold, X)
%
% Runs simulation with fitted parameters and then measure how many
% responses you were able to match to the animals
%
% Arguments:
%   - simfun: handle to simulation function
%   - test_fold: held out data on which to test performance
%   - X: paramters to send to model
%
% Returns:
%   S: structure containing performance metrics for plotting
%
% Version History
%   - 2021-8-23: Pulled from TestModel_CF8_FullAllo_Theta.m

[predicted_response, ~] = simfun(X, test_fold);

correct = predicted_response == test_fold.Response;

S = struct();
S.nCorrect = sum(correct);
S.nTrials = numel(correct);
S.pCorrect = mean(correct) * 100;
S = struct2table(S);