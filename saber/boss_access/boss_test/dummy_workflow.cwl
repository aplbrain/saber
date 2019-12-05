
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

cwlVersion: v1.0
class: Workflow
doc: local
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
    output_name: string
    coord_name: string
    dtype_name: string
    itype_name: string
    ## Boss pull
    in_chan_name: string

outputs:
    pull_output:
        type: File
        outputSource: boss_pull/pull_output
steps:
    boss_pull:
        run: ../../../../saber/boss_access/boss_pull_nos3.cwl
        in:
            host_name: host_name
            token: token
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
            output_name: output_name
            coord_name: coord_name
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/volumes/data/local
        out:
            [pull_output]
