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
class: Workflow
doc: local

cwlVersion: v1.0
class: Workflow
inputs:
    input: File
    min: string
    max: string
    outfile: string 

outputs:
    blob_detect_output:
        type: File
        outputSource: blob_detect/blob_detect_out
steps:
    blob_detect:
        run: ../blob_detect.cwl
        in:
            input: input
            min: min
            max: max
            outfile: outfile
        out:
            [blob_detect_out]
        hints: 
            saber:
                local: True
                file_path: /Users/xenesd1/Projects/aplbrain/saber/output