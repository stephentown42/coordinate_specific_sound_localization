function [line_h, patch_h] = plotStd_patch(x,y,s,ax,color)
% [line_h, patch_h] = plotSE_patch(x,y,s,ax,color)
%
% Can be used to calculate mean and standard deviation if ischar(s) or for 
% data on which standard error is already calculated (s = double input)
% 
% If calculating standard error, y is matrix with rows as trials and columns
% as time samples.


if nargin < 4
    ax = gca;
end

hold on

if ~ischar(s) % Classic method
    
    x2 = [x(:);         flipud(x(:))];
    y2 = [y(:)-s(:);    flipud(y(:)+s(:))];
    
    patch_h = patch(x2,y2,y2.*0,'EdgeColor','none','parent',ax,'FaceAlpha',0.5);
    line_h  = plot(x,y,'parent',ax);
    
    if exist('color','var')
        set(line_h,'Color',color)
        set(patch_h,'FaceColor',color)
    end    
else
   
    ym = nanmean(y,1); % Average across rows    
    ys = nanstd(y,[],1);
    
    [line_h, patch_h] = plotSE_patch(x, ym, ys, ax, color);
end