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

from subprocess import call
import argparse
import h5py
import numpy as np

def get_parser():
    parser = argparse.ArgumentParser(description='Neuroproof Aggolmeration script')
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument(
            '-m',
            '--mode',
            required=True,
            help='Train(0) or Deploy(1)')
    parser.add_argument(
            '--ws_file',
            required=True,
            help='Watershed file (oversegmented)')
    parser.add_argument(
            '--pred_file',
            required=True,
            help='Prediction file (channel 2 must be mitochondria if use_mito = 1)')
    parser.add_argument(
            '--gt_file',
            required=False,
            help='Ground truth file')
    parser.add_argument(
            '--train_file',
            required=False,
            help='Pretrained classifier file')
    parser.add_argument(
            '-o',
            '--outfile',
            required=True,
            help='Output file')
    parser.add_argument('--num_iterations', default='1',
                        help='Number of training iterations')
    parser.add_argument('--use_mito', default='0',
                        help='Toggles context-aware training with mitochrondria prediciton (0 or 1)')
    return parser

def npy_to_h5(file):
    raw_arr = np.load(file)
    fn = file.split('.')[0] + '.h5'
    hf = h5py.File(fn, 'w')
    hf.create_dataset('stack', data = raw_arr)
    hf.close()
    return fn

def train(args):
    files = [args.ws_file, args.pred_file, args.gt_file]
    for i in range(len(files)):
        if files[i][-2:] != 'h5' and files[i] != '':
            files[i] = npy_to_h5(files[i])
    proc = call(['neuroproof_graph_learn', files[0], files[1], files[2],
    "--num-iterations", args.num_iterations,
    "--use_mito", args.use_mito,
    "--classifier-name", args.outfile])
    if proc != 0:
        raise SystemError('Child process failed with exit code {}... exiting...'.format(proc)) 

def deploy(args):
    files = [args.ws_file, args.pred_file]
    for i in range(len(files)):
        if files[i][-2:] != 'h5' and files[i] != '':
            files[i] = npy_to_h5(files[i])
    proc = call(['neuroproof_graph_predict', files[0], files[1], args.train_file])
    if proc != 0:
        raise SystemError('Child process failed with exit code {}... exiting...'.format(proc)) 
    f = h5py.File('segmentation.h5', 'r')
    seg_array = f.get('stack')[()]
    np.save(args.outfile, seg_array)
    return

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    if(int(args.mode)==0):
        train(args)
    else:
        deploy(args)


