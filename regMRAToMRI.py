"""regMRAToMRI.py
"""


__license__ = "Apache License, Version 2.0"
__author__  = "Roland Kwitt, Kitware Inc., 2013"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"



import os
import sys
import subprocess
from optparse import OptionParser
from core import regtools
import pickle


def usage():
    """Print usage information"""
    print("""
Run a RIGID registration between MRA and MRI images (in a
pairwise manner).


USAGE:
    {0} [OPTIONS]
    {0} -h

OPTIONS (Overview):

    -l FILE0 FILE1
    -d FILE0 FILE1
    -c FILE
    -x

OPTIONS (Detailed):

    -x

    Set this flag to FORCE the recomputation of all intermediate
    results.

    -c FILE

    FILE is a configuration FILE in JSON format that contains the
    absolute path's to all binaries that are used during the
    registration process. For help, see the examplary configuration
    file config.json.example.

    -l FILE0 FILE1

    FILE0 is an ASCII file that contains the absolute path of
    each TARGET image, e.g.,

        /tmp/target1.mha
        /tmp/target2.mha
        ....

    FILE1 is an ASCII file that contains the absolute path of
    each MOVING image, e.g.,

        /tmp/moving1.mha
        /tmp/moving2.mha
        ....

    -d FILE0 FILE1

    Upon completion of the script, these files will contain
    lists of various files produced during the RIGID registration
    process. The format of these files is compatible with
    Python's pickle functionality.

    FILE0 will contain a list of all moving images, resampled
    in the space of the corresponding fixed image.

    FILE1 will contain a list of all RIGID transformation
    files that were generated during the registration process.

AUTHOR: Roland Kwitt, Kitware Inc., 2013
        (roland.kwitt@kitware.com)
""".format(sys.argv[0]))


if __name__ == "__main__":
    parser = OptionParser(add_help_option=False)
    parser.add_option("-d", dest="dFiles", action="store", nargs=2)
    parser.add_option("-l", dest="lFiles", action="store", nargs=2)
    parser.add_option("-h", dest="doHelp", action="store_true", default=False)
    parser.add_option("-x", dest="recomp", action="store_true", default=False)
    parser.add_option("-c", dest="config")
    options, args = parser.parse_args()

    if options.doHelp:
        usage()
        sys.exit(-1)

    if (options.lFiles is None or
        options.dFiles is None or
        options.config is None):
        usage()
        sys.exit(-1)

    helper = regtools.regtools(options.config)

    tListFile, mListFile = options.lFiles
    iListFile, xListFile = options.dFiles

    tList = open(tListFile).readlines()
    mList = open(mListFile).readlines()
    tList = [c.strip() for c in tList]
    mList = [c.strip() for c in mList]

    # register moving images to target images (pairwise)
    iFileList, xFileList  = helper.rReg2(tList,
                                         mList,
                                         "RigidMRAToMRI",
                                         options.recomp)
    # dump the list files to HDD
    pickle.dump(iFileList, open(iListFile, "w"))
    pickle.dump(xFileList, open(xListFile, "w"))