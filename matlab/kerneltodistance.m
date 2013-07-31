function Distance = kerneltodistance(K)
% Computes distances from a normalized kernel.
%
% INPUTS:
%   K - NxN kernel matrix
%
% OUTPUTS:
%   D - NxN distance matrix
%
% AUTHOR(s):
%  Roland Kwitt, Kitware Inc., 2013

    Distance = zeros(size(K));
    N = size(Distance,1);
    for i = 1:N
        for j = 1:N
            Distance(i,j) =2 - 2*K(i,j);
        end
    end
    Distance(Distance<=0)=0;
    Distance = sqrt(Distance);
end
