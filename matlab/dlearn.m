function [X, Dict, Gamma] = dlearn(dataFile, shape, T, D, outDir, N)
% Dictionary learning using KSVD.
%
% INPUTS:
%    dataFile - File that contains all data values (as 32bit float)
%    shape    - [x y] specification of how to reshape the data vector
%    T        - Sparsity (for KSVD)
%    D        - Dictionary size (i.e., number of ATOMS)
%    outDir   - Write data to this directory
%    N        - Write N ATOMS to disk (as ASCII images)
%
% OUTPUTS:
%    X        - Original data (N x M matrix) used for dictionary learning
%    Dict     - Dictionary ATOMS (N x D matrix)
%    Gamma    - Dictionary coefficients (D x T matrix)
%
% The code write a 'list' file containing all the filenames of the ATOMS
% into the 'outDir' directory.
%
% AUTHOR(s):
%   Roland Kwitt, Kitware Inc., 2013

    assert(N <= D, 'Oops: N > D');

    % load data
    fid = fopen(dataFile);
    dat = fread(fid,'float32');
    fclose(fid);

    % reshape data and configure KSVD
    dat = reshape(dat, shape)';
    par.data = dat;
    par.iternum = 50;
    par.Tdata = T;
    par.dictsize = D;
    X = dat;

    % run KSVD
    [Dict, Gamma] = ksvd(par,'','t');
    Gamma = full(Gamma);
    norms = zeros(D,1);
    for i=1:D
        norms(i)=norm(Gamma(i,:));
    end
    [~,iNorms] = sort(norms);

    fid = fopen(fullfile(outDir, 'list'),'w');
    for i=1:N
        atomFileName = sprintf('atom-%.4d.bin', i);
        fid = fopen(fullfile(outDir, atomFileName),'w');
        fwrite(fid, Dict(:,iNorms(i)), 'float');
        fclose(fid);
    end
    fclose(fid);
end
