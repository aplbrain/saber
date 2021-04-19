# Copyright 2021 The Johns Hopkins University Applied Physics Laboratory
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
import os
import pickle
import tempfile

import numpy as np
import boto3

from intern.remote.boss import BossRemote
from intern import array
from segmentation_error import SegmentationError


def get_parser():
    parser = argparse.ArgumentParser(description="Error Detection Tool")
    parser.set_defaults(func=lambda _: parser.print_help())
    
    # BossDB Arguments
    parser.add_argument("--image_uri", required=False, help="bossDB Image Channel")
    parser.add_argument("--seg_uri", required=True, help="bossDB Segmentation Channel")
    parser.add_argument("--xmin", required=True, type=int, help="Xmin")
    parser.add_argument("--xmax", required=True, type=int, help="Xmax")
    parser.add_argument("--ymin", required=True, type=int, help="Ymin")
    parser.add_argument("--ymax", required=True, type=int, help="Ymax")
    parser.add_argument("--zmin", required=True, type=int, help="Zmin")
    parser.add_argument("--zmax", required=True, type=int, help="Zmax")
    parser.add_argument("--host", required=False, default="api.bossdb.io", help="bossDB Host")
    parser.add_argument("--token", required=False, default="public", help="bossDB Token")
    parser.add_argument("--resolution", required=False, default=0, help="bossDB Resolution")

    # TODO: Error Detection Algo Arguments

    # Local Args
    parser.add_argument("--output_file", required=False, help="Output Filename")
    
    # AWS Args
    parser.add_argument("--queue", required=False, help="AWS SQS Queue Name")
    parser.add_argument("--bucket", required=False, help="AWS S3 Bucket Name and prefix")
    
    return parser


def download_data(args, channel="segmentation"):
    config = {
        "protocol": "https",
        "host": args.host,
        "token": args.token
    }
    if channel == "segmentation":
        volume = array(args.seg_uri, resolution=args.resolution, boss_config=config)
    elif channel == "image":
        volume = array(args.image_uri, resolution=args.resolution, boss_config=config)
    else:
        print(f"Channel {channel} not valid. Must be ['Segmentation'|'Image']")
        return
    data = volume[args.zmin:args.zmax, args.ymin:args.ymax, args.xmin:args.xmax]
    # Return data in X,Y,Z
    return data.T


def detect_errors(args):
    # Download segmentation data
    try:
        data = download_data(args, channel="segmentation")
    except Exception as e:
        raise Exception(f"Failed to download segmentation data. {e}")

    # Download image data
    if args.image_uri:
        try:
            data = download_data(args, channel="image")
        except Exception as e:
            raise Exception(f"Failed to download image data. {e}")
    
    error_list = []
    # Run Error Detection on this volume:
    # TODO: Add Error detection algorithm 
    # Input: Flat segmentation
    # Returns: SegmentationError Objects 

    # Placeholder code
    bboxes = generate_random_bboxes((100, 100, 5), data.shape, 10)
    # Once we have detected errors. place them in error detection class. 
    if len(bboxes) == 0:
        print("No errors found in this volume.")
        return
    
    for bbox in bboxes:
        subvolume = data[
            bbox[0][0]:bbox[0][1],
            bbox[1][0]:bbox[1][1],
            bbox[2][0]:bbox[2][1],
        ]
        ids = np.random.choice(np.unique(subvolume), size=2, replace=False)
        error = SegmentationError(
            host=args.host,
            seg_uri=args.seg_uri,
            image_uri=args.image_uri,
            resolution=args.resolution,
            error_type="merge",
            x_bounds=bbox[0],
            y_bounds=bbox[1],
            z_bounds=bbox[2],
            ids=tuple(ids)
        )
        error_list.append(error)

    return error_list

def save_errors(output_name, error_list):
    with open(output_name, 'wb') as f:
        pickle.dump(error_list, f)

def upload_errors(queue, bucket, error_list):
    # Get the service resource
    s3 = boto3.client('s3')
    sqs = boto3.client('sqs')
    queue_url = sqs.get_queue_url(QueueName=queue)['QueueUrl']
    
    if "/" in bucket:
        bucket, prefix = bucket.split('/')
    
    for error in error_list:
        if prefix:
            key = os.path.join(prefix, error.uuid)
        else:
            key = error.uuid
        response = sqs.send_message(QueueUrl=queue_url, MessageBody=os.path.join(bucket, key))
        with tempfile.TemporaryFile() as fp:
            pickle.dump(error, fp)
            fp.seek(0)
            s3.upload_fileobj(fp, bucket, key)


def generate_random_bboxes(shape, extents, n=1):
    """
    Generate n number of random bounding boxes in the data. Useful for testing purposes.

    shape (tuple[int]): shape of the data
    extents (tuple(int))
    """
    bboxes = []
    for i in range(n):
        x_max = extents[0] - shape[0]
        y_max = extents[1] - shape[1]
        z_max = extents[2] - shape[2]

        x_start = np.random.randint(x_max)
        y_start = np.random.randint(y_max)
        z_start = np.random.randint(z_max)

        bboxes.append(
            (
                [x_start, x_start+shape[0]],
                [y_start, y_start+shape[1]],
                [z_start, z_start+shape[2]]
            )
        )
    return bboxes

if __name__ == "__main__":
    # Get parser from CWL definition
    parser = get_parser()
    args = parser.parse_args()
    
    # Run Algorithm
    error_list = detect_errors(args)

    # Check if we want output
    if args.output_file:
        save_errors(args.output_file, error_list)

    # check if we want AWS
    if args.queue and args.bucket:
        upload_errors(args.queue, args.bucket, error_list)
