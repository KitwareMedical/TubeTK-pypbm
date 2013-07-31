"""chstr.py
"""

__author__ = "Roland Kwitt, Kitware Inc., 2013"
__email__ = "roland.kwitt@kitware.com"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"


from optparse import OptionParser
import pickle
import os
import sys

def usage():
    """Print usage information"""
    print("""
Reads a pickled Python list, replaces a string and writes the list back to disk.

    USAGE:
        {0} [OPTIONS]
        {0} -h

    OPTIONS (Overview):

        -i FILE
        -s STR
        -r STR

    OPTIONS (Detailed):

        -i FILE

        FILE is the filename of the pickled list.

        -s STR

        STR is the search string.

        -r STR

        STR is the string to replace the search string with.

AUTHOR: Roland Kwitt, Kitware Inc., 2013
        roland.kwitt@kitware.com
""".format(sys.argv[0]))


def main(argv=None):
    if argv is None:
        argv=sys.argv

    parser = OptionParser(add_help_option=False)
    parser.add_option("-i", dest="inList")
    parser.add_option("-c", dest="sStr")
    parser.add_option("-a", dest="rStr")
    parser.add_option("-h", dest="doHelp", action="store_true", default=False)
    options, _ = parser.parse_args()

    if options.doHelp:
        usage()
        sys.exit(-1)

    inFile = options.inFile
    sStr = options.sStr
    rStr = options.rStr

    data = pickle.load(open(inFile))
    for i, p in enumerate(data):
        data[i] = p.replace(sStr, rStr)
    pickle.dump(data, open(inFile, "w"))


if __name__ == "__main__":
    sys.exit(main())
