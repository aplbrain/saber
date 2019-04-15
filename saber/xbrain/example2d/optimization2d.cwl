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
    data: File
    cell_gt: File
    detect_threshold: float?
    stop: float?
    initial_template_size: int?
    detect_dilation: int?
    max_cells: int?
    num_samp: int?
    num_comp: int?
    erode: int?

outputs:
    membrane_classify_output:
        type: File
        outputSource: membrane_classify/membrane_probability_map
    cell_detect_output:
        type: File
        outputSource: cell_detect/cell_detect_results
    metrics_output:
        type: File
        outputSource: metrics/metrics
steps:
    membrane_classify:
        run: ../tools/unsup_membrane_classify_nos3.cwl
        in:
            input: data
            output_name: 
                default: 'optiout.npy'
            num_samp: num_samp
            num_comp: num_comp
            erodesz: erode
        hints: 
            saber:
                local: True
        out: [membrane_probability_map]
    cell_detect:
        run: ../tools/unsup_cell_detect_nos3.cwl
        in:
            input: membrane_classify/membrane_probability_map
            output_name: 
                default: 'optiout.npy'
            threshold: detect_threshold
            stop: stop
            initial_template_size: initial_template_size
            dilation: detect_dilation
            max_cells: max_cells
        hints: 
            saber:
                local: True
        out: [cell_detect_results]
    metrics:
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
