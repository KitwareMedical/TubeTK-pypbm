#!/bin/bash

################################################################################
# Modify the next line to match your system configuration
################################################################################
TUBESTODENSITYIMAGEBIN="/Users/rkwitt/Kitware/TubeTK/Build/TubeTK-Build/bin/TubesToDensityImage"

usage="$(basename "$0") [-l FILE] [-h]

Runs TubeTK's TubesToDensityImage on a set of .tre files (given a reference)

where:
  -h  shows this help
  -l  specify the list of .tre files
  -r  specify the reference image

Example:

  List file list.txt has contents (NOTE: absolute path):

  /tmp/x0.tre
  /tmp/x1.tre

  Then, running

  $ ./runskeltrace.sh -l list.txt -c atlas.png -b /tmp/

  runs skeleton tracing on images /tmp/img0.png and /tmp/img1.png using
  the tessellation image atlas.png and produces

  /tmp/img1-atlas.mat
  /tmp/img2-atlas.mat

Author: Roland Kwitt, Kitware Inc, 2013"


for f in `cat $1`; do
  BASE=`basename $f .tre`
  DIR=`dirname $f`
  DENIMAGE="${DIR}/${BASE}-Den.mha"
  RADIMAGE="${DIR}/${BASE}-Rad.mha"
  TANIMAGE="${DIR}/${BASE}-Tan.mha"
  CMD="${TUBESTODENSITYIMAGEBIN} ${f} ${DENIMAGE} ${RADIMAGE} ${TANIMAGE} \
       --inputTemplateImage $2"
  $CMD
done
