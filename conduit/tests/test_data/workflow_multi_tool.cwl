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
    input_bool: boolean
    input_float: float
    input_double: double
    input_string: string
    input_file: File
    # Optional arguments
    input_optint: int?
    input_optbool: boolean?
    input_optfloat: float?
    input_optdouble: double?
    input_optstring: string?
    input_optfile: File?
    

outputs:
    output_int:
        type: int
        outputSource: step1/output
    output_bool:
        type: boolean
        outputSource: step2/output
    output_float:
        type: float
        outputSource: step3/output
    output_double:
        type: double
        outputSource: step4/output
    output_string:
        type: string
        outputSource: step5/output
    output_file:
        type: file
        outputSource: step6/output

steps:
    step1:
        run: ./multitool.cwl
        in:
            input_int: inputint
            input_opt_int: input_opt_int
            input_bool: input_bool
            input_optbool: input_opt_bool
        hints: 
            saber:
                local: True
        out: [output]
    step2:
        run: ./multitool.cwl
        in:
            input_file: step1/output

    
        hints: 
            saber:
                local: True
        out: [output]
    step3:
        run: ./tool_mid.cwl
        in:
            input_file: step2/output

        hints: 
            saber:
                local: True
        out: [output]
    step3:
        run: ../tools/unsup_metrics_nos3.cwl
        in:
            input: cell_detect/cell_detect_results
            output_name: 
                default: 'optiout.npy'
            initial_template_size: initial_template_size
            ground_truth: cell_gt
        hints: 
            saber:
                local: True
                score_format: "F1: {score}"
        out: [metrics]
