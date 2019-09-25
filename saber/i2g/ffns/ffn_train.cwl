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
        dockerPull: aplbrain/ffn_train
baseCommand: /bin/bash
arguments: ["main.sh"]
inputs:
  input:
    type: File
    inputBinding:
      position: 1
      prefix: --input
  seg_input:
    type: File
    inputBinding:
      position: 2
      prefix: --seg_input
  min_thres:
    type: float?
    inputBinding:
      position: 3
      prefix: --min_thres
  max_thres:
    type: float?
    inputBinding:
      position: 4
      prefix: --max_thres
  thres_step:
    type: float?
    inputBinding:
      position: 5
      prefix: --thres_step
  lom_radius:
    type: int?
    inputBinding:
      position: 6
      prefix: --lom_radius
  min_size:
    type: int?
    inputBinding:
      position: 7
      prefix: --min_size
  margin:
    type: int?
    inputBinding:
      position: 8
      prefix: --margin
  model_name:
    type: string
    inputBinding:
      position: 9
      prefix: --name
  depth:
    type: int?
    inputBinding:
      position: 10
      prefix: --depth  
  fov:
    type: int?
    inputBinding:
      position: 11
      prefix: --fov  
  deltas:
    type: int?
    inputBinding:
      position: 12
      prefix: --deltas  
  image_mean:
    type: int?
    inputBinding:
      position: 13
      prefix: --image_mean  
  image_std:
    type: int?
    inputBinding:
      position: 14
      prefix: --image_std  
  max_steps:
    type: int?
    inputBinding:
      position: 15
      prefix: --max_steps  
  output:
    type: string
    inputBinding:
      position: 16
      prefix: --output
outputs:
  training_out:
    type: File
    outputBinding:
      glob: $(inputs.output)
