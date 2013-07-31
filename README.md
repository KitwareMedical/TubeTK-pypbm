Python Pattern Based Morphometry
================================

pypbm implements a set of tools to study population differences in vasculature using ideas from the field 
of (pattern-based) brain morphometry.

## Contents
- [What problem are we trying to solve](#problemstatement)
- [Requirements](#requirements)
- [References](#references)
- [Example (Toy Data)](#toyexample)
- [Example (Clinical Data)](#clinicalexample)
- [Using the convenience scripts](#conveniencescripts)


<a name="problemstatement"/>
What problem are we trying to solve ?
-------------------------------------

Lets assume we have vascular networks (e.g., intra-cranial vasculature)
extracted from a set of patients in a centerline + radius representation.
Such data could be obtained for instance from MRA images by means of
vessel extraction in a semi-supervised way. In many cases, structural MR
images are also available. A freely available dataset of that kind is
available [here](http://midas3.kitware.com/midas/folder/8051) for instance.

Now, given a specific attribute (e.g., age, gender, disease type etc.) we
could group all of the images by that attribute and thus obtain multiple
populations (e.g., male vs. female). One question of interest could then
be to ask if there are differences in the vasculature architecture of both
populations (e.g., are vessels missing, are there different connections,
etc.).

Traditionally, such questions have been assessed in the context of changes
that manifest as changes in the appearance of structural MR images of the
brain. This field of research is usually referred to as *brain morphometry*
and a variety of approaches have been proposed in that context with
*voxel-based morphometry (VBM)* being the most prominent one. **pypbm**
implements a collection of tools that can be used to study exactly the
problem of population differences for **vasculature**, so it could be
referred to as a toolbox for *vascular morphometry*.

<a name="requirements"/>
Requirements
------------

To run all of the code included in pypbm, the following software packages are
required:

1. **MATLAB**:
  1. [KSVD Toolbox (available from R. Rubinstein's
     webpage)](http://www.cs.technion.ac.il/~ronrubin/software.html)
  2. [Nino Shervashidze's graph kernel MATLAB
     code](http://mlcb.is.tuebingen.mpg.de/Mitarbeiter/Nino/Graphkernels/)
2. [**SimpleITK**](http://www.simpleitk.org) (incl. Python wrapping)
3. [**OpenCV**](http://opencv.willowgarage.com/wiki/) (incl. Python wrapping, recommended: v2.4.2)
4. [**ANTS**](http://stnava.github.io/ANTs/) (for image registration)
5. [**TubeTK**](http://public.kitware.com/Wiki/TubeTK)
6. [**numpy**](http://www.numpy.org)
7. [**scipy**](http://www.scipy.org)
8. [**matplotlib**](http://www.matplotlib.org)

To test if the Python wrappings for **OpenCV** and **SimpleITK** are working,
type

```python
import SimpleITK as sitk
import cv2
```

in a Python console. If no error occurs, you are ready to go. For the KSVD
MATLAB toolbox, please follow the instructions contained in the package (i.e.,
MEX file compilation, etc.). The same holds for SimpleITK, ANTS and OpenCV.

<a name="references"/>
References
----------

For the general idea of pattern-based morphometry (upon which a large part
of pypbm is based) please cite:

```bibtex
@inproceedings{Gaonkar11a,
    author    = {B.~Gaonkar and K.~Pohl and C.~Davatzikos},
    title     = {Pattern based morphometry},
    booktitle = {MICCAI}}
    year      = {2011}}
```

The idea of encoding intra-cranial vasculature in the form of spatial-graphs
was originally proposed in:

```bibtex
@inproceedings{Aylward05a,
  title     = {Spatial graphs for intra-cranial vascular network characterization, generation, and discrimination}
  author    = {S.~Aylward and J.~Jomier and C.~Vivert and V.~LeDigarcher and E.~Bullit},
  booktitle = {MICCAI},
  year      = {2005}}
```

The concept of using graph-kernel based machine learning to test the hypothesis
of global population differences in the architecture of spatial-graphs was recently
introduced in:

```bibtex
@inproceedings{Kwitt13a,
  title     = {Studying Cerebral Vasculature Using Structure Proximity and Graph Kernels}
  author    = {R.~Kwitt, D.~Pace, M.~Niethammer and S.~Aylward},
  booktitle = {MICCAI},
  year      = {2013}}
```

<a name="toyexample"/>
Example (Toy Data - Circle of Willis)
-------------------------------------

To illustrate the key concepts, we will use a toy example (of an artificial
Circle of Willis). pypbm's `testdata` directory contains three variants of an
exemplar Circle of Willis (.pdf and .png) files. Those files were created with
[**IPE**](http://ipe7.sourceforge.net) and can be modified in case you want to change the topology. We will use
the templates to create our population representatives next.

### Directory structure for the example

In this example, we assume that all data that is created will be stored under
`/tmp/` and the base directory of pypbm will be referred to as `<Base>`. Hence,
the data directory with some example image templates can be found under
`<Base>/data`.

### Creating population images

We will choose *variant-A* and *variant-C* for illustration. Those images
serve as templates for the population A and C. In a first step, we will apply
random deformations to the images to simulate anatomical variation (or slight
registration misalignment). In a real clinical example, we would have to go
through several registration steps in order to register the source images (from
which the vasculature was extracted) to a common reference image. In our toy
example, all images will be already aligned and we only need to simulate slight
variations. We use ImageMagick for that and create our own deformations based
on a set of control points. To create control points we use `controlpoints.py`.

```bash
cd <Base>/data
python controlpoints.py -W 256 -H 256 -n 5 -r 5 -o /tmp/cp.txt
convert -alpha set -virtual-pixel white -distort Shepards '@/tmp/cp.txt' variant-A.png /tmp/Image-0001.png
```

This will create a distorted image of the template `variant-A.png`. Repeating
that process multiple times (for `variant-A.png` and `variant-C.png`) creates
our collection of population images. We assume that the images are stored in
the folders `/tmp/variant-A` and `/tmp/variant-C` for this example (we create
10 images for each population).

Finally, we will use a MATLAB script to prepare the data for further
processing. The script converts all images to binary images and inverts them
such that the blood vessels are the foreground objects. First, we need to
create a list of all deformed images `/tmp/raw.list`:

```bash
/tmp/variant-A/Image-0001.png
/tmp/variant-A/Image-0002.png
...
/tmp/variant-C/Image-0010.png
```
and run (in MATLAB, assuming that you added the `<Base>/matlab` directory to your
MATLAB path):

```matlab
prepimg('/tmp/raw.list');
```
The newly created images can be identified by the appended `-Matlab` in the
filename, e.g., `/tmp/variant-A/Image-0001-Matlab.png`.

### Establishing a common space

To create a graph representation, we will first need to establish a common
space which we can use to define graph nodes. This is done by building a
*vessel density* map for all input images by means of an *Euclidean distance
transform (EDT)*. The EDT computes, for all pixel (voxel), the distance to the
closest foreground object, i.e., a vessels of the Circle of Willis in our toy
example. Inverting these EDM images and averaging all the values over both
populations can then be interpreted as a *vessel density map*, since the values
at a specific location are proportional to the occurrence probability (i.e.,
the density) of observing a vessel at that location. Technically, this is done
by running

```bash
python bwdist.py -i /tmp/variant-A/Image-0001-Matlab.png -o /tmp/variant-A/image-0001-Matlab-Den.png
```
on all the images (written by the MATLAB script of the previous step) in
`/tmp/variant-A` and `/tmp/variant-C`. Building an average vessel density image
can then be done by

```bash
python imgavg.py -i density.list -o /tmp/atlas.tiff
```
where `density.list` contains the absolute filenames of the vessel density
images of both populations, e.g.,

```
/tmp/variant-A/Image-0001-Matlab-Den.png
/tmp/variant-A/Image-0002-Matlab-Den.png
...
/tmp/variant-B/Image-0009-Matlab-Den.png
/tmp/variant-B/Image-0010-Matlab-Den.png
```
Eventually, we partition the average vessel density image *atlas.tiff* by a
*centroidal Voronoi tessellation (CVT)*.  This will create a partitioning of
the vessel density space that we can use to define a *node* in our graph.
Technically, we use TubeTK's `ImageMath` tool to partition the space into 100
cells for instance:

```bash
ImageMath /tmp/atlas.tiff -Z 100 1000 1000 atlas-100.cvt -W 1 atlas-100.png
```
This creates a file `atlas-100.cvt` of CVT centers and also writes an image
`atlas-100.png` of the actual CVT (each pixel/voxel will have a unique ID that
identifies the cell it belongs to).

### Creating spatial-graph representations

To create a spatial-graph representation of our Circle of Willis examples, we
need to identify if two CVT cells are connected. This is done by simply
recording a 1 in a CxC adjacency matrix if there is a vessel connects two CVT
cells (and 0 otherwise). Since we do not know the direction of blood flow, we
can only a create an adjacency matrix for an undirected graph using this
strategy.  Technically, all we need to do is to call `skeltrace.py` with the
desired CVT image representing the *atlas* and a particular Circle of Willis
skeleton image:

```bash
python skeltrace.py -i /tmp/variant-A/Image-0001-Matlab.png -c /tmp/atlas-100.png -o /tmp/variant-A/Image-0001-Matlab-atlas-100.mat
```
Again, running `skeltrace.py` on all images (written by the MATLAB script)
creates both populations of graphs (for population A and C) in the form of
adjacency matrices (stored in `/tmp/variant-A/Image-0001-Matlab-atlas-100.mat`
for instance).

### Identifying population differences through dictionary learning

In the original work on pattern-based morphometry, the authors propose to find
the *closest* K images in population C to a given image from population A and
then compute K difference images (by simply subtraction). While, originally,
this was done on structural MR images, we use the vessel density images for
that purpose.  A sparse dictionary with A atoms is then learned to represent
the difference images with the intuition that the atoms will capture the most
prominent differences.

We differ to the original work in the following way: Instead of vectorizing
each vessel density image and computing the Euclidean distance to find the
nearest neighbors, we use the spatial-graph representations and a graph-kernel
to perform the same task in a more principled way. Once we have the K neighbors
to a given graph, we build the difference images using the corresponding vessel
density images. In our toy example, we use a Shortest-Path kernel for
similarity measurement and K-SVD for dictionary learning.

First, we need to load the adjacency matrices in a format compatible with Nino
Shervashidze's implementation of the Shortest-Path kernel using `readgraphs.m`.
This routine expects a list `/tmp/adj-100.list` of adjacency matrix files
(absolute path)

```
/tmp/variant-A/Image-0001-Matlab-atlas-100.mat
/tmp/variant-A/Image-0002-Matlab-atlas-100.mat
...
/tmp/variant-C/Image-0009-Matlab-atlas-100.mat
/tmp/variant-C/Image-0010-Matlab-atlas-100.mat
```

In MATLAB, we load the graphs with
```matlab
data = readgraphs('/tmp/adj-100.list', 100)
```
and can then compute the Shortest-Path kernel using
```
Ksp = spkernel(data,0)
```
This gives a 2Nx2N kernel matrix that can easily be converted into a distance
matrix to find nearest neighbors. Computation of the difference images and
execution of the dictionary learning is implemented in `klearn.m`, Assuming we
want to use three neighbors and to learn a dictionary of six atoms (with each
difference image represented as a linear combination of two atoms) we use (in
MATLAB):

```matlab
[O,X,D,Gamma] = klearn('/tmp/density.list', Ksp, lab, 3, 2, 6)
```
`D` contains the dictionary atoms (as column vectors), sorted by importance,
`X` contains the original difference images (as column vectors) and `O`
contains the original vessel density images (as column vectors). Visualizing
the atoms (or maybe the absolute values) should give a pretty good impression
of where the most prominent difference between both populations are.

<a name="clinicalexample"/>
Example (Clinical Data)
-----------------------

While our toy example shows the basic steps to do *vascular morphometry*, there
is one important step missing which is required with true clinical data:
**registration**.  pypbm contains a set of convenience routines that allow you
to run a registration pipeline (using ANTS) in order to align images from
different patients with a template/reference image.

In case of the [freely available
dataset](http://midas3.kitware.com/midas/folder/8051) for instance, we have MRA
and MRI images for each patient and we need to transform all the vasculature
(extracted from the MRA images) into a reference image space. To show how this
can be done, we first (rigidly) register the MRA images to the MRI images and
then (deformably) register theMRI images to a reference MRI image. The rigid
transform and the displacement field are then applied on the extracted vessels
to map them into the reference image space for further processing (see our toy
example).

First, you need to edit the `config.json.example` file and set the correct
paths to the required binaries in order to run the registration, e.g., replace
`<Path>` for the `BRAINSFit` binary with the absolute path to Slicer's
`BRAINSFit` binary. Then, for the rigid transformation step (using
`regMRAToMRI.py`) create two lists of images: one list for the moving images
(i.e., the MRA image list `mra.list`) and one list of fixed images (i.e., the
MRI image list `mri.list`). Two example lists (with only a single image) could
be

```
/tmp/Data/Normal-002/Normal002-MRA.mha
```

and

```
/tmp/Data/Normal-002/Normal002-T1-Flash.mha
```

Calling


```bash
python regMRAToMRI.py -c config.json -l mri.list mra.list /tmp/MRAInMRI.imgs /tmp/RigMRAToMRI.tfms
```

will register all MRA images to the MRI images and create two files: 1) a
Python pickled list `/tmp/MRAInMRI.imgs` of absolute paths to the MRA images
resampled in the space of the MRI images and a Python pickled list
`/tmp/RigMRAToMRI.tfms` of the actual rigid transformations.  Internally,
`regMRAToMRI.py` uses Slicer's *BRAINSFit* module to perform the rigid
registration.

Next, we need to (deformably) register the MRI images to the reference images.
This is implemented in `regMRIToRef.py` and internally calls ANTS to do the
actual registration.  **Note**: In this example, we have a second list of MRI
images `/tmp/mriNoSkull.list` which contains the full path to (skull-stripped)
versions of the original MRI images (this is required, since the template is
also a skull-stripped MRI image).

```bash
py regMRIToRef.py -l /tmp/mriNoSkull.list \
  -c config.json \
  -t /tmp/ref.mha \
  -d /tmp/AffMRIToRef.tfms \
     /tmp/FwdMRIToRef.tfms \
     /tmp/InvMRIToRef.tfms \
     /tmp/MRIInRef.imgs
  -f 0.5
```

The parameter `-t` specifies the template image, the arguments to parameter
`-d` specify 1) the list of generated affine transforms (to pre-align the MRI
images), 2) the list of forward displacement fields, 3) the list of inverse
displacement fields (to be used on the vascular networks later) and 4) a list
of MRI images resampled in the space of the reference image (all those lists
will be pickled Python lists). Finally, the parameter `-f 0.5` specifies that
we want to use 50% of all available CPUs to perform the registration.

As a last step, we take the extracted vasculature and use the rigid +
deformable registration results to map the centerline + radius representations
into the space of the reference image `/tmp/ref.mha`. Once, this is done we can
continue with the steps discussed in the toy example. The script
`mapMRIToRef.py` will perform the mapping task. The first important parameter
is the list of vascular network files to process (i.e., the `.tre` files in our
clinical data example), e.g.,

```
/tmp/Data/Normal-002/VascularNetwork.tre
```

Calling

```bash
python mapMRAToRef.py \
  -c config.json \
  -l /tmp/mriNoSkull.list
  -t /tmp/ref.mha \
  -i /tmp/RigMRAToMRI.tfms \
     /tmp/AffMRIToRef.tfms \
     /tmp/FwdMRAToRef.tfms \
     /tmp/InvMRAToRef.tfms
```

will produce `.tre` files (for each patient) all of which reside in the
reference image space. In summary, we are kind of *indirectly* registering all
the vascular networks w.r.t. a reference image via the corresponding MRA and
MRI images.

<a name="conveniencescripts"/>
Using the convenience scripts ...
---------------------------------

pypbm contains a collection of scripts under `scripts` could help to run
important commands on a list of images. Just type `./<ScriptName> -h` to get
some help on the required input arguments.

---
```
Author:    Roland Kwitt
License:   Apache License, Version 2.0
```
