#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
inputs:
    use_boss: int
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

    # Unet training
    train_pct: float
    n_epochs: int
    mb_size: int
    n_mb_per_epoch: int
    use_adam: boolean
    learning_rate: float
    decay: float
    momentum: float
    beta1: float
    beta2: float
    save_freq: int
    do_warp: boolean
    tile_size: int

    #Unet Classify 
    classify_output_name: string

    threshold: float
    stop: float
    initial_template_size: int
    detect_dilation: int
#   max_cells: int
    dense_output_name: string

    optimize_output: string
    score_out: string
    raw_pull_output_name: string
    anno_pull_output_name: string
    detect_output_name: string
    metrics_out: string
outputs:
    pull_output:
        type: File
        outputSource: raw_boss_pull/pull_output
    anno_output:
        type: File
        outputSource: anno_boss_pull/pull_output
    train_output:
        type: File
        outputSource: optimize/classifier_weights
    membrane_output:
        type: File
        outputSource: classify/membrane_probability_map
    cell_detect_output:
        type: File
        outputSource: cell_detect/cell_detect_results
    metric_output:
        type: File
        outputSource: metrics/metrics
steps:
    raw_boss_pull:
        run: ../../../boss_access/boss_pull_nos3.cwl
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
    anno_boss_pull:
        run: ../../../boss_access/boss_pull_nos3.cwl
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
    optimize:
        run: ../../tools/membrane_unets_train.cwl
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
            use_adam: use_adam
            learning_rate: learning_rate
            momentum: momentum
            decay: decay
            beta1: beta1
            beta2: beta2
            save_freq: save_freq
            do_warp: do_warp
            tile_size: tile_size
            output: optimize_output
            score_out: score_out
        out: [classifier_weights, scores]
    
    classify:
        run: ../../unets/deploy_unets.cwl
        in: 
            img_file: raw_boss_pull/pull_output
            lbl_file: anno_boss_pull/pull_output
            weights_file: optimize/classifier_weights
            output: classify_output_name
        out: [membrane_probability_map]
        hints:
            saber: 
                score_format: "F1: {score}"

    cell_detect:
        run: ../../tools/unsup_cell_detect_3D_nos3.cwl
        in:
            input: classify/membrane_probability_map
            output_name: detect_output_name
            threshold: threshold
            stop: stop
            initial_template_size: initial_template_size
            dilation: detect_dilation
#           max_cells: max_cells
            dense_output_name: dense_output_name
        out: [cell_detect_results, dense_output]

    metrics:
        run: ../../tools/unsup_metrics_nos3.cwl
        in:
            input: cell_detect/cell_detect_results
            output_name: metrics_out
            ground_truth: anno_boss_pull/pull_output
            initial_template_size: initial_template_size
        out: [metrics]
        hints:
            saber: 
                score_format: "F1: {score}"