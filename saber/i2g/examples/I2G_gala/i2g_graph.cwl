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
    synapse_detection_input_name: string
    neuron_segmentation_input_name: string
    graph_gen_output_name: string
    dilation: int?

outputs:
    graph_generation_output:
        type: File
        outputSource: graph_generation/graph_generation_out

steps:
    graph_generation:
        run: ../tools/graph_generation.cwl
        in: 
            seginput: neuron_segmentation_input_name
            synapseinput: synapse_detection_out
            dilation: dilation
            output_name: graph_gen_output_name
        out: [graph_generation_out]


