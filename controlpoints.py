"""controlpoints.py
"""


__license__ = "Apache License, Version 2.0"
__author__  = "Roland Kwitt, Kitware Inc., 2013"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"


from optparse import OptionParser
import numpy as np
import sys
import os


def usage():
    """Print usage information"""
    print("""
Compute a collection of control points that can be input to ImageMagick's
convert to deform an image. The control points define a mapping (x,y) ->
(x',y'), i.e., point (x,y) is moved to (x',y'). Depending on what type
of distortion is used with ImageMagick (e.g., Shepards), the rest of the
displacements is interpolated. NOTE: The displacements are chosen as
random vectors (i.e., random angle + radi).

    USAGE:
        {0} [OPTIONS]
        {0} -h

    OPTIONS (Overview):

        -W NUM
        -H NUM
        -n NUM
        -r NUM
        -o FILE

    OPTIONS (Detailed):

        -W NUM

        Image width.

        -H NUM

        Image height.

        -n NUM (default: 5)

        Number of control points (along each direction). Hence the total
        number of control points will be N**2.

        -r NUM (default: 1)

        Maximum displacement radius.

        -o FILE

        FILE is the output filename where to write the control point
        displacements to.

    EXAMPLE:

        Assume we have a 100x100 image img.png. We create a 25 control points
        evenly distributed over the image and then distort the image:

        $ py controlpoints -W 100 -H 100 -n 5 -r 5 -o cp.txt
        $ convert -alpha set -virtual-pixel white -distort Shepards '@cp.txt' \\
          img.png img-distorted.png

AUTHOR: Roland Kwitt, Kitware Inc., 2013
        roland.kwitt@kitware.com
""".format(sys.argv[0]))


def main(argv=None):
    if argv is None:
        argv=sys.argv

    parser = OptionParser(add_help_option=False)
    parser.add_option("-W", dest="imW", type="int")
    parser.add_option("-H", dest="imH", type="float")
    parser.add_option("-o", dest="outF")
    parser.add_option("-n", dest="maxN", type="int", default=5)
    parser.add_option("-r", dest="maxR", type="int", default=1)
    parser.add_option("-h", dest="doHelp", action="store_true", default=False)
    options, _ = parser.parse_args()

    if options.doHelp:
        usage()
        sys.exit(-1)

    w = options.imW
    h = options.imH
    N = options.maxN
    maxR = options.maxR
    outF = options.outF

    wMin, wMax = maxR, w-maxR
    hMin, hMax = maxR, h-maxR

    px = np.round(np.linspace(wMin, wMax, N, endpoint=False))
    py = np.round(np.linspace(hMin, hMax, N, endpoint=False))
    xv, yv = np.meshgrid(px,py,  sparse=False, indexing='ij')

    cList = []
    for i in range(len(xv)):
        for j in range(len(yv)):
            cList.append((xv[i,j],yv[j,j]))

    nPoints = len(cList)

    rad = np.random.randint(1, maxR, nPoints)
    phi = np.random.uniform(0, 1, nPoints)*np.pi*2

    dList = [(np.round(np.cos(phi[i])*rad[i]),
              np.round(np.sin(phi[i])*rad[i])) for i in range(nPoints)]

    fid = open(outF,'w')
    for i in range(nPoints):
        px, py = cList[i]
        dx, dy = dList[i]
        qx, qy = px+dx, py+dy
        fid.write("%d %d %d %d\n" % (px, py, qx, qy))
    fid.close()


if __name__ == "__main__":
    sys.exit(main())