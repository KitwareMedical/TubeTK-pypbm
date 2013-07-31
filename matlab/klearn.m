function [Orig, Data, Dict, Gamma] = klearn(imgListFile, K, lab, N, S, C)
% Use a kernel to measure distances for NN computation and dict. learning.
%
% INPUTS:
%   imgListFile - File with L image filenames (absolute path)
%   K           - LxL kernel matrix
%   lab         - Lx1 label array (0/1 labeling)
%   N           - Compute N-nearest neighbors
%   S           - Sparsity (for KSVD)
%   C           - C dictionary ATOMS (for KSVD)
%
% OUTPUTS:
%   Orig        - Original image data
%   Data        - Difference images (with NN's computed using the kernel)
%   Dict        - Dictionary ATOMS (sorted by dominance)
%   Gamma       - Signal representation Matrix
%
% AUTHOR(s):
%   Roland Kwitt, Kitware Inc., 2013

    % get distance matrix
    D = kernelToDistance(normalizekm(K));

    % read labels and assert that we only have two labels
    uniqueLab = unique(lab);
    assert(length(uniqueLab) == 2, 'Oops (more than 2 labels) ...');
    p = find(lab == uniqueLab(1));

    % read list of image filenames
    imgList = importdata(imgListFile);
    assert(length(imgList) > 1, 'Oops (less than 1 image) ...');
    im = imread(imgList{1});

    % allocate memory
    Data = zeros(numel(im), length(p)*N);
    Orig = zeros(numel(im), length(imgList));

    % read images
    for j=1:length(imgList)
        im = imread(imgList{j});
        Orig(:,j) = im(:);
    end

    % iterate over first population (i.e., those with label 0)
    for i=1:length(p)
        ref = imread(imgList{p(i)});
        [~, ind] = sort(D(p(i),:));
        ind = ind(2:end);
        nnLab = find(lab(ind) == uniqueLab(2));
        disp(ind(nnLab(1:N)))
        for j=1:N
            im = imread(imgList{ind(nnLab(j))});
            Data(:,(i-1)*N+j) = ref(:) - im(:);
        end
    end

    % configure KSVD
    par.data = Data;
    par.iternum = 50;
    par.Tdata = S;
    par.dictsize = C;

    % run KSVD
    [Dict, Gamma] = ksvd(par,'','t');
    Gamma = full(Gamma);
    norms = zeros(DSize,1);
    for i=1:DSize
        norms(i)=norm(Gamma(i,:));
    end

    % Sort by dominant ATOMS
    [sNorms,iNorms] = sort(norms,1,'descend');
    disp([sNorms(:) iNorms(:)])
    Dict = Dict(:,iNorms);
 end
