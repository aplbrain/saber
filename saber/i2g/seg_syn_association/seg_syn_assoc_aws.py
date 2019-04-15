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

import boto3
import botocore


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

def get_aws_data(args):
    session = boto3.Session(
        aws_access_key_id=args.access_id,               
        aws_secret_access_key=args.token,
        region_name='us-east-1'
    )
    s3 = session.resource('s3')

    try:
        s3.Bucket(args.bucket).download_file(args.seg_file, '/data/seg.npy')
        s3.Bucket(args.bucket).download_file(args.lbl_file, '/data/syn.npy')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    seg_data = np.load('/data/seg.npy')
    syn_data = np.load('/data/syn.npy')

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
            '--bucket',
            required=False,
            help='s3 bucket'
            )
    parser.add_argument(
            '--token',
            required=False,
            help='s3 bucket token'
            )
    parser.add_argument(
            '--access_id',
            required=False,
            help='s3 bucket access_id'
            )
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
    seg, syn = get_aws_data(args)
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
