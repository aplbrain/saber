# Copyright 2019 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function,
                    unicode_literals)

def classify_pixel(input_data, classifier, threads=8, ram=4000):

    """
    Runs a pre-trained ilastik classifier on a volume of data
    Adapted from Stuart Berg's example here:
    https://github.com/ilastik/ilastik/blob/master/examples/example_python_client.py
    Arguments:
        input_data: data to be classified - 3D numpy array
        classifier: ilastik trained/classified file
        threads: number of thread to use for classifying input data
        ram: RAM to use in MB
    Returns:
        pixel_out: The raw trained classifier
    """

    import numpy as np
    import six
    import pdb
    from collections import OrderedDict
    import vigra
    import os
    import ilastik_main
    from ilastik.applets.dataSelection import DatasetInfo
    from ilastik.workflows.pixelClassification import PixelClassificationWorkflow

    # Before we start ilastik, prepare these environment variable settings.
    os.environ["LAZYFLOW_THREADS"] = str(threads)
    os.environ["LAZYFLOW_TOTAL_RAM_MB"] = str(ram)

    # Set the command-line arguments directly into argparse.Namespace object
    # Provide your project file, and don't forget to specify headless.
    args = ilastik_main.parser.parse_args([])
    args.headless = True
    args.project = classifier

    # Instantiate the 'shell', (an instance of ilastik.shell.HeadlessShell)
    # This also loads the project file into shell.projectManager
    shell = ilastik_main.main(args)
    assert isinstance(shell.workflow, PixelClassificationWorkflow)

    # Obtain the training operator
    opPixelClassification = shell.workflow.pcApplet.topLevelOperator

    # Sanity checks
    assert len(opPixelClassification.InputImages) > 0
    assert opPixelClassification.Classifier.ready()

    # For this example, we'll use random input data to "batch process"
    print("input_data.shape", input_data.shape)

    # In this example, we're using 2D data (extra dimension for channel).
    # Tagging the data ensures that ilastik interprets the axes correctly.
    input_data = vigra.taggedView(input_data, 'xyz')

    # In case you're curious about which label class is which,
    # let's read the label names from the project file.
    label_names = opPixelClassification.LabelNames.value
    label_colors = opPixelClassification.LabelColors.value
    probability_colors = opPixelClassification.PmapColors.value

    print("label_names, label_colors, probability_colors", label_names, label_colors, probability_colors)

    # Construct an OrderedDict of role-names -> DatasetInfos
    # (See PixelClassificationWorkflow.ROLE_NAMES)
    role_data_dict = OrderedDict([("Raw Data",
                                   [DatasetInfo(preloaded_array=input_data)])])

    # Run the export via the BatchProcessingApplet
    # Note: If you don't provide export_to_array, then the results will
    #       be exported to disk according to project's DataExport settings.
    #       In that case, run_export() returns None.

    predictions = shell.workflow.batchProcessingApplet.\
        run_export(role_data_dict, export_to_array=True)
    predictions = np.squeeze(predictions)
    print("predictions.dtype, predictions.shape", predictions.dtype, predictions.shape)

    print("DONE.")

    return predictions

#Unsupervised gmm clasification
def gmm_classify_pixel(volume,numsamp,numcomp,erodesz):
    import numpy as np
    import sklearn.mixture
    import scipy.ndimage.morphology

    IM = volume
    whichsamp = np.random.randint(IM.shape[0]*IM.shape[1],size=numsamp)
    trainind = IM.ravel()[whichsamp].astype(float)
    im_gmm = sklearn.mixture.GaussianMixture(n_components=numcomp, covariance_type='diag')
    im_gmm.fit(trainind.reshape(-1, 1))
    #gm = fitgmdist(traind,numcomp, 'CovType','diagonal','Options',options);
    whichCell = np.argmin(im_gmm.means_)
    #[~,whichCell] = min(gm.mu); 
    Probx = im_gmm.predict_proba(IM.ravel().astype(float).reshape(-1, 1))
    #Probx = posterior(gm,IM(:));
    CellMap = np.reshape(Probx[:,whichCell],IM.shape)
    if erodesz > 0:
        CellMapErode = scipy.ndimage.morphology.grey_erosion(CellMap,footprint=strel2D(erodesz))
        #print(strel2D(args.erodesz))
        #print(CellMap[0:5,0:5])
        #print(CellMapErode[0:5,0:5])
    else:
        CellMapErode = CellMap
    return CellMapErode

#Unsupervised gmm clasification (3D for xbrain data)
#cell_class=1, then cells are darker than background. Cell_class=0, cells are lighter than background
def gmm_classify_pixel3D(volume,numsamp,numcomp,vessel_thres,min_size,cell_class=1):
    import numpy as np
    import sklearn.mixture
    import scipy.ndimage.morphology
    import skimage.measure

    IM = volume
    whichsamp = np.random.randint(IM.size,size=numsamp)
    trainind = IM.ravel()[whichsamp].astype(float)
    im_gmm = sklearn.mixture.GaussianMixture(n_components=numcomp, covariance_type='diag')
    im_gmm.fit(trainind.reshape(-1, 1))
    #gm = fitgmdist(traind,numcomp, 'CovType','diagonal','Options',options);
    if cell_class==1:
        whichCell = np.argmin(im_gmm.means_)
    else:
        whichCell = np.argmax(im_gmm.means_)
    
    #[~,whichCell] = min(gm.mu); 
    Probx = im_gmm.predict_proba(IM.ravel().astype(float).reshape(-1, 1))
    #Probx = posterior(gm,IM(:));
    CellMap = np.reshape(Probx[:,whichCell],IM.shape)
    #Now remove vessels that have been detected
    CellMapT = np.multiply(CellMap,(CellMap>vessel_thres).astype(int))
    #foot = strel(1)
    foot = [[[True]]]
    CellMapErode = scipy.ndimage.morphology.grey_erosion((CellMapT*255).astype(int),footprint=foot)
    cc_labels,num = skimage.measure.label((CellMapErode>0).astype(int),connectivity=1,background=0,return_num=True)
    numslices = []
    for i_label in range(1,num+1):
        inds = np.where(cc_labels==i_label)
        z_inds = inds[2]
        numslices.append(len(np.unique(z_inds))) # np.unique(tempinds)))  #unique z inds
    for i_label in range(1,num+1):
        if numslices[i_label-1] < np.round(min_size * CellMapErode.shape[2]): 
            CellMapErode[np.where(cc_labels==i_label)] = 0 #eliminate vessels
    Vmap = scipy.ndimage.morphology.grey_dilation(CellMapErode,footprint=strel(1)) #note that tjs strel3d function is not same as this strel
    VmapT = (Vmap==0).astype(int)
    ProbMap = np.multiply(CellMap,VmapT)
    return ProbMap
    #print(strel2D(args.erodesz))
    #print(CellMap[0:5,0:5])
    #print(CellMapErode[0:5,0:5])

def segment_vessels(vessel_probability, probability_threshold, dilation_size, minimum_size):

    """
    This function produces a binary image with segmented vessels from a probability map (from
    ilastik or another classifier).
    Copyright (c) 2016, UChicago Argonne, LLC.

    Parameters
    ----------
    vessel_probability : ndarray
        Nr x Nc x Nz matrix which contains the probability of each voxel being a vessel.

    probability_threshold : float
        threshold between (0,1) to apply to probability map (only consider voxels for which
        vessel_probability(r,c,z) > probability_threshold).

    dilation_size : int
        Sphere Structural Element diameter size.

    minimum_size : int
        components smaller than this are removed from image.

    Returns
    -------
    ndarry
        Binary Image
    """
    import numpy as np
    import scipy.io as sio
    from scipy import ndimage as ndi
    from skimage import morphology

    smallsize = 100 # components smaller than this size are removed. WHY Fixed Size??

    unfiltered_im = (vessel_probability >= probability_threshold)
    im_removed_small_objects = morphology.remove_small_objects(unfiltered_im,
                                                               min_size = smallsize, in_place = True)

    dilated_im = ndi.binary_dilation(im_removed_small_objects, morphology.ball((dilation_size-1)/2))
    image_out = morphology.remove_small_objects(dilated_im, min_size = minimum_size,
                                                in_place = True)
    return(image_out)

def detect_cells2D(cell_probability, probability_threshold, stopping_criterion,
                initial_template_size, dilation_size, max_no_cells):

    """
    This is the top level function to infer the position (and eventually size) of all cells in a 2D
    volume of image data. We assume that we already have computed a "probability map" which encodes
    the probability that each voxel corresponds to a cell body.

    Copyright (c) 2016, UChicago Argonne, LLC.

    Parameters
    ----------
    cell_probability : ndarray
        Nr x Nc x Nz matrix which contains the probability of each voxel being a cell body.

    probability_threshold : float
        threshold between (0,1) to apply to probability map (only consider voxels for which
        cell_probability(r,c,z) > probability_threshold)
    stopping_criterion : float
        stopping criterion is a value between (0,1) (minimum normalized correlation between
        template and probability map) (Example = 0.47)
    initial_template_size : int
        initial size of spherical template (to use in sweep)
    dilation_size : int
        size to increase mask around each detected cell (zero out sphere of radius with
        initial_template_size+dilation_size around each centroid)
    max_no_cells : int
        maximum number of cells (alternative stopping criterion)

    Returns
    -------
    ndarray
        centroids = D x 4 matrix, where D = number of detected cells.
        The (x,y,z) coordinate of each cell are in columns 1-3.
        The fourth column contains the correlation (ptest) between the template
        and probability map and thus represents our "confidence" in the estimate.
        The algorithm terminates when ptest<=stopping_criterion.
    ndarray
        new_map = Nr x Nc x Nz matrix containing labeled detected cells (1,...,D)
    """

    # following imports to be updated when directory structure are finalized
    #import create_synth_dict
    #from compute3dvec import compute3dvec
    from scipy import signal
    import numpy as np
    import pdb
    import logging

    # threshold probability map.
    newtest = (cell_probability * (cell_probability > probability_threshold)).astype('float32')
    #initial_template_size is an int now but could a vector later on - convert it to an array
    initial_template_size = np.atleast_1d(initial_template_size)

    # create dictionary of spherical templates
    box_radius = np.ceil(np.max(initial_template_size)/2) + 1
    dict = create_synth_dict2D(initial_template_size, box_radius)
    dilate_dict = create_synth_dict2D(initial_template_size + dilation_size, box_radius)
    box_length = int(round(np.shape(dict)[0] ** (1/2)))
    new_map = np.zeros((np.shape(cell_probability)), dtype='uint8')
    newid = 1
    centroids = np.empty((0, 3))

    # run greedy search step for at most max_no_cells steps (# cells <= max_no_cells)
    for ktot in range(max_no_cells):
        val = np.zeros((np.shape(dict)[1], 1), dtype='float32')
        id = np.zeros((np.shape(dict)[1], 1), dtype='uint32')

        # loop to convolve the probability cube with each template in dict
        for j in range(np.shape(dict)[1]):
            convout = signal.fftconvolve(newtest, np.reshape(dict[:,j], (box_length, box_length)), mode='same')
            # get the max value of the flattened convout array and its index
            val[j],id[j] = np.real(np.amax(convout)), np.argmax(convout)

        # find position in image with max correlation
        which_atom = np.argmax(val)
        which_loc = id[which_atom]

        # Save dict into a cube array with its center given by which_loc and place it into a 3-D array.
        x2 = compute2dvec(dict[:, which_atom], which_loc, box_length, np.shape(newtest))
        xid = np.nonzero(x2)

        # Save dilate_dict into a cube array with its center given by which_loc and place it into a 3-D array.
        x3 = compute2dvec(dilate_dict[:, which_atom], which_loc, box_length, np.shape(newtest))

        newtest = newtest * (x3 == 0)
        ptest = val/np.sum(dict, axis=0)
        if ptest < stopping_criterion:
            print("Cell Detection is done")
            return(centroids, new_map)

        # Label detected cell
        new_map[xid] = newid
        newid = newid + 1

        #Convert flat index to indices
        rr, cc = np.unravel_index(which_loc, np.shape(newtest))
        new_centroid = cc, rr  #Check - why cc is first? Flip indices

        # insert a row into centroids
        centroids = np.vstack((centroids, np.append(new_centroid, ptest)))
        # for later: convert to logging and print with much less frequency
        if(ktot % 10 == 0):
            print('Iteration remaining = ', (max_no_cells - ktot - 1), 'Correlation = ', ptest )

    print("Cell Detection is done")
    return(centroids, new_map)

def detect_cells(cell_probability, probability_threshold, stopping_criterion,
                initial_template_size, dilation_size, max_no_cells):

    """
    This is the top level function to infer the position (and eventually size) of all cells in a 3D
    volume of image data. We assume that we already have computed a "probability map" which encodes
    the probability that each voxel corresponds to a cell body.

    Copyright (c) 2016, UChicago Argonne, LLC.

    Parameters
    ----------
    cell_probability : ndarray
        Nr x Nc x Nz matrix which contains the probability of each voxel being a cell body.

    probability_threshold : float
        threshold between (0,1) to apply to probability map (only consider voxels for which
        cell_probability(r,c,z) > probability_threshold)
    stopping_criterion : float
        stopping criterion is a value between (0,1) (minimum normalized correlation between
        template and probability map) (Example = 0.47)
    initial_template_size : int
        initial size of spherical template (to use in sweep)
    dilation_size : int
        size to increase mask around each detected cell (zero out sphere of radius with
        initial_template_size+dilation_size around each centroid)
    max_no_cells : int
        maximum number of cells (alternative stopping criterion)

    Returns
    -------
    ndarray
        centroids = D x 4 matrix, where D = number of detected cells.
        The (x,y,z) coordinate of each cell are in columns 1-3.
        The fourth column contains the correlation (ptest) between the template
        and probability map and thus represents our "confidence" in the estimate.
        The algorithm terminates when ptest<=stopping_criterion.
    ndarray
        new_map = Nr x Nc x Nz matrix containing labeled detected cells (1,...,D)
    """

    # following imports to be updated when directory structure are finalized
    #import create_synth_dict
    #from compute3dvec import compute3dvec
    from scipy import signal
    import numpy as np
    import pdb
    import logging

    if len(cell_probability.shape) == 4:
        print('Assuming Z, Chan, Y, X input')
        cell_probability = np.transpose(cell_probability[:,0,:,:], (2,1,0))

    # threshold probability map.
    newtest = (cell_probability * (cell_probability > probability_threshold)).astype('float32')
    #initial_template_size is an int now but could a vector later on - convert it to an array
    initial_template_size = np.atleast_1d(initial_template_size)

    # create dictionary of spherical templates
    box_radius = np.ceil(np.max(initial_template_size)/2) + 1
    dict = create_synth_dict(initial_template_size, box_radius)
    dilate_dict = create_synth_dict(initial_template_size + dilation_size, box_radius)
    box_length = int(round(np.shape(dict)[0] ** (1/3)))
    new_map = np.zeros((np.shape(cell_probability)), dtype='uint8')
    newid = 1
    centroids = np.empty((0, 4))

    # run greedy search step for at most max_no_cells steps (# cells <= max_no_cells)
    for ktot in range(max_no_cells):
        val = np.zeros((np.shape(dict)[1], 1), dtype='float32')
        id = np.zeros((np.shape(dict)[1], 1), dtype='uint32')

        # loop to convolve the probability cube with each template in dict
        for j in range(np.shape(dict)[1]):
            convout = signal.fftconvolve(newtest, np.reshape(dict[:,j], (box_length, box_length,
                                                                         box_length)), mode='same')
            # get the max value of the flattened convout array and its index
            val[j],id[j] = np.real(np.amax(convout)), np.argmax(convout)

        # find position in image with max correlation
        which_atom = np.argmax(val)
        which_loc = id[which_atom]

        # Save dict into a cube array with its center given by which_loc and place it into a 3-D array.
        x2 = compute3dvec(dict[:, which_atom], which_loc, box_length, np.shape(newtest))
        xid = np.nonzero(x2)

        # Save dilate_dict into a cube array with its center given by which_loc and place it into a 3-D array.
        x3 = compute3dvec(dilate_dict[:, which_atom], which_loc, box_length, np.shape(newtest))

        newtest = newtest * (x3 == 0)
        ptest = val/np.sum(dict, axis=0)
        if ptest < stopping_criterion:
            print("Cell Detection is done")
            return(centroids, new_map)

        # Label detected cell
        new_map[xid] = newid
        newid = newid + 1

        #Convert flat index to indices
        rr, cc, zz = np.unravel_index(which_loc, np.shape(newtest))
        new_centroid = rr, cc, zz  #Check - why cc is first?

        # insert a row into centroids
        centroids = np.vstack((centroids, np.append(new_centroid, ptest)))
        # for later: convert to logging and print with much less frequency
        if(ktot % 10 == 0):
            print('Iteration remaining = ', (max_no_cells - ktot - 1), 'Correlation = ', ptest )

    print("Cell Detection is done, centroids: {} map: {}".format(centroids.shape, new_map.shape))
    return(centroids, new_map)


def create_synth_dict(radii, box_radius):
    """
    This function creates a collection of spherical templates of different sizes.

    Copyright (c) 2016, UChicago Argonne, LLC.

    Parameters
    ----------
    radii : int
        radii coubld be 1xN vector but currently is an integer
    box_radius : float
    Returns
    -------
    ndarray
        dictionary of template vectors, of size (box_length ** 3 x length(radii)), where
        box_length = box_radius*2 +1 and radii is an input to the function which contains a vector
        of different sphere sizes.
    """

    import numpy as np
    from numpy import linalg as LA
    from scipy import ndimage as ndi
    from skimage.morphology import ball

    box_length = int(box_radius * 2 + 1)     #used for array dimension
    dict = np.zeros((box_length**3, np.size(radii)), dtype='float32')
    cvox = int((box_length-1)/2 + 1)

    for i in range(len(radii)):
        template = np.zeros((box_length, box_length, box_length))
        template[cvox, cvox, cvox] = 1
        dict[:, i] = np.reshape(ndi.binary_dilation(template, ball((radii[i] - 1)/2)), (box_length**3))
        dict[:, i] = dict[:, i]/(LA.norm(dict[:, i]))

    return(dict)

def create_synth_dict2D(radii, box_radius):
    """
    This function creates a collection of spherical templates of different sizes.

    Copyright (c) 2016, UChicago Argonne, LLC.

    Parameters
    ----------
    radii : int
        radii coubld be 1xN vector but currently is an integer
    box_radius : float
    Returns
    -------
    ndarray
        dictionary of template vectors, of size (box_length ** 3 x length(radii)), where
        box_length = box_radius*2 +1 and radii is an input to the function which contains a vector
        of different sphere sizes.
    """

    import numpy as np
    from numpy import linalg as LA
    from scipy import ndimage as ndi
    from skimage.morphology import ball

    box_length = int(box_radius * 2 + 1)     #used for array dimension
    dict = np.zeros((box_length**2, np.size(radii)), dtype='float32')
    cvox = int((box_length-1)/2 + 1)

    for i in range(len(radii)):
        template = np.zeros((box_length, box_length, box_length))
        template[cvox, cvox, cvox] = 1
        tmp = ndi.binary_dilation(template, ball((radii[i] - 1)/2))
        dict[:, i] = np.reshape(tmp[:,:,cvox], (box_length**2))
        if(LA.norm(dict[:, i])>0):
            dict[:, i] = dict[:, i]/(LA.norm(dict[:, i]))

    return(dict)

def placeatom(vector, box_length, which_loc, stacksz):

    """
    Copies the data from vector into a cube with the width of "box_length" and places the cube
    into a 3-D array with the shape/size defined by the "stacksz" parameter. The center of cube is
    given by the "which_loc" parameter.

    Copyright (c) 2016, UChicago Argonne, LLC.

    Parameters
    ----------
    vector : ndarray
        Nx1 array
    box_length : int
        Lenght
    which_loc : int
        location to place atom in the flattened array
    stacksz : ndarry
        shape of the array (3D)

    Returns
    -------
    ndarray
    """

    import numpy as np

    output_array = np.zeros((stacksz), dtype='float32')

    #Convert flat index to indices
    r, c, z = np.unravel_index(which_loc, (stacksz))
    output_array[r, c, z] = 1

    # Increase every dimension by box_length at the top and at the bottom and fill them with zeroes.
    output_array = np.lib.pad(output_array, ((box_length, box_length), (box_length, box_length),
                           (box_length, box_length)), 'constant', constant_values=(0, 0))

    # get the indices of the center of cube into increased dimensions output_array.
    r, c, z = np.nonzero(output_array)

    #save the output of round() function to avoid multiple calls to it.
    half_length = np.int(round(box_length/2))

    # TODO: casting to int to avoid problems downstream with indexing
    c = np.int(c)
    r = np.int(r)
    z = np.int(z)

    #Save the data from the cube into output_array.
    output_array[(r - half_length +1) : (r + box_length - half_length +1), \
            (c - half_length +1) : (c + box_length - half_length +1), \
            (z - half_length +1) : (z + box_length - half_length +1)] = \
            np.reshape(vector, (box_length, box_length, box_length))
    return(output_array)

def placeatom2D(vector, box_length, which_loc, stacksz):

    """
    Copies the data from vector into a cube with the width of "box_length" and places the
    into a 2-D array with the shape/size defined by the "stacksz" parameter. The center of tbhe data is
    given by the "which_loc" parameter.

    Copyright (c) 2016, UChicago Argonne, LLC.

    Parameters
    ----------
    vector : ndarray
        Nx1 array
    box_length : int
        Lenght
    which_loc : int
        location to place atom in the flattened array
    stacksz : ndarry
        shape of the array (3D)

    Returns
    -------
    ndarray
    """

    import numpy as np

    output_array = np.zeros((stacksz), dtype='float32')

    #Convert flat index to indices
    r, c = np.unravel_index(which_loc, (stacksz))
    output_array[r, c] = 1

    # Increase every dimension by box_length at the top and at the bottom and fill them with zeroes.
    output_array = np.lib.pad(output_array, ((box_length, box_length), (box_length, box_length)), 'constant', constant_values=(0, 0))

    # get the indices of the center of cube into increased dimensions output_array.
    r, c = np.nonzero(output_array)

    #save the output of round() function to avoid multiple calls to it.
    half_length = np.int(round(box_length/2))

    # TODO: casting to int to avoid problems downstream with indexing
    c = np.int(c)
    r = np.int(r)
    
    #Save the data from the cube into output_array.
    output_array[(r - half_length +1) : (r + box_length - half_length +1), \
            (c - half_length +1) : (c + box_length - half_length +1)] = \
            np.reshape(vector, (box_length, box_length))
    return(output_array)

def compute3dvec(vector, which_loc, box_length, stacksz):

    """
    Resizes the array dimension returned by placeatom() to the shape/size given by "stacksz" parameter.

    Copyright (c) 2016, UChicago Argonne, LLC.

    Parameters
    ----------
    vector : ndarray
        Nx1 array
    box_length : int
        Lenght
    which_loc : int
        location to place atom
    stacksz : ndarry
        shape of the array (3D)

    Returns
    -------
    ndarray
    """

    import numpy as np

    output_array = placeatom(vector, box_length, which_loc, stacksz)

    #delete the top "box_length" arrays for all dimensions.
    x, y, z = np.shape(output_array)
    output_array = output_array[box_length:x, box_length:y, box_length:z]

    #delete the bottom "box_length" arrays for all dimensions.
    x, y, z = np.shape(output_array)
    output_array = output_array[0 : (x - box_length), 0 : (y - box_length), 0 : (z - box_length)]

    return output_array

def compute2dvec(vector, which_loc, box_length, stacksz):

    """
    Resizes the array dimension returned by placeatom() to the shape/size given by "stacksz" parameter.

    Copyright (c) 2016, UChicago Argonne, LLC.

    Parameters
    ----------
    vector : ndarray
        Nx1 array
    box_length : int
        Lenght
    which_loc : int
        location to place atom
    stacksz : ndarry
        shape of the array (3D)

    Returns
    -------
    ndarray
    """

    import numpy as np

    output_array = placeatom2D(vector, box_length, which_loc, stacksz)

    #delete the top "box_length" arrays for all dimensions.
    x, y = np.shape(output_array)
    output_array = output_array[box_length:x, box_length:y]

    #delete the bottom "box_length" arrays for all dimensions.
    x, y = np.shape(output_array)
    output_array = output_array[0 : (x - box_length), 0 : (y - box_length)]

    return output_array

def strel2D(sesize):
    import numpy as np
    #sw = ((sesize-1)/2)
    #ses2 = int(math.ceil(sesize/2))
    [y,x] = np.meshgrid(list(range(-sesize,sesize+1)), list(range(-sesize,sesize+1)))
    se = ((((x/sesize)**2.0 + (y/sesize)**2.0) **(1/2.0))<=1)
    return(se)

def strel(sesize):
    import numpy as np
    #sw = ((sesize-1)/2)
    #ses2 = int(math.ceil(sesize/2))
    [y,x,z] = np.meshgrid(list(range(-sesize,sesize+1)), list(range(-sesize,sesize+1)), list(range(-sesize,sesize+1)))
    se = ((((x/sesize)**2.0 + (y/sesize)**2.0 + (z/sesize)**2.0) **(1/2.0))<=1)
    return(se)

#Call this function for centroid-level f1 score on 2d (nii) data
def cell_metrics2D(cells,im_train,initial_template_size):
    import numpy as np

    from skimage.measure import label, regionprops

    im_truth_labeled = label(im_train)
    regions = regionprops(im_truth_labeled)
    C0_prev = np.empty((0, 2))
    for props in regions:
        y0, x0 = props.centroid
        C0_prev = np.concatenate((C0_prev, [[x0,y0]]), axis=0)

    #CC = measure.label(im_train)
    #CC = measure.label(im_train, background=0)
    #regions = regionprops(CC)
    #C0_prev = np.zeros((1,2))
    #for props in regions:
    #    y0, x0 = props.centroid
    #    C0_prev = np.concatenate((C0_prev, [x0,y0]), axis=0)
    C1 = pad2D(cells[:,:2], initial_template_size, im_train.shape[0], im_train.shape[1])
    #C1 = pad(C1_prev, args.initial_template_size, im_train.shape[0], im_train.shape[1])
    C0 = pad2D(C0_prev, initial_template_size, im_train.shape[0], im_train.shape[1])
    C0 = np.transpose(C0)
    C1 = np.transpose(C1)

    thresh = initial_template_size
    f1 = centroid_f1(C0,C1,thresh)
    return f1                         
                            

def pad2D(C0_prev, sphere_sz, improb0_sz, improb1_sz):
    import numpy as np

    C0 = np.empty((0,2))
    for i in range(0,C0_prev.shape[0]):
        curr_row = C0_prev[i,:]
        if curr_row[0] > sphere_sz and curr_row[0] < improb0_sz - sphere_sz and curr_row[1] > sphere_sz and curr_row[1] < improb1_sz - sphere_sz :     
            C0 = np.concatenate((C0,[curr_row]),axis=0)
    return C0

#Call this function for centroid-level f1 score on 2d (nii) data
def f1_centroid3D(cells,im_train,initial_template_size):
    import numpy as np

    from skimage.measure import label, regionprops

    cells = cells[:,0:3] #Chop off last column, which is correlation score
    im_truth_labeled = label(im_train)
    regions = regionprops(im_truth_labeled)
    C0_prev = np.empty((0, 3))
    for props in regions:
        x0, y0, z0 = props.centroid #poss pull should put in x,y,z
        C0_prev = np.concatenate((C0_prev, [[x0,y0,z0]]), axis=0)

    #CC = measure.label(im_train)
    #CC = measure.label(im_train, background=0)
    #regions = regionprops(CC)
    #C0_prev = np.zeros((1,2))
    #for props in regions:
    #    y0, x0 = props.centroid
    #    C0_prev = np.concatenate((C0_prev, [x0,y0]), axis=0)
    C1 = pad3D(cells, initial_template_size, im_train.shape[0], im_train.shape[1], im_train.shape[2])
    #C1 = pad(C1_prev, args.initial_template_size, im_train.shape[0], im_train.shape[1])
    C0 = pad3D(C0_prev, initial_template_size, im_train.shape[0], im_train.shape[1], im_train.shape[2])
    C0 = np.transpose(C0)
    C1 = np.transpose(C1)

    thresh = initial_template_size
    f1 = centroid_f1(C0,C1,thresh)
    return f1                         
                            

def pad3D(C0_prev, sphere_sz, improb0_sz, improb1_sz, improb2_sz):
    import numpy as np

    C0 = np.empty((0,3))
    for i in range(0,C0_prev.shape[0]):
        curr_row = C0_prev[i,:]
        if curr_row[0] > sphere_sz and curr_row[0] < improb0_sz - sphere_sz and curr_row[1] > sphere_sz and curr_row[1] < improb1_sz - sphere_sz and curr_row[2] > sphere_sz and curr_row[2] < improb2_sz - sphere_sz :     
            C0 = np.concatenate((C0,[curr_row]),axis=0)
    return C0

#Dense, 3D f1 score of cell detection
def dense_f1_3D(cell_map,cell_gt_map):
    import numpy as np
    import math
    # processing params
    bin_cell_map = cell_map
    bin_cell_map[bin_cell_map>0]=1
    bin_cell_map[bin_cell_map<=0]=0
    bin_gt_map = cell_gt_map
    bin_gt_map[bin_gt_map>0]=1
    bin_gt_map[bin_gt_map<=0]=0
    
    beta = 2
    #cells
    cell_true_detect = np.sum(np.logical_and(bin_cell_map,bin_gt_map).astype(int).ravel())
    cell_detections = np.sum(bin_cell_map.ravel())
    cell_true_positives = np.sum(bin_gt_map.ravel())
    if(cell_detections>0):                
        cell_p = cell_true_detect/cell_detections
    else:
        cell_p = 0
    if(cell_true_positives>0):    
        cell_r = cell_true_detect/cell_true_positives
    else:
        cell_r = 0
                    
    if(cell_p + cell_r >0):
        f_cell = (1+math.pow(beta,2)) * (cell_p*cell_r)/(math.pow(beta,2)*cell_p + cell_r)
    else:
        f_cell = 0
    return f_cell

def centroid_f1(C0,C1,thres):
    import scipy
    import numpy as np
    C0 = np.transpose(C0)
    C1 = np.transpose(C1)
    Y = scipy.spatial.distance.cdist(C0, C1, 'euclidean')
    try:
        vals = np.sort(np.amin(Y,axis=1)) 
        valinds = np.argsort(np.min(Y,axis=1)) 
    except ValueError:
        print("No Detected Objects")
        return 0

    L = len(vals[np.where(vals<=thres)])

    C0 = np.transpose(C0)
    C0 = C0[:,valinds]
    Y2 = scipy.spatial.distance.cdist(C1, np.transpose(C0), 'euclidean')

    matches = np.zeros((2,L))
    dvec = np.zeros((L,1))

    for i in range(0,L):    
        idcol = i
        valtmp = np.amin(Y2[:,i])
        idrow = np.argmin(Y2[:,i])
        #idrow = np.argmin(Y2[i,:])
    
        if valtmp<=thres:
            matches[:,i] = [idrow,idcol]
            dvec[i] = valtmp
    
        Y2[idrow,:]=thres+100
        Y2[:,idcol]=thres+100

    idd = np.where(dvec>thres)
    matches[:,idd]=[]
    matches = np.asarray(matches)

    numcorrect = sum([sum(x)!=0 for x in zip(*matches)])

    numgt = C0.shape[1]
    numrecov = C1.shape[0]

    b=1 #f1 score
    TP = numcorrect/numrecov
    FP = 1 - TP
    FN = (numgt - numcorrect)/numgt
    p = TP /(TP + FP)
    r = TP /(TP + FN)
    f1 = (1 + b**2)*p*r/(((b**2)*p)+r)
    return f1
