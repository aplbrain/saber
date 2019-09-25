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
        dockerPull: aplbrain/ffn-inference
baseCommand: python
arguments: ["driver.py"]
inputs:
  input:
    type: File
    inputBinding:
      position: 1
      prefix: --input_file 
  image_mean:
    type: string
    inputBinding:
      position: 2
      prefix: --image_mean   
  image_stddev:
    type: string
    inputBinding:
      position: 3
      prefix: --image_stddev 
  depth:
    type: string
    inputBinding:
      position: 4
      prefix: --depth
  fov_size:
    type: string
    inputBinding:
      position: 5
      prefix: --fov_size
  deltas:
    type: string
    inputBinding:
      position: 6
      prefix: --deltas
  init_activation:
    type: string
    inputBinding:
      position: 7
      prefix: --init_activation 
  pad_value:
    type: string
    inputBinding:
      position: 8
      prefix: --pad_value
  move_threshold:
    type: string
    inputBinding:
      position: 9
      prefix: --move_threshold 
  min_boundary_dist:
    type: string
    inputBinding:
      position: 10
      prefix: --min_boundary_dist
  segment_threshold:
    type: string
    inputBinding:
      position: 11
      prefix: --segment_threshold
  min_segment_size:
    type: string
    inputBinding:
      position: 12
      prefix: --min_segment_size
  bound_start:
    type: string
    inputBinding:
      position: 13
      prefix: --bound_start
  bound_stop:
    type: string
    inputBinding:
      position: 14
      prefix: --bound_stop
  outfile:
    type: string
    inputBinding:
      position: 15
      prefix: --outfile 

outputs:
  ffn_out:
    type: File
    outputBinding:
      glob: $(inputs.outfile)
