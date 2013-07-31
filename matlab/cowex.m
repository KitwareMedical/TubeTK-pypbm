%
% Exp. 1 - Pop. A vs. B and C
%

variants = {'AB', 'AC'};
cvtCells = 100;
sparsity = 2;
nNeigh = 2;
D = 4;

srcDir = '~/cow/';
dstDir = '/tmp/cowres';

for v = 1:length(variants)
    labStr = fullfile(srcDir,sprintf('lab-%s',variants{v}));
    adjStr = fullfile(srcDir,sprintf('Adj-%s-%d',variants{v}, cvtCells));

    lab = load(labStr);
    gkData = readGraphs(adjStr,cvtCells);
    spKern = spkernel(gkData, 0);

    [orig, data, dict, gamma] = gkDiffImg(...
        fullfile(srcDir,sprintf('DensityImagesAbsolute-%s',variants{v})), ...
        spKern, lab, nNeigh, sparsity, D);

    ma = max(abs(data(:)));
    mi = min(abs(data(:)));

    for i=1:D
        atom = reshape(abs(data(:,i)),[256 256]);
        fid = fopen(fullfile(dstDir,sprintf('atom-%s-%.4d.bin', variants{v}, i)),'w');
        fwrite(fid, atom(:), 'float');
        fclose(fid);
    end

    [lowRank,sp] = Candes11a_TFOCS(single(orig),0.8/sqrt(size(orig,1)));

    mL = mean(lowRank,2);
    mLStr = sprintf('avg-lowRank-%s.bin', variants{v});
    fid = fopen(fullfile(dstDir, mLStr),'w');
    fwrite(fid, mL, 'float');
    fclose(fid);

    labs = unique(lab);
    for l=1:length(labs)
        p = find(lab==labs(l));
        mE = mean(sp(:,p),2);
        mEStr = sprintf('avg-sparse-%s-%d.bin', variants{v}, labs(l));
        fid = fopen(fullfile(dstDir, mEStr),'w');
        fwrite(fid, mE, 'float');
        fclose(fid);
    end
end
