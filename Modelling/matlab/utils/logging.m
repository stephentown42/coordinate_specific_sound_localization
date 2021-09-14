function log_path = logging(varargin)
 
% Create folder to store files 
dt = datestr(now, 'yyyy-mm-dd_HH-MM');
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
