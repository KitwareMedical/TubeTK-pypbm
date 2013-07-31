function prepimg(ListFile)
% Read images from list, convert to binary image and invert.
%
% The script writes the inverted binary images to disk, using the
% original image filename appended by '-Matlab'.
%
% INPUTS:
%   ListFile - File containing the (absolute) paths to the images.
%
% AUTHOR(s):
%   Roland Kwitt, Kitware Inc., 2013

    list=importdata(ListFile);
    for i=1:length(list)
        [p,nam,~] = fileparts(list{i});
        imName = sprintf('%s-Matlab.png', nam);
        imName = fullfile(p, imName);
        im = imread(list{i});
        im = ~im2bw(im);
        imwrite(im, imName);
    end

end
