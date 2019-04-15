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
import sys

import numpy as np

from santiago import graph_error

def metrics(args):
    true_graph = np.load(args.gtinput)
    test_graph = np.load(args.siminput)
    f1 = graph_error(true_graph,test_graph)
    with open(args.output, 'wb') as f:
        np.save(f, f1)

def main():
    parser = argparse.ArgumentParser(description='I2G graph generation processing script')
    parent_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(title='commands')

    parser.set_defaults(func=lambda _: parser.print_help())

    parser.add_argument('--gtinput', required=True, help='Ground truth graph input file')
    parser.add_argument('--siminput', required=True, help='Pipeline graph input file')
    parser.add_argument('--output', required=True, help='Output file')
    
    args = parser.parse_args()
    metrics(args)

if __name__ == '__main__':
    main()