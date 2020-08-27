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
import sys
import tempfile
import math
import boto3
from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *
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

    # Create or get a channel to write to
    chan_setup = ChannelResource(
        CHAN_NAME, COLL_NAME, EXP_NAME, type=args.itype, datatype=args.dtype
    )
    try:
        chan_actual = rmt.get_project(chan_setup)
    except HTTPError:
        chan_actual = rmt.create_project(chan_setup)
    # get coordinate frame to determine padding bounds
    cfr = CoordinateFrameResource(args.coord)
    cfr_actual = rmt.get_project(cfr)
    x_min_bound = cfr_actual.x_start
    x_max_bound = cfr_actual.x_stop
    y_min_bound = cfr_actual.y_start
    y_max_bound = cfr_actual.y_stop
    z_min_bound = cfr_actual.z_start
    z_max_bound = cfr_actual.z_stop

    print("Data model setup.")

    xmin = np.max([x_min_bound, args.xmin - args.padding])
    xmax = np.min([x_max_bound, args.xmax + args.padding])
    x_rng = [xmin, xmax]
    ymin = np.max([y_min_bound, args.ymin - args.padding])
    ymax = np.min([y_max_bound, args.ymax + args.padding])
    y_rng = [ymin, ymax]
    zmin = np.max([z_min_bound, args.zmin - args.padding])
    zmax = np.min([z_max_bound, args.zmax + args.padding])
    z_rng = [zmin, zmax]
    # Verify that the cutout uploaded correctly.
    attempts = 0
    while attempts < 3:
        try:
            cutout_data = rmt.get_cutout(chan_actual, args.res, x_rng, y_rng, z_rng)
            break
        except HTTPError as e:
            if attempts < 3:
                attempts += 1
                print("Obtained HTTP error from server. Trial {}".format(attempts))
            else:
                print("Failed 3 times: {}".format(e))
    # Data will be in Z,Y,X format
    # Change to X,Y,Z for pipeline
    cutout_data = np.transpose(cutout_data, (2, 1, 0))

    def _upload(f):
        print("Uploading to s3:/{}/{}".format(args.bucket, args.output))
        s3 = boto3.resource("s3")
        f.seek(0, 0)
        s3.Object(args.bucket, args.output).put(Body=f)

    # Clean up.
    if args.bucket and args.s3_only:
        with tempfile.TemporaryFile() as f:
            np.save(f, cutout_data)
            _upload(f)
    else:
        with open(args.output, "w+b") as f:
            np.save(f, cutout_data)
            if args.bucket:
                _upload(f)


# here we push a subset of padded data back to BOSS
def boss_push_cutout(args):
    if args.config:
        rmt = BossRemote(args.config)
    else:
        cfg = _generate_config(args.token, args)
        with open("intern.cfg", "w") as f:
            cfg.write(f)
        rmt = BossRemote("intern.cfg")

    # data is desired range
    if args.bucket:
        s3 = boto3.resource("s3")
        with tempfile.TemporaryFile() as f:
            s3.Bucket(args.bucket).download_fileobj(args.input, f)
            f.seek(0, 0)
            data = np.load(f)
    else:
        data = np.load(args.input)

    numpyType = np.uint8
    if args.dtype == "uint32":
        numpyType = np.uint32
    elif args.dtype == "uint64":
        numpyType = np.uint64

    if data.dtype != args.dtype:
        data = data.astype(numpyType)
    sources = []
    if args.source:
        sources.append(args.source)

    COLL_NAME = args.coll
    EXP_NAME = args.exp
    CHAN_NAME = args.chan

    # Create or get a channel to write to
    chan_setup = ChannelResource(
        CHAN_NAME,
        COLL_NAME,
        EXP_NAME,
        type=args.itype,
        datatype=args.dtype,
        sources=sources,
    )
    try:
        chan_actual = rmt.get_project(chan_setup)
    except HTTPError:
        chan_actual = rmt.create_project(chan_setup)

    # get coordinate frame to determine padding bounds
    cfr = CoordinateFrameResource(args.coord)
    cfr_actual = rmt.get_project(cfr)
    x_min_bound = cfr_actual.x_start
    x_max_bound = cfr_actual.x_stop
    y_min_bound = cfr_actual.y_start
    y_max_bound = cfr_actual.y_stop
    z_min_bound = cfr_actual.z_start
    z_max_bound = cfr_actual.z_stop

    print("Data model setup.")

    # Ranges use the Python convention where the number after the : is the stop
    # value.  Thus, x_rng specifies x values where: 0 <= x < 8.
    data_shape = data.shape  # with padding, will be bigger than needed
    # find data cutoffs to get rid of padding
    # if nmin = 0, this means that the data wasn't padded on there to begin with
    xstart = args.padding if args.xmin != 0 else 0
    ystart = args.padding if args.ymin != 0 else 0
    zstart = args.padding if args.zmin != 0 else 0
    xend = data_shape[0] - args.padding
    yend = data_shape[1] - args.padding
    zend = data_shape[2] - args.padding

    # xstart = np.min([args.padding,args.xmin-x_min_bound])
    # xend = np.max([data.shape[0]-args.padding,data.shape[0]-(x_max_bound-args.xmax)])
    # ystart = np.min([args.padding,args.ymin-y_min_bound])
    # yend = np.max([data.shape[1]-args.padding,data.shape[1]-(y_max_bound-args.ymax)])
    # zstart = np.min([args.padding,args.zmin-z_min_bound])
    # zend = np.max([data.shape[2]-args.padding,data.shape[2]-(z_max_bound-args.zmax)])
    # get range which will be uploaded
    x_rng = [args.xmin, args.xmax]
    y_rng = [args.ymin, args.ymax]
    z_rng = [args.zmin, args.zmax]
    # Pipeline Data will be in X,Y,Z format
    # Change to Z,Y,X for upload
    data = np.transpose(data, (2, 1, 0))
    data = data[zstart:zend, ystart:yend, xstart:xend]
    data = data.copy(order="C")
    # Verify that the cutout uploaded correctly.
    attempts = 0
    while attempts < 3:
        try:
            rmt.create_cutout(chan_actual, args.res, x_rng, y_rng, z_rng, data)
            break
        except HTTPError as e:
            if attempts < 3:
                attempts += 1
                print("These are the dimensions: ")
                print(data.shape)
                print("This is the data type:")
                print(data.dtype)
                print("Specified data type was:")
                print(args.dtype)
                print("Specified image type")
                print(args.itype)
                print("Obtained HTTP error from server. Trial {}".format(attempts))
                print("The error: {}".format(e))
            else:
                raise Exception("Failed 3 times: {}".format(e))
    # Clean up.


"""boss_merge_xbrain
Here we push a subset of padded data back to BOSS, merging with existing data in BOSS in padded region
Merging here is for XBrain only, will need to work more on EM
Here we are pushing a block of data into a channel which has other blocks of data, possibly already in it
The blocks are padded to detect objects at the edges
This requires merging of the blocks
Not that currently, it is assumed that all cells are detected using templatesize- as a single value. 
Overlapping cells should already be handled by cell_detect, where the dilation dictionary zeros out around a detected cell

    Inputs:
        xmin: integer index of start of data block, before padding (in coordinate frame of raw data channel)
        xmax: integer index of end of data block, before padding (in coordinate frame of raw data channel)
        ymin: integer index of start of data block, before padding (in coordinate frame of raw data channel)
        ymax: integer index of end of data block, before padding (in coordinate frame of raw data channel)
        zmin: integer index of start of data block, before padding (in coordinate frame of raw data channel)
        zmax: integer index of end of data block, before padding (in coordinate frame of raw data channel)
        Padding: integer amount of padding added to each side of block (if valid given the channel boundaries)
        One sided: int, if 1, only merge on the max edge of block. This prevents duplicates in the padding zone. If zero, merge all edges, risking duplicates
        templatesize: integer value giving initial diameter of cell detection templates. Padding should be at least templatesize+1
        input: dense cell detection output from cell detection step
        centroids: centroid location output from cell detections step (coordinates are referenced to the )
    Output: 
        output: centroid output, with any cells on border removed, and coordinates shifted into frame of raw data
    Side effect:
        Data is uploaded to the BOSS channel, covering [xmin:xmax,ymin:ymax,zmin:zmax]. Any padded regions around this block are also merged
    
"""


def boss_merge_xbrain(args):
    # Verify that the cutout uploaded correctly.
    def pull_margin_cutout(chan_actual, x_rng, y_rng, z_rng):
        attempts = 0
        while attempts < 3:
            try:
                cutout_data = rmt.get_cutout(chan_actual, 0, x_rng, y_rng, z_rng)
                break
            except HTTPError as e:
                if attempts < 3:
                    attempts += 1
                    print("Obtained HTTP error from server. Trial {}".format(attempts))
                else:
                    print("Failed 3 times: {}".format(e))
        # Data will be in Z,Y,X format
        # Change to X,Y,Z for pipeline
        cutout_data = np.transpose(cutout_data, (2, 1, 0))
        return cutout_data

    templatesize = args.templatesize
    if args.config:
        rmt = BossRemote(args.config)
    else:
        cfg = _generate_config(args.token, args)
        with open("intern.cfg", "w") as f:
            cfg.write(f)
        rmt = BossRemote("intern.cfg")

    # data is desired range
    if args.bucket:
        s3 = boto3.resource("s3")
        with tempfile.TemporaryFile() as f:
            s3.Bucket(args.bucket).download_fileobj(args.input, f)
            f.seek(0, 0)
            data = np.load(f)
        with tempfile.TemporaryFile() as f:
            s3.Bucket(args.bucket).download_fileobj(args.centroids, f)
            f.seek(0, 0)
            centroids = np.load(f)
    else:
        data = np.load(args.input)
        centroids = np.load(args.centroids)

    COLL_NAME = args.coll
    EXP_NAME = args.exp
    CHAN_NAME = args.chan

    # Create or get a channel to write to
    chan_setup = ChannelResource(
        CHAN_NAME, COLL_NAME, EXP_NAME, type=args.itype, datatype=args.dtype
    )
    try:
        chan_actual = rmt.get_project(chan_setup)
    except HTTPError:
        chan_actual = rmt.create_project(chan_setup)

    # get coordinate frame to determine padding bounds
    cfr = CoordinateFrameResource(args.coord)
    cfr_actual = rmt.get_project(cfr)
    x_min_bound = cfr_actual.x_start
    x_max_bound = cfr_actual.x_stop
    y_min_bound = cfr_actual.y_start
    y_max_bound = cfr_actual.y_stop
    z_min_bound = cfr_actual.z_start
    z_max_bound = cfr_actual.z_stop

    # coordinates of data block in original coordinate frame, before padding
    x_block = [args.xmin, args.xmax]
    y_block = [args.ymin, args.ymax]
    z_block = [args.zmin, args.zmax]

    # Coordinates of data block with padding in original coordinate frame
    x_block_pad = [
        np.amax([args.xmin - args.padding, x_min_bound]),
        np.amin([args.xmax + args.padding, x_max_bound]),
    ]
    y_block_pad = [
        np.amax([args.ymin - args.padding, y_min_bound]),
        np.amin([args.ymax + args.padding, y_max_bound]),
    ]
    z_block_pad = [
        np.amax([args.zmin - args.padding, z_min_bound]),
        np.amin([args.zmax + args.padding, z_max_bound]),
    ]

    # Coordinates of core data block in local coordinate frame
    xstart = np.amin([args.padding, args.xmin - x_min_bound])
    xend = np.amax(
        [data.shape[0] - args.padding, data.shape[0] - (x_max_bound - args.xmax)]
    )
    ystart = np.amin([args.padding, args.ymin - y_min_bound])
    yend = np.amax(
        [data.shape[1] - args.padding, data.shape[1] - (y_max_bound - args.ymax)]
    )
    zstart = np.amin([args.padding, args.zmin - z_min_bound])
    zend = np.amax(
        [data.shape[2] - args.padding, data.shape[2] - (z_max_bound - args.zmax)]
    )

    print("Data model setup.")
    # Template size to decide which centroids to eliminate

    # Ranges use the Python convention where the number after the : is the stop
    # value.  Thus, x_rng specifies x values where: 0 <= x < 8.
    if args.onesided:
        # Only merge on the max side, to prevent duplication of detection
        # Binarize Map
        data[np.where(data > 0)] = 1

        # Search through centroids
        # On side of max values, keep anything where centroid is in padded region
        # On side of min values, remove anything that is partially in padded region (covered by another block)
        n_centers, _ = centroids.shape  # n by 4
        bad_inds = []
        for i in range(0, n_centers):
            if centroids[i, 0] < xstart or centroids[i, 0] - templatesize / 2 > xend:
                bad_inds.append(i)
            elif centroids[i, 1] < ystart or centroids[i, 1] - templatesize / 2 > yend:
                bad_inds.append(i)
            elif centroids[i, 2] < zstart or centroids[i, 2] - templatesize / 2 > zend:
                bad_inds.append(i)
        centroids_out = np.delete(centroids, bad_inds, axis=0)
        # translate into global coordinates from local data block
        centroids_out[:, 0] = centroids_out[:, 0] - xstart + args.xmin
        centroids_out[:, 1] = centroids_out[:, 1] - ystart + args.ymin
        centroids_out[:, 2] = centroids_out[:, 2] - zstart + args.zmin

        # Eliminate any cells form data which overlap with the padding edge
        for ind in bad_inds:
            xi = np.array(
                [
                    centroids[ind, 0] - np.ceil(templatesize / 2),
                    centroids[ind, 0] + np.ceil(templatesize / 2),
                ]
            ).astype(int)
            yi = np.array(
                [
                    centroids[ind, 1] - np.ceil(templatesize / 2),
                    centroids[ind, 1] + np.ceil(templatesize / 2),
                ]
            ).astype(int)
            zi = np.array(
                [
                    centroids[ind, 2] - np.ceil(templatesize / 2),
                    centroids[ind, 2] + np.ceil(templatesize / 2),
                ]
            ).astype(int)
            data[xi, yi, zi] = 0
        # Keep any interior cells, any which overlap original boundary and not padding
        # Pull down existing boundary area, if area is valid
        # Test side 4
        if (
            xend < data.shape[0]
        ):  # There is padding on side 4 of cube [xmax+pad:xmax+2*pad,pad:ymax+2*pad,pad:zmax+2*pad]
            margin = pull_margin_cutout(
                chan_actual,
                [x_block[1], x_block_pad[1]],
                [y_block[0], y_block_pad[1]],
                [z_block[0], z_block_pad[1]],
            )
            data[
                xend : data.shape[0], ystart : data.shape[1], zstart : data.shape[2]
            ] = np.maximum(
                data[
                    xend : data.shape[0], ystart : data.shape[1], zstart : data.shape[2]
                ],
                margin,
            )
        # Test side 5
        if (
            yend < data.shape[1]
        ):  # There is padding on side 5 of cube [pad:xmax+2*pad,ymax+pad:ymax+2*pad,pad:zmax+2*pad]
            margin = pull_margin_cutout(
                chan_actual,
                [x_block[0], x_block_pad[1]],
                [y_block[1], y_block_pad[1]],
                [z_block[0], z_block_pad[1]],
            )
            data[
                xstart : data.shape[0], yend : data.shape[1], zstart : data.shape[2]
            ] = np.maximum(
                data[
                    xstart : data.shape[0], yend : data.shape[1], zstart : data.shape[2]
                ],
                margin,
            )
        # Test side 6
        if (
            zend < data.shape[2]
        ):  # There is padding on side 4 of cube [pad:xmax+2*pad,pad:ymax+2*pad,zmax+pad:zmax+2*pad]
            margin = pull_margin_cutout(
                chan_actual,
                [x_block[0], x_block_pad[1]],
                [y_block[0], y_block_pad[1]],
                [z_block[1], z_block_pad[1]],
            )
            data[
                xstart : data.shape[0], ystart : data.shape[1], zend : data.shape[2]
            ] = np.maximum(
                data[
                    xstart : data.shape[0], ystart : data.shape[1], zend : data.shape[2]
                ],
                margin,
            )

        # push results over entire padded area
        # Pipeline Data will be in X,Y,Z format
        # Change to Z,Y,X for upload
        data = data[
            xstart : data.shape[0], ystart : data.shape[1], zstart : data.shape[2]
        ]
        data = np.transpose(data, (2, 1, 0))
        data = data.copy(order="C").astype(eval("np.{}".format(args.dtype)))
        # Verify that the cutout uploaded correctly.
        rmt.create_cutout(
            chan_actual,
            0,
            [x_block[0], x_block_pad[1]],
            [y_block[0], y_block_pad[1]],
            [z_block[0], z_block_pad[1]],
            data,
        )
        # Clean up.
    else:
        # Binarize Map
        data[np.where(data > 0)] = 1

        # Search through centroids
        n_centers, _ = centroids.shape  # n by 4
        bad_inds = []
        for i in range(0, n_centers):
            if (
                centroids[i, 0] + templatesize / 2 < xstart
                or centroids[i, 0] - templatesize / 2 > xend
            ):
                bad_inds.append(i)
            elif (
                centroids[i, 1] + templatesize / 2 < ystart
                or centroids[i, 1] - templatesize / 2 > yend
            ):
                bad_inds.append(i)
            elif (
                centroids[i, 2] + templatesize / 2 < zstart
                or centroids[i, 2] - templatesize / 2 > zend
            ):
                bad_inds.append(i)
        centroids_out = np.delete(centroids, bad_inds, axis=0)
        # translate into global coordinates from local data block
        centroids_out[:, 0] = centroids_out[:, 0] - xstart + args.xmin
        centroids_out[:, 1] = centroids_out[:, 1] - ystart + args.ymin
        centroids_out[:, 2] = centroids_out[:, 2] - zstart + args.zmin

        # Eliminate any cells form data which overlap with the padding edge
        for ind in bad_inds:
            xi = np.array(
                [
                    centroids[ind, 0] - np.ceil(templatesize / 2),
                    centroids[ind, 0] + np.ceil(templatesize / 2),
                ]
            ).astype(int)
            yi = np.array(
                [
                    centroids[ind, 1] - np.ceil(templatesize / 2),
                    centroids[ind, 1] + np.ceil(templatesize / 2),
                ]
            ).astype(int)
            zi = np.array(
                [
                    centroids[ind, 2] - np.ceil(templatesize / 2),
                    centroids[ind, 2] + np.ceil(templatesize / 2),
                ]
            ).astype(int)
            data[xi, yi, zi] = 0
        # Keep any interior cells, any which overlap original boundary and not padding
        # Pull down existing boundary area, if area is valid
        # Test side 1
        if (
            xstart > 0
        ):  # There is padding on side 1 of cube [0:pad,0:ymax+2*pad,0:zmax+2*pad]
            margin = pull_margin_cutout(
                chan_actual, [x_block_pad[0], x_block[0]], y_block_pad, z_block_pad
            )
            data[0:xstart, :, :] = np.maximum(data[0:xstart, :, :], margin)
        # Test side 2
        if (
            ystart > 0
        ):  # There is padding on side 2 of cube [pad:xmax+2*pad,0:pad,pad:zmax+2*pad]
            margin = pull_margin_cutout(
                chan_actual,
                [x_block[0], x_block_pad[1]],
                [y_block_pad[0], y_block[0]],
                [z_block[0], z_block_pad[1]],
            )
            data[xstart : data.shape[0], 0:ystart, zstart : data.shape[2]] = np.maximum(
                data[xstart : data.shape[0], 0:ystart, zstart : data.shape[1]], margin
            )
        # Test side 3
        if (
            zstart > 0
        ):  # There is padding on side 3 of cube [pad:xmax+2*pad,pad:ymax+2*pad,0:pad]
            margin = pull_margin_cutout(
                chan_actual,
                [x_block[0], x_block_pad[1]],
                [y_block[0], y_block_pad[1]],
                [z_block_pad[0], z_block[0]],
            )
            data[xstart : data.shape[0], ystart : data.shape[1], 0:zstart] = np.maximum(
                data[xstart : data.shape[0], ystart : data.shape[1], 0:zstart], margin
            )
        # Test side 4
        if (
            xend < data.shape[0]
        ):  # There is padding on side 4 of cube [xmax+pad:xmax+2*pad,pad:ymax+2*pad,pad:zmax+2*pad]
            margin = pull_margin_cutout(
                chan_actual,
                [x_block[1], x_block_pad[1]],
                [y_block[0], y_block_pad[1]],
                [z_block[0], z_block_pad[1]],
            )
            data[
                xend : data.shape[0], ystart : data.shape[1], zstart : data.shape[2]
            ] = np.maximum(
                data[
                    xend : data.shape[0], ystart : data.shape[1], zstart : data.shape[2]
                ],
                margin,
            )
        # Test side 5
        if (
            yend < data.shape[1]
        ):  # There is padding on side 5 of cube [pad:xmax+2*pad,ymax+pad:ymax+2*pad,pad:zmax+2*pad]
            margin = pull_margin_cutout(
                chan_actual,
                [x_block[0], x_block_pad[1]],
                [y_block[1], y_block_pad[1]],
                [z_block[0], z_block_pad[1]],
            )
            data[
                xstart : data.shape[0], yend : data.shape[1], zstart : data.shape[2]
            ] = np.maximum(
                data[
                    xstart : data.shape[0], yend : data.shape[1], zstart : data.shape[2]
                ],
                margin,
            )
        # Test side 6
        if (
            zend < data.shape[2]
        ):  # There is padding on side 4 of cube [pad:xmax+2*pad,pad:ymax+2*pad,zmax+pad:zmax+2*pad]
            margin = pull_margin_cutout(
                chan_actual,
                [x_block[0], x_block_pad[1]],
                [y_block[0], y_block_pad[1]],
                [z_block[1], z_block_pad[1]],
            )
            data[
                xstart : data.shape[0], ystart : data.shape[1], zend : data.shape[2]
            ] = np.maximum(
                data[
                    xstart : data.shape[0], ystart : data.shape[1], zend : data.shape[2]
                ],
                margin,
            )

        # push results over entire padded area
        # Pipeline Data will be in X,Y,Z format
        # Change to Z,Y,X for upload
        data = np.transpose(data, (2, 1, 0))
        data = data.copy(order="C").astype(eval("np.{}".format(args.dtype)))
        # Verify that the cutout uploaded correctly.
        rmt.create_cutout(chan_actual, 0, x_block_pad, y_block_pad, z_block_pad, data)
        # Clean up.

    def _upload(f):
        print("Uploading to s3:/{}/{}".format(args.bucket, args.output))
        s3 = boto3.resource("s3")
        f.seek(0, 0)
        s3.Object(args.bucket, args.output).put(Body=f)

    # Clean up.
    if args.bucket and args.s3_only:
        with tempfile.TemporaryFile() as f:
            np.save(f, centroids_out)
            _upload(f)
    else:
        print("Saving output")
        with open(args.output, "w+b") as f:
            np.save(f, centroids_out)
            if args.bucket:
                _upload(f)
    return


def main():
    parser = argparse.ArgumentParser(description="boss processing script")
    parent_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(title="commands")

    parser.set_defaults(func=lambda _: parser.print_help())

    group = parent_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--config", default=None, help="Boss config file")
    group.add_argument("-t", "--token", default=None, help="Boss API Token")
    parent_parser.add_argument(
        "-b", "--bucket", default=None, help="S3 bucket to save to or load from"
    )

    parent_parser.add_argument("--coll", required=True, help="Coll name")
    parent_parser.add_argument("--exp", required=True, help="EXP_NAME")
    parent_parser.add_argument("--chan", required=True, help="CHAN_NAME")
    parent_parser.add_argument("--coord", required=True, help="Coordinate_Frame")
    parent_parser.add_argument("--dtype", required=True, help="data type")
    parent_parser.add_argument("--itype", required=True, help="I type")
    parent_parser.add_argument(
        "--host",
        required=False,
        default="api.bossdb.org",
        help="Name of boss host: api.bossdb.org",
    )

    parent_parser.add_argument("--res", type=int, help="Resolution")
    parent_parser.add_argument("--xmin", type=int, default=0, help="Xmin")
    parent_parser.add_argument("--xmax", type=int, default=1, help="Xmax")
    parent_parser.add_argument("--ymin", type=int, default=0, help="Ymin")
    parent_parser.add_argument("--ymax", type=int, default=1, help="Ymax")
    parent_parser.add_argument("--zmin", type=int, default=0, help="Zmin")
    parent_parser.add_argument("--zmax", type=int, default=1, help="Zmax")
    parent_parser.add_argument("--padding", type=int, default=0, help="padding")
    parent_parser.add_argument(
        "--onesided", type=int, default=0, help="flag for one-sided padding"
    )  # indicates whether padding is one-sided or two-sided

    push_parser = subparsers.add_parser(
        "push", help="Push images to boss", parents=[parent_parser]
    )
    pull_parser = subparsers.add_parser(
        "pull",
        help="Pull images from boss and optionally save to AWS S3",
        parents=[parent_parser],
    )
    merge_parser = subparsers.add_parser(
        "merge", help="Merge xbrain images to boss", parents=[parent_parser]
    )

    push_parser.add_argument("-i", "--input", required=True, help="Input file")
    push_parser.add_argument(
        "--source", required=False, help="Source channel for upload"
    )
    push_parser.set_defaults(func=boss_push_cutout)

    merge_parser.add_argument(
        "--templatesize",
        required=True,
        help="Template size (diameter of spherical template)",
        type=int,
    )
    merge_parser.add_argument("-i", "--input", required=True, help="Input file")
    merge_parser.add_argument("--centroids", required=True, help="Centroid numpy file")
    merge_parser.add_argument(
        "-o", "--output", required=True, help="Output centroid file"
    )
    merge_parser.set_defaults(func=boss_merge_xbrain)

    pull_parser.add_argument("-o", "--output", required=True, help="Output file")
    pull_parser.add_argument(
        "--s3-only",
        dest="s3_only",
        action="store_true",
        default=False,
        help="Only save output to AWS S3",
    )
    pull_parser.set_defaults(func=boss_pull_cutout)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
