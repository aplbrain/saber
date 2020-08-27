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
    #Inputs for Neuroproof
    mode: string
    ws_file: File
    pred_file: File
    gt_file: File
    

    #Inputs for output names:
    neuroproof_output: string

outputs:
    neuroproof:
        type: File
        outputSource: neuroproof/neuroproof_out

steps:
    neuroproof:
        run: ../../../../saber/i2g/neuroproof/neuroproof.cwl
        in:
            mode: mode
            ws_file: ws_file
            pred_file: pred_file
            gt_file: gt_file
            outfile: neuroproof_output
        hints:
            saber:
                local: True
                file_path: /Users/xenesd1/Projects/aplbrain/saber/volumes/data/local
        out: [neuroproof_out]
