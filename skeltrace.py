"""skeltrace.py
"""


__license__ = "Apache License, Version 2.0"
__author__  = "Roland Kwitt, Kitware Inc., 2013"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"


from optparse import OptionParser
import SimpleITK as sitk
import numpy as np
import cv2 as cv
import sys


def usage():
    """Shows usage information."""
    print("""
Take a 2D binary image of an object and a CVT tesellation of the image space
and trace the skeleton of the object on the CVT tesellation to create an
adjacency matrix. The adjacency matrix is of size CxC, where C is the number
of CVT cells.

    USAGE:
        {0} [OPTIONS]
        {0} -h

    OPTIONS (Overview):

        -i FILE
        -c FILE
        -o FILE
        -v

    OPTIONS (Detailed):

        -i FILE

        Name of the binary input image file. The foreground object is supposed
        to only contain '1' pixel values - background is '0'. The image will
        be input to ITK's BinaryThinningImageFilter to obtain the skeleton of
        the object.

        -c FILE

        Name of the input image file that contains the space partitioning.
        Cells are marked with a unique discrete identifier.

        -o FILE

        Name of the output adjacency matrix file. The file is outputted in
        ASCII format, i.e.,

        0 0 2 0 0 1 ...
        1 0 0 1 1 0 ...
        ...

        -v

        If this flag is set, the contour elements are shown in an image to
        check the result of the contour finding process.


AUTHOR: Roland Kwitt, Kitware Inc., 2013
roland.kwitt@kitware.com
""".format(sys.argv[0]))


def main(argv=None):
    if argv is None:
        argv=sys.argv

    parser = OptionParser(add_help_option=False)
    parser.add_option("-i", dest="imgFile")
    parser.add_option("-c", dest="cvtFile")
    parser.add_option("-o", dest="adjFile")
    parser.add_option("-h", dest="showHelp", action="store_true", default=False)
    parser.add_option("-v", dest="showVerb", action="store_true", default=False)
    options, _ = parser.parse_args()

    if options.showHelp:
        usage()
        sys.exit(-1)

    objImg = sitk.ReadImage(options.imgFile)
    cvtImg = sitk.ReadImage(options.cvtFile)

    thinFilter = sitk.BinaryThinningImageFilter()
    thinnedImg = thinFilter.Execute(objImg)

    imgMat = sitk.GetArrayFromImage(thinnedImg)
    cntLst, _ = cv.findContours(imgMat, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

    cellMat = sitk.GetArrayFromImage(cvtImg)
    cellIds = np.unique(cellMat)
    numCell = len(cellIds)

    if options.showVerb:
        print "%d CVT cells" % numCell

    adjMat = np.zeros((numCell, numCell))
    cntMat = np.zeros(imgMat.shape, np.uint8)

    for cnt  in cntLst:
        for i in range(1, len(cnt)):
            (iBeg, jBeg) = cnt[i-1][0]
            (iEnd, jEnd) = cnt[i][0]

            # coordinate switch (skeleton x,y = iamge y,x)
            cBeg = cellMat[jBeg][iBeg]
            cEnd = cellMat[jEnd][iEnd]
            if cBeg != cEnd:
                adjMat[cBeg-1][cEnd-1] += 1

            if options.showVerb:
                cv.line(cntMat,
                        (iBeg, jBeg),
                        (iEnd, jEnd),
                        [255],1,cv.CV_AA)

    if options.showVerb:
        cv.imshow("Debug", cntMat)
        print "press any key to continue ..."
        raw_input()
        cv.destroyAllWindows()

    np.savetxt(options.adjFile, adjMat, delimiter=' ', fmt='%d')


if __name__ == "__main__":
    sys.exit(main())