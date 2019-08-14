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
import os

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
    parser.add_argument('--num_iterations', type=int, default=1,
                        help='Number of training iterations')
    parser.add_argument('--use_mito', type=int, default=0,
                        help='Toggles context-aware training with mitochrondria prediciton (0 or 1)')
    return parser

def train(args):
    call(['neuroproof_graph_learn', args.ws_file, args.pred_file, args.gt_file, args.num_iterations, args.use_mito])
    os.rename('classifier.xml', args.outfile)

def deploy(args):
    #probability map
    pass


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    if(int(args.mode)==0):
        train(args)
    else:
        deploy(args)


