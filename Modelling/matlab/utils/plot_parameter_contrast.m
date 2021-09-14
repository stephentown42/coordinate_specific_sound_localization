function plot_parameter_contrast(X0, Xfit, NegLL, ax)
% function plot_parameter_contrast(X0, Xfit, NegLL, ax)
%
% Show comparison as colored scatter plot

% For each parameter
for i = 1 : size(Xfit, 2)
    scatter(X0(:,i), Xfit(:,i), [], NegLL, 'filled', 'parent', ax(i))
end