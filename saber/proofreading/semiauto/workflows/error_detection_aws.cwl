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

#!/usr/bin/env cwl-runner
## This workflow will make use of the general synapse and membrane detection cwl files, meaning the processes will happen on CPU rather than on GPU. Does not include Boss push steps. 

cwlVersion: v1.0
class: Workflow
doc: local

inputs:
    # Error Detection Inputs
    image_channel: string
    seg_channel: string
    experiment: string
    collection: string
    xmin: int
    xmax: int
    ymin: int
    ymax: int
    zmin: int
    zmax: int
    queue: string
    bucket: string

outputs: []

steps:
    error_detection:
        run: ../tools/error_detection_v3/error_detection.cwl
        in:
            image_channel: image_channel
            seg_channel: seg_channel
            experiment: experiment
            collection: collection
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            queue: queue
            bucket: bucket
            output_file: output_file
    out: []
