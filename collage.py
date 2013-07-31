"""collage.py
"""

__license__ = "Apache License, Version 2.0"
__author__  = "Roland Kwitt, Kitware Inc., 2013"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"


from optparse import OptionParser
import matplotlib.pylab as lab
import numpy as np
import sys
import os


def usage():
    """Print usage information"""
    print("""
Take a file with a list of 2D images that have been written out as a vector
in binary format and build a collage of those images (horizontally). A JET
colormap is used and the color axis is chosen such that all images have the
same scale.

    USAGE:
        {0} [OPTIONS]
        {0} -h

    OPTIONS (Overview):

        -l FILE
        -o FILE
        -b DIR

    OPTIONS (Detailed):

        -l FILE

        FILE is the list of input images.

        -o FILE

        FILE is the generated output image collage.

        -b DIR

        DIR is the base directory of the images.

    EXAMPLE:

        Asssume in MATLAB you processed an image and wrote the image out as
        follows (float values):

        > img = imread('img.png');
        > res = processImage(img);
        > fid = fopen('/tmp/result.bin', 'w');
        > fwrite(fid, res(:), 'float32');
        > fclose(fid)

        Next, you want to make a collage (with just one image :) using the
        script; first, we generate a list file img.list which contains

        result.bin

        and then call the script as follows:

        $ py collage -l img.list -b /tmp/ -o /tmp/collage.png

        This will generate the image /tmp/collage.png with just one image
        (using a jet colormap).

AUTHOR: Roland Kwitt, Kitware Inc., 2013
        roland.kwitt@kitware.com
""".format(sys.argv[0]))


def main(argv=None):
    if argv is None:
        argv=sys.argv

    parser = OptionParser(add_help_option=False)
    parser.add_option("-l", dest="inList")
    parser.add_option("-b", dest="inBase")
    parser.add_option("-o", dest="outImg")
    parser.add_option("-h", dest="doHelp", action="store_true", default=False)
    options, _ = parser.parse_args()

    if options.doHelp:
        usage()
        sys.exit(-1)

    inBase = options.inBase
    inList = options.inList
    outImg = options.outImg

    with open(inList) as fid:
        lines = fid.readlines()

    data = []
    for l in lines:
        imgName = os.path.join(inBase, l.rstrip())
        basName, ext = os.path.splitext(l.rstrip())
        img = np.fromfile(imgName, dtype=np.float32)
        data.append(img)


    maxVals = [np.amax(x.ravel()) for x in data]
    minVals = [np.amin(x.ravel()) for x in data]
    amax = np.amax(maxVals)
    amin = np.amin(minVals)

    for cnt, x in enumerate(data):
        subplotId = "1" + str(len(data)) + str(cnt+1)
        lab.subplot(subplotId)
        lab.imshow(x.reshape((256,256)).T, cmap=lab.cm.jet)
        lab.clim(amin, amax)
        lab.axis('Off')

    lab.savefig(outImg, bbox_inches='tight')


if __name__ == "__main__":
    sys.exit(main())