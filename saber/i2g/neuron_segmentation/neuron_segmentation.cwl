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
        dockerPull: aplbrain/i2gseg
baseCommand: python3
arguments: ["driver.py"]
inputs:
  mode:
    type: string
    inputBinding:
      position: 1
      prefix: --mode
  prob_file:
    type: File
    inputBinding:
      position: 2
      prefix: --prob_file
#  gt_file:
#    type: File?
#    inputBinding:
#      position: 3
#      prefix: --gt_file
#  ws_file:
#    type: File?
#    inputBinding:
#      position: 4
#      prefix: --ws_file
  train_file:
    type: File?
    inputBinding:
      position: 5
      prefix: --train_file
  seeds_cc_threshold:
    type: string
    inputBinding:
      position: 6
      prefix: --seeds_cc_threshold
  agg_threshold:
    type: string
    inputBinding:
      position: 7
      prefix: --agg_threshold
  outfile:
    type: string
    inputBinding:
      position: 8
      prefix: --outfile
outputs:
  neuron_segmentation_out:
    type: File
    outputBinding:
      glob: $(inputs.outfile)
      
