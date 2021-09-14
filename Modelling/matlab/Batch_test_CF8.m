
% Paths
modelling_dir = fileparts( pwd());
repo_dir = fileparts(modelling_dir);
addpath( genpath( modelling_dir))


file_path = fullfile(repo_dir, 'Analysis\Main\Data\Formatted');
files = dir( fullfile( file_path, '*.csv'));

for i = 1 : numel(files)
    TestModel_CF8_FullAllo_Theta(file_path, files(i).name)
end

pause(120)

for i = 1 : numel(files)
    TestModel_CF8_HeadCentred_Theta(file_path, files(i).name)
end
