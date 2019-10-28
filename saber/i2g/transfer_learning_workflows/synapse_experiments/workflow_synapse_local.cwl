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
## This workflow will make use of the general synapse and membrane detection cwl files, meaning the processes will happen on CPU rather than on GPU. Does not include Boss push steps. 

cwlVersion: v1.0
class: Workflow
doc: local

inputs:
    #Inputs for processing
    width: int?
    height: int?
    mode: string
    input: File

    #Inputs for output names:
    synapse_output: string

outputs:
    synapse_detection:
        type: File
        outputSource: synapse_detection/synapse_detection_out

steps:

    synapse_detection:
        run: ../../../i2g/detection/synapse_detection_gpu.cwl
        in:
            input: input
            width: width
            height: height
            mode: mode
            output: synapse_output
        hints:
            saber:
                local: True
                file_path: ""
        out: [synapse_detection_out]
