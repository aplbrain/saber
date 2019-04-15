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
inputs:
    # Boss 
    im_chan_name: string
    an_chan_name: string
    token: string?
    coll_name: string
    exp_name: string
    dtype_name: string
    out_dtype_name: string
    itype_name: string
    out_itype_name: string
    resolution: int?
    xmin: int?
    xmax: int?
    ymin: int?
    ymax: int?
    zmin: int?
    zmax: int?
    padding: int?
    pull_output_name: string
    anno_output_name: string
    coord_name: string
    host_name: string
    onesided: int?
    # Membrane classify
    membrane_output_name: string
    num_samp: int?
    num_comp: int?
    erode: int?
    vessel_thres: float?
    min_size: float?
    cell_class: int?
    
    # Cell detect
    detect_threshold: float?
    stop: float?
    initial_template_size: int?
    detect_dilation: int?
    max_cells: int?
    detect_output_name: string
    dense_output_name: string
    
    #metrics
    metrics_output_name: string


    
outputs:
    boss_output:
        type: File
        outputSource: data_pull/pull_output
    anno_output:
        type: File
        outputSource: annotation_pull/pull_output
    membrane_classify_output:
        type: File
        outputSource: membrane_classify/membrane_probability_map
    cell_detect_output:
        type: File
        outputSource: cell_detect/cell_detect_results
    cell_detect_dense:
        type: File
        outputSource: cell_detect/dense_output    
    metrics_output:
        type: File
        outputSource: metrics/metrics
steps:
    data_pull:
        run: ../../../../saber/boss_access/boss_pull_nos3.cwl
        in:
            host_name: host_name
            token: token
            coll_name: coll_name
            exp_name: exp_name
            chan_name: im_chan_name
            dtype_name: out_dtype_name
            itype_name: out_itype_name
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            output_name: pull_output_name
            coord_name: coord_name
        out:
            [pull_output]
        hints:
            saber:
                local: True
    annotation_pull:
        run: ../../../../saber/boss_access/boss_pull_nos3.cwl
        in:
            host_name: host_name
            token: token
            coll_name: coll_name
            exp_name: exp_name
            chan_name: an_chan_name
            dtype_name: dtype_name
            itype_name: itype_name
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            output_name: anno_output_name
            coord_name: coord_name
        out:
            [pull_output]
        hints:
            saber:
                local: True
    membrane_classify:
        run: ../../tools/unsup_membrane_classify_3D_nos3.cwl
        in:
            input: data_pull/pull_output
            output_name: membrane_output_name
            num_samp: num_samp
            num_comp: num_comp
            erode: erode
            vessel_thres: vessel_thres
            min_size: min_size
            cell_class: cell_class
        out: [membrane_probability_map]
        hints:
            saber:
                local: True
    cell_detect:
        run: ../../tools/unsup_cell_detect_3D_nos3.cwl
        in:
            input: membrane_classify/membrane_probability_map
            output_name: detect_output_name
            threshold: detect_threshold
            stop: stop
            initial_template_size: initial_template_size
            dilation: detect_dilation
            max_cells: max_cells
            dense_output_name: dense_output_name
        out: [cell_detect_results, dense_output]
        hints:
            saber:
                local: True
                
    metrics:
        run: ../../tools/unsup_metrics_nos3.cwl
        in:
            input: cell_detect/cell_detect_results
            output_name: metrics_output_name
            ground_truth: annotation_pull/pull_output
            initial_template_size: initial_template_size
        out: [metrics]
        hints:
            saber:
                score_format: "F1: {score}"
                local: True
