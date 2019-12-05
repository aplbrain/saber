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
arguments: ['/app/dvid-access.py', 'push']
inputs:
    input:
        type: File
        inputBinding:
            position: 2
            prefix: -i
    host_name:
        type: string
        inputBinding:
            position: 18
            prefix: --host
    uuid:
        type: string
        inputBinding:
            position: 19
            prefix: --uuid
    dtype_name:
        type: string
        inputBinding:
            position: 8
            prefix: --data_type
    resource_name:
        type: string
        inputBinding:
            position: 7
            prefix: --data_instance
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
    source:
        type: string?
        inputBinding:
            prefix: --source
            position: 18
outputs: []

