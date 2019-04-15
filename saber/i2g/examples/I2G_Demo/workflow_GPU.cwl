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
### GPU Specific workflow will call the membrane and synapse detection cwl files that are configured to run with the GPU enabled docker image.

cwlVersion: v1.0
class: Workflow
inputs:

    # Inputs for BOSS
    host_boss: string
    host_bossdb: string
    token_boss: string?
    token_bossdb: string?
    coll_name: string
    exp_name: string
    in_chan_name_raw: string
    out_chan_name_syn: string
    out_chan_name_neu: string
    out_chan_name_mem: string
    dtype_name_in: string
    dtype_name_out: string
    itype_name_in: string
    itype_name_out: string
    coord_name: string
    resolution: int?
    xmin: int?
    xmax: int?
    ymin: int?
    ymax: int?
    zmin: int?
    zmax: int?
    padding: int?
    pull_output_name_raw: string
    pull_output_name_ann: string
    
    #Inputs for neuron_segmentation
    train_file: File?
    neuron_mode: string
    seeds_cc_threshold: string
    agg_threshold: string
    
    #Inputs for processing
    width: int?
    height: int?
    mode: string

    #Inputs for output names:
    membrane_output: string
    synapse_output: string
    neuron_output: string

outputs:
    pull_output_raw:
        type: File
        outputSource: boss_pull_raw/pull_output
    membrane_detection:
        type: File
        outputSource: membrane_detection/membrane_detection_out
    neuron_segmentation:
        type: File
        outputSource: neuron_segmentation/neuron_segmentation_out
    synapse_detection:
        type: File
        outputSource: synapse_detection/synapse_detection_out

steps:
    boss_pull_raw:
        run: ../../../../saber/boss_access/boss_pull_nos3.cwl
        in:
            token: token_boss
            host_name: host_boss
            coll_name: coll_name
            exp_name: exp_name
            chan_name: in_chan_name_raw
            dtype_name: dtype_name_in
            itype_name: itype_name_in
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            output_name: pull_output_name_raw
            coord_name: coord_name
        out:
            [pull_output]
           
    membrane_detection:
        run: ../../../../saber/i2g/detection/membrane_detection_gpu.cwl
        in:
            input: boss_pull_raw/pull_output
            width: width
            height: height
            output: membrane_output
        out: [membrane_detection_out]
    synapse_detection:
        run: ../../../../saber/i2g/detection/synapse_detection_gpu.cwl
        in:
            input: boss_pull_raw/pull_output
            width: width
            height: height
            mode: mode
            output: synapse_output
        out: [synapse_detection_out]
    neuron_segmentation:
        run: ../../../../saber/i2g/neuron_segmentation/neuron_segmentation.cwl
        in:
            prob_file: membrane_detection/membrane_detection_out
            mode: neuron_mode
            train_file: train_file
            agg_threshold: agg_threshold
            seeds_cc_threshold: seeds_cc_threshold
            outfile: neuron_output
        out: [neuron_segmentation_out]
    boss_push_neurons_boss:
        run: ../../../../saber/boss_access/boss_push_nos3.cwl
        in:
            token: token_boss
            host_name: host_boss
            coll_name: coll_name
            exp_name: exp_name
            chan_name: out_chan_name_neu
            dtype_name: dtype_name_out
            itype_name: itype_name_out
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            input: neuron_segmentation/neuron_segmentation_out
            coord_name: coord_name
        out: []

    boss_push_synapses_boss:
        run: ../../../../saber/boss_access/boss_push_nos3.cwl
        in:
            token: token_boss
            host_name: host_boss
            coll_name: coll_name
            exp_name: exp_name
            chan_name: out_chan_name_syn
            dtype_name: dtype_name_in
            itype_name: itype_name_in
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            input: synapse_detection/synapse_detection_out
            coord_name: coord_name
        out: []

    boss_push_neurons_bossdb:
        run: ../../../../saber/boss_access/boss_push_nos3.cwl
        in:
            token: token_bossdb
            host_name: host_bossdb
            coll_name: coll_name
            exp_name: exp_name
            chan_name: out_chan_name_neu
            dtype_name: dtype_name_out
            itype_name: itype_name_out
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            input: neuron_segmentation/neuron_segmentation_out
            coord_name: coord_name
        out: []

    boss_push_synapses_bossdb:
        run: ../../../../saber/boss_access/boss_push_nos3.cwl
        in:
            token: token_bossdb
            host_name: host_bossdb
            coll_name: coll_name
            exp_name: exp_name
            chan_name: out_chan_name_syn
            dtype_name: dtype_name_in
            itype_name: itype_name_in
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            input: synapse_detection/synapse_detection_out
            coord_name: coord_name
        out: []
        
    boss_push_membranes_boss:
        run: ../../../../saber/boss_access/boss_push_nos3.cwl
        in:
            token: token_boss
            host_name: host_boss
            coll_name: coll_name
            exp_name: exp_name
            chan_name: out_chan_name_mem
            dtype_name: dtype_name_in
            itype_name: itype_name_in
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            input: membrane_detection/membrane_detection_out
            coord_name: coord_name
        out: []

    boss_push_membranes_bossdb:
        run: ../../../../saber/boss_access/boss_push_nos3.cwl
        in:
            token: token_bossdb
            host_name: host_bossdb
            coll_name: coll_name
            exp_name: exp_name
            chan_name: out_chan_name_mem
            dtype_name: dtype_name_in
            itype_name: itype_name_in
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            input: membrane_detection/membrane_detection_out
            coord_name: coord_name
        out: []