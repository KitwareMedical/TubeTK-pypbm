"""pbmtest.py
"""


__license__ = "Apache License, Version 2.0"
__author__  = "Roland Kwitt, Kitware Inc., 2013"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"


from optparse import OptionParser
from core import pbmutils
import SimpleITK as sitk
import numpy as np
import sys
import os


def usage():
    """Print usage information"""
    print("""
This is a simple PBM test script that works on 2D images. It takes a list of
images and labels (binary) and builds a difference matrix. The matrix is
constructed by taking each image with label 0 and subtracting its K closest
images with label 1. Closeness is defined in the Euclidean sense, i.e., images
are considered large vectors.

    USAGE:
        {0} [OPTIONS]
        {0} -h

    OPTIONS (Overview):

        -f NUM
        -l NUM
        -N NUM
        -o FILE

    OPTIONS (Detailed):

        -f FILE

        FILE is the list of input image files (plain ASCII).

        -l FILE

        FILE is the label file (only a binary 0/1 labeling is supported).

        -o FILE

        FILE is the filename for writing the difference matrix (as float32).

        -N NUM (default: 3)

        NUM is the number of neighbors to use.

AUTHOR: Roland Kwitt, Kitware Inc., 2013
        roland.kwitt@kitware.com
""".format(sys.argv[0]))


def main(argv=None):
    if argv is None:
        argv=sys.argv

    parser = OptionParser(add_help_option=False)
    parser.add_option("-N", dest="nNeighbor", type="int", default=3)
    parser.add_option("-f", dest="filesList")
    parser.add_option("-l", dest="labelList")
    parser.add_option("-o", dest="outDiffFile")
    parser.add_option("-h", dest="doHelp", action="store_true", default=False)
    options, _ = parser.parse_args()

    if options.doHelp:
        usage()
        sys.exit(-1)

    filesList = options.filesList
    labelList = options.labelList
    nNeighbor = options.nNeighbor
    outDiffFile = options.outDiffFile

    if filesList is None or labelList is None or outDiffFile is None:
        usage()
        sys.exit(-1)

    with open(filesList) as fid: files = fid.readlines()
    with open(labelList) as fid: label = fid.readlines()

    numLab = []
    [numLab.append(int(x)) for x in label]

    dataLst = []
    for img in files:
        sitkIm = sitk.ReadImage(img.rstrip())
        x = sitk.GetArrayFromImage(sitkIm)
        dataLst.append(sitk.GetArrayFromImage(sitkIm).ravel())

    # build difference image matrix (using Euclidean distance as similarity)
    diffImg = pbmutils.groupDiff(np.asmatrix(dataLst).T, numLab, nNeighbor)
    print "Difference image matrix (%d x %d)" % diffImg.shape

    outFid = open(outDiffFile, 'w')
    np.reshape(diffImg, -1).ravel().astype('float32').tofile(outFid)
    outFid.close()


if __name__ == "__main__":
    sys.exit(main())