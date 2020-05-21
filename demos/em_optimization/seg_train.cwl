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

    # Inputs for BOSS
    host_bossdb: string
    token_bossdb: string?
    coll_name: string
    exp_name: string
    in_chan_name_raw: string
    dtype_name_in: string
    itype_name_in: string
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

    #Inputs for processing
    width: int?
    height: int?
    mode: string

    #Inputs for neuron_segmentation
    train_mode: string
    deploy_mode: string 
    gt_file: File?
    ws_file: File?

    seeds_cc_threshold: string
    agg_threshold: string

    #Inputs for output names:
    synapse_output: string
    membrane_output: string
    neuron_output: string

outputs:
    pull_output_raw:
        type: File
        outputSource: boss_pull_raw/pull_output
    synapse_detection:
        type: File
        outputSource: synapse_detection/synapse_detection_out
    membrane_detection:
        type: File
        outputSource: membrane_detection/membrane_detection_out
    neuron_segmentation_train:
        type: File
        outputSource: neuron_segmentation_train/neuron_segmentation_train_out
    neuron_segmentation_deploy:
        type: File
        outputSource: neuron_segmentation_deploy/neuron_segmentation_deploy_out

steps:
    boss_pull_raw:
        run: ../../../../saber/boss_access/boss_pull_nos3.cwl
        in:
            token: token_bossdb
            host_name: host_bossdb
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
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/volumes/data/local
        out:
            [pull_output]


    synapse_detection:
        run: ../../../../saber/i2g/detection/synapse_detection.cwl
        in:
            input: boss_pull_raw/pull_output
            width: width
            height: height
            mode: mode
            output: synapse_output
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/volumes/data/local
        out: [synapse_detection_out]

    membrane_detection:
        run: ../../../../saber/i2g/detection/membrane_detection.cwl
        in:
            input: boss_pull_raw/pull_output
            width: width
            height: height
            output: membrane_output
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/volumes/data/local
        out: [membrane_detection_out]

    neuron_segmentation_train:
        run: ../../../../saber/i2g/neuron_segmentation/neuron_segmentation.cwl
        in:
            prob_file: membrane_detection/membrane_detection_out
            mode: train_mode
            gt_file: gt_file
            ws_file: ws_file
            outfile: neuron_output
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/volumes/data/local
        out: [neuron_segmentation_train_out]

    neuron_segmentation_deploy:
        run: ../../../../saber/i2g/neuron_segmentation/neuron_segmentation.cwl
        in:
            prob_file: membrane_detection/membrane_detection_out
            mode: deploy_mode
            train_file: neuron_segmentation_train/neuron_segmentation_train_out
            agg_threshold: agg_threshold
            seeds_cc_threshold: seeds_cc_threshold
            outfile: neuron_output
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/volumes/data/local
        out: [neuron_segmentation_deploy_out]