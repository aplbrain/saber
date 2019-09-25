#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
inputs:
    use_boss: int
    coord: string?
    token: string?
    host_name: string?
    coll: string?
    exp: string?
    chan_labels: string?
    chan_img: string?
    dtype_img: string?
    dtype_lbl: string?
    itype: string?
    padding: int?
    res: int?
    xmin: int?
    xmax: int?
    ymin: int?
    ymax: int?
    zmin: int?
    zmax: int?
    train_pct: float?
    n_epochs: int?
    mb_size: int?
    n_mb_per_epoch: int?
    use_adam: int?
    learning_rate: float?
    decay: float?
    momentum: float?
    beta1: float?
    beta2: float?
    save_freq: int?
    do_warp: boolean?
    tile_size: int?
    weights_file: File?

    detect_threshold: float?
    stop: float?
    initial_template_size: int?
    detect_dilation: int?

    output: string
    score_out: string
    raw_pull_output_name: string
    anno_pull_output_name: string
    metrics_out: string
outputs:
    train_output:
        type: File
        outputSource: optimize/classifier_weights
steps:
    raw_boss_pull:
        run: ../../boss_access/boss_pull.cwl
        in:
            host_name: host_name
            token: token
            coll_name: coll_name
            exp_name: exp_name
            chan_name: chan_img
            dtype_name: dtype_img
            itype_name: itype
            resolution: res
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            output_name: raw_pull_output_name
            coord_name: coord_name
            bucket: bucket
        out:
            [raw_pull_output]
    anno_boss_pull:
        run: ../../boss_access/boss_pull.cwl
        in:
            host_name: host_name
            token: token
            coll_name: coll_name
            exp_name: exp_name
            chan_name: chan_lbl
            dtype_name: dtype_lbl
            itype_name: itype
            resolution: res
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            output_name: anno_pull_output_name
            coord_name: coord_name
            bucket: bucket
        out:
            [anno_pull_output]
    optimize:
        run: ../tools/membrane_unets_train.cwl
        in:
            use_boss: use_boss
            img_file: raw_boss_pull/raw_pull_output
            lbl_file: anno_boss_pull/anno_pull_output
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
            use_adam: use_adam
            learning_rate: learning_rate
            momentum: momentum
            decay: decay
            beta1: beta1
            beta2: beta2
            save_freq: save_freq
            do_warp: do_warp
            tile_size: tile_size
            weights_file: weights_file
            output: output
            score_out: score_out
        out: [membrane_probability,classifier_weights,scores]
        hints:
            saber: 
                score_format: "F1: {score}"
                local: True
    cell_detect:
        run: ../tools/unsup_cell_detect_3D_nos3.cwl
        in:
            input: membrane_classify/membrane_probability
            output_name: optimize_output_name
            threshold: detect_threshold
            stop: stop
            initial_template_size: initial_template_size
            dilation: detect_dilation
            max_cells: max_cells
        out: [cell_detect_results]
    metrics:
        run: ../tools/unsup_metrics_3D_nos3.cwl
        in:
            input: cell_detect/cell_detect_results
            output_name: metrics_out
            groundtruth: anno_boss_pull/anno_pull_output
        out: [metrics]
        hints:
            saber: 
                score_format: "F1: {score}"
                local: True
