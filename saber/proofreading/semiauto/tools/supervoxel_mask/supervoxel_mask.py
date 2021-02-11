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
    parser = argparse.ArgumentParser(description="Masking Tool")
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument("-i", "--input", required=True, help="Input numpy array file")
    parser.add_argument(
        "-id", "--supervoxel_ids", required=False, help="IDs numpy array file"
    )
    parser.add_argument("-o", "--output", required=True, help="Output file")
    return parser


def mask(segmentation, ids=None):
    if ids:
        # logic for masking specific IDs
        pass
    else:
        # demo 
        random_ids = np.random.choice(np.unique(segmentation), size=2)
        mask_array = np.zeros(segmentation.shape, dtype=np.uint8)
        mask_array[segmentation==random_ids[0]] = 1
        mask_array[segmentation==random_ids[1]] = 1
        return mask_array

def main():
    parser = get_parser()
    args = parser.parse_args()
    input_array = np.load(args.input)
    mask_array = mask(input_array, args.supervoxel_ids)
    np.save(args.output, mask_array)

if __name__ == "__main__":
    main()
