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

import argparse
import configparser
import os
import sys
import tempfile
import math 
import boto3
from intern.remote.dvid import DVIDRemote
from intern.resource.dvid.resource import DataInstanceResource
import numpy as np
from requests import HTTPError

def DVID_pull_cutout(args):
    if args.config:
        rmt = DVIDRemote(args.config)
    else:
        cfg = _generate_config(args.token, args)
        with open('intern.cfg', 'w') as f:
            cfg.write(f)
        rmt = DVIDRemote('intern.cfg')

    COLL_NAME = args.coll
    EXP_NAME = args.exp
    CHAN_NAME = args.chan

    # Create or get a channel to write to
    chan_setup = ChannelResource(
        CHAN_NAME, COLL_NAME, EXP_NAME, type=args.itype, datatype=args.dtype)
    try:
        chan_actual = rmt.get_project(chan_setup)
    except HTTPError:
        chan_actual = rmt.create_project(chan_setup)
    #get coordinate frame to determine padding bounds
    cfr = CoordinateFrameResource(args.coord)
    cfr_actual = rmt.get_project(cfr)
    x_min_bound = cfr_actual.x_start
    x_max_bound = cfr_actual.x_stop
    y_min_bound = cfr_actual.y_start
    y_max_bound = cfr_actual.y_stop
    z_min_bound = cfr_actual.z_start
    z_max_bound = cfr_actual.z_stop
    
    print('Data model setup.')

    xmin = np.max([x_min_bound,args.xmin-args.padding])
    xmax = np.min([x_max_bound,args.xmax+args.padding])   
    x_rng = [xmin,xmax] 
    ymin = np.max([y_min_bound,args.ymin-args.padding])
    ymax = np.min([y_max_bound,args.ymax+args.padding])   
    y_rng = [ymin,ymax]
    zmin = np.max([z_min_bound,args.zmin-args.padding])
    zmax = np.min([z_max_bound,args.zmax+args.padding])   
    z_rng = [zmin,zmax]
    # Verify that the cutout uploaded correctly.
    attempts = 0
    while attempts < 3:
        try:
            cutout_data = rmt.get_cutout(chan_actual, args.res, x_rng, y_rng, z_rng)
            break
        except HTTPError as e: 
            if attempts < 3:
                attempts += 1
                print("Obtained HTTP error from server. Trial {}".format(attempts))
            else:
                print("Failed 3 times: {}".format(e))
    #Data will be in Z,Y,X format
    #Change to X,Y,Z for pipeline
    cutout_data = np.transpose(cutout_data,(2,1,0))

    def _upload(f):
        print('Uploading to s3:/{}/{}'.format(args.bucket, args.output))
        s3 = boto3.resource('s3')
        f.seek(0, 0)
        s3.Object(args.bucket, args.output).put(Body=f)
    
    # Clean up.
    if args.bucket and args.s3_only:
        with tempfile.TemporaryFile() as f:
            np.save(f, cutout_data)
            _upload(f)
    else:
        with open(args.output, 'w+b') as f:
            np.save(f, cutout_data)
            if args.bucket:
                _upload(f)
    

#here we push a subset of padded data back to DVID
def DVID_push_cutout(args):
    if args.config:
        rmt = DVIDRemote(args.config)
    else:
        cfg = _generate_config(args.token, args)
        with open('intern.cfg', 'w') as f:
            cfg.write(f)
        rmt = DVIDRemote('intern.cfg')

    #data is desired range
    if args.bucket:
        s3 = boto3.resource('s3')
        with tempfile.TemporaryFile() as f:
            s3.Bucket(args.bucket).download_fileobj(args.input, f)
            f.seek(0, 0)
            data = np.load(f)
    else:
        data = np.load(args.input)

    numpyType = np.uint8
    if args.dtype=="uint32":
        numpyType = np.uint32
    elif args.dtype=="uint64":
        numpyType = np.uint64

    if  data.dtype != args.dtype:
        data = data.astype(numpyType)
    sources = []
    if  args.source:
        sources.append(args.source)

    COLL_NAME = args.coll
    EXP_NAME = args.exp
    CHAN_NAME = args.chan

    # Create or get a channel to write to
    chan_setup = ChannelResource(
        CHAN_NAME, COLL_NAME, EXP_NAME, type=args.itype, datatype=args.dtype, sources=sources)
    try:
        chan_actual = rmt.get_project(chan_setup)
    except HTTPError:
        chan_actual = rmt.create_project(chan_setup)

    #get coordinate frame to determine padding bounds
    cfr = CoordinateFrameResource(args.coord)
    cfr_actual = rmt.get_project(cfr)
    x_min_bound = cfr_actual.x_start
    x_max_bound = cfr_actual.x_stop
    y_min_bound = cfr_actual.y_start
    y_max_bound = cfr_actual.y_stop
    z_min_bound = cfr_actual.z_start
    z_max_bound = cfr_actual.z_stop

    print('Data model setup.')

    # Ranges use the Python convention where the number after the : is the stop
    # value.  Thus, x_rng specifies x values where: 0 <= x < 8.
    data_shape = data.shape #with padding, will be bigger than needed
    #find data cutoffs to get rid of padding
    # if nmin = 0, this means that the data wasn't padded on there to begin with
    xstart = args.padding if args.xmin != 0 else 0
    ystart = args.padding if args.ymin != 0 else 0
    zstart = args.padding if args.zmin != 0 else 0
    xend = data_shape[0] - args.padding
    yend = data_shape[1] - args.padding
    zend = data_shape[2] - args.padding

    # xstart = np.min([args.padding,args.xmin-x_min_bound])
    # xend = np.max([data.shape[0]-args.padding,data.shape[0]-(x_max_bound-args.xmax)])
    # ystart = np.min([args.padding,args.ymin-y_min_bound])
    # yend = np.max([data.shape[1]-args.padding,data.shape[1]-(y_max_bound-args.ymax)])
    # zstart = np.min([args.padding,args.zmin-z_min_bound])
    # zend = np.max([data.shape[2]-args.padding,data.shape[2]-(z_max_bound-args.zmax)])
    #get range which will be uploaded
    x_rng = [args.xmin, args.xmax]
    y_rng = [args.ymin, args.ymax]
    z_rng = [args.zmin, args.zmax]
    #Pipeline Data will be in X,Y,Z format
    #Change to Z,Y,X for upload
    data = np.transpose(data,(2,1,0))
    data = data[zstart:zend,ystart:yend,xstart:xend]
    data = data.copy(order='C')
    # Verify that the cutout uploaded correctly.
    attempts = 0
    while attempts < 3:
        try:
            rmt.create_cutout(chan_actual, args.res, x_rng, y_rng, z_rng, data)
            break
        except HTTPError as e: 
            if attempts < 3:
                attempts += 1
                print("These are the dimensions: ")
                print(data.shape)
                print("This is the data type:")
                print(data.dtype)
                print("Specified data type was:")
                print(args.dtype)
                print("Specified image type")
                print(args.itype)
                print("Obtained HTTP error from server. Trial {}".format(attempts))
                print("The error: {}".format(e))
            else:
                raise Exception("Failed 3 times: {}".format(e))
    # Clean up

def main():
    parser = argparse.ArgumentParser(description='dvid processing script')
    parent_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(title='commands')

    parser.set_defaults(func=lambda _: parser.print_help())

    parent_parser.add_argument('-b', '--bucket', default=None, help='S3 bucket to save to or load from')

    parent_parser.add_argument('--uuid', required=True, help='Root UUID of the repository')
    parent_parser.add_argument('--data_instance', required=True, help='Name of data instance within repository ')
    parent_parser.add_argument('--datatype', required=False, help='data type of the instance (uint8, uint16, uint64) defaults to uint8')
    parent_parser.add_argument('--host', required=True, help='Name of DVID host)

    parent_parser.add_argument('--res', type=int, help='Resolution')
    parent_parser.add_argument('--xmin', type=int, default=0, help='Xmin')
    parent_parser.add_argument('--xmax', type=int, default=1, help='Xmax')
    parent_parser.add_argument('--ymin', type=int, default=0, help='Ymin')
    parent_parser.add_argument('--ymax', type=int, default=1, help='Ymax')
    parent_parser.add_argument('--zmin', type=int, default=0, help='Zmin')
    parent_parser.add_argument('--zmax', type=int, default=1, help='Zmax')

    push_parser = subparsers.add_parser(
        'push', help='Push images to dvid', parents=[parent_parser]
    )
    pull_parser = subparsers.add_parser(
        'pull', help='Pull images from dvid and optionally save to AWS S3',
        parents=[parent_parser]
    )

    push_parser.add_argument('-i', '--input', required=True, help='Input file')
    push_parser.add_argument('--source', required=False, help='Source channel for upload')
    push_parser.set_defaults(func=boss_push_cutout)

    pull_parser.add_argument('-o', '--output', required=True, help='Output file')
    pull_parser.add_argument(
        '--s3-only', dest='s3_only', action='store_true', default=False, help='Only save output to AWS S3'
    )
    pull_parser.set_defaults(func=boss_pull_cutout)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

