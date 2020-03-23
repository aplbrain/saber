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
    coord: string
    token: string
    host_name: string
    coll: string
    exp: string
    chan_labels: string
    chan_img: string
    dtype_img: string
    dtype_lbl: string
    itype_name: string
    padding: int
    res: int
    xmin: int
    xmax: int
    ymin: int
    ymax: int
    zmin: int
    zmax: int
    raw_pull_output_name: string
    anno_pull_output_name: string

    width: int
    height: int
    mode: string
    synapse_output_name: string

    threshold: string
    threshold_output_name: string

outputs:
    pull_output:
        type: File
        outputSource: raw_boss_pull/pull_output
    anno_output:
        type: File
        outputSource: anno_boss_pull/pull_output
    synapse_detection:
        type: File
        outputSource: synapse_detection/synapse_detection_out
    threshold_output:
        type: File
        outputSource: threshold/threshold_out

steps:
    raw_boss_pull:
        run: ../../saber/boss_access/boss_pull_nos3.cwl
        in:
            host_name: host_name
            token: token
            coll_name: coll
            exp_name: exp
            chan_name: chan_img
            dtype_name: dtype_img
            resolution: res
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            itype_name: itype_name
            padding: padding
            output_name: raw_pull_output_name
            coord_name: coord
        out:
            [pull_output]
        hints: 
            saber:
                local: True
                file_path: /home/xenesd1-a/saber/output
    
    anno_boss_pull:
        run: ../../saber/boss_access/boss_pull_nos3.cwl
        in:
            host_name: host_name
            token: token
            coll_name: coll
            exp_name: exp
            chan_name: chan_labels
            dtype_name: dtype_lbl
            resolution: res
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            itype_name: itype_name
            padding: padding
            output_name: anno_pull_output_name
            coord_name: coord
        out:
            [pull_output]
        hints: 
            saber:
                local: True
                file_path: /home/xenesd1-a/saber/output
    
    synapse_detection:
        run: ../../saber/i2g/detection/synapse_detection.cwl
        in:
            input: raw_boss_pull/pull_output
            width: width
            height: height
            mode: mode
            output: synapse_output_name
        hints:
            saber:
                local: True
                file_path: /home/xenesd1-a/saber/output
        out: [synapse_detection_out]
    
    threshold:
        run: ../../saber/postprocessing/threshold/threshold.cwl
        in:
            input: synapse_detection/synapse_detection_out
            groundtruth: anno_boss_pull/pull_output
            threshold: threshold
            outfile: threshold_output_name
        out:
            [threshold_out]
        hints: 
            saber:
                local: True
                file_path: /home/xenesd1-a/saber/output
                score_format: "F1: {score}"