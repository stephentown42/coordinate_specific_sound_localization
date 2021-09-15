function check_upload_integrity
%
% For some reason, some behavioral files have been empty when uploaded to
% github. To make this more annoying, windows lists the file size as being
% normal when the contents of the file do not appear. To ensure that the
% files are correct, this script checks that for every file on github, the
% number of rows in each uploaded file is the same as the number of rows on
% the acqusition machine.
%
% Note that any empty files will be overwritten with original files
%
% Stephen Town - 29 Aug 2020

% Define paths and list ferrets
acq_dir = 'E:\Behavior';
github_dir = fullfile('C:\Users\steph\Documents\GitHub',...
        '\Allocentric-and-Egocentric-Sound-Localization\Data\Original');

ferrets = dir( fullfile( github_dir, 'F*'));   
warning('off','MATLAB:table:ModifiedAndSavedVarnames')

% For each ferret
for i = 3 : numel(ferrets)
    
    fprintf('%s...\n', ferrets(i).name)
    
    % Extend paths
    github_ferret = fullfile( github_dir, ferrets(i).name);
    acq_ferret = fullfile( acq_dir, ferrets(i).name);
    
    % List behavioural files    
    files = dir( fullfile( github_ferret, '*.txt'));
    
    % For each file
    for j = 1 : numel(files)
        
        % Extend file path
        github_file = fullfile( github_ferret, files(j).name);
        acq_file = fullfile( acq_ferret, files(j).name);
        
        % Check acquisition PC has file
        if ~exist( acq_file, 'file')
            fprintf('\t%s - not found\n', files(j).name)
            continue
        end        
        
        % Load data
        G = readtable( github_file);
        A = readtable( acq_file);
        
        % Report disparities
        if size(G,1) ~= size(A,1)
            fprintf('\t%s\n', files(j).name)                        
            
            % Overwrite if uploaded file is empty
            if size(G,1) == 0
               copyfile( acq_file, github_file) 
            else
                keyboard
            end
        end        
    end              
end

warning('on','MATLAB:table:ModifiedAndSavedVarnames')