function simulate_E1_stimWorld_respWorld
% 
% 
% Stephen Town - 29 May 2019 
% 
% Note that the visualization here is retained so that (i) we don't have to
% make large scale changes to the coe that could introduce errors, and (ii)
% so we can see things make sense as they run.

% D

% Simulated spatial tuning
b0 = 0; % Parameters
b1 = 4;    

xv = linspace(-2, 2, 200);
yv = linspace(-2, 2, 200);
[x, y] = meshgrid(xv, yv);
    
px = 1 ./ (1 + exp(-1 .* (b0 + b1.*x)));   % Logistic 
py = ones( size(y)) ./ numel(y);    % Uniform
z = bsxfun(@plus, px, py');

sim_map = v2struct(x, y, z, xv, yv);

nTrials = 100;

% Stimulus 
stim.speaker = 1:12;
stim.response = [nan(1,5) 9 nan(1,5) 3];
stim.n = numel( stim.speaker);

% Platform 
platform.rho = 3/7; % Arbritrary units
platform.theta_d = -180 : 30 : 180;            % <----------- OPTION
platform = add_info( platform);
platform.delta_ang_d = [platform.theta_d(1) diff(platform.theta_d)];    % Change in angle

% Speakers
speaker.rho = 1;    % Unit distance measure for now (could make cm)
speaker.idx = [11 : -1 : 1, 12];
speaker.theta_d = -150 : 30 : 180;
speaker = add_info( speaker);

% Response ports
response.rho = 0.95;
response.idx = [9 3];
response.theta_d = [-90 90];
response = add_info( response);

% Define paths and create save file
dirs.root = Cloudstation('CoordinateFrames\BehavioralModels');
dirs.result = fullfile( dirs.root, 'SimulationResults');

txtName = sprintf('E1sWrW_%s.txt', datestr(now,'yyyy_mm_dd_T_HH_MM'));

fid = fopen( fullfile( dirs.result, txtName), 'wt+');

fprintf(fid,'Platform_angle_d\t');
fprintf(fid,'Stim_idx\t');
fprintf(fid,'Stim_angle_dWorld\t');
fprintf(fid,'Stim_angle_dPlatform\t');
fprintf(fid,'Response_idx\t');
fprintf(fid,'Response_angle_dWorld\t');
fprintf(fid,'Response_angle_dPlatform\t');
fprintf(fid,'Correct\t');



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Create figure and axes

% Create figure (frame)
fig = figureST('units','centimeters','position',[3 3 48 23.3]);
cmap = colormap('gray');
colormap(cmap(1:32,:));

% Visualization of experiment
ax.world = axes('nextplot','add','position',[0.0333    0.5240    0.2083    0.4295],...
                'xlim',[-1.25 1.25],'ylim',[-1.25 1.25],'view',[90 90]);

ax.platform = axes('nextplot','add','position',[0.2832    0.5240    0.2083    0.4295],...
                   'xlim',[-1.25 1.25],'ylim',[-1.25 1.25],'view',[90 90]);
               
title(ax.world, 'World CF')            
title(ax.platform, 'Platform CF')
               
axis([ax.world ax.platform],'off')

% Measures of stimulus position in different CFs               
ax.metric.stim = axes('nextplot','add','position',[0.5415    0.7818    0.2083    0.1718],...
                      'ylim',[-180 180],'ytick',-180:60:180,'YGrid','on');
                  
ax.metric.response = axes('nextplot','add','position',[0.5415    0.5584    0.2083    0.1718],...
                          'ylim',[-180 180],'ytick',-180:60:180,'YGrid','on');
                      
xlabel( ax.metric.response, 'Iteration')
ylabel( ax.metric.stim, ' Angle (°)')
ylabel( ax.metric.response, 'Angle (°)')
title( ax.metric.stim, 'Stimulus')
title( ax.metric.response, 'Response')

% Performance predictions
ax.performance.world = axes('nextplot','add','position',[0.0333 0.3093 0.2083 0.1546],...
                            'xlim',[-180 180],'ylim',[0 1]);
ax.performance.platform = axes('nextplot','add','position',[0.2832 0.3093 0.2083 0.1546],...
                            'xlim',[-180 180],'ylim',[0 1]);
ax.performance.probe = axes('nextplot','add','position',[0.5498 0.2233 0.2083 0.2577],...
                            'xlim',[-150 180],'ylim',[-180 180]);
ax.performance.correct = axes('nextplot','add','position',[0.0333 0.06 0.2083 0.1546],...
                            'xlim',[-180 180],'ylim',[0 1]);

xlabel( ax.performance.world, 'Stim Angle: World (°)')
ylabel( ax.performance.world, 'p(Spout 9)')
xlabel( ax.performance.platform, 'Stim Angle: Platform (°)')
xlabel( ax.performance.probe, 'Platform Angle (°)')
ylabel( ax.performance.probe, 'Stim Angle: World (°)')
xlabel( ax.performance.correct, 'Platform Angle (°)')
ylabel( ax.performance.correct, 'p(Correct)')


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Create fixed graphics objects (quicker to update properties than redraw
% on every iteration)

% World centered space (speakers and response ports never move)
plot_coordinate_axes( ax.world);
h.world.speaker = intial_plot( speaker, 'speaker', 'o', ax.world);
h.world.response = intial_plot( response, 'response', '^', ax.world);
h.world.map = surf(sim_map.x, sim_map.y, sim_map.z,...
                    'EdgeColor','none','parent', ax.world);

% Platform centered space
plot_coordinate_axes( ax.platform);
plot3([0 platform.rho(1)],[0 0],[3 3],'LineWidth',20,'parent', ax.platform,'Color','g')


% Measures of stimulus position in different CFs         
h.metric.stim.platform = plot(0,0,'m','Userdata',0,'parent', ax.metric.stim);
h.metric.stim.world = plot(0,0,'k','Userdata',0,'parent', ax.metric.stim);
h.metric.response.platform = plot(0,0,'m','Userdata',0,'parent', ax.metric.response);
h.metric.response.world = plot(0,0,'k','Userdata',0,'parent', ax.metric.response);

text(1, 1, 'Platform','Color','m','parent',ax.metric.stim,'FontWeight','bold','units','normalized')
text(1, 0.9, 'World','Color','k','parent',ax.metric.stim,'FontWeight','bold','units','normalized')                        
text(1, 1, 'Platform','Color','m','parent',ax.metric.response,'FontWeight','bold','units','normalized')
text(1, 0.9, 'World','Color','k','parent',ax.metric.response,'FontWeight','bold','units','normalized')
                        
% Performance metrics
h.performance.platform.pSpout3 = scatter(0,nan,'k','Userdata',0,...
                             'parent', ax.performance.platform);
h.performance.world.pSpout3 = scatter(0,nan,'k','Userdata',0,...
                            'parent', ax.performance.world);
h.performance.pCorrect = scatter(0,nan,'r','Userdata',0,...
                                'parent', ax.performance.correct);

h.probe_map.world = imagesc(speaker.theta_d, platform.theta_d,...
                            zeros(speaker.n, platform.n),...
                            'parent',ax.performance.probe);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Intial plotting of items for later rotation (assume CFs aligned during
% initialization for simplicity)

h.world.platform = plot3([0 platform.rho(1)],[0 0],[3 3],'LineWidth',20,...
                        'parent',ax.world,'Color','g');
                    
h.platform.speaker = intial_plot( speaker, 'speaker', 'o', ax.platform);
h.platform.response = intial_plot( response, 'response', '^', ax.platform);

% Surface plot in frame under rotation
h.platform.map = surf(sim_map.x, sim_map.y, sim_map.z,...
                    'EdgeColor','none','parent', ax.platform);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% For each platform rotation
for i = 1 : platform.n   
    
    % Calculate rotation matrices
    platform_to_world = rotz( platform.delta_ang_d(i));
    world_to_platform = transpose(platform_to_world); % Inverted matrix
    
    % Rotate platform
    rotate_line_obj( h.world.platform, platform_to_world)
    
    % Rotate speakers
    for j = 1 : speaker.n
       rotate_line_obj( h.platform.speaker.h(j), world_to_platform)
       rotate_text_obj( h.platform.speaker.t(j), world_to_platform)
    end
    
    % Rotate response ports
    for j = 1 : response.n
       rotate_line_obj( h.platform.response.h(j), world_to_platform)
       rotate_text_obj( h.platform.response.t(j), world_to_platform)
    end
    
    % Rotate tuning function
    remap_simulation(h.platform.map, world_to_platform);
   
    % For each stimulus
    for j = 1 : stim.n
        
        % Highlight current stimulus 
        stim.speaker_j = highlight_current( fig, h, 'speaker', stim.speaker(j));
                
        update_h_metric( h.metric.stim.world,    stim.speaker_j.world_theta_d)        
        update_h_metric( h.metric.stim.platform, stim.speaker_j.platform_theta_d)
        
        % Get probability of response                
        pSpout9_world    = my_interp2( h.world.map,    stim.speaker_j.world_pos);
        pSpout9_platform = my_interp2( h.platform.map, stim.speaker_j.platform_pos);
                
        % Get response from model              
        % (here's where the translation between stimulus and reponse begins to get interesting)                      
        respond_spout9 = rand(nTrials, 1) < pSpout9_world;
        response.j = respond_spout9 .* 9;
        response.j( respond_spout9 == 0) = 3;       
        
        % Get angles
        response.j_theta_world = respond_spout9 .* -90;
        response.j_theta_world(response.j_theta_world == 0) = 90;
        
        % Highlight current response        
        stim.response_j = highlight_current( fig, h, 'response', mode(response.j));
        
        update_h_metric( h.metric.response.world,    stim.response_j.world_theta_d)        
        update_h_metric( h.metric.response.platform, stim.response_j.platform_theta_d)                        
                
        % Update record of stimulus position in platform and world coordinate frames
        update_h_performance(h, stim, 'platform','pSpout3', pSpout9_platform)        
        update_h_performance(h, stim, 'world','pSpout3', pSpout9_world)
        
        % Update probe plot
        row_idx = speaker.idx == stim.speaker(j);
        col_idx = i; % This could be a source of errors if platform angles become unsorted in future
        
        z = get(h.probe_map.world, 'CData');
        z(row_idx, col_idx) = z(row_idx, col_idx) + mean(respond_spout9);
        set(h.probe_map.world, 'CData', z);        
        
        % Get target response
        response.target = stim.response(j);
        
        if ~isnan( response.target)            
            isCorrect = response.j == response.target;
            
            x_c = [h.performance.pCorrect.XData, platform.theta_d(i)];
            y_c = [h.performance.pCorrect.YData, mean(isCorrect)];
            
            set(h.performance.pCorrect,'XData', x_c, 'YData', y_c)            
        end                     
        
        % Write data to log
        for k = 1 : nTrials
            fprintf(fid,'%d\t', platform.theta_d(i));
            fprintf(fid,'%d\t', stim.speaker(j));
            fprintf(fid,'%.0f\t', stim.speaker_j.world_theta_d);
            fprintf(fid,'%.0f\t', stim.speaker_j.platform_theta_d);
            fprintf(fid,'%d\t', response.j(k));
            fprintf(fid,'Response_angle_dWorld\t');
            fprintf(fid,'Response_angle_dPlatform\t');
            fprintf(fid,'Correct\t');
        end
    end
end

% Show mean ± s.e.m. across rotations / stimuli
scatter_to_mean( h.performance.world.pSpout3);
scatter_to_mean( h.performance.platform.pSpout3);

% Reset time-varying data plots to show all iterations
set(ax.metric.stim,'xlimmode','auto')
set(ax.metric.response,'xlimmode','auto')

% Close save log
fclose(fid);





function S = add_info(S)

    S.n = numel( S.theta_d);
    S.rho = repmat( S.rho, 1, S.n);
    S.theta_r = deg2rad( S.theta_d);
    [S.x, S.y] = pol2cart( S.theta_r, S.rho); 

    
function h = plot_coordinate_axes( ax)

h(1) = plot3([0 1], [0 0], [2 2],'-', 'parent', ax,'tag','Positive X');
h(2) = plot3([0 -1], [0 0], [2 2],'--', 'parent', ax,'tag','Negative X');
h(3) = plot3([0 0],  [0 1], [2 2],'-', 'parent', ax,'tag', 'Positive Y');
h(4) = plot3([0 0], [0 -1], [2 2],'--', 'parent', ax,'tag','Negative Y');

set(h,'LineWidth',1.5)

text(0.6, 0, 'X','parent',ax, 'VerticalAlignment','bottom',...
    'HorizontalAlignment','center', 'BackgroundColor','w')
text(0, 0.6, 'Y','parent',ax, 'VerticalAlignment','middle',...
    'HorizontalAlignment','Left', 'BackgroundColor','w')


function A = intial_plot( S, prefix, marker, ax)

A = struct('h', nan(S.n, 1), 't', nan(S.n, 1));

for i = 1 : S.n
    
   A.h(i) = plot3( S.x(i), S.y(i), 3, marker,'MarkerSize',12,...
               'parent', ax,'MarkerFaceColor','w',...
               'tag',sprintf('%s %02d', prefix, S.idx(i)));
   
   A.t(i) = text( S.x(i), S.y(i), 3, num2str( S.idx(i)),...
               'parent', ax, 'HorizontalAlignment','center',...
               'FontSize',8,'VerticalAlignment','middle');  
end


function rotate_line_obj(h, R)
    
    v = [get(h,'xdata'); get(h,'ydata')]; % x, y        
    w = R(1:2,1:2) * v; % Use 2D only

    set(h, 'xdata', w(1,:), 'ydata', w(2,:));

    
function rotate_text_obj(h, R)
    
    set(h,'position', R * transpose(get(h,'position'))); 


function remap_simulation( h, R)

    x = get(h,'XData');
    y = get(h,'YData');
    
    v = transpose([x(:) y(:)]); 
    w = R(1:2,1:2) * v; % Use 2D only
    
    x = reshape(w(1,:), size(x));
    y = reshape(w(2,:), size(y));
    
    set(h,'xdata', x, 'ydata', y)
        
    
function out = highlight_current( fig, h, str, val)

    % Reset all objects
    eval( sprintf( 'h_w = h.world.%s.h;', str))
    eval( sprintf( 'h_p = h.platform.%s.h;', str))
    set([h_w h_p], 'LineWidth', 1, 'MarkerFaceColor','w')

    % Highlight target
    target = findobj(fig, 'tag', sprintf('%s %02d', str, val));
    set(target,'MarkerSize', 20,'LineWidth',4,'MarkerFaceColor','y')
    
    % Return positions of stimuli in two coordinate frames
    x = cell2mat( get(target,'xdata'));
    y = cell2mat( get(target,'ydata'));
    
    tag_1 = get( get( get(target(1),'parent'), 'title'), 'string');
    
    if strcmp(tag_1, 'Platform CF')
       out.platform_pos = [x(1); y(1)];
       out.world_pos = [x(2); y(2)];
    else
       out.world_pos = [x(1); y(1)];
       out.platform_pos = [x(2); y(2)];
    end
    
    % Get angles 
    out.platform_theta_d = atan2d( out.platform_pos(2), out.platform_pos(1)); 
    out.world_theta_d = atan2d( out.world_pos(2), out.world_pos(1)); 
    
    
    
function stim = get_position(j, stim, obj, R)

    % Read stimulus field from input name of object   
    obj_name = inputname(3);    % stimulus/response)  
    eval( sprintf('val = stim.%s(j);', obj_name))

    % Do some geometry
    X.world_theta_d = obj.theta_d( obj.idx == val); 

    X.world_pos = [obj.x( obj.idx == val); 
                   obj.y( obj.idx == val)];                       

    X.platform_pos = R(1:2,1:2) * X.world_pos;      
    X.platform_theta_d = atan2d( X.platform_pos(2), X.platform_pos(1));        
    
    % Return variables as part of stimulus structure
    eval( sprintf('stim.%s_j = X;', obj_name))
    
    dBug_val = X.platform_theta_d - X.world_theta_d;
    fprintf('%.1f\n', dBug_val);
    
    if dBug_val == -1
        keyboard
    end
    
    
    
function update_h_metric(h, current_angle)

current_iteration = get(h,'UserData') + 1;

set(h,'Xdata',[get(h,'XData') current_iteration],...
      'Ydata',[get(h,'YData') current_angle],...
      'Userdata', current_iteration);

if current_iteration > 100
    set( get(h,'parent'), 'xlim',[-100 0] + current_iteration)
end
    
  

function zv = my_interp2( h, pos)

x = get(h, 'xdata');
y = get(h, 'ydata');
z = get(h, 'zdata');

delta(:,1) = x(:) - pos(1);
delta(:,2) = y(:) - pos(2);
delta = sum(delta .^ 2, 2);
[~, min_idx] = min(delta);
zv = z(min_idx);


function update_h_performance(h, stim, CF, responseVar, y)
        
    eval( sprintf('h = h.performance.%s.%s;', CF, responseVar))
    eval( sprintf('x = stim.speaker_j.%s_theta_d;', CF))

    set(h,'Xdata',[get(h,'XData') x],'Ydata',[get(h,'YData') y]);
    
    
function scatter_to_mean(h)

    set(h,'MarkerEdgeAlpha',0.05)
    
    x = get(h,'XData');
    y = get(h,'YData');
    
    ux = unique(x);
    nx = numel(ux);
    
    mean_y = nan(nx, 1);
    std_y = nan(nx, 1);
    
    for i = 1 : nx       
        yi = y( x == ux(i));
        mean_y(i) = nanmean( yi);
        std_y(i) = nanstd( yi);        
    end
    
    ax = get(h, 'parent');
    plotSE_patch( ux, mean_y, std_y, ax, 'k');