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

#!/usr/bin/env cwl-runner
## This workflow will make use of the general synapse and membrane detection cwl files, meaning the processes will happen on CPU rather than on GPU. Does not include Boss push steps. 

cwlVersion: v1.0
class: Workflow
doc: local

inputs:

    # Inputs for BOSS
    host_bossdb: string
    token_bossdb: string?
    coll_name: string
    exp_name: string
    chan_name_image: string
    dtype_name_image: string
    itype_name_image: string
    chan_name_anno: string
    dtype_name_anno: string
    itype_name_anno: string
    coord_name: string
    resolution: int?
    xmin: int?
    xmax: int?
    ymin: int?
    ymax: int?
    zmin: int?
    zmax: int?
    padding: int?
    image_output_name: string
    anno_output_name: string

    #inputs for mask
    mask_output_name: string

    #inputs for error detection
    error_detection_output_name: string



outputs:
    pull_output_image:
        type: File
        outputSource: boss_pull_image/pull_output
    pull_output_anno:
        type: File
        outputSource: boss_pull_anno/pull_output
    supervoxel_mask:
        type: File
        outputSource: generate_supervoxel_mask/supervoxel_mask_out
    errors:
        type: File
        outputSource: error_detection/error_detection_out

steps:
    boss_pull_image:
        run: ../../../boss_access/boss_pull_nos3.cwl
        in:
            token: token_bossdb
            host_name: host_bossdb
            coll_name: coll_name
            exp_name: exp_name
            chan_name: chan_name_image
            dtype_name: dtype_name_image
            itype_name: itype_name_image
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            output_name: image_output_name
            coord_name: coord_name
        hints:
            saber:
                local: True
                file_path: /Users/xenesd1/Projects/aplbrain/saber/output
        out:
            [pull_output]


    boss_pull_anno:
        run: ../../../boss_access/boss_pull_nos3.cwl
        in:
            token: token_bossdb
            host_name: host_bossdb
            coll_name: coll_name
            exp_name: exp_name
            chan_name: chan_name_anno
            dtype_name: dtype_name_anno
            itype_name: itype_name_anno
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            output_name: anno_output_name
            coord_name: coord_name
        hints:
            saber:
                local: True
                file_path: /Users/xenesd1/Projects/aplbrain/saber/output
        out:
            [pull_output]


    generate_supervoxel_mask:
        run: ../tools/supervoxel_mask/supervoxel_mask.cwl
        in:
            input: boss_pull_anno/pull_output
            output: mask_output_name
        hints:
            saber:
                local: True
                file_path: /Users/xenesd1/Projects/aplbrain/saber/output
        out: [supervoxel_mask_out]


    error_detection:
        run: ../tools/error_detection/error_detection.cwl
        in:
            image: boss_pull_image/pull_output
            mask: generate_supervoxel_mask/supervoxel_mask_out
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            output: error_detection_output_name
        hints:
            saber:
                local: True
                file_path: /Users/xenesd1/Projects/aplbrain/saber/output
        out: [error_detection_out]
