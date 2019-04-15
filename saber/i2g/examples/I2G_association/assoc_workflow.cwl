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
    seg_chan_name: string
    syn_chan_name: string
    token: string?
    coll_name: string
    exp_name: string
    dtype_seg: string
    dtype_syn: string
    resolution: int?
    xmin: int?
    xmax: int?
    ymin: int?
    ymax: int?
    zmin: int?
    zmax: int?
    coord_name: string
    host_name: string
    assoc_output_name: string
    assoc_output_name_noneu: string
    use_boss: int
outputs:
    assoc_output:
        type: File
        outputSource: assoc/assoc_output
    assoc_output_noneu:
        type: File
        outputSource: assoc/assoc_output_noneu
steps:
    assoc:
        run: ../seg_syn_association/assoc.cwl
        in:
            use_boss: use_boss
            host_name: host_name
            token: token
            coll_name: coll_name
            exp_name: exp_name
            chan_seg: seg_chan_name
            chan_syn: syn_chan_name
            dtype_syn: dtype_syn
            dtype_seg: dtype_seg
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            output_name: assoc_output_name
            output_name_noneu: assoc_output_name_noneu
            coord_name: coord_name
        out:
            [assoc_output,assoc_output_noneu]
        hints:
            saber:
                local: True
