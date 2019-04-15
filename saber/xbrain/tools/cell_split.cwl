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
        dockerPull: aplbrain/xbrain:latest
baseCommand: split_cells.py 
arguments: []
inputs:
    input:
        type: File
        inputBinding:
            position: 1
            prefix: -i
    map_output_name:
        type: string
        inputBinding:
            position: 2
            prefix: --map_output
    list_output_name:
        type: string
        inputBinding:
            position: 3
            prefix: --list_output
    centroid_volume_output_name:
        type: string
        inputBinding:
            position: 4
            prefix: --centroid_volume_output
    # bucket:
    #     type: string 
outputs:
    cell_map:
        type: File
        outputBinding:
            glob: $(inputs.map_output_name)
    cell_list:
        type: File
        outputBinding:
            glob: $(inputs.list_output_name)
    centroid_volume:
        type: File
        outputBinding:
            glob: $(inputs.centroid_volume_output_name)
