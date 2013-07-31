function Data = readgraphs(listFile, C)
% Build graphs from adjaceny matrices.
%
% INPUTS:
%   ListFile - File containing adjaceny matrix filenames
%   C        - Number of nodes in the graph
%
% OUTPUTS:
%   Data     - Struct array of graph data (compatible with Nino
%              Shervashidze's graph kernel code).
%
%              Data(i).am - Adjaceny matrix
%              Data(i).al - Cell array with C entries; The j-th entry
%                           contains the nodes connected to node j.
%              Data(i).nl.values - Array with C entries containing a label
%                                  for each node (here: just the node ID)
% AUTHOR(s):
%   Roland Kwitt, Kitware Inc., 2013

    list = importdata(listFile);
    for i=1:length(list)
        adjMat = load(list{i}, '-ASCII');
        adjMat(adjMat>0) = 1;
        Data(i).am = adjMat;
        Data(i).al = cell(C,1);
        Data(i).nl.values = zeros(C,1);
        for j=1:size(adjMat,1)
            Data(i).al{j} = find(adjMat(j,:)>=1);
        end
        Data(i).nl.values = (1:C)';
    end
end
