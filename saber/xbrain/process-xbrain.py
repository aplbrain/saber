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

from xbrain import classify_pixel, detect_cells, segment_vessels, dense_f1_3D

#runall things
def runall(args):
    volume = np.load(args.input)
    # run classification
    if args.threads == -1:
        import multiprocessing
        args.threads = multiprocessing.cpu_count()
    
    probability_maps = classify_pixel(
        volume,
        args.classifier,
        threads=args.threads,
        ram=args.ram
    )
    cell_prob_map = probability_maps[:, :, :, args.cell_index]
    vessel_prob_map = probability_maps[:, :, :, args.vessel_index]
    centroids, cell_map = detect_cells(
        cell_prob_map,
        args.threshold,
        args.stop,
        args.initial_template_size,
        args.dilation,
        args.max_cells
    )
    with open(args.output, 'wb') as f:
        np.save(f, cell_map)

#optimize given gt data
def optimize(args):
    volume = np.load(args.input)
    cell_gt = np.load(args.cellgt)
    # run classification
    if args.threads == -1:
        import multiprocessing
        args.threads = multiprocessing.cpu_count()
    
    probability_maps = classify_pixel(
        volume,
        args.classifier,
        threads=args.threads,
        ram=args.ram
    )
    cell_prob_map = probability_maps[:, :, :, args.cell_index]
    #vessel_prob_map = probability_maps[:, :, :, 1]
    centroids, cell_map = detect_cells(
        cell_prob_map,
        args.threshold,
        args.stop,
        args.initial_template_size,
        args.dilation,
        args.max_cells
    )
    f1 = dense_f1_3D(cell_map,cell_gt)
    with open(args.output, 'wb') as f:
        np.save(f, f1)

def membrane_classify(args):
    volume = np.load(args.input)
    # run classification
    if args.threads == -1:
        import multiprocessing
        args.threads = multiprocessing.cpu_count()
    
    probability_maps = classify_pixel(
        volume,
        args.classifier,
        threads=args.threads,
        ram=args.ram
    )
    with open(args.output, 'wb') as f:
        np.save(f, probability_maps)

def cell_detect(args):
    probability_maps = np.load(args.input)
    cell_prob_map = probability_maps[:, :, :, args.cell_index]
    centroids, cell_map = detect_cells(
        cell_prob_map,
        args.threshold,
        args.stop,
        args.initial_template_size,
        args.dilation,
        args.max_cells
    )
    with open(args.output, 'wb') as f:
        np.save(f, (centroids, cell_map))

def vessel_segment(args):
    probability_maps = np.load(args.input)
    vessel_prob_map = probability_maps[:, :, :, args.vessel_index]
    vessel_map = segment_vessels(
        vessel_prob_map,
        args.threshold,
        args.dilation,
        args.minimum
    )
    with open(args.output, 'wb') as f:
        np.save(f, vessel_map)

def main():
    parser = argparse.ArgumentParser(description='xbrain processing script')
    parent_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(title='commands')

    parser.set_defaults(func=lambda _: parser.print_help())

    parent_parser.add_argument('-i', '--input', required=True, help='Input file')
    parent_parser.add_argument('-o', '--output', required=True, help='Output file')
    #parent_parser.add_argument('-c', '--classifier', required=True, help='Classifier file')

    parser_classify = subparsers.add_parser('classify', help='Classify pixels',
                                            parents=[parent_parser])
    parser_detect = subparsers.add_parser('detect', help='Detect cells', parents=[parent_parser])
    parser_segment = subparsers.add_parser('segment', help='Segment vessels',
                                           parents=[parent_parser])
    parser_runall = subparsers.add_parser('runall', help='Run entire pipeline',
                                           parents=[parent_parser])
    parser_optimize = subparsers.add_parser('optimize', help='Optimize entire pipeline using F1 metric',
                                           parents=[parent_parser])


    parser_classify.add_argument('-c', '--classifier', required=True, default='/classifier/xbrain.ilp', help='Classifier file')

    parser_classify.add_argument('--ram', type=int, default=4096,
                                 help='Amount of RAM to use for classification')
    parser_classify.add_argument(
        '--threads', type=int, default=-1,
        help='Number of threads to use (-1 means number of CPUs available)'
    )
    parser_classify.set_defaults(func=membrane_classify)

    parser_detect.add_argument('--threshold', type=float, default=0.2, help='Cell probability threshold')
    parser_detect.add_argument('--stop', type=float, default=0.47, help='Stopping criterion')
    parser_detect.add_argument('--initial-template-size', dest='initial_template_size', type=int,
                               default=18, help='Initial template size')
    parser_detect.add_argument('--dilation', type=int, default=8, help='Dilation size')
    parser_detect.add_argument('--max-cells', dest='max_cells', type=int, default=500,
                               help='Max number of cells')
    parser_detect.add_argument('--cell-index', type=int, default=1, help='Index in the classify output that corresponds to cell bodies')
    parser_detect.set_defaults(func=cell_detect)

    parser_segment.add_argument('--threshold', type=float, default=0.68, help='Vessel probability threshold')
    parser_segment.add_argument('--dilation', type=int, default=3, help='Dilation size')
    parser_segment.add_argument('--minimum', type=int, default=4000, help='Minimum size')
    parser_segment.add_argument('--vessel-index', type=int, default=1, help='Index in the classify output that corresponds to vessels')

    parser_segment.set_defaults(func=vessel_segment)

    parser_runall.add_argument('--ram', type=int, default=4096,
                                 help='Amount of RAM to use for classification')
    parser_runall.add_argument(
        '--threads', type=int, default=-1,
        help='Number of threads to use (-1 means number of CPUs available)'
    )
    
    parser_runall.add_argument('--threshold', type=float, default=0.2, help='Cell probability threshold')
    parser_runall.add_argument('--stop', type=float, default=0.47, help='Stopping criterion')
    parser_runall.add_argument('--initial-template-size', dest='initial_template_size', type=int,
                               default=18, help='Initial template size')
    parser_runall.add_argument('--dilation', type=int, default=8, help='Dilation size')
    parser_runall.add_argument('--max-cells', dest='max_cells', type=int, default=500,
                               help='Max number of cells')
    parser_runall.set_defaults(func=runall)

    parser_optimize.add_argument('--threshold', type=float, default=0.2, help='Cell probability threshold')
    parser_optimize.add_argument('--stop', type=float, default=0.47, help='Stopping criterion')
    parser_optimize.add_argument('--initial-template-size', dest='initial_template_size', type=int,
                               default=18, help='Initial template size')
    parser_optimize.add_argument('--dilation', type=int, default=8, help='Dilation size')
    parser_optimize.add_argument('--max-cells', dest='max_cells', type=int, default=500,
                               help='Max number of cells')
    parser_optimize.add_argument('--cellgt', required=True, help='Cell ground truth file')
    parser_optimize.set_defaults(func=optimize)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
