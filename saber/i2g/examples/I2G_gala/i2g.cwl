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
    membrane_detection_output_name: string
    synapse_detection_output_name: string
    neuron_segmentation_output_name: string
    graph_gen_output_name: string
    data: File
    mode: int?
    height: int?
    width: int?
    z_step: int?
    seed_thres: int?
    agg_thres: float?
    train_file: File
    dilation: int?

outputs:
    membrane_detection_output:
        type: File
        outputSource: membrane_detection/membrane_detection_out
    synapse_detection_output:
        type: File
        outputSource: synapse_detection/synapse_detection_out
    neuron_segmentation_output:
        type: File
        outputSource: neuron_segmentation/neuron_segmentation_out
    graph_generation_output:
        type: File
        outputSource: graph_generation/graph_generation_out

steps:
    membrane_detection:
        run: ../detection/membrane_detection.cwl
        in:
            input: data
            height : height
            width : width
            z_step : z_step
            output: membrane_detection_output_name
        out: [membrane_detection_out]
    synapse_detection:
        run: ../detection/synapse_detection.cwl
        in:
            input: data
            height: height
            width: width
            z_step: z_step
            output: synapse_detection_output_name
        out: [synapse_detection_out]
    neuron_segmentation:
        run: ../neuron_segmentation/neuron_segmentation.cwl
        in:
            mode: mode
            prob_file: membrane_detection/membrane_detection_out
            train_file: train_file
            seeds_cc_threshold: seed_thres
            agg_threshold: agg_thres
            outfile: neuron_segmentation_output_name
        out: [neuron_segmentation_out]
    graph_generation:
        run: ../graph_generation/graph_generation.cwl
        in: 
            seginput: neuron_segmentation/neuron_segmentation_out
            synapseinput: synapse_detection/synapse_detection_out
            dilation: dilation
            output_name: graph_gen_output_name
        out: [graph_generation_out]


