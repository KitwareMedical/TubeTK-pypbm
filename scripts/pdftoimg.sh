#!/bin/bash

################################################################################
# Convert all pdf files in a directory to PNG images (256 x 256) without
# keeping the aspect ratio!
################################################################################

for f in `find . -name 'i*.pdf'`; do
    BASE=`basename $f .pdf`
    DIRN=`dirname $f`
    CMD="convert $f -trim -resize 256x256\! ${DIRN}/${BASE}.png"
    echo $CMD
    $CMD
done
