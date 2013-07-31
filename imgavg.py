"""imgavg.py
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


def usage():
    """Print usage information"""
    print("""
Take a file with a list of images and output the mean image.

    USAGE:
        {0} [OPTIONS]
        {0} -h

    OPTIONS (Overview):

        -l FILE
        -o FILE

    OPTIONS (Detailed):

        -l FILE

        FILE is the list of input images (absolute paths).

        -o FILE

        FILE is the generated output image.

AUTHOR: Roland Kwitt, Kitware Inc., 2013
        roland.kwitt@kitware.com
""".format(sys.argv[0]))


def main(argv=None):
    if argv is None:
        argv=sys.argv

    parser = OptionParser(add_help_option=False)
    parser.add_option("-l", dest="inList")
    parser.add_option("-o", dest="outImg")
    parser.add_option("-h", dest="doHelp", action="store_true", default=False)
    options, _ = parser.parse_args()

    if options.doHelp:
        usage()
        sys.exit(-1)

    inList = options.inList
    outImg = options.outImg

    with open(inList) as fid:
        lines = fid.readlines()

    avg = None
    for l in lines:
        img = sitk.ReadImage(l.rstrip())
        dat = sitk.GetArrayFromImage(img).astype('float32')
        if avg is None:
            avg = dat
        avg += dat

    avg = avg * 1.0/len(lines)
    atl = sitk.GetImageFromArray(avg)
    sitk.WriteImage(atl, outImg)


if __name__ == "__main__":
    sys.exit(main())