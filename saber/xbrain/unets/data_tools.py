"""
Copyright 2018 The Johns Hopkins University Applied Physics Laboratory.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Some functions for manipulating data/images.
"""

#from __future__ import print_function

__author__ = 'mjp, Nov 2016'
__license__ = 'Apache 2.0'

import numpy as np
from functools import partial

from scipy.interpolate import griddata


# ------------------------------------------------------------------------------
def random_minibatch(X, Y, num_in_batch, sz=(256, 256), do_warping=False):
    """ Creates a single minibatch of training data by randomly sampling
    subsets of the training data (X, Y).
    This does not methodically examine all subsets of the domain, therefore
    the notion of an 'epoch' is not tied to some guarantee of covering
    all data if you use this function.
    Parameters:    
       X := tensor with dimensions (#examples, #channels, rows, colums)
       Y := tensor with dimensions (#examples, rows, columns)
       num_in_batch := scalar; number of objects in the minibatch
       sz := tuple (n_rows, n_cols) indicating the chip size
       
    """
    n, d, r, c = X.shape

    # preallocate memory for result
    X_mb = np.zeros((num_in_batch, X.shape[1], sz[0], sz[0]), dtype=np.float32)
    Y_mb = np.zeros((num_in_batch, Y.shape[1], sz[0], sz[0]), dtype=np.float32)

    for ii in range(num_in_batch):
        # grab a random slice
        ni = np.random.randint(low=0, high=n-1)
        Xi = X[ni, ...]
        Yi = Y[ni, ...]
        
        # grab a random tile of size sz
        if not Xi.shape[-2:] == sz:
            Xi, Yi = random_crop([Xi, Yi], sz)

        # warp/transform        
        Xi, Yi = apply_symmetry([Xi, Yi])
        if do_warping:
            Xi,Yi = apply_warping(Xi, Yi)

        X_mb[ii, ...] = Xi
        Y_mb[ii, ...] = Yi

    return X_mb, Y_mb


def apply_2d_operator(X, op):
    """ Applies the function op to all 2d images contained in the tensor X.
    Parameters:
       X  : A tensor with dimension (..., rows, cols)
       op : a function that takes a single argument, an 2d matrix (rows, cols) and
            returns a new 2d matrix of the same shape.
    Example:
       op = lambda M: M.transpose()
       X = np.random.rand(5,5,3,3)
       Y = apply_2d_operator(X, op)
       X[0,2,...]
       Y[0,2,...]
    """
    if X.ndim == 2:
        return op(X)
    else:
        sz = X.shape
        X = np.reshape(X, (np.prod(sz[0:-2]), sz[-2], sz[-1]))
        X_out = [op(X[ii]) for ii in range(X.shape[0])]
        return np.reshape(X_out, sz)


def random_crop(tensors, sz):
    """
    Grabs a random subset of the spatial dimensions of the provided tensors.
    The same spatial extent will be extracted from all tensors.
    
       tensors := a list of image tensors with dimensions (..., rows, columns)
       sz      := a tuple (n_rows, n_cols) specifing the size of the crop
    """

    if isinstance(tensors, list):
        r,c = tensors[0].shape[-2:]
    else:
        # caller provided a single tensor (rather than a list)
        r,c = tensors.shape[-2:]

    # choose an upper-left corner for the crop
    ri = np.random.randint(low=0, high=r-sz[0]-1)
    ci = np.random.randint(low=0, high=c-sz[1]-1)

    # extract subset
    if isinstance(tensors, list):
        return [ X[..., ri:ri+sz[0], ci:ci+sz[1]] for X in tensors]
    else:
        X = tensors
        return X[..., ri:ri+sz[0], ci:ci+sz[1]]


def apply_symmetry(tensors, op_idx=-1):
    """Implements synthetic data augmentation by randomly appling
    an element of the group of symmetries of the square.
    The default set of data augmentation operations correspond to
    the symmetries of the square (a non abelian group).  The
    elements of this group are:
      o four rotations (0, pi/2, pi, 3*pi/4)
        Denote these by: R0 R1 R2 R3
      o two mirror images (about y-axis or x-axis)
        Denote these by: M1 M2
      o two diagonal flips (about y=-x or y=x)
        Denote these by: D1 D2
    This page has a nice visual depiction:
      http://www.cs.umb.edu/~eb/d4/
    Parameters:
       tensors  := a list of image tensors with dimensions (..., rows, columns)
       op_index := An integer in [0,7] indicating which operator to apply.
                   If unspecified, the operation used will be random.
    """

    def R0(X):
        return X  # this is the identity map

    def M1(X):
        return X[..., ::-1, :]

    def M2(X): 
        return X[..., ::-1]

    def D1(X):
        sz = list(range(X.ndim))
        sz[-2], sz[-1] = sz[-1], sz[-2]
        return np.transpose(X, sz)

    def R1(X):
        return D1(M2(X))   # = rot90 on the last two dimensions

    def R2(X):
        return M2(M1(X))

    def R3(X): 
        return D2(M2(X))

    def D2(X):
        return R1(M1(X))

    symmetries = [R0, R1, R2, R3, M1, M2, D1, D2]

    # choose the operation    
    op = symmetries[op_idx] if op_idx >= 0 else np.random.choice(symmetries)

    if isinstance(tensors, list): 
        return [op(x) for x in tensors]
    else:
        # presumably caller passed in just one tensor
        return op(tensors)


def apply_warping(X, Y, sigma=10):
    X0 = get_slice_0(X)
    
    # make sure images are square
    n = X0.shape[0];
    assert(X0.shape[1] == n)
    assert(Y.shape[-2] == Y.shape[-1] == n)

    omega_xnew, omega_ynew = make_displacement_mesh(n, sigma)
    f_warp = partial(apply_displacement_mesh, omega_xnew=omega_xnew, omega_ynew=omega_ynew)

    X_new = apply_2d_operator(X, f_warp)
    Y_new = apply_2d_operator(Y, f_warp)

    # TODO: something smarter here to deal with issues at boundary
    X_new[np.isnan(X_new)] = 0
    Y_new[np.isnan(Y_new)] = 0
    
    return X_new, Y_new


def make_displacement_mesh(n, sigma, n_seed_points=5):
    """ Creates a warping/displacement mesh (for synthetic data augmentation).
    
    Parameters:
      n     : The width/height of the target image (assumed to be square)
      sigma : standard deviation of displacements. 
              If negative, is interpreted as a deterministic displacement.
              This latter usage is for testing, not actual applications.
      n_seed_points : The number of random displacements to choose (in each dimension).
              Displacements at all locations will be obtained via interpolation.
    """
    glue = lambda X, Y: np.vstack([X.flatten(), Y.flatten()]).transpose()

    # the domain Omega is [0:n)^2
    omega_x, omega_y = np.meshgrid(np.arange(n), np.arange(n))

    # create random displacement in the domain.
    # Note: we "overshoot" the domain to avoid edge artifacts when
    #       interpolating back to the lattice on Z^2.
    d_pts = np.linspace(0, n, n_seed_points)
    d_xx, d_yy = np.meshgrid(d_pts, d_pts)

    if sigma > 0:
        # random displacement
        dx = sigma * np.random.randn(d_xx.size)
        dy = sigma * np.random.randn(d_yy.size)
    else:
        # deterministic displacement (for testing)
        dx = abs(sigma) * np.ones(d_xx.size)
        dy = abs(sigma) * np.ones(d_yy.size)
    
    # use interpolation to generate a smooth displacement field.
    omega_dx = griddata(glue(d_xx, d_yy), dx.flatten(), glue(omega_x, omega_y))
    omega_dy = griddata(glue(d_xx, d_yy), dy.flatten(), glue(omega_x, omega_y))

    # reshape 1d -> 2d
    omega_dx = np.reshape(omega_dx, (n, n))
    omega_dy = np.reshape(omega_dy, (n, n))

    # generate a perturbed mesh
    omega_xnew = omega_x + omega_dx
    omega_ynew = omega_y + omega_dy

    return omega_xnew, omega_ynew


def plot_mesh(xx, yy, linespec='k-'):
    """ Plots a pixel location mesh/lattice.
    
     xx : an (m x n) matrix of x-indices
     yy : an (m x n) matrix of y-indices
    """
    assert(xx.ndim == 2)
    assert(yy.ndim == 2)
    plt.hold(True)
    for r in range(xx.shape[0]):
        for c in range(xx.shape[1]):
            if c+1 < xx.shape[1]: plt.plot((xx[r, c], xx[r, c+1]),
                                           (yy[r, c], yy[r, c]), 'k-')  # east
            if r+1 < xx.shape[0]: plt.plot((xx[r, c], xx[r, c]),
                                           (yy[r, c], yy[r+1, c]), 'k-')  # south
    plt.gca().set_xlim([np.min(xx), np.max(xx)])
    plt.gca().set_ylim([np.min(yy), np.max(yy)])
    plt.hold(False)


def apply_displacement_mesh(X, omega_xnew, omega_ynew):
    """Interpolates pixel intensities back into a regular mesh.
    Parameters:
      X := an (m x n) matrix of pixel intensities
      omega_xnew := an (m x n) matrix of perturbed x locations in R^2
      omega_ynew := an (m x n) matrix of perturbed y locations in R^2
    Returns:
      X_int : an (m x n) matrix of interpolated pixel values
              which live in Z^2
    """
    glue = lambda X, Y: np.vstack([X.flatten(), Y.flatten()]).transpose()
    
    n = X.shape[0]
    assert(X.ndim == 2 and n == X.shape[1])

    # this is the natural/original lattice where we wish to generate
    # interpolated values.    
    omega_x, omega_y = np.meshgrid(np.arange(n), np.arange(n))
    
    # use interpolation to estimate pixel intensities on original lattice
    X_int = griddata(glue(omega_xnew, omega_ynew),
                     X.flatten(),
                     glue(omega_x, omega_y))
    X_int = np.reshape(X_int, (n, n))

    return X_int


def get_slice_0(X):
    """ Returns X[0,..,0, :, :]
    """
    if X.ndim == 2:
        return X
    else:
        sz = X.shape
        new_sz = (np.prod(sz[0:-2]), sz[-2], sz[-1])
        return np.squeeze(np.reshape(X, sz)[0, :, :])
