function writetiff(imageFile, data)
% Write data (possibly float) to TIFF image file.
%
% INPUTS:
%   imageFile - Filename of the image to write
%   data      - Image data
%
% AUTHOR(s):
%   Roland Kwitt, Kitware Inc., 2013
    t = Tiff(imageFile, 'w');
    tagstruct.ImageLength = size(data, 1);
    tagstruct.ImageWidth = size(data, 2);
    tagstruct.Compression = Tiff.Compression.None;
    tagstruct.SampleFormat = Tiff.SampleFormat.IEEEFP;
    tagstruct.Photometric = Tiff.Photometric.MinIsBlack;
    tagstruct.BitsPerSample = 32;
    tagstruct.SamplesPerPixel = 1;
    tagstruct.PlanarConfiguration = Tiff.PlanarConfiguration.Chunky;
    t.setTag(tagstruct);
    t.write(single(atlas));
    t.close();
end
