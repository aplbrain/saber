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
    # Inputs for DVID
    host_name: string
    uuid: string?
    resource_name: string
    dtype_name: string
    type: string
    resolution: int?
    xmin: int?
    xmax: int?
    ymin: int?
    ymax: int?
    zmin: int?
    zmax: int?
    pull_output_name: string
    
    #Inputs for FFN
    image_mean: string
    image_stddev: string
    depth: string
    fov_size: string
    deltas: string
    init_activation: string
    pad_value: string
    move_threshold: string
    min_boundary_dist: string
    segment_threshold: string
    min_segment_size: string
    bound_start: string
    bound_stop: string
    outfile: string 

outputs:
    pull_output_raw:
        type: File
        outputSource: dvid_pull_raw/pull_output
    ffn_segmentation:
        type: File
        outputSource: ffn_segmentation/ffn_out

steps:
    dvid_pull_raw:
        run: ../saber/dvid_access/dvid_pull.cwl
        in:
            host_name: host_name
            uuid: uuid
            resource_name: resource_name
            dtype_name: dtype_name
            type: type
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            output_name: pull_output_name
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/volumes/data/local
        out:
            [pull_output]

    ffn_segmentation:
        run: ../saber/i2g/ffns/ffn_segmentation.cwl
        in:
            input: dvid_pull_raw/pull_output
            image_mean: image_mean
            image_stddev: image_stddev
            depth: depth
            fov_size: fov_size
            deltas: deltas
            init_activation: init_activation
            pad_value: pad_value
            move_threshold: move_threshold
            min_boundary_dist: min_boundary_dist
            segment_threshold: segment_threshold
            min_segment_size: min_segment_size
            bound_start: bound_start
            bound_stop: bound_stop
            outfile: outfile
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/volumes/data/local
        out: [ffn_out]
