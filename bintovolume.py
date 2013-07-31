"""bintovolume.py
"""


__license__ = "Apache License, Version 2.0"
__author__  = "Roland Kwitt, Kitware Inc., 2013"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"


from optparse import OptionParser
import SimpleITK as sitk
import numpy as np
import sys


def usage():
    """Print usage information"""
    print("""
Take a binary file with float values and reshape the data into a 3D image that
is readable by Slicer for instance.

    USAGE:
        {0} [OPTIONS]
        {0} -h

    OPTIONS (Overview):

        -i FILE
        -o FILE
        -s NUM NUM NUM

    OPTIONS (Detailed):

        -i FILE

        FILE is the filename of the input file (in binary format, float32).

        -o FILE

        FILE is the filename of the output image file.

        -s NUM NUM NUM

        Specifies the x,y,z dimensions to reshape the binary data (int).

AUTHOR: Roland Kwitt, Kitware Inc., 2013
        roland.kwitt@kitware.com
""".format(sys.argv[0]))


parser = OptionParser(add_help_option=False)
parser.add_option("-i", dest="binFile")
parser.add_option("-o", dest="outFile")
parser.add_option("-s", dest="reshape", nargs=3)
parser.add_option("-h", dest="useHelp", action="store_true", default=False)
options, _ = parser.parse_args()

if options.useHelp:
    usage()
    sys.exit(-1)

if (options.outFile is None or
    options.binFile is None or
    options.reshape is None):
    usage()
    sys.exit(-1)

dstShape = [int(x) for x in options.reshape]
data = np.fromfile(options.binFile,dtype=np.float32)
data = data.reshape(dstShape)

im = sitk.GetImageFromArray(data)
sitk.WriteImage(im, options.outFile)
