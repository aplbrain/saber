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
        dockerPull: aplbrain/i2gassoc
baseCommand: python 
arguments: ['/app/seg_syn_assoc.py']
inputs:
    seg_file:
        type: File
        inputBinding:
            position: 1
            prefix: --seg_file
    syn_file:
        type: File
        inputBinding:
            position: 2
            prefix: --syn_file
    output_name:
        type: string
        inputBinding:
            position: 3
            prefix: --output
    output_name_noneu:
        type: string
        inputBinding: 
            position: 4
            prefix: --output_noneu
    dilation:
        type: string? 
        inputBinding:
            position: 5
            prefix: --dilation
    threshold: 
        type: string?
        inputBinding:
            position: 6
            prefix: --threshold
    blob: 
        type: string?
        inputBinding:
            position: 7
            prefix: --blob
outputs: 
    assoc_output:
        type: File
        outputBinding:
            glob: $(inputs.output_name)
    assoc_output_noneu:
        type: File
        outputBinding:
            glob: $(inputs.output_name_noneu)
