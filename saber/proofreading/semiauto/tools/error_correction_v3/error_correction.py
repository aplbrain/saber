import argparse
import os
import time
import tempfile
import pickle 

import numpy as np
import boto3
import fastremap
from intern.remote.boss import BossRemote
from segmentation_error import SegmentationError

def get_parser():
    parser = argparse.ArgumentParser(description="Error Correction Tool")
    parser.set_defaults(func=lambda _: parser.print_help())
    
    # BossDB Arguments
    parser.add_argument("--seg_uri", required=False, help="bossDB Segmentation Channel")
    parser.add_argument("--host", required=False, default="api.bossdb.io", help="bossDB Host")
    parser.add_argument("--token", required=False, default="public", help="bossDB Token")
    
    # AWS Args
    parser.add_argument("--queue", required=True, help="AWS SQS Queue Name")
    
    return parser


def process_messages(args):
    sqs = boto3.client('sqs')
    queue_url = sqs.get_queue_url(QueueName=args.queue)['QueueUrl']
    while True: 
        message = sqs.receive_message(QueueUrl=queue_url)['Messages']
        if len(message) == 0:
            # Possibly done with all messages. Wait 5 minutes.
            time.sleep(300)

            # Check if there is a new message.
            message = sqs.recieve_message(QueueUrl=queue_url)["Messages"]
            if len(message) == 0:
                break
        status = process_error(args, message[0]['Body'])
        if status:
            print("Message successfully processed.")
        else:
            print("Message failed to be processed. Deleting anyways for now.")
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message[0]['ReceiptHandle'])


def process_error(args, message):
    s3 = boto3.client('s3')
    bucket, key = message.split('/', 1)
    try:
        with tempfile.TemporaryFile() as fp:
            s3.download_fileobj(bucket, key, fp)
            fp.seek(0)
            error = pickle.load(fp)
        if error.error_type == 'merge':
            return process_merge_error(args, error)
        else:
            return process_split_error(args, error)
    except Exception as e:
        print(f"Error: {e}")
        return False


def process_split_error(args, error):
    rmt = BossRemote({
        "protocol": "https",
        "host": error.host,
        "token": args.token
    })
    resource = rmt.get_channel(error.channel_segmentation, error.collection, error.experiment)
    if len(error.ids) != 2:
        print("Keypoint ID value error. Only 2 keypoint IDs allowed.")
        return False
    
    # Get the cuboids for each ID
    cuboids_id1 = rmt.get_cuboids_from_id(resource, resolution=error.resolution, id=error.ids[0])['cuboids']
    cuboids_id2 = rmt.get_cuboids_from_id(resource, resolution=error.resolution, id=error.ids[1])['cuboids']

    # Get the intersection for the IDs. In other words, only get the cuboids that contain both of the IDs.
    all_cuboids = set(cuboids_id1) & set(cuboids_id2)

    # Temporary threshold to not blow up bossDB.
    if len(all_cuboids) > 100:
        print("Too many cuboids to download.")
        return False
    
    # Fix all the cuboids iteratively. 
    for cuboid in all_cuboids:
        x_rng = [cuboid[0], cuboid[0]+512]
        y_rng = [cuboid[1], cuboid[1]+512]
        z_rng = [cuboid[2], cuboid[2]+16]

        # Download data
        data = rmt.get_cutout(resource, error.resolution, x_rng, y_rng, z_rng)
        
        # Remap IDs
        remap = fastremap.remap(
            data, 
            {error.ids[0]: error.ids[1]}, 
            preserve_missing_labels=True, 
            in_place=True
        )

        # Upload fixed data
        rmt.create_cutout(resource, error.resolution, x_rng, y_rng, z_rng, remap)
    
    return True

def process_merge_error(args, error):
    # Find a way to process split errors. 
    pass


if __name__ == "__main__":
    # Get parser from CWL definition
    parser = get_parser()
    args = parser.parse_args()
    
    # Run Algorithm
    process_messages(args)