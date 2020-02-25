#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
doc: local
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
    
    test_xmin: int
    test_xmax: int
    test_ymin: int
    test_ymax: int
    test_zmin: int
    test_zmax: int

    train_xmin: int
    train_xmax: int
    train_ymin: int
    train_ymax: int
    train_zmin: int
    train_zmax: int

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

    # Threshold 
    threshold: string

    # Blob Detect
    min: string
    max: string

    # metrics
    initial_template_size: int 

    optimize_output: string
    score_out: string
    raw_pull_output_name: string
    anno_pull_output_name: string
    classify_output_name: string
    threshold_output_name: string
    blob_detect_output_name: string
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
    threshold_output:
        type: File
        outputSource: threshold/threshold_out
    blob_detect_output:
        type: File
        outputSource: blob_detect/blob_detect_out
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
            xmin: test_xmin
            xmax: test_xmax
            ymin: test_ymin
            ymax: test_ymax
            zmin: test_zmin
            zmax: test_zmax
            itype_name: itype_name
            padding: padding
            output_name: raw_pull_output_name
            coord_name: coord
        out:
            [pull_output]
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/outputs
                use_cache: True
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
            xmin: test_xmin
            xmax: test_xmax
            ymin: test_ymin
            ymax: test_ymax
            zmin: test_zmin
            zmax: test_zmax
            itype_name: itype_name
            padding: padding
            output_name: anno_pull_output_name
            coord_name: coord
        out:
            [pull_output]
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/outputs
                use_cache: True
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
            xmin: train_xmin
            xmax: train_xmax
            ymin: train_ymin
            ymax: train_ymax
            zmin: train_zmin
            zmax: train_zmax
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
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/outputs
                score_format: "F1: {score}"
                use_cache: True
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
                local: True
                file_path: /home/ubuntu/saber/outputs
                score_format: "F1: {score}"
    threshold:
        run: ../../../postprocessing/threshold/threshold.cwl
        in:
            input: classify/membrane_probability_map
            groundtruth: anno_boss_pull/pull_output
            threshold: threshold
            outfile: threshold_output_name
        out:
            [threshold_out]
        hints: 
            saber:
                local: True
                file_path: /home/ubuntu/saber/outputs
                score_format: "F1: {score}"

    blob_detect:
        run: ../../../postprocessing/blob_detect/blob_detect.cwl
        in:
            input: threshold/threshold_out
            min: min
            max: max
            outfile: blob_detect_output_name
        out:
            [blob_detect_out]
        hints: 
            saber:
                local: True
                file_path: /home/ubuntu/saber/outputs

    metrics:
        run: ../../tools/unsup_metrics_nos3.cwl
        in:
            input: blob_detect/blob_detect_out
            output_name: metrics_out
            ground_truth: anno_boss_pull/pull_output
            initial_template_size: initial_template_size
        out: [metrics]
        hints:
            saber:
                local: True
                file_path: /home/ubuntu/saber/outputs 
                score_format: "F1: {score}"