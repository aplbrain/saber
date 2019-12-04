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

cwlVersion: v1.0
class: CommandLineTool
hints:
    DockerRequirement:
        dockerPull: aplbrain/boss-access:latest
baseCommand: python 
arguments: ['/app/boss_access.py', 'pull']
inputs:
    # config:
    #     type: File?
    #     inputBinding:
    #         position: 3
    #         prefix: --config

    coord_name:
        type: string
        inputBinding:
            position: 7
            prefix: --coord  

    token:
        type: string?
        inputBinding:
            position: 3
            prefix: --token
            
    host_name:
        type: string
        inputBinding:
            position: 19
            prefix: --host

    coll_name:
        type: string
        inputBinding:
            position: 4
            prefix: --coll
    exp_name:
        type: string
        inputBinding:
            position: 5
            prefix: --exp
    chan_name:
        type: string
        inputBinding:
            position: 6
            prefix: --chan
    dtype_name:
        type: string
        inputBinding:
            position: 7
            prefix: --dtype
    itype_name:
        type: string
        inputBinding:
            position: 8
            prefix: --itype
    resolution:
        type: int?
        inputBinding:
            prefix: --res
            position: 9
    xmin:
        type: int?
        inputBinding:
            prefix: --xmin
            position: 10
    xmax:
        type: int?
        inputBinding:
            prefix: --xmax
            position: 11
    ymin:
        type: int?
        inputBinding:
            prefix: --ymin
            position: 12
    ymax:
        type: int?
        inputBinding:
            prefix: --ymax
            position: 13
    zmin:
        type: int?
        inputBinding:
            prefix: --zmin
            position: 14
    zmax:
        type: int?
        inputBinding:
            prefix: --zmax
            position: 15
    padding:
        type: int?
        inputBinding:
            prefix: --padding
            position: 16
    output_name:
        type: string
        inputBinding:
            position: 18
            prefix: --output
outputs: 
    pull_output:
        type: File
        outputBinding:
            glob: $(inputs.output_name)
