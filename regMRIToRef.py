"""regMRItoRef.py
"""


__license__ = "Apache License, Version 2.0"
__author__  = "Roland Kwitt, Kitware Inc., 2013"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"


import os
import sys
import time
import Queue
import pickle
import signal
import subprocess
import numpy as np
from core import regtools
import multiprocessing as mp
from optparse import OptionParser
from itertools import izip_longest


def usage():
    """Print usage information"""
    print("""
Run ANTS registration for a collection of moving images to ONE reference image.

USAGE:
    {0} [OPTIONS]
    {0} -h

OPTIONS (Overview):

    -l FILE
    -c FILE
    -t FILE
    -d FILE0 FILE1 FILE2 FILE3
    -f [0,1]
    -x

OPTIONS (Detailed):

    -f [0,1]

    Specify the fraction of CPU's to use. Depending on that setting, the list
    of moving images is split and ANTS registration is run in parallel.

    -c FILE

    FILE is a configuration FILE in JSON format that contains the absolute
    path's to all binaries that are used during the registration process. For
    help, see the examplary configuration file config.json.example.

    -x

    Set this flag to FORCE the recomputation of all intermediate results.

    -l FILE

    FILE is an ASCII file that contains the absolute path of each moving
    image, e.g.,

        /tmp/image1.mha
        /tmp/image2.mha
        ....

    -t FILE

    Absolute path the the reference image to which all moving images are
    registered to.

    -d FILE0 FILE1 FILE2 FILE3

    Upon completion of the script, these files will contain lists of various
    files produced during the ANTS registration process. The format of these
    files iscompatible with Python's pickle functionality.

    FILE0 will contain a list of all affine transformations that were computed
    to align the i-th moving image with the reference image.

    FILE1 will contain a list of FORWARD deformation fields that were computed
    to deformably register the (already affinely) aligned moving images to the
    reference image. These vector fields can be used to resample the moving
    image in the space of the reference image.

    FILE2 will contain exactly the INVERSE of the deformation fields. These
    vector fields are usually used either to do the inverse mapping or to
    transform spatial objects, e.g., tubes from the space of the moving images
    into the space of the reference image.

    FILE3 will contain a list of warped moving images (in the space of the
    reference image) that have been generated by 1) aligning the i-th moving
    image with the reference image using the affine transforms and 2) applying
    the FORWARD deformation field.

AUTHOR: Roland Kwitt, Kitware Inc., 2013
        roland.kwitt@kitware.com
""".format(sys.argv[0]))


class ANTSWorker(mp.Process):
    """ANTS registration worker class.
    """

    def __init__(self, wrkQ, resQ, opts):
        mp.Process.__init__(self)
        self.wrkQ = wrkQ
        self.resQ = resQ
        self.opts = opts
        self.kill = False

    def run(self):
        while not self.kill:
            try:
                job = self.wrkQ.get_nowait()
            except Queue.Empty:
                break

            movLst = self.opts["movLst"]
            refImg = self.opts["refImg"]
            recomp = self.opts["recomp"]
            jobIdx = self.opts["jobIdx"]

            lists = helper.antsReg(movLst, refImg, recomp)
            self.resQ.put((jobIdx, lists))


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.

    Parameters
    ----------

    iterable: iterable
        Any of Python's iterables

    n : int
        Chunk size

    fillvalue: any value (default: None)
        The value to use to pad lists which are not exactly
        equal to the chunk size.

    Returns
    -------

    chunks : see izip_longest documentation
    """
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


def computeChunkSize(movLst, useFrac=0.5):
    """Compute the size of chunks to process by the worker.

    Parameters
    ----------

    movLst : list
        List of moving image file names

    useFrac: float (default: 0.5)
        Fraction of CPU's to use

    Returns
    -------

    chunkSize : int
        Size of the largest chunk (sublist) to process
    """
    nProc = mp.cpu_count() * useFrac
    return np.floor(len(movLst) / nProc).astype(int)


if __name__ == "__main__":
    parser = OptionParser(add_help_option=False)
    parser.add_option("-l", dest="lFiles")
    parser.add_option("-c", dest="config")
    parser.add_option("-t", dest="refImg")
    parser.add_option("-h", dest="doHelp", action="store_true", default=False)
    parser.add_option("-x", dest="recomp", action="store_true", default=False)
    parser.add_option("-f", dest="cpuUse", type="float", default=0.5)
    parser.add_option("-d", dest="dFiles", action="store", nargs=4)
    options, args = parser.parse_args()

    if options.doHelp:
        usage()
        sys.exit(-1)

    if (options.lFiles is None or
        options.config is None or
        options.dFiles is None or
        options.refImg is None) :
        usage()
        sys.exit(-1)

    helper = regtools.regtools(options.config)

    mList = open(options.lFiles).readlines()
    mList = [c.strip() for c in mList]
    listN = len(mList)

    wrkQ = mp.Queue()
    resQ = mp.Queue()

    blks = list(grouper(range(listN), computeChunkSize(mList, options.cpuUse)))
    for job in range(len(blks)):
        wrkQ.put(job)

    for cnt, b in enumerate(blks):
        idx = filter(lambda x: x is not None, b)
        opt = dict(movLst=[mList[j] for j in idx],
                   jobIdx=cnt,
                   refImg=options.refImg,
                   recomp=options.recomp)
        worker = ANTSWorker(wrkQ, resQ, opt)
        worker.start()

    results = dict()
    for i in range(len(list(blks))):
        wRes = resQ.get()
        results[wRes[0]] = wRes[1]

    affTfmList = [] # list of affine transforms
    fwdDefList = [] # list of forward deformation fields
    invDefList = [] # list of inverse deformation fields

    for k in sorted(results.iterkeys()):
        affTfmList.extend(results[k][0])
        fwdDefList.extend(results[k][1])
        invDefList.extend(results[k][2])

    helper.infoMsg("resampling images ...")
    imgDefList = helper.antsMap(mList,
                               options.refImg,
                               affTfmList,
                               fwdDefList,
                               options.recomp)

    #Write output lists to HDD
    affTfmListFile, fwdDefListFile, invDefListFile, imgDefListFile = options.dFiles
    pickle.dump(affTfmList, open(affTfmListFile, "w"))
    pickle.dump(fwdDefList, open(fwdDefListFile, "w"))
    pickle.dump(invDefList, open(invDefListFile, "w"))
    pickle.dump(imgDefList, open(imgDefListFile, "w"))
