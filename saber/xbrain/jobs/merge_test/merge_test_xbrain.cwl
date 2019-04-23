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
    # Inputs for BOSS
    host_name: string
    config: File?
    token: string?
    coll_name: string
    exp_name: string
    in_chan_name: string
    out_chan_name: string
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
    coord_name: string
    # Inputs for steps
    
    classifier: File
    membrane_classify_output_name: string
    cell_detect_output_name: string
    vessel_segment_output_name: string
    ram_amount: int?
    num_threads: int?
    detect_threshold: float?
    stop: float?
    initial_template_size: int?
    detect_dilation: int?
    max_cells: int?
    segment_threshold: float?
    segment_dilation: int?
    minimum: int?

    map_output_name: string
    list_output_name: string
    centroid_volume_output_name: string

    template_size: int
outputs:
    pull_output:
        type: File
        outputSource: boss_pull/pull_output
    membrane_classify_output:
        type: File
        outputSource: membrane_classify/membrane_probability_map
    cell_detect_output:
        type: File
        outputSource: cell_detect/cell_detect_results
    vessel_segment_output:
        type: File
        outputSource: vessel_segment/vessel_segment_results

steps:
    boss_pull:
        run: ../../../../saber/boss_access/boss_pull_nos3.cwl
        in:
            config: config
            token: token
            host_name: host_name
            coll_name: coll_name
            exp_name: exp_name
            chan_name: in_chan_name
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
            output_name: pull_output_name
            coord_name: coord_name
        out:
            [pull_output]
        hints:
            saber:
                local: True
           
    membrane_classify:
        run: ../../../../saber/xbrain/tools/membrane_classify_nos3.cwl
        in:
            input: boss_pull/pull_output
            output_name: membrane_classify_output_name
            classifier: classifier
            ram_amount: ram_amount
            num_threads: num_threads
            
        out: [membrane_probability_map]
        hints:
            saber:
              score_format: '{} Average OOB: {score}'
    cell_detect:
        run: ../../../../saber/xbrain/tools/cell_detect_nos3.cwl
        in:
            input: membrane_classify/membrane_probability_map
            output_name: cell_detect_output_name
            classifier: classifier
            threshold: detect_threshold
            stop: stop
            initial_template_size: initial_template_size
            dilation: detect_dilation
            max_cells: max_cells
            
        out: [cell_detect_results]
        hints:
            saber:
              score_format: 'Iteration remaining = {} Correlation = [[{score}]]'

    vessel_segment:
        run: ../../../../saber/xbrain/tools/vessel_segment_nos3.cwl
        in:
            input: membrane_classify/membrane_probability_map
            output_name: vessel_segment_output_name
            classifier: classifier
            threshold: segment_threshold
            dilation: segment_dilation
            minimum: minimum
        out: [vessel_segment_results]
    cell_split:
        run: ../../../../saber/xbrain/tools/cell_split.cwl
        in:
            input: cell_detect/cell_detect_results
            map_output_name: map_output_name
            list_output_name: list_output_name
            centroid_volume_output_name: centroid_volume_output_name
        out:
            [cell_map, cell_list, centroid_volume]
        hints:
            saber:
                local: True
    boss_merge:
        run: ../../../../saber/boss_access/boss_merge_nos3.cwl
        in:
            input: cell_split/cell_map
            centroids: cell_split/cell_list
            host_name: host_name
            output_name: list_output_name
            templatesize: template_size

            token: token
            coll_name: coll_name
            exp_name: exp_name
            chan_name: out_chan_name
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
            
            coord_name: coord_name
        out: [pull_output]
        hints:
            saber:
                local: True
