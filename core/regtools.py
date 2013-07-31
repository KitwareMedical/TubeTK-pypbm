"""regTools.py

Class with helper routines for image registration.
"""


__author__ = "Roland Kwitt, Kitware Inc., 2013"
__email__ = "roland.kwitt@kitware.com"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"


from termcolor import colored
import SimpleITK as sitk
import numpy as np
import subprocess
import itertools
import json
import sys
import os


class regtools:
    """Registration tools.
    """

    def failMsg(self, msgText):
        self.__msg(msgText, "fail")


    def warnMsg(self, msgText):
        self._msg(msgText, "warn")


    def infoMsg(self, msgText):
        self.__msg(msgText, "info")


    def __msg(self, msgText, level="info"):
        """Write color message.
        """
        levelText = "[" + level + "]: "
        message = {
            "info" : colored(levelText + msgText, 'green'),
            "warn" : colored(levelText + msgText, 'blue'),
            "fail" : colored(levelText + msgText, 'red')
        }[level]
        print message


    def __init__(self, configFile):
        """Initialization (read config).
        """
        self.__config = json.load(open(configFile))


    def flipAxis(self, imgList, selector=None, force=False):
        """Flip axis in images.
        """
        if selector is None:
            return imgList
        pass

        L = []
        for f in imgList:
            woExt, ext = os.path.splitext(f)
            imgFlipped = woExt + "-%sFlipped" % selector + ext

            # compose command
            cmd = [self.__config["c3d"],
                   "%s" % f, "-flip", selector, "-o", imgFlipped]
            # unless we force, do NOT execute the command if file exists
            if not os.path.exists(imgFlipped) or force:
                self.infoMsg("file=%s, flipping %s axis ..." % (f, selector))
                subprocess.call(cmd)
            L.append(imgFlipped)
        return L


    def aReg(self, imgList, tImg, tfmName, force=False):
        """Affine registration.
        """
        L = []
        T = []
        for f in imgList:
            woExt, ext = os.path.splitext(f)
            imgReg = woExt + "-" + tfmName + ext
            imgTfm = woExt + "-" + tfmName + ".tfm"

            # compose registration command (using Slicer's BRAINSFit)
            cmd =[self.__config["BRAINSFit"],
                  "--movingVolume %s" % f,
                  "--fixedVolume %s" % tImg,
                  "--outputVolume %s" % imgReg,
                  "--linearTransform %s" % imgTfm,
                  "--useAffine",
                  "--initializeTransformMode useCenterOfHeadAlign"]

            # do NOT execute unless forced or file does NOT exist
            if not os.path.exists(imgReg) or force:
                self.infoMsg("affine registration of %s to %s ..." % (f, tImg))
                subprocess.call(cmd)
            L.append(imgReg)
            T.append(imgTfm)
        return L, T


    def rReg(self, imgList, tImg, tfmName, force=False):
        """Rigid registration.
        """
        L = []
        T = []
        for f in imgList:
            woExt, ext = os.path.splitext(f)
            imgReg = woExt + "-" + tfmName + ext
            imgTfm = woExt + "-" + tfmName + ".tfm"

            # compose registration command (using Slicer's BRAINSFit)
            cmd =[self.__config["BRAINSFit"],
                  "--movingVolume %s" % f,
                  "--fixedVolume %s" % tImg,
                  "--outputVolume %s" % imgReg,
                  "--linearTransform %s" % imgTfm,
                  "--useRigid",
                  "--initializeTransformMode useCenterOfHeadAlign"]

            # do NOT execute unless forced or file does NOT exist
            if not os.path.exists(imgReg) or force:
                self.infoMsg("rigid registration of %s to %s ..." % (f, tImg))
                subprocess.call(cmd)
            L.append(imgReg)
            T.append(imgTfm)
        return L, T


    def antsReg(self, movList, tImg, smoothDispField=0, force=False):
        """ANTS deformable registration to template.
        """
        affTfmList = [] # Affine part of the registration
        fwdDefList = [] # Deformation field part of the registration
        invDefList = [] # Moving images resampled in template space
        for f in movList:
            inpath = os.path.dirname(f)

            cmd =[self.__config["ANTS"],
                  "3",
                  "-m", "PR[%s,%s,1,4]" % (tImg, f),
                  "-t", "SyN[0.25]",
                  "-r", "Gauss[3,%d]" % smoothDispField,
                  "-o", "%s" % os.path.join(inpath,"ANTS"),
                  "-i", "30x90x20",
                  "--use-Histogram-Matching",
                  "--number-of-affine-iterations", "10000x10000x10000x10000x10000",
                  "--MI-option", "32x16000"]

            affFile = os.path.join(inpath,"ANTSAffine.txt");
            fwdDefF = os.path.join(inpath,"ANTSWarp.nii.gz")
            invDefF = os.path.join(inpath,"ANTSInverseWarp.nii.gz")

            if (not os.path.exists(affFile) or
                not os.path.exists(fwdDefF) or
                not os.path.exists(invDefF) or force):
                pass
                #print cmd
                #subprocess.call(cmd)

            affTfmList.append(affFile);
            fwdDefList.append(fwdDefF)
            invDefList.append(invDefF)
        return affTfmList, fwdDefList, invDefList


    def antsMap(self, movList, tImg, affTfmList, fwdDfmList, force=False):
        """Resample moving images in template space (FORWARD mapping).
        """
        assert len(movList) == len(affTfmList), 'Size mismatch!'
        if not fwdDfmList is None:
            assert len(movList) == len(fwdDfmList), 'Size mismatch!'

        regList = []
        for cnt, f in enumerate(movList):
            woExt, ext = os.path.splitext(movList[cnt])
            imgReg = woExt + "-ANTSDeformed" + ext

            cmd =[self.__config["WarpImageMultiTransform"],
                  "3",
                  movList[cnt],
                  imgReg,
                  fwdDfmList[cnt],
                  affTfmList[cnt],
                  "-R", tImg]

            if (not os.path.exists(imgReg) or force):
                subprocess.call(cmd)
            regList.append(imgReg)
        return regList


    def rReg2(self, fixList, movList, tfmName, force=False):
        """Rigid registration (pairwise).
        """
        assert len(fixList) == len(movList), "Size mismatch!"

        L = []
        T = []
        for cnt, fixIm in enumerate(fixList):
            woExt, ext = os.path.splitext(movList[cnt])
            imgReg = woExt + "-" + tfmName + ext
            imgTfm = woExt + "-" + tfmName + ".tfm"

            # compose registration command (using Slicer's BRAINSFit)
            cmd =[self.__config["BRAINSFit"],
                  "--movingVolume %s" % movList[cnt],
                  "--fixedVolume %s" % fixIm,
                  "--outputVolume %s" % imgReg,
                  "--linearTransform %s" % imgTfm,
                  "--useRigid",
                  "--initializeTransformMode useCenterOfHeadAlign"]

            # do NOT execute unless forced or file does NOT exist
            if not os.path.exists(imgReg) or force:
                self.infoMsg("rigid registration of %s to %s ..." % (movList[cnt], fixIm))
                subprocess.call(cmd)
            L.append(imgReg)
            T.append(imgTfm)
        return L, T


    def treeApplyTfm(self, vesselList, tfmList, tfmName, force=False):
        """Map vessels into the space of the reference images using transforms.
        """
        assert len(vesselList) == len(tfmList), "Size mismatch!"

        L=[]
        for cnt, vesselFile in enumerate(vesselList):
            woExt, ext = os.path.splitext(vesselFile)
            mappedVesselFile = woExt + "-" + tfmName + ext

            cmd = [self.__config["TubeTransform"],
                   vesselFile,
                   mappedVesselFile,
                   "--transformFile %s" % tfmList[cnt],
                   "--useInverseTransform"]

            if (not os.path.exists(mappedVesselFile) or force):
                self.infoMsg('apply transform %s to %s ...' % (tfmList[cnt], vesselFile))
                subprocess.call(cmd)
            L.append(mappedVesselFile)
        return L


    def treeApplyDfm(self, vesselList, dfmFile, dfmName, force=None):
        """Apply deformation field on vessel tree.
        """
        L=[]
        for cnt, vesselFile in enumerate(vesselList):
            woExt, ext = os.path.splitext(vesselFile)
            mappedVesselFile = woExt + "-" + dfmName + ext

            cmd = [self.__config["TubeTransform"],
                   vesselFile,
                   mappedVesselFile,
                   "--displacementField %s" % dfmFile[cnt]]

            if (not os.path.exists(mappedVesselFile) or force):
                self.infoMsg('apply deformation field %s on %s ...' % (dfmFile[cnt], vesselFile))
                subprocess.call(cmd)
            L.append(mappedVesselFile)
        return L


    def createTreeImage(self, vesselList, refList, force=False):
        """Compute binary image from extracted vessels.
        """
        assert len(vesselList) == len(refList), "Size mismatch!"

        L = []
        for cnt, treFile in enumerate(vesselList):
            woExt, ext = os.path.splitext(treFile)
            bIm = woExt + "-" + "Binary" + ".mha"

            cmd =[self.__config["TubesToImage"],
                  treFile, bIm, "--inputTemplateImage %s" % refList[cnt]]

            # do NOT execute unless forced or file does NOT exist
            if not os.path.exists(bIm) or force:
                self.infoMsg("vessel tree %s to binary image %s ..." % (treFile, bIm))
                subprocess.call(cmd)
            L.append(bIm)
        return L


    def applyTfm(self, imgList, imgTfms, tImg, tfmName, pixType="uchar", intp="Linear", force=False):
        """Apply image transform.
        """
        assert len(imgList) == len(imgTfms), "Size mismatch!"

        L = []
        for cnt, f in enumerate(imgList):
            woExt, ext = os.path.splitext(f)
            imgReg = woExt + "-" + tfmName + ext
            imgTfm = imgTfms[cnt]

            cmd =[self.__config["BRAINSResample"],
                  "--inputVolume %s" % f,
                  "--referenceVolume %s" % tImg,
                  "--outputVolume %s" % imgReg,
                  "--pixelType %s" % pixType,
                  "--warpTransform %s" % imgTfm,
                  "--numberOfThreads %d" % -1,
                  "--interpolationMode %s" % intp]

            if not os.path.exists(imgReg) or force:
                subprocess.call(cmd)
            L.append(imgReg)
        return L


    def applyTfm2(self, imgList, refList, tfmList, tfmName, pixType="uchar", intp="Linear", force=False):
        """Apply image transforms (pairwise).
        """
        assert len(imgList) == len(refList) == len(tfmList), "Size mismatch!"

        L = []
        for cnt, f in enumerate(imgList):
            woExt, ext = os.path.splitext(f)
            imgReg = woExt + "-" + tfmName + ext # Filename of transformed image
            imgTfm = tfmList[cnt] # Transform to apply
            imgRef = refList[cnt] # Reference image

            cmd =[self.__config["BRAINSResample"],
                  "--inputVolume %s" % f,
                  "--referenceVolume %s" % imgRef,
                  "--outputVolume %s" % imgReg,
                  "--pixelType %s" % pixType,
                  "--warpTransform %s" % imgTfm,
                  "--numberOfThreads %d" % -1,
                  "--interpolationMode %s" % intp]

            if not os.path.exists(imgReg) or force:
                subprocess.call(cmd)
            L.append(imgReg)
        return L


    def remapLabels(self, imgList, mapFile, force=False):
        """Map labels according to custom label map.
        """

        mapInfo = json.load(open(mapFile))
        mapping =[]

        # build mapping string
        for key in mapInfo.keys():
            mapping.append(int(key))
            mapping.append(int(mapInfo[key]))

        L = []
        for f in imgList:
            woExt, ext = os.path.splitext(f)
            labImg = woExt + "-customMap" + ext

            mapList = [str(x) for x in mapping]
            cmd = [self.__config["c3d"], f, "-replace"]
            cmd.extend(mapList)
            cmd.extend(["-type", "uchar", "-o", labImg])
            subprocess.call(cmd)
            if not os.path.exists(labImg) or force:
                subprocess.call(cmd)
            L.append(labImg)
        return L


    def resample(self, imgList, fac=None, useNN=False, force=False):
        """Image resampling.
        """
        if fac is None:
            return imgList

        L = []
        for f in imgList:
            woExt, ext = os.path.splitext(f)
            resImg = woExt + "-Resampled-" + str(fac) + ext

            # compose command
            cmd =[self.__config["ResampleScalarVolume"], f,
                  "--spacing", ",".join([str(fac)]*3),
                  resImg]
            if useNN:
                cmd.append("--interpolation nearestNeighbor")
            if not os.path.exists(resImg) or force:
                self.infoMsg("file=%s, resampling with spacing=%.2f ..." % (f, fac))
                subprocess.call(cmd)
            L.append(resImg)
        return L
