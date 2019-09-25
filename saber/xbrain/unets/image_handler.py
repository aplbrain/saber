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

__author__ = 'drenkng1'

import numpy as np
import SimpleITK as sitk
import logging
import math

dtype_map = {
    'uint8': sitk.sitkUInt8,
    'int16': sitk.sitkInt16,
    'uint16': sitk.sitkUInt16,
    'int32': sitk.sitkInt32,
    'uint32': sitk.sitkUInt32,
    'float32': sitk.sitkFloat32,
    'float64': sitk.sitkFloat64
}


# ------------------------------------------------------------------------------
def load_nii(filename, data_type='float32', do_transpose=False):
    """
    This function takes a NIFTI filename as input and returns the loaded image
    with the correct shape.  SimpleITK loads images with the 3rd dimension
    first, so the image is transposed to be in RAI format.
    :param filename: NIFTI file
    :return: img: NIFTI/Analyze image (float32)
    """
    logging.info('Loading: %s' % filename)
    nii = sitk.ReadImage(filename)
    nii = sitk.Cast(nii, dtype_map[data_type])
    img = sitk.GetArrayFromImage(nii)
    if do_transpose:
        # Fix the image orientation so Z is last dimension
        img = np.transpose(img, axes=(2, 1, 0))
    return img


# ------------------------------------------------------------------------------
def save_nii(save_img, sample_nifti_file, filename, data_type='uint16'):
    """
    This function saves a NIFTI file given a numpy array.  Image data is cast to
    the specified precision (with range rescaling).
    :param save_img: Numpy image array to be saved
    :param sample_nifti: Numpy image array to get header information from
    :param filename: Filename with .nii.gz extension
    :param data_type: String data type to cast data to
    :return: None
    """
    logging.info('Saving: %s' % filename)
    sample_nii = sitk.ReadImage(sample_nifti_file)
    # Setup raw label image
    out_nii = sitk.GetImageFromArray(save_img)
    out_nii.CopyInformation(sample_nii)
    # Write images to file
    sitk.WriteImage(sitk.Cast(out_nii, dtype_map[data_type]), filename)


# ------------------------------------------------------------------------------
def save_nii2(save_img, filename, data_type='uint16'):
    """
    This function saves a NIFTI file given a numpy array.  Image data is cast to
    the specified precision (with range rescaling).
    :param save_img: Numpy image array to be saved
    :param filename: Filename with .nii.gz extension
    :param data_type: String data type to cast data to
    :return: None
    """
    logging.info('Saving: %s' % filename)
    # d, r, c = save_img.shape
    # dum_nii = sitk.Image(r, c, d, save_img.dtype)
    # Setup raw label image
    out_nii = sitk.GetImageFromArray(save_img)
    # Write images to file
    sitk.WriteImage(sitk.Cast(out_nii, dtype_map[data_type]), filename)


# ------------------------------------------------------------------------------
def get_bounding_box(model_vol, pad=15):
    """
    Function returns the bounding box for the given data volume.  The bounding
    box is based on the volume that encapsulates all nonzero voxels.
    :param model_vol: Numpy array of data corresponding to labels/probabilities
    :param pad: Optional parameter to specify how much to pad bounding box
            (applies to min and max ends of the box).
    :return:
        A list with the bounding box row, col, and depth indices
    """
    nonzero_inds_tup = np.nonzero(model_vol)

    bb = []
    dim = 0
    for arr in nonzero_inds_tup:
        min_val = int(np.min(arr))
        max_val = int(np.max(arr))

        # Include pad
        min_val = max(min_val - pad, 0)
        max_val = min(max_val + pad, model_vol.shape[dim])

        bb.append((min_val, max_val))
        dim += 1

    return bb


# ------------------------------------------------------------------------------
def extract_volume(orig_vol, bb):
    """
    Extract a sub-volume defined by the provided bounding box
    :param orig_vol: Original data volume
    :param bb: Bounding box list [(min_r,max_r),(min_c,max_c),(min_d,max_d)]
    :return:
        Numpy array with same size as the bounding box
    """
    sub_r = range(bb[0][0], bb[0][1])
    sub_c = range(bb[1][0], bb[1][1])
    sub_d = range(bb[2][0], bb[2][1])
    out_vol = orig_vol[np.ix_(sub_r, sub_c, sub_d)]

    return out_vol


# ------------------------------------------------------------------------------
def insert_volume(orig_vol, bb, sz):
    """
    Inserts the given volume into a new volume (filled with zeros) of the given
    size at the location of the specified bounding box.
    :param orig_vol: Smaller volume containing original data
    :param bb: Bounding box list [(min_r,max_r),(min_c,max_c),(min_d,max_d)]
    :param sz: Tuple defining size of new volume (row,col,depth)
    :return:
        Numpy array with the same size as defined by the sz tuple
    """
    sub_r = range(bb[0][0], bb[0][1])
    sub_c = range(bb[1][0], bb[1][1])
    sub_d = range(bb[2][0], bb[2][1])
    out_vol = np.zeros(sz)
    out_vol[np.ix_(sub_r, sub_c, sub_d)] = orig_vol
    return out_vol


# ------------------------------------------------------------------------------
def get_neighborhood(data, pt, neighborhood=(5, 5, 5), force_cube=True,
                     pad_value=0):
    """
    This function takes a full data matrix as input and returns the submatrix
    centered at the specified point.  If the point is on a boundary, the matrix
    is padded by the
    :param data: 3D input array
    :param pt: Center point - (R,C,D) tuple
    :param neighborhood: Tuple describing neighborhood shape (R,C,D)
    :param pad_value: Value to use if neighborhood needs to be padded
    :return: Volume with same shape as neighborhood tuple
    """
    rows, cols, depth = data.shape
    nrows, ncols, ndepth = neighborhood

    # Get neighborhood indices
    start_r = np.floor(pt[0] - nrows / 2).astype(int)
    stop_r = start_r + nrows
    start_c = np.floor(pt[1] - ncols / 2).astype(int)
    stop_c = start_c + nrows
    start_d = np.floor(pt[2] - ndepth / 2).astype(int)
    stop_d = start_d + nrows

    sub_r = range(max(start_r, 0), min(stop_r, rows))
    sub_c = range(max(start_c, 0), min(stop_c, cols))
    sub_d = range(max(start_d, 0), min(stop_d, depth))

    temp_vol = data[np.ix_(sub_r, sub_c, sub_d)]

    if force_cube:
        out_vol = pad_value * np.ones(neighborhood)
        r = max(-start_r, 0)
        c = max(-start_c, 0)
        d = max(-start_d, 0)
        out_vol[r:temp_vol.shape[0] + r, c:temp_vol.shape[1] + c,
                d:temp_vol.shape[2] + d] = temp_vol
    else:
        out_vol = temp_vol

    return out_vol


# ------------------------------------------------------------------------------
def convert_to_subvolumes(img, cube_dim):
    """
    Convert the input image to a new volume that has been zero padded to
    accomodate the requested number of sub-volumes.
    :param img: Input volume
    :param num_cubes: Requested number of cubes (may not equal the actual
    number of cubes)
    :param overlap: Fraction of overlap between adjacent sub-volumes
    :return: out_img: Zero padded image
             r_inds: Row indices for the subvolumes
             c_inds: Col indices for the subvolumes
             d_inds: Depth indices for the subvolumes
    """

    r, c, d = img.shape

    new_r = int(math.ceil(r / float(cube_dim)) * cube_dim)
    new_c = int(math.ceil(c / float(cube_dim)) * cube_dim)
    new_d = int(math.ceil(d / float(cube_dim)) * cube_dim)

    out_img = np.zeros((new_r, new_c, new_d), dtype=img.dtype)

    # Resize the image to the new size which accomodates the requested number
    #  of cubes
    out_img[:r, :c, :d] = img

    step = int(cube_dim)
    r_inds = np.arange(0, new_r, step)
    c_inds = np.arange(0, new_c, step)
    d_inds = np.arange(0, new_d, step)

    return out_img, r_inds.astype(int), c_inds.astype(int), d_inds.astype(int)
