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
    token: string
    coll_name: string
    exp_name: string
    coord_name: string
    xmin: int?
    xmax: int?
    ymin: int?
    ymax: int?
    zmin: int?
    zmax: int?
    padding: int?
    resolution: int?

    ## Boss pull
    in_chan_name: string
    ## Boss push (membranes)
    mem_chan_name: string
    ## Boss push (vessels)
    ves_chan_name: string
    ## Boss push (cells)
    cell_chan_name: string
    
    # Membrane classify
    classifier: File
    ram_amount: int?
    num_threads: int?

    # Cell detect
    detect_threshold: float?
    stop: float?
    initial_template_size: int?
    detect_dilation: int?
    max_cells: int?
    cell_index: int

    # Vessel segment
    segment_threshold: float?
    segment_dilation: int?
    minimum: int?
    vessel_index: int


    
   
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
        run: ../../boss_access/boss_pull_nos3.cwl
        in:
            host_name: host_name
            token: token
            coll_name: coll_name
            exp_name: exp_name
            chan_name: in_chan_name
            dtype_name: 
                default: uint8
            itype_name: 
                default: image
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            output_name: 
                default: raw.npy
            coord_name: coord_name
        out:
            [pull_output]

           
    membrane_classify:
        run: ../tools/membrane_classify_nos3.cwl
        in:
            input: boss_pull/pull_output
            output_name: 
                default: membrane_classify_output.npy
            classifier: classifier
            ram_amount: ram_amount
            num_threads: num_threads
            
        out: [membrane_probability_map]
        hints:
            saber:
              score_format: '{} Average OOB: {score}'
    boss_push_membranes:
        run: ../../boss_access/boss_push_nos3.cwl
        in:
            host_name: host_name
            token: token
            coll_name: coll_name
            exp_name: exp_name
            chan_name: mem_chan_name
            dtype_name: 
                default: uint64
            itype_name: 
                default: annotation
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            coord_name: coord_name
            input: membrane_classify/membrane_probability_map
        out: []

    cell_detect:
        run: ../tools/cell_detect_nos3.cwl
        in:
            input: membrane_classify/membrane_probability_map
            output_name: 
                default: cell_detect_output.npy
            threshold: detect_threshold
            stop: stop
            initial_template_size: initial_template_size
            dilation: detect_dilation
            max_cells: max_cells
            cell_index: cell_index
        out: [cell_detect_results]
        hints:
            saber:
              score_format: 'Iteration remaining = {} Correlation = [[{score}]]'
    
    vessel_segment:
        run: ../tools/vessel_segment_nos3.cwl
        in:
            input: membrane_classify/membrane_probability_map
            output_name: 
                default: vessel_segment_output.npy
            threshold: segment_threshold
            dilation: segment_dilation
            minimum: minimum
            vessel_index: vessel_index
        out: [vessel_segment_results]
    boss_push_vessels:
        run: ../../boss_access/boss_push_nos3.cwl
        in:
            host_name: host_name
            token: token
            coll_name: coll_name
            exp_name: exp_name
            chan_name: ves_chan_name
            dtype_name: 
                default: uint64
            itype_name: 
                default: annotation
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            coord_name: coord_name
            input: vessel_segment/vessel_segment_results
        out: []

    cell_split:
        run: ../tools/cell_split.cwl
        in:
            input: cell_detect/cell_detect_results
            map_output_name: 
                default: cell_detect_map_output.npy
            list_output_name: 
                default: cell_detect_list_output.npy
            centroid_volume_output_name: 
                default: cell_detect_centroid_volume_output.npy
        out:
            [cell_map, cell_list, centroid_volume]
    boss_push_cells:
        run: ../../boss_access/boss_push_nos3.cwl
        in:
            host_name: host_name
            token: token
            coll_name: coll_name
            exp_name: exp_name
            chan_name: cell_chan_name
            dtype_name: 
                default: uint64
            itype_name: 
                default: annotation
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            coord_name: coord_name
            input: cell_split/centroid_volume
        out: []
