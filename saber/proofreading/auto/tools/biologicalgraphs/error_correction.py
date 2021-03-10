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

    # TODO: Error Correction Algo Arguments


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

def correct_errors(args):
    #TODO: Add Michael and Raph's Biological graph code here
    pass


if __name__ == "__main__":
    # Get parser from CWL definition
    parser = get_parser()
    args = parser.parse_args()
    
    # Run Algorithm
    post_questions(args)
