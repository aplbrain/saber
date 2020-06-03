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

#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
doc: local

inputs:
    # Inputs for BOSS
    host_bossdb: string
    token_bossdb: string
    coll_name: string
    exp_name: string
    chan_name_img: string
    chan_name_lbl:
    dtype_img: string
    dtype_lbl: string
    itype_name_in: string
    coord_name: string
    resolution: int
    xmin: int
    xmax: int
    ymin: int
    ymax: int
    zmin: int
    zmax: int
    padding: int?

    Inputs for U-Net Train Steps:
    use_boss: int?
    train_pct: float?
    n_epochs: int?
    mb_size: int?
    n_mb_per_epoch: int?
    learning_rate: float?
    use_adam: boolean?
    beta1: float?
    beta2: float?
    decay: float?
    momentum: float?
    save_freq: int?
    do_warp: boolean?
    tile_size: int?
    output: string

    #Inputs for processing
    width: int?
    height: int?

    #Inputs for neuron_segmentation
    train_file: File?
    neuron_mode: string
    seeds_cc_threshold: string
    agg_threshold: string

    #Inputs for output file names:
    synapse_weights_output: string
    membrane_weights_output: string
    pull_output_name_raw: string
    synapse_output: string
    membrane_output: string
    neuron_output: string
    assoc_output_name: string
    assoc_output_name_noneu: string

outputs:
    synapse_detection_train:
        type: File
        outputSource: synapse_detection_train/detection_train_out
    membrane_detection_train:
        type: File
        outputSource: membrane_detection_train/detection_train_out
    boss_pull_raw:
        type: File
        outputSource: boss_pull_raw/pull_output
    synapse_detection:
        type: File
        outputSource: synapse_detection/synapse_detection_out
    membrane_detection:
        type: File
        outputSource: membrane_detection/membrane_detection_out
    neuron_segmentation:
        type: File
        outputSource: neuron_segmentation/neuron_segmentation_out
    assoc_output:
        type: File
        outputSource: assoc/assoc_output
    assoc_output_noneu:
        type: File
        outputSource: assoc/assoc_output_noneu

steps:
    synapse_detection_train:
        run: ../../../../saber/i2g/detection/detection_train.cwl
        in:
            use_boss: use_boss
            coord: coord
            token: token_bossdb
            coll: coll_name
            exp: exp_name
            chan_labels: chan_labels
            chan_img: chan_name
            dtype_img: dtype_img
            dtype_lbl: dtype_lbl
            res: res
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            train_pct: train_pct
            n_epochs: n_epochs
            mb_size: mb_size
            n_mb_per_epoch: n_mb_per_epoch
            learning_rate: learning_rate
            use_adam: use_adam
            beta1: beta1
            beta2: beta2
            decay: decay
            momentum: momentum
            save_freq: save_freq
            do_warp: do_warp
            tile_size: tile_size
            output: synapse_weights_output
        out: [detection_train_out]
        hints:
            saber: 
                score_format: "F1: {score}\n" 
                file_path: /home/ubuntu/saber/outputs
                local: True

    membrane_detection_train:
        run: ../../../../saber/i2g/detection/detection_train.cwl
        in:
            use_boss: use_boss
            coord: coord
            token: token
            coll: coll
            exp: exp
            chan_labels: chan_labels
            chan_img: chan_img
            dtype_img: dtype_img
            dtype_lbl: dtype_lbl
            res: res
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            train_pct: train_pct
            n_epochs: n_epochs
            mb_size: mb_size
            n_mb_per_epoch: n_mb_per_epoch
            learning_rate: learning_rate
            use_adam: use_adam
            beta1: beta1
            beta2: beta2
            decay: decay
            momentum: momentum
            save_freq: save_freq
            do_warp: do_warp
            tile_size: tile_size
            output: membrane_weights_output
        out: [detection_train_out]
        hints:
            saber: 
                score_format: "F1: {score}\n" 
                file_path: /home/ubuntu/saber/outputs
                local: True

    boss_pull_raw:
        run: ../../../../saber/boss_access/boss_pull_nos3.cwl
        in:
            token: token_bossdb
            host_name: host_bossdb
            coll_name: coll_name
            exp_name: exp_name
            chan_name: in_chan_name_raw
            dtype_name: dtype_img
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
                file_path: /home/ubuntu/saber/outputs
        out:
            [pull_output]

    synapse_detection:
        run: ../../../../saber/i2g/detection/detection_deploy.cwl
        in:
            input: boss_pull_raw/pull_output
            width: width
            height: height
            weights: synapse_detection_train/detection_train_out
            output: synapse_output
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/outputs
        out: [synapse_detection_out]

    membrane_detection:
        run: ../../../../saber/i2g/detection/detection_deploy.cwl
        in:
            input: boss_pull_raw/pull_output
            width: width
            height: height
            output: membrane_output
            weights: membrane_detection_train/detection_train_out
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/outputs
        out: [membrane_detection_out]

    neuron_segmentation:
        run: ../../../../saber/i2g/neuron_segmentation/neuron_segmentation.cwl
        in:
            prob_file: membrane_detection/membrane_detection_out
            mode: neuron_mode
            train_file: train_file
            agg_threshold: agg_threshold
            seeds_cc_threshold: seeds_cc_threshold
            outfile: neuron_output
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/outputs
        out: [neuron_segmentation_out]
    
    assoc:
        run: ../../saber/i2g/seg_syn_association/assoc_local.cwl
        in:
            seg_file: neuron_segmentation/neuron_segmentation_out
            syn_file: synapse_detection/synapse_detection_out
            output_name: assoc_output_name
            output_name_noneu: assoc_output_name_noneu
        out:
            [assoc_output,assoc_output_noneu]
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/outputs