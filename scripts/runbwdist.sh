#!/bin/bash

################################################################################
# Modify the following lines to match your system configuration
################################################################################
SCRIPT='/Users/rkwitt/Remote/pypbm/utils/dmap.py'
PYTHON='/opt/local/bin/python2'

usage="$(basename "$0") [-l FILE] [-h]

Runs bwdist.py on a all images in a list.

where:
  -h  shows this help
  -l  specify the image list

Example:

  List file list.txt has contents:

  /tmp/img1.png
  /tmp/img2.png

  Then, running

  $ ./runbwdist.sh -l list.txt

  produces

  /tmp/img1-Den.tiff
  /tmp/img2-Den.tiff

Author: Roland Kwitt, Kitware Inc, 2013"

while getopts ':hl:' option; do
  case "$option" in
    h) echo "$usage"
       exit
       ;;
    l) LIST=$OPTARG
       ;;
    :) printf "missing argument for -%s\n" "$OPTARG" >&2
       echo "$usage" >&2
       exit 1
       ;;
   \?) printf "illegal option: -%s\n" "$OPTARG" >&2
       echo "$usage" >&2
       exit 1
       ;;
  esac
done
shift $((OPTIND - 1))


for f in `cat ${LIST}`; do
    BASE=`basename $f .png`
    DIRN=$2
    CMD="${PYTHON} ${SCRIPT} ${DIRN}/$f ${DIRN}/${BASE}-Den.tiff 0"
    echo $CMD
    $CMD
done
