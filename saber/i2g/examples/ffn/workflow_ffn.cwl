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
    #Inputs for FFN
    config_file: string
    bounding_box: string
    outfile: string 

outputs:
    ffn_segmentation:
        type: File
        outputSource: ffn_segmentation/ffn_out

steps:
    ffn_segmentation:
        run: ../../../../saber/i2g/ffns/ffn_segmentation.cwl
        in:
            config_file: config_file
            bounding_box: bounding_box
            outfile: outfile
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/volumes/data/local
        out: [ffn_out]