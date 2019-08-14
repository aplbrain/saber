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
                use_subdag: False
                local: True
        out:
            [pull_output]
