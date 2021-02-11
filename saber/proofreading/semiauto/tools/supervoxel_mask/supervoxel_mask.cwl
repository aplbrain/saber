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
        dockerPull: proofreading/supervoxel_mask
baseCommand: python
arguments: ["supervoxel_mask.py"]
inputs:
  input:
    type: File
    inputBinding:
      position: 1
      prefix: --input
  supervoxel_ids:
    type: File?
    inputBinding:
      position: 2
      prefix: --supervoxel_ids
  output:
    type: string
    inputBinding:
      position: 4
      prefix: --output
outputs:
  supervoxel_mask_out:
    type: File
    outputBinding:
      glob: $(inputs.output)
