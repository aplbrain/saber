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
            '--image_mean',
            required=True,
            help='image mean')
    parser.add_argument(
            '--image_stddev',
            required=True,
            help='image std dev')
    parser.add_argument(
            '--depth',
            required=True,
            help='depth, fov size, deltas')
    parser.add_argument(
            '--fov_size',
            required=True,
            help='depth, fov size, deltas')
    parser.add_argument(
            '--deltas',
            required=True,
            help='depth, fov size, deltas')
    parser.add_argument(
            '--init_activation',
            required=True,
            help='init activation')
    parser.add_argument(
            '--pad_value',
            required=True,
            help='pad value')
    parser.add_argument(
            '--move_threshold',
            required=True,
            help='move threshold')
    parser.add_argument(
            '--min_boundary_dist',
            required=True,
            help='min boundary dist')
    parser.add_argument(
            '--segment_threshold',
            required=True,
            help='segment thresh')
    parser.add_argument(
            '--min_segment_size',
            required=True,
            help='segment size')
    parser.add_argument(
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

def config_file_parser(args):
    model_args = "\"{{\\\"depth\\\": {}, \\\"fov_size\\\": [{}], \\\"deltas\\\": [{}]}}\"".format(
        args.depth,
        args.fov_size,
        args.deltas
    )
    min_boundary_dist = "{{ x: {} y: {} z: {}}}".format(
        args.min_boundary_dist.split(',')[0],
        args.min_boundary_dist.split(',')[1],
        args.min_boundary_dist.split(',')[2]
    )
    params = {
    'image_mean': args.image_mean,
    'image_stddev': args.image_stddev,
    'model_args': model_args,
    'init_activation': args.init_activation,
    'pad_value': args.pad_value,
    'move_threshold': args.move_threshold,
    'min_boundary_dist': min_boundary_dist,
    'segment_threshold': args.segment_threshold,
    'min_segment_size': args.min_segment_size
    }
    
    config_file = open('config.pbtxt','w')
    with open('config_template.pbtxt', 'r') as template_file:
        for line in template_file.readlines():
            if "{}" in line:
                param = line.split(':')[0].strip()
                if param in params.keys():
                    line = line.format(params[param])
                elif 'min_boundary_dist' in line:
                    line = line.format(params['min_boundary_dist'])
            config_file.write(line)
    config_file.close()

def bounding_box_parser(start,stop):
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
    config_file_parser(args)
    npy2h5.convert(args.input_file, '/data/raw.h5', 'raw')
    bounding_box = bounding_box_parser(args.bound_start, args.bound_stop)
    with open('config.pbtxt') as params:
        params = params.read()
    ec = call(['python', 'run_inference.py', 
    '--inference_request={}'.format(params), 
    "--bounding_box", bounding_box])
    if ec != 0:
        raise SystemError('Child process failed with exit code {}... exiting...'.format(ec)) 
    for file in os.listdir('/results/0/0/'):
        if file[-4:] == '.npz':
            data = np.load('/results/0/0/'+file)
            seg_arr = data['segmentation'].astype(np.uint64)
    with open(args.outfile, 'wb') as f:
        np.save(f,seg_arr)
    return


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    deploy(args)
    print('Done')


