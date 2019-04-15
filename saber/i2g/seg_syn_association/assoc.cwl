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
        dockerPull: aplbrain/i2g:assoc
baseCommand: python 
arguments: ['/app/seg_syn_assoc.py']
inputs:
    # config:
    #     type: File?
    #     inputBinding:
    #         position: 3
    #         prefix: --config

    use_boss:
        type: int
        inputBinding:
            position: 1
            prefix: --use_boss  

    token:
        type: string?
        inputBinding:
            position: 2
            prefix: --token
            
    host_name:
        type: string
        inputBinding:
            position: 3
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
    chan_syn:
        type: string
        inputBinding:
            position: 6
            prefix: --chan_syn
    chan_seg:
        type: string
        inputBinding:
            position: 7
            prefix: --chan_seg
    dtype_syn:
        type: string
        inputBinding:
            position: 8
            prefix: --dtype_syn
    dtype_seg:
        type: string
        inputBinding:
            position: 9
            prefix: --dtype_seg     
    resolution:
        type: int?
        inputBinding:
            prefix: --res
            position: 10
    xmin:
        type: int?
        inputBinding:
            prefix: --xmin
            position: 11
    xmax:
        type: int?
        inputBinding:
            prefix: --xmax
            position: 12
    ymin:
        type: int?
        inputBinding:
            prefix: --ymin
            position: 13
    ymax:
        type: int?
        inputBinding:
            prefix: --ymax
            position: 14
    zmin:
        type: int?
        inputBinding:
            prefix: --zmin
            position: 15
    zmax:
        type: int?
        inputBinding:
            prefix: --zmax
            position: 16
    output_name:
        type: string
        inputBinding:
            position: 17
            prefix: --output
    output_name_noneu:
        type: string
        inputBinding: 
            position: 18
            prefix: --output_noneu
outputs: 
    assoc_output:
        type: File
        outputBinding:
            glob: $(inputs.output_name)
    assoc_output_noneu:
        type: File
        outputBinding:
            glob: $(inputs.output_name_noneu)
