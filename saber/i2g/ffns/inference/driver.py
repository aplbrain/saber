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

import argparse
import os
import numpy as np
import npy2h5
from subprocess import call

def get_parser():
    parser = argparse.ArgumentParser(description='Flood-filling Networks Script')
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument(
            '-i',
            '--input_file',
            required=True,
            help='Raw EM Volume')
    parser.add_argument(
            '-c',
            '--config_file',
            required=True,
            help='Configuration File')
    parser.add_argument(
            '-d',
            '--bound_start',
            required=True,
            help='X,Y,Z start bound')
    parser.add_argument(
            '-p',
            '--bound_stop',
            required=True,
            help='X,Y,Z stop bound')
    parser.add_argument(
            '-o',
            '--outfile',
            required=True,
            help='Output file')
    return parser

def bounding_box_parser(start,stop):
    print(start,stop)
    start_list = start.split(',')
    stop_list = stop.split(',')
    if len(start_list) != 3 and len(stop_list) != 3:
        raise Exception('Unable to parse bounding box. {}:{}'.format(start,stop))
    flag = "start {{ x:{} y:{} z:{} }} size {{ x:{} y:{} z:{} }}".format(
        start_list[0], start_list[1], start_list[2],
        stop_list[0], stop_list[1], stop_list[2]
    )
    return flag

def deploy(args):
    npy2h5.convert(args.input_file, 'data/raw.h5', 'raw')
    bounding_box = bounding_box_parser(args.bound_start, args.bound_stop)
    with open(args.config_file) as params:
        params = params.read()
    ec = call(['python', 'run_inference.py', 
    '--inference_request={}'.format(params), 
    "--bounding_box", bounding_box])
    if ec != 0:
        raise SystemError('Child process failed with exit code {}... exiting...'.format(ec)) 
    for file in os.listdir('/results/0/0/'):
        if file[-4:] == '.npz':
            data = np.load('/results/0/0/'+file)
            seg_arr = data['segmentation']
    with open(args.outfile, 'wb') as f:
        np.save(f,seg_arr)
    return


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    deploy(args)
    print('Done')


