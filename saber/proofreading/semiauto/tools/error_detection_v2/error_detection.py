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
from intern.remote.boss import BossRemote
import colocarpy

def get_parser():
    parser = argparse.ArgumentParser(description="Error Detection Tool")
    parser.set_defaults(func=lambda _: parser.print_help())
    
    # BossDB Arguments
    parser.add_argument("--channel", required=True, help="bossDB Channel")
    parser.add_argument("--experiment", required=True, help="bossDB experiment")
    parser.add_argument("--collection", required=True, help="bossDB collection")
    parser.add_argument("--xmin", required=True, type=int, help="Xmin")
    parser.add_argument("--xmax", required=True, type=int, help="Xmax")
    parser.add_argument("--ymin", required=True, type=int, help="Ymin")
    parser.add_argument("--ymax", required=True, type=int, help="Ymax")
    parser.add_argument("--zmin", required=True, type=int, help="Zmin")
    parser.add_argument("--zmax", required=True, type=int, help="Zmax")
    parser.add_argument("--host", required=False, default="api.theboss.io", help="bossDB Host")
    parser.add_argument("--token", required=False, default="public", help="bossDB Token")
    parser.add_argument("--resolution", required=False, default=0, help="bossDB Resolution")

    # TODO: Error Detection Algo Arguments

    # Colocarpy Arguments
    parser.add_argument("--colocard", required=False, default="https://colocard.thebossdev.io/", help="Colocard instance URL")
    parser.add_argument("--colocard_username", required=True, help="bossDB Username")
    parser.add_argument("--colocard_password", required=True, help="bossDB Password")
    parser.add_argument("--assignees", required=True, help="Assignees for questions. Delimit with commas.")
    parser.add_argument("--author", required=False, default="SABER", help="Question author.")
    parser.add_argument("--priority", required=True, type=int, default=100, help="Question priority.")

    return parser

def download_data(args):
    x_rng = [args.xmin, args.xmax]
    y_rng = [args.ymin, args.ymax]
    z_rng = [args.zmin, args.zmax]

    rmt = BossRemote({
        "protocol": "https",
        "host": args.host,
        "token": args.token
    })
    resource = rmt.get_channel(args.channel, args.collection, args.experiment)
    return rmt.get_cutout(resource, args.resolution, x_rng, y_rng, z_rng)

def detect_errors(args):
    # Download data
    try:
        data = download_data(args)
    except Exception as e:
        raise Exception(f"Failed to download segmentation data. {e}")
    
    bboxes = []
    # Run Error Detection on this volume:
    # TODO: Add Error detection algorithm 
    # Input: Flat segmentation
    # Returns: Bounding Boxes 

    # Placeholder code
    bboxes.append(
        [
            [args.xmin, args.ymin, args.zmin], 
            [args.xmax // 2, args.xmax // 2, args.xmax // 2]
        ]
    )

    # Once we have detected errors, add questions to colocard.
    if len(bboxes) == 0:
        print("No errors found in this volume.")
        return
    else:
        return bboxes 
    

def post_questions(args):
    # Get bbox of errors
    bbox = detect_errors(args)
    if bbox is None:
        return 

    C = colocarpy.Colocard(args.colocard, username=args.colocard_username, password=args.colocard_password)
    assignees = args.assignees.split(',')
    split_error_instructions = {
        'prompt' : 'Please place two keypoint nodes at the processes that should be merged',
        'type' : 'split_error',
        'confidence' : True, 
        'artifact' : True 
    }

    for box in bboxes:
        name = f"{arg.collection}/{args.experiment}/{args.channel}/{args.resolution}/{box[0][0]}:{box[1][0]}/{box[0][1]}:{box[1][1]}/{box[0][2]}:{box[1][2]}"
        boss_uri = f"bossdb://{args.host}/{args.collection}/{args.experiment}/{args.channel}"
        
        resp = C.post_volume(
            name=name,
            uri=boss_uri,
            bounds=box,
            resolution=args.resolution,
            author=args.author,
            namespace="scheduler"
        )
        vol_id = resp[0]["_id"] 
        
        # post the question
        C.post_question_broadcast(
                volume=vol_id,
                author=args.author,
                assignees=args.assignees.split(','),
                priority=args.priority,
                namespace="pointfog",
                instructions=split_error_instructions
        )


if __name__ == "__main__":
    # Get parser from CWL definition
    parser = get_parser()
    args = parser.parse_args()
    
    # Run Algorithm
    post_questions(args)
