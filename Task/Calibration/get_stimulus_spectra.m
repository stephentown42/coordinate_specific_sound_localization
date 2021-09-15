function get_stimulus_spectra(blockNum)
%
% Each block contains multiple sounds from a single speaker, produced
% through the same stimulus generation system.
%
% The goal of this script is to extract the stimulus snippets from a
% proprietary format and save them for later spectral analysis (we will
% stick to matlab, but the data should have an open format).
%
% Sounds from different speakers are stored in different blocks. Refer to
% github repo for index table linking speaker number with block number.
%

if nargin == 0
    blockNum = input('Please give block number: ');
end


snip_path = 'C:\Users\steph\Desktop\Jumbo_Sound_Test_2021_07_06';
snip_files = dir( fullfile( snip_path, sprintf('*%d.mat', blockNum)));

edge_times = [0.005 0.005];


for i = 1 : numel(snip_files)

    load( fullfile( snip_path, snip_files(i).name), 'fS', 'examples')
    

    figure('name', snip_files(i).name); 

    sp(1) = subplot(3,1,[1 2]);
    sp(2) = subplot(3,1,3);
    set(sp,'nextplot','add')
        
    % Drop any signals that contain nans 
    examples( any(isnan(examples), 2), :) = [];

    % Drop border times involving cos ramp
%     edge_samps = round(edge_times .* fS);
%     examples = examples(:, edge_samps(1):end-edge_samps(2));
    
    n_samps = size(examples, 2) / 2;
    n_snips = size(examples, 1);    
    
    % For each example
    for j = 1 : n_snips
        
        baseline = examples(j, 1:n_samps);
        stimulus = examples(j, n_samps+1:end);
        
        [pxx_base, f] = pspectrum(baseline, fS, 'FrequencyResolution',100);
        plot( f, pow2db(pxx_base), 'color', [0.5 0.5 0.5], 'parent', sp(1))
        
        [pxx_stim, f] = pspectrum(stimulus, fS, 'FrequencyResolution',100);
        plot( f, pow2db(pxx_stim), 'color', 'k', 'parent', sp(1))                
        
        plot(f, pow2db(pxx_stim) - pow2db(pxx_base), 'parent', sp(2));
        
                
        % Save spectra as csv file
        output_table = table(f, pow2db(pxx_base), pow2db(pxx_stim), 'VariableNames',...
            {'Frequency','Baseline_dB','Stimulus_dB'});
        
        output_file = replace(snip_files(i).name, '.mat', sprintf('_Snip%02d.csv', j));
        
        writetable( output_table, fullfile( snip_path, output_file))        
    end        
end



if numel(snip_files) == 1
    set(gcf,'name', snip_files.name)
end


