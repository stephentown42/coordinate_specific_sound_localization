function TestModel_CF7_FullyAllocentric


% Load behavioral data
rootDir = Cloudstation('CoordinateFrames\BehavioralModels\Ferret_Behavior');
ferret = 'F1703_Grainger';

[data, header] = xlsread( fullfile( rootDir, [ferret '.xlsx']));

response = data(:, strcmp(header, 'Response'));
stim.theta_d = data(:, strcmp( header, 'speaker_angle'));

% Report to user to ensure source data is correct
fprintf('Response = %d\n', unique(response))
fprintf('Speaker = %d\n', unique(stim.theta_d))

% Convert speaker angle into cartesian coordinates, using assumed rho value
% from model (rho = 1)
stim.rho = ones(size(stim.theta_d));
[stim.x, stim.y] = pol2cart( deg2rad(stim.theta_d), stim.rho);

% Convert responses into action indices (response 3 = action 1, response 9
% == action 2)
response = double(response == 9) + 1;

% Fit data, with check for reliability
[Xfit, ~] = fit_data_multiple_runs(response, stim.x);

% Simulate data with the fitted parameters
figure
hold on

nRuns = 20;
[uniq_x, p9] = deal([]);

for i = 1 : nRuns
    [sim_resp, sim_stim] = simulate_CF7_FullyAllocentric(1000, Xfit(1), Xfit(2), Xfit(3));

    [uniq_x(:,i), p9(:,i)] = get_spout9_byStimX(sim_stim.x, sim_resp);    
end

uniq_x = unique( transpose(uniq_x), 'rows');


plotStd_patch( uniq_x, transpose(p9), 'x', gca, [1 0.5 0])


[uniq_x, p9] = get_spout9_byStimX(stim.x, response);  

plot( uniq_x, p9, 'color',[0 0.4 0.8],'LineWidth', 2,'Marker','.','MarkerSize',12)

xlabel('Stim: X Position')
ylabel('p(Spout9)')
legend( getLines, strrep(ferret,'_',' '),'Simulation')


% Manual search of parameter space
% manual_search( response, stim.x)




function [uniq_x, p9] = get_spout9_byStimX(stim, response)
    
uniq_x = unique(stim);
n_x = size( uniq_x, 1);
p9 = nan(n_x, 1);

for j = 1 : n_x    
    resp_i = response( stim == uniq_x(j), :);    
    p9(j) = mean( resp_i == 2);
end




function [params, minNLL] = fit_data_multiple_runs(response, stim)
%
%
% Fit the data many times to see how reliable the resulting parameters are,
% and if/how they depend on starting values

nRuns = 20;
[Xfit, X0] = deal(nan(nRuns, 3));
NegLL = nan(nRuns, 1);

for i = 1 : nRuns
    [Xfit(i,:), X0(i,:), NegLL(i), ~] = fit_CF7_FullyAllocentric_Xpos( response, stim);
end

% Get best fitting parameters
[minNLL, idx] = min(NegLL);
params = Xfit(idx,:);


% Show comparison as colored scatter plot
figure
colormap('jet')

subplot(131)
scatter(X0(:,1), Xfit(:,1), [], NegLL,'filled')
title('x0: cross-over point')

subplot(132)
scatter(X0(:,2), Xfit(:,2), [], NegLL,'filled')
title('K: Sharpness')

subplot(133)
scatter(X0(:,3), Xfit(:,3), [], NegLL,'filled')
title('Beta: Inverse Temperature')

xlabels(getAxes, 'Initial')
ylabels(getAxes, 'Final')



function manual_search( response, stim)

% Specify test values
sim_n = 100;
x0_test = linspace(-1, 1, 21);
k_test = linspace(-10, 10, sim_n);
beta_test = logspace(-1, 1, sim_n);

% Create figure
figure
ax_count = 0;
[min_clim, max_clim] = deal([]);

% Get negative log-likelihood for each combination of parameter values
for x_idx = 1 : sim_n

    NegLL = nan(sim_n);

    for beta_idx = 1 : sim_n

        for k_idx = 1 : sim_n

            NegLL(beta_idx, k_idx) = lik_CF7_FullyAllocentric( response, stim,...
                                                      x0_test(x_idx),...
                                                      k_test(k_idx),...
                                                      beta_test(beta_idx));
        end
    end

    % Get best fit
    [~, min_idx] = min( NegLL(:));
    [min_row, min_col] = ind2sub( size(NegLL), min_idx);
    best_beta = beta_test(min_row);
    best_k = k_test(min_col);

    % Create axis
    ax_count = ax_count + 1;
    subplot(3,7, ax_count)
    hold on
    surf(k_test, beta_test, NegLL,'EdgeColor','none','FaceAlpha',1)
%     plot3(k_sim, beta_sim, max(NegLL(:))+1, 'xk','LineWidth',2,'MarkerSize',6)
    plot3(best_k, best_beta, max(NegLL(:))+1, '+r','LineWidth',1.5,'MarkerSize',6)

    ylabel('Beta')
    xlabel('K')
    title( sprintf('x0 = %.1f', x0_test(x_idx)))
    
    cbar = colorbar;
    ylabel(cbar, 'Negative Log Likelihood')
    set(gca,'yscale','log')
    
    axis tight    
    
    max_clim = max( [max_clim get(gca,'clim')]);
    min_clim = min( [min_clim get(gca,'clim')]);
end

set(getAxes,'clim',[min_clim max_clim])
