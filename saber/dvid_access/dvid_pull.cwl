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
        dockerPull: aplbrain/dvid-access
baseCommand: python 
arguments: ['/app/dvid_access.py', 'pull']
inputs:  
    host_name:
        type: string
        inputBinding:
            position: 1
            prefix: --host
    uuid:
        type: string
        inputBinding:
            position: 2
            prefix: --uuid
    dtype_name:
        type: string
        inputBinding:
            position: 3
            prefix: --datatype
    resource_name:
        type: string
        inputBinding:
            position: 4
            prefix: --data_instance
    resolution:
        type: int?
        inputBinding:
            prefix: --res
            position: 5
    xmin:
        type: int?
        inputBinding:
            prefix: --xmin
            position: 6
    xmax:
        type: int?
        inputBinding:
            prefix: --xmax
            position: 7
    ymin:
        type: int?
        inputBinding:
            prefix: --ymin
            position: 8
    ymax:
        type: int?
        inputBinding:
            prefix: --ymax
            position: 9
    zmin:
        type: int?
        inputBinding:
            prefix: --zmin
            position: 10
    zmax:
        type: int?
        inputBinding:
            prefix: --zmax
            position: 11
    output_name:
        type: string
        inputBinding:
            position: 12
            prefix: --output
    type:
        type: string?
        inputBinding:
            prefix: --type
            position: 13
outputs: 
    pull_output:
        type: File
        outputBinding:
            glob: $(inputs.output_name)
