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
  image_uri:
    type: string
    inputBinding:
      position: 1
      prefix: --image_uri
  seg_uri:
    type: string
    inputBinding:
      position: 2
      prefix: --seg_uri
  xmin:
    type: int
    inputBinding:
      position: 5
      prefix: --xmin
  xmax:
    type: int
    inputBinding:
      position: 6
      prefix: --xmax
  ymin:
    type: int
    inputBinding:
      position: 7
      prefix: --ymin
  ymax:
    type: int
    inputBinding:
      position: 8
      prefix: --ymax
  zmin:
    type: int
    inputBinding:
      position: 9
      prefix: --zmin
  zmax:
    type: int
    inputBinding:
      position: 10
      prefix: --zmax

  host:
    type: string?
    inputBinding:
      position: 11
      prefix: --host
  token:
    type: string?
    inputBinding:
      position: 12
      prefix: --token
  resolution:
    type: string?
    inputBinding:
      position: 13
      prefix: --resolution
  output_file:
    type: string?
    default: "error_detection.pkl"
    inputBinding:
      position: 14
      prefix: --output_file

# AWS Args
  queue:
    type: string?
    inputBinding:
      position: 15
      prefix: --queue
  bucket:
    type: string?
    inputBinding:
      position: 16
      prefix: --bucket

outputs:
  error_detection_out:
    type: ["null", File] 
    outputBinding:
      glob: $(inputs.output_file)