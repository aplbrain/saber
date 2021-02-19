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

import argparse
import csv
import json

import numpy as np
import fastremap
from skimage.measure import label, regionprops

def get_parser():
    parser = argparse.ArgumentParser(description="Error Detection Tool")
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument("-s", "--seg", required=True, help="Input segmentation file")
    parser.add_argument("-f", "--source", required=True, help="bossDB URI")
    parser.add_argument("-i", "--ids", required=False, help="IDs file")
    parser.add_argument("-o", "--output", required=True, help="Output CSV filename")
    return parser

def generate_ng_link(centroid, segments, source="boss://https://api.bossdb.io/"):
    state = {
        "layers": [
            {
                "source": source,
                "type": "segmentation",
                "name": "seg",
                "segments" : segments
            },
        ],
        "navigation": {
            "pose": {
                "position": {
                    "voxelCoordinates": [
                        centroid[2],
                        centroid[1],
                        centroid[1]
                    ],
                },
            },
            "zoomFactor": 8,
        },
        "showAxisLines": False,
        "layout": "xy",
    }
    
    return "https://neuroglancer.bossdb.io/#!"+ json.dumps(state)


def detect_errors(seg, source, output, ids=None):
    """
    Detect errors in 3D UINT64 segmentation data. 

    Args:
        seg (numpy.array) : segmentation volume
        source (str) : bossdb URI
        output (str) : output file name. Outputs saved as CSV.
        ids (numpy.array) : 1D of segment IDs to detect on. 
    """
    if ids is None:
        ids = fastremap.unique(seg)

    # Below is code for demo. It just picks two IDs and sees if they touch at some point. 
    connections = 0
    
    csv_rows = []
    csv_columns = ["ID1", "ID2", "Centroid", "NG Link"]
    while connections < 10:
        random_ids = np.random.choice(ids, size=2)
        mask = fastremap.mask_except(seg, list(random_ids)).astype('bool')
        labels, ncomponents = label(mask, return_num=True)
        if ncomponents == 1:
            connections += 1
            rp = regionprops(labels)
            centroid = tuple(map(int, rp[0].centroid))
            csv_rows.append({
                "ID1":random_ids[0], 
                "ID2":random_ids[1], 
                "Centroid": centroid, 
                "NG Link": generate_ng_link(centroid, list(map(str, random_ids)), source)
            })
            
    try:
        with open(output, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in csv_rows:
                writer.writerow(data)
    except IOError:
        print("I/O error")
    
def main():
    # Get parser from CWL definition
    parser = get_parser()
    args = parser.parse_args()
    
    # Load input arrays
    seg = np.load(args.seg)
    if args.ids:
        ids = np.load(args.ids)
    else:
        ids = None

    source = args.source
    output = args.output
    
    # Run Algorithm
    detect_errors(seg, source, output, ids)

if __name__ == "__main__":
    main()
