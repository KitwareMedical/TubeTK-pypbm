"""bwdist.py
"""


__license__ = "Apache License, Version 2.0"
__author__  = "Roland Kwitt, Kitware Inc., 2013"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"


from optparse import OptionParser
import SimpleITK as sitk
import numpy as np
import sys
import os


def invert(orgImg):
    """Compute image inverse.

    Paramters
    ---------
    orgImg : sitk.Image
        Input image.

    Returns
    -------
    invImg : sitk.Image
        Inverse of input image.
    """

    orgMat = sitk.GetArrayFromImage(orgImg)
    minVal = np.amin(orgMat)
    maxVal = np.amax(orgMat)
    invMat = (maxVal + minVal) - orgMat
    invImg = sitk.GetImageFromArray(invMat)
    imgImg.CopyInformation(orgImg)


def usage():
    """Print usage information"""
    print("""
Take a binary image, apply skeletonization and output an inverted Euclidean
distance transform image.

    USAGE:
        {0} [OPTIONS]
        {0} -h

    OPTIONS (Overview):

        -i NUM
        -o NUM
        -s

    OPTIONS (Detailed):

        -i FILE

        FILE is the filename of the input image file.

        -o FILE

        FILE is the filename of the output distance image.

        -s

        If -s is specified, use the squared Euclidean distance.

AUTHOR: Roland Kwitt, Kitware Inc., 2013
        roland.kwitt@kitware.com
""".format(sys.argv[0]))


def main(argv=None):
    if argv is None:
        argv=sys.argv

    parser = OptionParser(add_help_option=False)
    parser.add_option("-l", dest="binFile")
    parser.add_option("-o", dest="denFile")
    parser.add_option("-s", dest="square", action="store_true", default=False)
    parser.add_option("-h", dest="doHelp", action="store_true", default=False)
    options, _ = parser.parse_args()

    if options.doHelp:
        usage()
        sys.exit(-1)

    binFile = options.binFile
    denFile = options.denFile
    useSquaredDistance = options.square

    if not os.path.exists(binFile):
        raise Exception("File %s does not exist!" % imgFile)

    # read the image from disk
    img = sitk.ReadImage(imgFile)

    # generate skeleton
    thinFilter = sitk.BinaryThinningImageFilter()
    thinnedImg = thinFilter.Execute(img)

    # compute the distance map
    dmapFilter = sitk.DanielssonDistanceMapImageFilter()
    dmapFilter.SetSquaredDistance(useSquaredDistance)
    dmap = dmapFilter.Execute(thinnedImg)
    pmap = invert(dmap)

    # ... and write the image back to disk
    sitk.WriteImage(pmap, denFile)


if __name__ == '__main__':
    sys.exit(main())
