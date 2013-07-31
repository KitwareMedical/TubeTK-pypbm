#!/bin/bash

################################################################################
# Modify to match your system configuration
################################################################################
CONVERT="/usr/local/bin/convert"
PYTHON="/opt/local/bin/python2"
SCRIPT="/Users/rkwitt/Remote/pypbm/controlpoints.py"

usage="$(basename "$0") [-t FILE] [-g FILE] [-n NUM]

Generate population individuals from template

where:
  -h  shows this help
  -t  specify template image
  -g  specify grid image
  -n  specify number of individuals

Author: Roland Kwitt, Kitware Inc, 2013"

while getopts ':hs:t:g:n:' option; do
  case "$option" in
    h) echo "$usage"
       exit
       ;;
    g) GIMG=$OPTARG
       ;;
    t) TIMG=$OPTARG
       ;;
    n) NIND=$OPTARG
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

for i in `seq 1 ${NIND}`; do
  NUM=`printf "%.4d" $i`
  CMD="${PYTHON} \
       ${SCRIPT} -W 256 -H 256 -r 5 -n 10 -o Image-${NUM}.cp"
  echo $CMD
  $CMD

  CMD="${CONVERT} \
       -alpha set \
       -virtual-pixel white \
       -distort Shepards @Image-${NUM}.cp \
       -resize 256x256! \
       ${TIMG} \
       Image-${NUM}.png"
  echo $CMD
  $CMD

  CMD="${CONVERT} \
       -alpha set \
       -virtual-pixel white \
       -distort Shepards @Image-${NUM}.cp \
       -resize 256x256! \
       ${GIMG} \
       Grid-${NUM}.png"
  echo $CMD
  $CMD
done
