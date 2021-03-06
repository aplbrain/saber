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

cwlVersion: v1.0
class: CommandLineTool
hints:
    DockerRequirement:
        dockerPull: aplbrain/i2gdetect
baseCommand: python
arguments: ["deploy_pipeline.py --mode synapse"]
inputs:
  input:
    type: File
    inputBinding:
      position: 1
      prefix: --input
  height:
    type: int?
    inputBinding:
      position: 2
      prefix: --height
  width:
    type: int?
    inputBinding:
      position: 3
      prefix: --width
#  z_step:
#    type: int?
#    inputBinding:
#      position: 4
#      prefix: --z_step
  output:
    type: string
    inputBinding:
      position: 5
      prefix: --output
  mode:
    type: string
    inputBinding:
      position: 6
      prefix: --mode
outputs:
  synapse_detection_out:
    type: File
    outputBinding:
      glob: $(inputs.output)
      
