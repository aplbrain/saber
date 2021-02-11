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
from scipy.ndimage.measurements import label
import math
import argparse


def get_parser():
    parser = argparse.ArgumentParser(description="Error Detection Tool")
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument("-b", "--binary", required=True, help="Input binary file")
    parser.add_argument("-i", "--image", required=True, help="Input image file")
    parser.add_argument("-o", "--output", required=True, help="Output file")
    return parser


def detect_errors(binary, image):
    # demo 
    structure = np.ones((3, 3), dtype="uint8")
    labeled, ncomponents = label(binary, structure)
    ids = image[labeled>0]
    if ncomponents == 1:
        return True
    else:
        return False

def main():
    parser = get_parser()
    args = parser.parse_args()
    image_array = np.load(args.image)
    mask_array = np.load(args.binary)
    try:
        error = detect_errors(mask_array, image_array)
    except:
        error = True
        with open(args.output, 'w') as f:
            if error:
                f.write("Connected components.")
            else:
                f.write("Not connected components.") 

if __name__ == "__main__":
    main()
