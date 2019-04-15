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
        dockerPull: xbrain:airflow-docker
baseCommand: python 
arguments: ["process-xbrain.py","optimize"]
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
    classifier:
        type: File?
        inputBinding:
            position: 3
            prefix: -c
    groundtruth:
        type: File
        inputBinding:
            position: 4
            prefix: --cellgt
    threshold:
        type: float?
        inputBinding:
            prefix: --threshold
            position: 5
    stop:
        type: float?
        inputBinding:
            prefix: --stop
            position: 6
    initial_template_size:
        type: int?
        inputBinding:
            prefix: --initial-template-size
            position: 7
    dilation:
        type: int?
        inputBinding:
            prefix: --dialation
            position: 8
    max_cells:
        type: int?
        inputBinding:
            prefix: --max-cells
            position: 9
outputs:
    metric_score:
        type: File
        outputBinding:
            glob: $(inputs.output_name)
