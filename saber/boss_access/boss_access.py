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
import configparser
import os
from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *
from intern import array
import numpy as np
from requests import HTTPError


def _generate_config(token, args):
    boss_host = os.getenv("BOSSDB_HOST", args.host)
    print(boss_host)

    cfg = configparser.ConfigParser()
    cfg["Project Service"] = {}
    cfg["Metadata Service"] = {}
    cfg["Volume Service"] = {}

    project = cfg["Project Service"]
    project["protocol"] = "https"
    project["host"] = boss_host
    project["token"] = token

    metadata = cfg["Metadata Service"]
    metadata["protocol"] = "https"
    metadata["host"] = boss_host
    metadata["token"] = token

    volume = cfg["Volume Service"]
    volume["protocol"] = "https"
    volume["host"] = boss_host
    volume["token"] = token

    return cfg


def boss_pull_cutout(args):
    if args.config:
        rmt = BossRemote(args.config)
    else:
        cfg = _generate_config(args.token, args)
        with open("intern.cfg", "w") as f:
            cfg.write(f)
        rmt = BossRemote("intern.cfg")

    COLL_NAME = args.coll
    EXP_NAME = args.exp
    CHAN_NAME = args.chan

    # Use intern to get d_type and i_type
    intern_chans = array("bossdb://" + COLL_NAME + '/' + EXP_NAME + '/' + CHAN_NAME)

    # Create or get a channel to write to
    chan_setup = ChannelResource(
        CHAN_NAME,
        COLL_NAME,
        EXP_NAME,
        type=intern_chans._channel.type,
        datatype=intern_chans.dtype
    )
    try:
        chan_actual = rmt.get_project(chan_setup)
    except HTTPError:
        chan_actual = rmt.create_project(chan_setup)

    print("Data model setup.")

    # Verify that the cutout uploaded correctly.
    # Data will be in Z,Y,X format
    cutout_data = rmt.get_cutout(resource=chan_actual,
                                 resolution=args.res,
                                 x_range=[args.xmin, args.xmax],
                                 y_range=[args.ymin, args.ymax],
                                 z_range=[args.zmin, args.zmax]
                                 )

    # Change to X,Y,Z for pipeline
    cutout_data = np.transpose(cutout_data, (2, 1, 0))

    # Clean up.
    with open(args.output, "w+b") as f:
        np.save(f, cutout_data)


# here we push a subset of data back to BOSS
def boss_push_cutout(args):
    if args.config:
        rmt = BossRemote(args.config)
    else:
        cfg = _generate_config(args.token, args)
        with open("intern.cfg", "w") as f:
            cfg.write(f)
        rmt = BossRemote("intern.cfg")

    # data is desired range
    data = np.load(args.input)

    COLL_NAME = args.coll
    EXP_NAME = args.exp
    CHAN_NAME = args.chan

    intern_chans = array("bossdb://" + COLL_NAME + '/' + EXP_NAME + '/' + CHAN_NAME)

    # Create or get a channel to write to
    if args.source:
        chan_setup = ChannelResource(
            CHAN_NAME,
            COLL_NAME,
            EXP_NAME,
            type=intern_chans._channel.type,
            datatype=intern_chans.dtype,
            sources=args.source
        )
    else:
        chan_setup = ChannelResource(
            CHAN_NAME,
            COLL_NAME,
            EXP_NAME,
            type=intern_chans._channel.type,
            datatype=intern_chans.dtype
        )
    try:
        chan_actual = rmt.get_project(chan_setup)
    except HTTPError:
        chan_actual = rmt.create_project(chan_setup)

    print("Data model setup.")

    # Change to Z,Y,X for upload
    data_shape = data.shape
    xstart = 0
    ystart = 0
    zstart = 0
    xend = data_shape[0]
    yend = data_shape[1]
    zend = data_shape[2]

    data = np.transpose(data, (2, 1, 0))
    data = data[zstart:zend, ystart:yend, xstart:xend]
    data = data.copy(order="C")

    # Verify that the cutout uploaded correctly.
    rmt.create_cutout(chan_actual,
                      1,
                      [args.xmin, args.ymax],
                      [args.ymin, args.ymax],
                      [args.zmin, args.zmax],
                      data
                      )
    print("These are the dimensions: ")
    print(data.shape)
    print("This is the data type:")
    print(data.dtype)
    # Clean up.

def main():
    parser = argparse.ArgumentParser(description="boss processing script")
    parent_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(title="commands")

    parser.set_defaults(func=lambda _: parser.print_help())

    group = parent_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--config", default=None, help="Boss config file")
    group.add_argument("-t", "--token", default=None, help="Boss API Token")

    parent_parser.add_argument("--coll", required=True, help="Coll name")
    parent_parser.add_argument("--exp", required=True, help="EXP_NAME")
    parent_parser.add_argument("--chan", required=True, help="CHAN_NAME")
    parent_parser.add_argument(
        "--host",
        required=False,
        default="api.bossdb.org",
        help="Name of boss host: api.bossdb.org",
    )

    parent_parser.add_argument("--res", type=int, default= 0, help="Resolution")
    parent_parser.add_argument("--xmin", type=int, default=0, help="Xmin")
    parent_parser.add_argument("--xmax", type=int, default=1, help="Xmax")
    parent_parser.add_argument("--ymin", type=int, default=0, help="Ymin")
    parent_parser.add_argument("--ymax", type=int, default=1, help="Ymax")
    parent_parser.add_argument("--zmin", type=int, default=0, help="Zmin")
    parent_parser.add_argument("--zmax", type=int, default=1, help="Zmax")

    push_parser = subparsers.add_parser(
        "push", help="Push images to boss", parents=[parent_parser]
    )
    push_parser.add_argument("-i", "--input", required=True, help="Input file")
    push_parser.add_argument(
        "--source", required=False, help="Source channel for upload"
    )
    push_parser.set_defaults(func=boss_push_cutout)

    pull_parser = subparsers.add_parser(
        "pull",
        help="Pull images from boss and optionally save to AWS S3",
        parents=[parent_parser],
    )
    pull_parser.add_argument("-o", "--output", required=True, help="Output file")
    pull_parser.set_defaults(func=boss_pull_cutout)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
