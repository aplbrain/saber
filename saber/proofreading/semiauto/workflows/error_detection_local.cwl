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
    image_uri: string
    seg_uri: string
    resolution: int?
    xmin: int
    xmax: int
    ymin: int
    ymax: int
    zmin: int
    zmax: int
    host: string?
    token: string?
    output_file: string

outputs:
    error_detection_out:
        type: File
        outputSource: error_detection/error_detection_out

steps:
    error_detection:
        run: ../tools/error_detection_v3/error_detection.cwl
        in:
            image_uri: image_uri
            seg_uri: seg_uri
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            host: host
            token: token
            output_file: output_file
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/code/saber/output
        out: [error_detection_out]
