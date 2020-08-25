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
from skimage.measure import label, regionprops
import argparse


def get_parser():
    parser = argparse.ArgumentParser(description="Blob Detect Tool")
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument("-i", "--input", required=True, help="Input numpy array file")
    parser.add_argument(
        "--min", required=True, help="minimum area for region to be counted"
    )
    parser.add_argument(
        "--max", required=True, help="maximum area for region to be counted"
    )
    parser.add_argument("-o", "--outfile", required=True, help="Output file")
    return parser


def blob_detect(dense_map, min, max):
    labels = label(dense_map)
    regions = regionprops(labels)
    output = np.empty((0, dense_map.ndim))
    for props in regions:
        if props.area >= float(min) and props.area <= float(max):
            output = np.concatenate((output, [props.centroid]), axis=0)
    return output


def main():
    parser = get_parser()
    args = parser.parse_args()
    input_array = np.load(args.input)
    output_array = blob_detect(input_array, min=args.min, max=args.max)
    np.save(args.outfile, output_array)


if __name__ == "__main__":
    main()
