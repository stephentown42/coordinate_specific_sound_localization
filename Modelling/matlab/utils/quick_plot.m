function quick_plot(file_path)
%QUICK_PLOT Summary of this function goes here
%   Detailed explanation goes here

% Get model fitting results
results = dir( file_path);

% Create figure
figure
hold on
x_head = 0;

% For each results file
for i = 3 : length(results)
    
    % Load performance
    r_file = fullfile(results(i).folder, results(i).name, 'fold_performance.csv');
    T = readtable( r_file);
    
    % Plot performance
    x_head = x_head + 1;
    jitter = rand(size(T,1), 1) / 10;
   
    bar(x_head + 0.1, mean(T.pCorrect))
    scatter(x_head + jitter, T.pCorrect)
    
end




