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

import os
import sys
import time
import numpy as np
import json
import argparse
import pandas as pd

np.random.seed(9999)


from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *


class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def parse_args(json_file=None):
    args = defaults

    if json_file:
        with open(json_file, 'r') as f:
            json_args = json.load(f)
        args.update(json_args)

    return Namespace(**args)


def get_boss_data(args):

    args.x_rng = [args.xmin, args.xmax]
    args.y_rng = [args.ymin, args.ymax]
    args.z_rng = [args.zmin, args.zmax]
    config = {"protocol": "https",
              "host": args.host,
              "token": args.token}
    rmt = BossRemote(config)

    segchan = ChannelResource(args.chan_seg,
                           args.coll,
                           args.exp,
                           'annotation',
                           datatype=args.dtype_seg)

    # Get the image data from the BOSS
    seg_data = rmt.get_cutout(segchan, args.res,
                             args.x_rng,
                             args.y_rng,
                             args.z_rng)

    synchan = ChannelResource(args.chan_syn,
                            args.coll,
                            args.exp,
                            'annotation',
                            datatype=args.dtype_syn)

    syn_data = rmt.get_cutout(synchan, args.res,
                             args.x_rng,
                             args.y_rng,
                             args.z_rng)
    
    #Wany XYZ
    seg_data = np.transpose(seg_data,(2,1,0))
    syn_data = np.transpose(syn_data,(2,1,0))
    return seg_data, syn_data

def get_file_data(args):
    seg_data = np.load(args.seg_file)
    syn_data = np.load(args.syn_file)

    return seg_data, syn_data

def edge_list_cv(neurons, synapses, dilation=5, syn_thres=0.8, blob_thres=4000):

    from scipy.stats import mode
    import numpy as np
    from skimage.measure import label
    import skimage.morphology as morpho
    from skimage.measure import regionprops

    synapses_dil = np.zeros_like(synapses)

    for z in range(0,synapses.shape[2]):
        synapses_dil[:,:,z] = morpho.dilation(synapses[:,:,z], selem=morpho.disk(dilation))    # find synapse objects
    synapses_dil = synapses_dil/255
    print(np.max(synapses_dil))
    print(np.min(synapses_dil))
    threshold = 0.8
    synapses_dil,num = label((synapses_dil>threshold).astype(int),connectivity=1,background=0,return_num=True)
    syn_regions = regionprops(synapses_dil)
    for region in syn_regions:
        if(region['area']<blob_thres):
            inds = region['bbox']
            synapses_dil[inds[0]:inds[3],inds[1]:inds[4],inds[2]:inds[5]] = 0

    synid = np.unique(synapses_dil)
    synid = synid[synid > 0]
    print(len(synid))

    syn_ids = []
    x = []
    y = []
    z = []
    post = []
    pre = []
    postNan = []
    preNan = []
    neusynlist = {}
    synlist = {}
    for s in synid:
        postval = 0
        preval = 0
        temp = (synapses_dil == s).astype(int)
        regions = regionprops(temp)
        for props in regions:
            x0, y0, z0 = props.centroid #poss pull should put in x,y,z
            break #only get first, in case there is some weird badness
        #print str(s).zfill(4),
        try:
            val = np.ravel(neurons[synapses_dil == s])
            val = val[val > 0]
            postval = mode(val)[0][0]
            val = val[val != postval]
            preval = mode(val)[0][0]
            syn_ids.append(s)
            x.append(x0)
            y.append(y0)
            z.append(z0)
            post.append(postval)
            pre.append(preval)
            postNan.append(np.nan)
            preNan.append(np.nan)
        except:
            print('skipping this id')
        
    print('complete')
    neusynlist['syn_ids'] = syn_ids
    neusynlist['xs'] = x
    neusynlist['ys'] = y
    neusynlist['zs'] = z
    neusynlist['pres'] = pre
    neusynlist['posts'] = post
    synlist['syn_ids'] = syn_ids
    synlist['xs'] = x
    synlist['ys'] = y
    synlist['zs'] = z
    synlist['pres'] = preNan
    synlist['posts'] = postNan
    return (neusynlist,synlist)

if __name__ == '__main__':
    # -------------------------------------------------------------------------

    parser = argparse.ArgumentParser(description='Seg syn association')
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument(
            '--use_boss',
            type=int,
            required=True,
            help='False(0) to use img_file and lbl_file or True(1) to pull data from boss')
    parser.add_argument(
            '--host',
            required=False,
            help='Host for boss')
    parser.add_argument(
            '--seg_file',
            required=False,
            help='Local segmentation file'
            )
    parser.add_argument(
            '--lbl_file',
            required=False,
            help='Local synapse file'
            )
    parser.add_argument(
            '--coord',
            required=False,
            help='Coord frame for BOSS'
            )
    parser.add_argument(
            '--token',
            required=False,
            help='Token for BOSS'
            )
    parser.add_argument(
            '--coll',
            required=False,
            help='Collection Name for BOSS'
            )
    parser.add_argument(
            '--exp',
            required=False,
            help='Experiment Name for BOSS'
            )
    parser.add_argument(
            '--chan_syn',
            required=False,
            help='Synapse channel for BOSS'
            )
    parser.add_argument(
            '--chan_seg',
            required=False,
            help='Segmentation channel for BOSS'
            )
    parser.add_argument(
            '--dtype_syn',
            required=False,
            help='Datatype for BOSS'
            )
    parser.add_argument(
            '--dtype_seg',
            required=False,
            help='Datatype for BOSS annotation'
            )
    parser.add_argument(
            '--res',
            type=int,
            required=False,
            help='resolution for BOSS'
            )
    parser.add_argument(
            '--xmin',
            type=int,
            required=False,
            help='Xmin of range for BOSS'
            )
    parser.add_argument(
            '--xmax',
            type=int,
            required=False,
            help='Xmax of range for BOSS'
            )
    parser.add_argument(
            '--ymin',
            type=int,
            required=False,
            help='Ymin of range for BOSS'
            )
    parser.add_argument(
            '--ymax',
            type=int,
            required=False,
            help='Ymax of range for BOSS'
            )
    parser.add_argument(
            '--zmin',
            type=int,
            required=False,
            help='Zmin of range for BOSS'
            )
    parser.add_argument(
            '--zmax',
            type=int,
            required=False,
            help='Zmax of range for BOSS'
            )
    parser.add_argument(
            '-d',
            '--dilation',
            default=5,
            required=False,
            help='Dilation of synapses')
    parser.add_argument(
            '-t',
            '--threshold',
            default=0.8,
            required=False,
            help='Synapse threshold')
    parser.add_argument(
            '-b',
            '--blob',
            default=4000,
            required=False,
            help='Blob size threshold')
    parser.add_argument(
            '--output',
            required=True,
            help='Synapse frame'
            )
    parser.add_argument(
            '--output_noneu',
            required=True,
            help='No neuron frame'
            )

    args = parser.parse_args()
    if args.use_boss:
        seg, syn = get_boss_data(args)
    else:
        seg, syn = get_file_data(args)
    threshold = 0.8
    if args.threshold:
        threshold = args.threshold 
    blob_thres = 4000
    if args.blob:
        blob_thres = args.blob
    dilation = 5
    if args.dilation:
        dilation = args.dilation

    neu_syn_list,syn_list = edge_list_cv(seg, syn, dilation=dilation, syn_thres=threshold, blob_thres=blob)
    neu_syn_list = pd.DataFrame.from_dict(neu_syn_list)
    syn_list = pd.DataFrame.from_dict(syn_list)
    
    print('done')
    neu_syn_list.to_pickle(args.output)
    syn_list.to_pickle(args.output_noneu)
#    np.savez(args.output, neu_syn_list=neu_syn_list, syn_list=syn_list)
    
