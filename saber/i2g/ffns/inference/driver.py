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
from subprocess import call

def get_parser():
    parser = argparse.ArgumentParser(description='Flood-filling Networks Script')
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument(
            '-c',
            '--config_file',
            required=True,
            help='Configuration File')
    parser.add_argument(
            '-bb',
            '--bounding_box',
            required=True,
            help='X,Y,Z Extents')
    parser.add_argument(
            '-o',
            '--outfile',
            required=True,
            help='Output file')
    return parser

def deploy(args):
    with open(args.config_file) as params:
        params = params.read()
    ec = call(['python', 'run_inference.py', 
    '--inference_request={}'.format(params), 
    "--bounding_box", args.bounding_box[1:-1]])
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
    print(args)
    deploy(args)
    print('Done')


