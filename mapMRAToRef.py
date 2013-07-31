"""mapMRAToRef.py
"""


__license__ = "Apache License, Version 2.0"
__author__  = "Roland Kwitt, Kitware Inc., 2013"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"


import os
import sys
import pickle
import subprocess
from core import regtools
from optparse import OptionParser


def usage():
    """Print usage information"""
    print("""
Take a list of spatial object files in MRA space and map them into the space of
the reference image by 1) mapping the objects into the space of the corresponding
MRI images and 2) applying a combination of AFFINE transformation + deformation
field to map them into the reference image space.

USAGE:
    {0} [OPTIONS]
    {0} -h

OPTIONS (Overview):

    -l FILE
    -c FILE
    -t FILE
    -i FILE0 FILE1 FILE2 FILE3
    -x

OPTIONS (Detailed):

    -l FILE

    FILE should contain a list of absolute filenames of spatial object files
    (i.e., the vessel trees), e.g.,

        /tmp/vessels1.tre
        /tmp/vessels2.tre
        ...

    that will be mapped into the space of the reference image (specified as
    an argument to -t - see below).

    -c FILE

    FILE is a configuration FILE in JSON format that contains the absolute
    path's to all binaries that are used during the registration process.
    For help, see the examplary configuration file config.json.example.

    -x

    Set this flag to FORCE the recomputation of all intermediate results. Be
    careful with this option, since it might take a while to recompute all the
    results.

    -t FILE

    Absolute path the the reference image to which all moving images are
    registered to.

    -i FILE0 FILE1 FILE2 FILE3

    All files need to be in a format compatible with Python's pickle
    functionality to load lists.

    FILE0 should contain the list of all RIGID transformations that were
    produced when registering the MRA to the MRI images (during mapping of
    the spatial objects, the inverse of this transformation will be computed
    and applied).

    FILE1 should contain the list of all AFFINE transformations that were
    produced when registering MRI images to the reference image. These are
    usually the affine transformations that were produced during the ANTS
    registration process (during mapping of the spatial objects, the inverse
    of this transformation wil be computed and applied).

    FILE2 should contain the list of FORWARD deformation fiels that were
    produced during the ANTS registration process (MRI images to reference
    image). These deformation fields are usually used to resample the moving
    images (i.e., the MRI images in our case) into the space of the reference
    image (currently these deformation fields are UNUSED).

    FILE3 should contain the list of INVERSE deformation fields. These
    deformation fields are used to refine the mapping of the spatial objects
    (after applying the inverse affine transformations given in FILE2) in
    the reference image space.


AUTHOR: Roland Kwitt, Kitware Inc., 2013
        roland.kwitt@kitware.com
""".format(sys.argv[0]))



if __name__ == "__main__":
    parser = OptionParser(add_help_option=False)
    parser.add_option("-l", dest="vFiles")
    parser.add_option("-c", dest="config")
    parser.add_option("-t", dest="refImg")
    parser.add_option("-i", dest="tFiles", action="store", nargs=4)
    parser.add_option("-h", dest="doHelp", action="store_true", default=False)
    parser.add_option("-x", dest="recomp", action="store_true", default=False)
    options, args = parser.parse_args()

    if options.doHelp:
        usage()
        sys.exit(-1)

    if (options.vFiles is None or
        options.config is None or
        options.tFiles is None or
        options.refImg is None):
        usage()
        sys.exit(-1)

    helper = regtools.regtools(options.config)

    vesselFileList = options.vFiles
    vList0 = open(vesselFileList).readlines()
    vList0 = [c.strip() for c in vList0]

    T0ListFile, T1ListFile, FDListFile, IDListFile = options.tFiles
    T0 = pickle.load(open(T0ListFile))
    T1 = pickle.load(open(T1ListFile))
    FD = pickle.load(open(FDListFile))
    ID = pickle.load(open(IDListFile))

    vList1 = helper.treeApplyTfm(vList0, T0, "RigidMRAToMRI",  options.recomp)
    vList2 = helper.treeApplyTfm(vList1, T1, "AffineMRIToRef", options.recomp)
    vList3 = helper.treeApplyDfm(vList2, ID, "DeformRefToRef", options.recomp)

    helper.createTreeImage(vList3,
                           [options.refImg]*len(vList3),
                           options.recomp)
