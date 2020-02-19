# Copyright 2020 The Johns Hopkins University Applied Physics Laboratory
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

import numpy as np
import math
import argparse

def get_parser():
    parser = argparse.ArgumentParser(description='Thresholding Tool')
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument(
            '-i',
            '--input',
            required=True,
            help='Input numpy array file')
    parser.add_argument(
            '-gt',
            '--groundtruth',
            required=False,
            help='Groundtruth numpy array file')
    parser.add_argument(
            '-t',
            '--threshold',
            required=True,
            help='Threshold, [0,1]')
    parser.add_argument(
            '-o',
            '--outfile',
            required=True,
            help='Output file')
    return parser

def apply_threshold(probability_map, threshold):
    """
    Aapplies a threshold to a real-valued probabilty map

    Args:
        probability_map: (numPy Array)
        threshold: (float) Threshold to apply 
    Returns:
        numPy Array
    """
    threshold = float(threshold)
    if threshold < 0 or threshold > 1:
        raise ValueError("Invalid threshold. Threshold must be between 0 and 1.")
    if probability_map.ndim == 4:
        # Input data is in Z, Chan, Y, X (Xbrain defacto)
        probability_map = np.squeeze(probability_map).T
    normal = (probability_map - np.min(probability_map))/(np.max(probability_map)-np.min(probability_map))
    normal[normal<threshold] = 0
    normal[normal>=threshold] = 1
    return normal

def f1_score(binary_map, binary_gt=None):
    """
    Calculates f1 score on thresholded array. 
    """
    beta = 2
    true_detect = np.sum(np.logical_and(binary_map,binary_gt).astype(int).ravel())
    detections = np.sum(binary_map.ravel())
    true_positives = np.sum(binary_gt.ravel())
    if detections>0:                
        precision = true_detect/detections
    else:
        precision = 0
    if true_positives>0:    
        recall = true_detect/true_positives
    else:
        recall = 0
                    
    if precision + recall >0:
        f1 = (1+math.pow(beta,2)) * (precision*recall)/(math.pow(beta,2)*precision + recall)
    else:
        f1 = 0
    return f1

def main():
    parser = get_parser()
    args = parser.parse_args()
    input_array = np.load(args.input)
    output_array = apply_threshold(input_array, args.threshold)
    np.save(args.outfile, output_array)
    
    if args.groundtruth: 
        groundtruth_array = np.load(args.groundtruth)
        f1 = f1_score(output_array, groundtruth_array)
        print("F1: {}".format(f1))

if __name__ == "__main__":
    main()
    