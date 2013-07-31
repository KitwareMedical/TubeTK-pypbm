#!/bin/bash

################################################################################
# Modify the following lines to match your system configuration
################################################################################
SCRIPT='/Users/rkwitt/Remote/pypbm/skeltrace.py'
PYTHON='/opt/local/bin/python2'

usage="$(basename "$0") [-l FILE] [-h]

Runs skeltrace.py on a all images in a list (for a given image tessellation)

where:
  -h  shows this help
  -l  specify the image list
  -c  specify the image tessellation
  -b  specify the base directory image the images

Example:

  List file list.txt has contents (NOTE: relative path):

  img0.png
  img0.png

  Then, running

  $ ./runskeltrace.sh -l list.txt -c atlas.png -b /tmp/

  runs skeleton tracing on images /tmp/img0.png and /tmp/img1.png using
  the tessellation image atlas.png and produces

  /tmp/img1-atlas.mat
  /tmp/img2-atlas.mat

Author: Roland Kwitt, Kitware Inc, 2013"

while getopts ':hl:c:b:' option; do
  case "$option" in
    h) echo "$usage"
       exit
       ;;
    l) LIST=$OPTARG
       ;;
    c) CIMG=$OPTARG
       ;;
    b) BASE=$OPTARG
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
    NOPREFIX_FIMG=`basename $f .png`
    NOPREFIX_CIMG=`basename ${CIMG} .png`
    CMD="${PYTHON} ${SCRIPT} \
      -i ${BASE}/$f \
      -c ${CIMG} \
      -o \${BASE}/${NOPREFIX_FIMG}-${PREF}.mat"
    echo $CMD
    #$CMD
done
