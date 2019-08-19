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
        dockerPull: aplbrain/neuroproof
baseCommand: python3
arguments: ["driver.py"]
inputs:
  mode:
    type: string
    inputBinding:
      position: 1
      prefix: --mode
  ws_file:
    type: File
    inputBinding:
      position: 2
      prefix: --ws_file
  pred_file:
    type: File
    inputBinding:
      position: 2
      prefix: --pred_file
  gt_file:
    type: File?
    inputBinding:
      position: 3
      prefix: --gt_file
  train_file:
    type: File?
    inputBinding:
      position: 4
      prefix: --train_file
  iterations:
    type: string?
    inputBinding:
      position: 5
      prefix: --num_iterations
  use_mito:
    type: string?
    inputBinding:
      position: 6
      prefix: --use_mito
  outfile:
    type: string
    inputBinding:
      position: 7
      prefix: --outfile
outputs:
  neuroproof_out:
    type: File
    outputBinding:
      glob: $(inputs.outfile)
