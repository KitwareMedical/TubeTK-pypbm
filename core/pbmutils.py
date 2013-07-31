"""pbmutils.py
"""


__license__ = "Apache License, Version 2.0"
__author__  = "Roland Kwitt, Kitware Inc., 2013"
__email__   = "E-Mail: roland.kwitt@kitware.com"
__status__  = "Development"


import numpy as np
import SimpleITK as sitk
from scipy.spatial.distance import cdist


def imResize(im, alpha=None):
    """Image scaling.

    Parameters
    ----------

    im : SimpleITK image
        Input image to scale.

    alpha : float
        Scaling factor to use.

    Returns
    -------

    im : SimpleITK image
        Rescaled image.
    """
    if alpha is None:
        return im

    # input size and spacing
    imSize = list(im.GetSize())
    imSpac = list(im.GetSpacing())

    # compute output size and spacing
    outSize = np.asarray(imSize)*alpha
    outSpac = np.asarray(imSpac)*np.asarray(imSize)/outSize

    sitkArgSize = map(int, list(outSize))
    sitkArgSpac = map(float, list(outSpac))

    resampler = sitk.ResampleImageFilter()
    resampler.SetSize(sitkArgSize)
    resampler.SetOutputSpacing(sitkArgSpac)
    return resampler.Execute(im)


def groupDiff(X, labels, K=3):
    """Groupwise differences based on nearest neighbor distance.

    Take a matrix with observations as columns and a binary group labeling (one
    label per column). For each observation in group A determine the closest K
    neighbors in group B and compute the difference between those observations
    (element-wise).

    Parameters
    ----------

    X : numpy matrix, shape (N, D)
        Input data matrix. Observations are columns.

    labels : list
        List of D numeric labels - one for each observation. Currently,
        only a binary label set is supported.

    K : int (default : 3)
        Number of nearest neighbors (in Euclidean sense) to consider for
        building the matrix of observation differences.

    Returns
    -------

    D : numpy matrix, shape (N, V)
        Given that n1 is the cardinality of the set of observations for
        group 1 and n2 is the cardinality of the set of observations for
        group 2, V will be V := n1*K, since we search for the K closest
        neighbors in group 2 and compute the difference with each of it's
        K neighbors.
    """

    u = np.unique(np.asarray(labels))
    if len(u) != 2:
        raise Exception('only binary grouping supported!')

    p0 = np.where(labels == u[0])[0] # group 0
    p1 = np.where(labels == u[1])[0] # group 1

    # make sure we have a signed data type
    S = np.asarray(X[:,p0], dtype=np.float32)
    Z = np.asarray(X[:,p1], dtype=np.float32)

    # pairwise distances
    pwd = np.argsort(cdist(np.asmatrix(S).T,
                           np.asmatrix(Z).T), axis=1)

    # build difference images
    D = np.zeros((X.shape[0],pwd.shape[0]*K))
    for i in range(pwd.shape[0]):
        #print i, p1[pwd[i,0:K]]
        for idx, j in enumerate(pwd[i,0:K]):
            D[:,i*K+idx] = (S[:,i]-Z[:,j]).ravel()
    return D


def imSlice(im, selector):
    """Extract an image slice as a numpy array.

    Takes a SimpleITK image and extracts a slice along the non-zero entry of
    'selector'. The slice data is then returned as a numpy array.

    Parameters
    ----------

    im : SimpleITK image
        The 3D input image.

    selector : list
        Slice image along the dimension of the non-zero entry and extract
        the slice at that position. E.g., [0 0 10] extracts the 10th slice
        along the 3rd dimension.

    Returns
    -------

    slice : numpy array, shape = (M, N)
        The extracted slice as a numpy array.
    """

    imSize = list(im.GetSize())
    if len(imSize) != 3:
        raise Exception('imslice() called on non-3D image!')

    p = np.where(np.asarray(selector)>0)[0]
    if len(p) > 1:
        raise Exception('wrong selector format!')

    index = [0, 0, selector[p]]
    imSize[p] = 0

    slicer = sitk.ExtractImageFilter()
    slicer.SetSize(imSize)
    slicer.SetIndex(index)
    imSlice = slicer.Execute(im)
    return sitk.GetArrayFromImage(imSlice)
