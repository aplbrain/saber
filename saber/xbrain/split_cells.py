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
import itertools
import numpy as np
sphere_radius = 5
#Take output of cell detect step, split into two streams- one list of cells, the other the map of cells
def split_cells(args):
    cells = np.load(args.input)
    cell_map = cells[1]
    cell_list = cells[0]
    with open(args.map_output, 'wb') as f:
        np.save(f, cell_map)

    # Make volume out of cell_list
    cell_centroid_volume = np.zeros(cell_map.shape)
    for cell in cell_list:
        axes_range = [[],[],[]] 
        for i,axes in enumerate(cell[:3]):
            min_range = max(int(axes-args.sphere_size), 0)
            max_range = min(int(axes+args.sphere_size), cell_map.shape[i]-1)
            axes_range[i]=range(min_range, max_range)
        coords = list(itertools.product(*axes_range))
        for pixel in coords:
            if np.linalg.norm(np.array(cell[:3])-np.array(pixel)) <= args.sphere_size:
                cell_centroid_volume[pixel] = 1 
    with open(args.list_output, 'wb') as f:
        np.save(f, cell_list)
    with open(args.centroid_volume_output, 'wb') as f:
        np.save(f, cell_centroid_volume)
    

def main():
    parser = argparse.ArgumentParser(description='cell results splitting script')
    parser.set_defaults(func=lambda _: parser.print_help())

    parser.add_argument('-i', '--input', required=True, help='Input file')
    parser.add_argument('--map_output', required=True, help='Map Output file')
    parser.add_argument('--list_output', required=True, help='List Output file')
    parser.add_argument('--centroid_volume_output', required=True, help='Output volume with spheres')
    parser.add_argument('--sphere_size', required=False, help='Size of the spheres in the centroids volume', default=5, type=int)
    args = parser.parse_args()
    split_cells(args)

if __name__ == '__main__':
    main()
