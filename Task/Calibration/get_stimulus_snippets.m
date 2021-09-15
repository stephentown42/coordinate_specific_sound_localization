function get_stimulus_snippets(tank, block)
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
    tank = 'E:\UCL_Behaving\F1902_Eclair';
    blockNum = 47;
    block = sprintf('Block-%d', blockNum); 
end

S = TDT2mat(tank, block, 'STORE','RecV');
S = S.streams.RecV;

fprintf('Sample rate: %.3f\n', S.fs)

% Drop first ten seconds (high background noise while task unresponsive to
% subject input - also a period in which we didn't present any calibration
% sounds
switch block
    case 'Block-10'
        start_trash = 40;        
    case 'Block-11'
        start_trash = 60;        
    case 'Block-31'
        start_trash = 32;        
    case 'Block-35'
        start_trash = 38;
    case 'Block-37'
        start_trash = 45;
    otherwise
        start_trash = 10;
end

switch block
    case 'Block-6'
        max_time = 50;
    otherwise
        max_time = inf;
end
    
tvec = (1 : numel(S.data)) / S.fs;
S.data(1: round(start_trash*S.fs)) = nan;

if ~isinf(max_time)
    max_samp = floor( max_time * S.fs);
    S.data(max_samp:end) = nan;
end

figure('name', block); 
hold on
h = plot(tvec, S.data,'k');

% Recursively move through data finding noise bursts
stim_durn = 0.25;
envelope_time = 0.005;

dur_samps = ceil( stim_durn * S.fs);
env_samps = ceil( envelope_time * S.fs);

rms_val = sqrt(nanmean(S.data.^2));
threshold = 5 * rms_val;

plot([tvec(1) tvec(end)], [threshold, threshold], '--','color',[.5 .5 .5])

cownt = 0;
snippet = [];
while any(S.data > threshold)
    
    first_above = find(abs(S.data) > threshold, 1, 'first');
        
    snip_start = first_above - env_samps;
    snip_start = snip_start - dur_samps;
        
    idx = [1:(dur_samps+env_samps)*2] + snip_start;
    
    cownt = cownt + 1;
    snippet(cownt) = plot(tvec(idx), S.data(idx));
    if cownt >= 10, break; end
        
    S.data(idx) = nan;
    delete(h)
    h = plot(tvec, S.data, 'k');
end

if cownt == 0
    fprintf('No stimuli detected\n');
    return
end

% Write snippets to disk
fS = S.fs;
examples = nan(cownt, numel(idx));

for i = 1 : cownt
    examples(i,:) = get(snippet(i),'YData');
end

save_path = 'C:\Users\steph\Desktop\Jumbo_Sound_Test_2021_07_06';
save_file = sprintf('%s.mat', block);

save( fullfile( save_path, save_file), 'fS', 'examples')


get_stimulus_spectra(blockNum)





