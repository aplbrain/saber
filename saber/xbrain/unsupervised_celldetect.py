#!/usr/bin/env python

import argparse
import sys

import numpy as np

from skimage import measure
import skimage.color
try:
    from skimage import filters
except ImportError:
    from skimage import filter as filters
from skimage.measure import label, regionprops
import sklearn.mixture
import scipy.ndimage.morphology
from xbrain import classify_pixel, detect_cells, segment_vessels, detect_cells2D, cell_metrics2D, dense_f1_3D, gmm_classify_pixel, gmm_classify_pixel3D, f1_centroid3D
import nibabel as nib
import math
import scipy.io

def membrane_classify(args):
    img = nib.load(args.input)
    volume = img.get_fdata()# np.load(args.input)
    # run classification
    if args.threads == -1:
        import multiprocessing
        args.threads = multiprocessing.cpu_count()
    
    probability_maps = classify_pixel(
        volume,
        args.classifier,
        threads=args.threads,
        ram=args.ram
    )
    with open(args.output, 'wb') as f:
        np.save(f, probability_maps)
    
#udpate this with GMM code
def gmm_membrane_classify2D(args):
    img = nib.load(args.input)
    volume = img.get_fdata()# np.load(args.input)
    #volume = np.load(args.input)
    #print(volume.shape)
    #if volume.shape[2] == 3:
    #    IM = skimage.rgb2gray(volume); # V1 image
    #else: 
    #    IM = image;
    CellMapErode = gmm_classify_pixel(volume,args.numsamp,args.numcomp,args.erodesz)
    with open(args.output, 'wb') as f:
        np.save(f, CellMapErode)

#udpate this with GMM code
def gmm_membrane_classify3D(args):
    img = np.load(args.input)
    #volume = np.load(args.input)
    #print(volume.shape)
    #if volume.shape[2] == 3:
    #    IM = skimage.rgb2gray(volume); # V1 image
    #else: 
    #    IM = image;
    CellMapErode = gmm_classify_pixel3D(img,args.numsamp,args.numcomp,args.vesselthres,args.minsize,args.cellclass)
    with open(args.output, 'wb') as f:
        np.save(f, CellMapErode)

def cell_detect2D(args):
    cell_prob_map = np.load(args.input)
    centroids, cell_map = detect_cells2D(
        cell_prob_map,
        args.pthreshold,
        args.presidual,
        args.initial_template_size,
        args.dilationsz,
        args.max_cells
    )
    with open(args.output, 'wb') as f:
        np.save(f, centroids)        

def cell_detect3D(args):
    cell_prob_map = np.load(args.input)
    centroids, cell_map = detect_cells(
        cell_prob_map,
        args.pthreshold,
        args.presidual,
        args.initial_template_size,
        args.dilationsz,
        args.max_cells
    )
    with open(args.output, 'wb') as f:
        np.save(f, centroids)   
    with open(args.denseoutput, 'wb') as f:
        np.save(f, cell_map)       

def cell_metrics(args):
    img = nib.load(args.groundtruth)
    centroids = np.load(args.input)
    volume = img.get_fdata()# np.load(args.input)
    f1 = cell_metrics2D(centroids,volume,args.initial_template_size)
    with open(args.output, 'wb') as f:
        np.save(f, f1)

def cell_metrics3D(args):
    img = np.load(args.groundtruth)
    centroids = np.load(args.input)
    #volume = img.get_fdata()# np.load(args.input)
    f1 = f1_centroid3D(centroids,img,args.initial_template_size)
    print("F1: {}".format(f1))
    with open(args.output, 'wb') as f:
        np.save(f, f1)

def cell_metrics3Ddense(args):
    img = np.load(args.groundtruth)
    cells = np.load(args.input)
    f1 = dense_f1_3D(cells,img)
    print("F1: {}".format(f1))
    with open(args.output, 'wb') as f:
        np.save(f, f1)

def run_all(args):
    pmaps = gmm_membrane_classify(args)
    #pmaps = pmaps[:, :, :, 2]
    cells,_ = detect_cells2D(
        pmaps,
        args.pthreshold,
        args.presidual,
        args.initial_template_size,
        args.dilationsz,
        args.max_cells
    )
    with open(args.output, 'wb') as f:
        np.save(f, cells)

def main():
    parser = argparse.ArgumentParser(description='hyperparam opt script')
    parent_parser = argparse.ArgumentParser(add_help=False)
    #Subparser for different steps
    subparsers = parser.add_subparsers(title='commands')

    parser.set_defaults(func=lambda _: parser.print_help())

    parent_parser.add_argument('-i', '--input', required=True, help='Input file')
    parent_parser.add_argument('-o', '--output', required=True, help='Output file')
    
    parser_probmap = subparsers.add_parser('classify', help='Classify pixels in 2D',
                                            parents=[parent_parser])
    parser_probmap3D = subparsers.add_parser('classify3D', help='Classify pixels in 3D',
                                            parents=[parent_parser])
    parser_detect = subparsers.add_parser('detect', help='Detect cells in 2D', parents=[parent_parser])
    parser_detect3D = subparsers.add_parser('detect3D', help='Detect cells in 3D', parents=[parent_parser])
    parser_metrics = subparsers.add_parser('metrics', help='Optimization metrics',
                                           parents=[parent_parser])
    parser_metrics3D = subparsers.add_parser('metrics3D', help='Optimization metrics in 3d',
                                           parents=[parent_parser])
    parser_metrics3Ddense = subparsers.add_parser('metrics3Ddense', help='Optimization metrics, dense, in 3d',
                                           parents=[parent_parser])
    parser_runall = subparsers.add_parser('runall', help='Run entire pipeline without metrics',
                                           parents=[parent_parser])
    
    #Unsupervised GMM classification
    parser_probmap.add_argument('--numsamp', type=int, default=500000, help='GMM num samples')
    parser_probmap.add_argument('--numcomp', type=int, default=2, help='GMM Num components')
    parser_probmap.add_argument('--erodesz', type=int, default=1, help='erode size GMM')
    parser_probmap.set_defaults(func=gmm_membrane_classify2D)

    parser_probmap3D.add_argument('--numsamp', type=int, default=500000, help='GMM num samples')
    parser_probmap3D.add_argument('--numcomp', type=int, default=2, help='GMM Num components')
    parser_probmap3D.add_argument('--vesselthres', type=float, default=0.5, help='prob threshold for vessels')
    parser_probmap3D.add_argument('--minsize', type=float, default=0.5, help='number of layers for vessel')
    parser_probmap3D.add_argument('--cellclass', type=int, default=1, help='(1) if cells darker, (0) if cells lighter')
    parser_probmap3D.set_defaults(func=gmm_membrane_classify3D)

    parser_detect.add_argument('--presidual', type=float, default=0.47, help='Residual Stopping criterion')
    parser_detect.add_argument('--pthreshold', type=float, default=0.2, help='Cell probability threshold')
    parser_detect.add_argument('--spheresz', dest='initial_template_size', type=int,
                               default=18, help='Initial template size')
    parser_detect.add_argument('--dilationsz', type=int, default=8, help='Dilation size')
    parser_detect.add_argument('--maxnumcells', dest='max_cells', type=int, default=500,
                               help='Max number of cells')
    parser_detect.set_defaults(func=cell_detect2D)

    parser_detect3D.add_argument('--denseoutput', required=True, help='Output file for dense cell map')
    parser_detect3D.add_argument('--presidual', type=float, default=0.47, help='Residual Stopping criterion')
    parser_detect3D.add_argument('--pthreshold', type=float, default=0.2, help='Cell probability threshold')
    parser_detect3D.add_argument('--spheresz', dest='initial_template_size', type=int,
                               default=18, help='Initial template size')
    parser_detect3D.add_argument('--dilationsz', type=int, default=8, help='Dilation size')
    parser_detect3D.add_argument('--maxnumcells', dest='max_cells', type=int, default=500,
                               help='Max number of cells')
    parser_detect3D.set_defaults(func=cell_detect3D)
    
    parser_metrics.add_argument('--spheresz', dest='initial_template_size', type=int,
                               default=18, help='Initial template size')
    parser_metrics.add_argument('--groundtruth', required=False, help = 'Ground truth file')
    parser_metrics.set_defaults(func=cell_metrics)
    parser_metrics3D.add_argument('--spheresz', dest='initial_template_size', type=int,
                               default=18, help='Initial template size')
    parser_metrics3D.add_argument('--groundtruth', required=False, help = 'Ground truth file')
    parser_metrics3D.set_defaults(func=cell_metrics3D)
    parser_metrics3Ddense.add_argument('--groundtruth', required=False, help = 'Ground truth file')
    parser_metrics3Ddense.set_defaults(func=cell_metrics3Ddense)
    
    parser_runall.add_argument('--numsamp', type=int, default=500000, help='GMM num samples')
    parser_runall.add_argument('--numcomp', type=int, default=2, help='GMM Num components')
    parser_runall.add_argument('--erodesz', type=int, default=1, help='erode size GMM')
    
    parser_runall.add_argument('--presidual', type=float, default=0.47, help='Residual Stopping criterion')
    parser_runall.add_argument('--pthreshold', type=float, default=0.2, help='Cell probability threshold')
    parser_runall.add_argument('--spheresz', dest='initial_template_size', type=int,
                               default=18, help='Initial template size')
    parser_runall.add_argument('--dilationsz', type=int, default=8, help='Dilation size')
    parser_runall.add_argument('--maxnumcells', dest='max_cells', type=int, default=500,
                               help='Max number of cells')
    parser_runall.set_defaults(func=run_all)
    
    args = parser.parse_args()
    args.func(args)
if __name__ == '__main__':
    main()
