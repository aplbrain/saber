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

cwlVersion: v1.0
class: Workflow
doc: local

inputs:
    input_int: int


    

outputs: 
    output1:
        type: File
        outputSource: step1/output
    output2:
        type: File
        outputSource: step2/output
    output3:
        type: File
        outputSource: step3/output

steps:
    step1:
        run: ../tools/echotool.cwl
        in:
            input_int: input_int

        hints: 
            saber:
                local: True
        out: [output]
    step2:
        run: ../tools/echotool.cwl
        in:
            input_int: input_int

        hints: 
            saber:
                local: True
        out: [output]
    step3:
        run: ../tools/echotool.cwl
        in:
            input_int: input_int

        hints: 
            saber:
                local: True
        out: [output]
