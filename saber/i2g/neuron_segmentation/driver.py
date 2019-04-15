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

import numpy as np
import sys
from gala import imio, classify, features, morpho, agglo, evaluate as ev
from scipy.ndimage import label
from skimage.morphology import dilation, erosion
from skimage.morphology import square, disk
import argparse
from skimage import morphology as skmorph
import pickle

def get_parser():
    parser = argparse.ArgumentParser(description='GALA neuron Aggolmeration script')
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument(
            '-m',
            '--mode',
            required=True,
            help='Train(0) or Deploy(1)')
    parser.add_argument(
            '--prob_file',
            required=True,
            help='Probability map file')
    parser.add_argument(
            '--gt_file',
            required=False,
            help='Ground truth file')
    parser.add_argument(
            '--ws_file',
            required=False,
            help='Watershed file')
    parser.add_argument(
            '--train_file',
            required=False,
            help='Pretrained classifier file')
    parser.add_argument(
            '-o',
            '--outfile',
            required=True,
            help='Output file')
    parser.add_argument('--seeds_cc_threshold', type=int, default=5,
                        help='Cutoff threshold on seed size')
    parser.add_argument('--agg_threshold', type=float, default=0.5,
                        help='Cutoff threshold for agglomeration classifier')
    return parser

def train(args):
    gt_train, pr_train, ws_train = (map(imio.read_h5_stack,
                                [args.gt_file, args.prob_file,
                                args.ws_file]))
                                #['train-gt.lzf.h5', 'train-p1.lzf.h5',
                                # 'train-ws.lzf.h5']))
    #print('training')
    #gt_train = np.load(args.gt_file) #X,Y,Z
    #gt_train = np.transpose(gt_train,(2,0,1)) #gala wants z,x,y?
    #pr_train = np.load(args.prob_file) #X,Y,Z
    #pr_train = np.transpose(np.squeeze(pr_train),(2,0,1)) #gala wants z,x,y?
    #pr_train = pr_train[0:50,0:256,0:256]
    #pr_train = np.around(pr_train,decimals=2)
    #gt_train = gt_train[0:50,0:256,0:256]
    #print('watershed')
    #seeds = label(pr_train==0)[0]
    #seeds_cc_threshold = args.seeds_cc_threshold
    #seeds = morpho.remove_small_connected_components(seeds,
    #    seeds_cc_threshold)
    #ws_train = skmorph.watershed(pr_train, seeds)


    fm = features.moments.Manager()
    fh = features.histogram.Manager()
    fc = features.base.Composite(children=[fm, fh])
    g_train = agglo.Rag(ws_train, pr_train, feature_manager=fc)
    (X, y, w, merges) = g_train.learn_agglomerate(gt_train, fc)[0]
    y = y[:, 0] # gala has 3 truth labeling schemes, pick the first one
    
    rf = classify.DefaultRandomForest().fit(X, y)
    learned_policy = agglo.classifier_probability(fc, rf)
    #save learned_policy
    #np.savez(args.outfile, rf=rf, fc=fc)
    binary_file = open(args.outfile,mode='wb')
    lp_dump = pickle.dump([fc,rf], binary_file)
    binary_file.close()

def deploy(args):
    #probability map
    print("Deploying through driver")
    if args.prob_file.endswith('.hdf5'):
        mem = imio.read_image_stack(args.prob_file, single_channel=False)
    else:
        mem = np.load(args.prob_file) #X,Y,Z
        mem = np.transpose(np.squeeze(mem),(2,0,1)) #gala wants z,x,y?

    pr_test = np.zeros_like(mem)

    for z in range(0,mem.shape[0]):
        pr_test[z,:,:] = dilation(mem[z,:,:], disk(10))
        pr_test[z,:,:] = erosion(mem[z,:,:], disk(4))

    seg_out = np.zeros(pr_test.shape)
    pr_dim = pr_test.shape
    xsize = pr_dim[1]
    ysize = pr_dim[2]
    zsize = pr_dim[0]
    print(pr_dim)
    print(pr_dim[0])
    print(np.int(pr_dim[0]/zsize))

    print("Starting loop")
    for iz in range(0,np.int(pr_dim[0]/zsize)):
        for ix in range(0,np.int(pr_dim[1]/xsize)):
            for iy in range(0,np.int(pr_dim[2]/ysize)):
                p0 = pr_test[iz*zsize+0:iz*zsize+zsize,ix*xsize+0:ix*xsize+xsize,iy*ysize+0:iy*ysize+ysize]
                p0 = np.around(p0,decimals=2)
                print(p0)
                #get trained classifier
                #npzfile = np.load(args.train_file)
                #rf = npzfile['rf']
                #fc = npzfile['fc']
                binary_file = open(args.train_file,mode='rb')
                print(binary_file)
                temp = pickle.load(binary_file)
                fc = temp[0]
                rf = temp[1]
                binary_file.close()
                learned_policy = agglo.classifier_probability(fc, rf)

                #pr_test = (map(imio.read_h5_stack,
                #                        ['test-p1.lzf.h5']))
                print('watershed')
                seeds = label(p0==0)[0]
                seeds_cc_threshold = args.seeds_cc_threshold
                seeds = morpho.remove_small_connected_components(seeds,
                    seeds_cc_threshold)
                ws_test = skmorph.watershed(p0, seeds)
    
                g_test = agglo.Rag(ws_test, p0, learned_policy, feature_manager=fc)
                g_test.agglomerate(args.agg_threshold)
                #This is a map of labels of the same shape as the original image.
                seg_test1 = g_test.get_segmentation()
                seg_out[iz*zsize+0:iz*zsize+zsize,ix*xsize+0:ix*xsize+xsize,iy*ysize+0:iy*ysize+ysize] = seg_test1
    seg_out = np.transpose(seg_out,(1,2,0))
    with open(args.outfile, 'wb') as f:
        np.save(f,seg_out)
    return


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    if(int(args.mode)==0):
        train(args)
    else:
        deploy(args)


