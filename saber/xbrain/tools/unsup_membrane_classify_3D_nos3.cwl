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
        # dockerPull: xbrain:airflow-docker
        dockerPull: aplbrain/xbrain:latest
baseCommand: python
arguments: ["/app/unsupervised_celldetect.py","classify3D"]
inputs:
    input:
        type: File
        inputBinding:
            position: 1
            prefix: -i
    output_name:
        type: string
        inputBinding:
            position: 2
            prefix: -o
    num_samp:
        type: int?
        inputBinding:
            position: 4
            prefix: --numsamp
    num_comp:
        type: int?
        inputBinding:
            position: 5
            prefix: --numcomp
    vessel_thres:
        type: float?
        inputBinding:
            position: 6
            prefix: --vesselthres
    min_size:
        type: float?
        inputBinding:
            position: 7
            prefix: --minsize
    cell_class:
        type: int?
        inputBinding:
            position: 8
            prefix: --cellclass
            
outputs:
    membrane_probability_map:
        type: File
        outputBinding:
            glob: $(inputs.output_name)

