# Copyright 2020 The Johns Hopkins University Applied Physics Laboratory
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
        dockerPull: proofreading/error_detection
baseCommand: python
arguments: ["error_detection.py"]
inputs:
  seg:
    type: File
    inputBinding:
      position: 1
      prefix: --seg
  source:
    type: string
    inputBinding:
      position: 2
      prefix: --source
  output:
    type: string
    inputBinding:
      position: 3
      prefix: --output
  ids:
    type: File?
    inputBinding:
      position: 1
      prefix: --ids
outputs:
  error_detection_out:
    type: File
    outputBinding:
      glob: $(inputs.output)
