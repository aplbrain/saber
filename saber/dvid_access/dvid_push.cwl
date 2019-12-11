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
arguments: ['/app/dvid_access.py', 'push']
inputs:
    input:
        type: File
        inputBinding:
            position: 1
            prefix: -i
    host_name:
        type: string
        inputBinding:
            position: 2
            prefix: --host
    uuid:
        type: string?
        inputBinding:
            position: 3
            prefix: --uuid
    dtype_name:
        type: string
        inputBinding:
            position: 4
            prefix: --datatype
    resource_name:
        type: string
        inputBinding:
            position: 5
            prefix: --data_instance
    resolution:
        type: int?
        inputBinding:
            prefix: --res
            position: 6
    xmin:
        type: int?
        inputBinding:
            prefix: --xmin
            position: 7
    xmax:
        type: int?
        inputBinding:
            prefix: --xmax
            position: 8
    ymin:
        type: int?
        inputBinding:
            prefix: --ymin
            position: 9
    ymax:
        type: int?
        inputBinding:
            prefix: --ymax
            position: 10
    zmin:
        type: int?
        inputBinding:
            prefix: --zmin
            position: 11
    zmax:
        type: int?
        inputBinding:
            prefix: --zmax
            position: 12
    source:
        type: string?
        inputBinding:
            prefix: --source
            position: 13
    type:
        type: string?
        inputBinding:
            prefix: --type
            position: 14
outputs: []

