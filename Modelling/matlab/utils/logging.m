function log_path = logging(varargin)
% function log_path = logging(varargin)
%
% Create a directory for model results and store configuration information
% ahead of model fitting
%
% Parameters:
%   varargin{1}: stack, from which calling function is extracted
%   varargin{2}: config, struct containing information about model runtime
%   values
%
% Returns:
%   - log_path: str of path containing log results, formatted with datetime
%            and model (e.g. 2021-08-25_12-48_TestModel_CF8_FullAllo_Theta)

% Create folder to store files 
dt = datestr(now, 'yyyy-mm-dd_HH-MM-SS');
stack = varargin{1}.name;
log_dir = sprintf('%s_%s', dt, stack);
log_path = fullfile(pwd, 'logs', log_dir);

if ~isfolder(log_path), mkdir(log_path); end   

% Save config file
fid = fopen( fullfile( log_path, 'config.txt'), 'wt+');        
config = varargin{2};                                  

c_field = fieldnames(config);          
for i = 1 : numel(c_field)            

    fprintf(fid, '%s\t', c_field{i});
    eval(sprintf('val = config.%s;', c_field{i}))

    switch class(val)                 
        case 'char'
            fprintf(fid, '%s\n', val);
        case 'double'
            fprintf(fid, '%f\n', val);                            
        case 'function_handle'
            fprintf(fid, '%s\n', func2str(val));
        case 'logical'
            fprintf(fid, '%d\n', val);
    end                                                
end                

fclose(fid);       


