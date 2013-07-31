"""pbm.py
"""


__license__ = "Apache License, Version 2.0"
__author__  = "Roland Kwitt, Kitware Inc., 2013"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"


import os
import sys
import json
import numpy as np
import SimpleITK as sitk
from scipy.spatial.distance import cdist
from sklearn.decomposition import DictionaryLearning
from sklearn.decomposition import MiniBatchDictionaryLearning
from sklearn.decomposition import sparse_encode
from optparse import OptionParser
from core import pbmutils
from core import regtools


def usage():
    """Print usage information"""
    print("""
Pattern based morphometry implementation using sklearn's dictionary learning
code. We learn a sparse dictionary for difference volumes (images), built by
subtracting an image of population A from its K closest neighbors (in the
Euclidean sense) in population B. The dictionary elements can then be visualized
and hopefully highlight characteristic differences between populations A and B.

    USAGE:
        {0} [OPTIONS]
        {0} -h

    OPTIONS (Overview):

        -k NUM
        -D NUM
        -r NUM
        -s NUM
        -r NUM
        -c FILE
        -d FILE
        -a FILE
        -x FILE

    OPTIONS (Detailed):

        -c FILE

        FILE is a JSON file that contains the absolute paths to a collection
        of binaries that are used by core.regtools.

        -i FILE

        FILE is a JSON file that contains information about all the image files
        that need to be processed, as well as the group information.

        -k NUM (default: 5)

        NUM specifies the number of neighbors that are used to build the
        difference images that are later used to compute the dictionary.

        -D NUM (default: 5)

        NUM is an integer value that specifies the size of the learned
        dictionary.

        -r NUM (optional)

        NUM is a float value that specifies the resizing factor of the input
        images. Resampling is a good way to achieve lower computation times
        in the dictionary learning stage.

        -s NUM (optional)

        First, this flag indicates that we only want to run on image slices.
        NUM specifies exactly the slice (in the AP direction) to use. CAUTION:
        Make sure that the slice is within the image!.

        -d FILE (optional)

        If -x is specified, FILE specifies the output file to which the
        difference image data is written (as float32).

        -a FILE (optional)

        If -a is given, FILE specifies the output dictionary file that will be
        written upon completion of the dictionary learning stage (as float32).

        -x FILE (optional)

        If -x is given, FILE specifies the output file to which the raw image
        data is written (as float32).

AUTHOR: Roland Kwitt, Kitware Inc., 2013
        roland.kwitt@kitware.com
""".format(sys.argv[0]))


def main(argv=None):
    if argv is None:
        argv=sys.argv

    parser = OptionParser(add_help_option=False)
    parser.add_option("-i", dest="imgJSON")
    parser.add_option("-c", dest="cfgJSON")
    parser.add_option("-a", dest="outAtomFile")
    parser.add_option("-d", dest="outDiffFile")
    parser.add_option("-x", dest="outImagFile")
    parser.add_option("-s", dest="imSlice", type="int")
    parser.add_option("-r", dest="imScale", type="float")
    parser.add_option("-D", dest="dictSiz", type="int", default=5)
    parser.add_option("-k", dest="nearest", type="int", default=5)
    parser.add_option("-h", dest="doHelp", action="store_true", default=False)
    options, _ = parser.parse_args()

    if options.doHelp:
        usage()
        sys.exit(-1)

    imgJSON = options.imgJSON
    cfgJSON = options.cfgJSON

    outAtomFile = options.outAtomFile
    outImagFile = options.outImagFile
    outDiffFile = options.outDiffFile

    imSlice = options.imSlice
    dictSiz = options.dictSiz
    imScale = options.imScale
    nearest = options.nearest

    imData = json.load(open(imgJSON))
    helper = regtools.regtools(cfgJSON)

    groupSet = set()
    groupMap = dict()
    groupLab = []

    # generate numeric labels for each image
    for entry in imData["Data"]: groupSet.add(entry["Group"])
    for cnt, group in enumerate(groupSet): groupMap[group] = cnt
    for entry in imData["Data"]: groupLab.append(groupMap[entry["Group"]])

    imgFiles = []
    [imgFiles.append(str(e["Source"])) for e in imData["Data"]]

    dataList = []
    for i, imFile in enumerate(imgFiles):
        im0 = sitk.ReadImage(imFile)
        im1 = pbmutils.imResize(im0, imScale)
        imSz = sitk.GetArrayFromImage(im1).shape
        helper.infoMsg("Image size : (%d,%d,%d)" % imSz)
        if not imSlice is None:
            sl0 = pbmutils.imSlice(im1, [0, 0, imSlice])
            dataList.append(sl0.ravel())
        else:
            dataList.append(sitk.GetArrayFromImage(im1).ravel())
        helper.infoMsg("Done with image %d!" % i)

    # write raw image data
    if not outImagFile is None:
        tfid = open(outImgFile, 'w')
        np.reshape(np.asmatrix(dataList).T,-1).astype('float32').tofile(tfid)
        tfid.close()

    # build difference images
    diffIm = pbmutils.groupDiff(np.asmatrix(dataList).T, groupLab, nearest)
    helper.infoMsg("Difference image matrix (%d x %d)" % diffIm.shape)

    # write raw difference data
    if not outDiffFile is None:
        outFid = open(outDiffFile, 'w')
        np.reshape(diffIm, -1).ravel().astype('float32').tofile(outFid)
        outFid.close()

    # create the dictionary learner and run (alpha=1)
    lrnObj = MiniBatchDictionaryLearning(dictSiz, 1, verbose=True)
    lrnRes = lrnObj.fit(np.asmatrix(diffIm).T).components_

    # write dictionary atoms
    if not outAtomFile is None:
        outFid = open(outAtomFile, 'w')
        np.reshape(lrnRes.T, -1).ravel().astype('float32').tofile(outFid)
        outFid.close()


if __name__ == "__main__":
    sys.exit(main())
