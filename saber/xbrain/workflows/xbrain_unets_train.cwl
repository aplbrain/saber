#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
inputs:
    use_boss: int
    img_file: File?
    lbl_file: File?
    coord: string?
    token: string?
    coll: string?
    exp: string?
    chan_labels: string?
    chan_img: string?
    dtype_img: string?
    dtype_lbl: string?
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
    learning_rate: float?
    beta1: float?
    beta2: float?
    save_freq: int?
    do_warp: boolean?
    tile_size: int?
    weights_file: File?
    output: string
    score_out: string
outputs:
    train_output:
        type: File
        outputSource: optimize/classifier_weights
steps:
    optimize:
        run: ../tools/membrane_unets_train.cwl
        in:
            use_boss: use_boss
            img_file: img_file
            lbl_file: lbl_file
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
            beta1: beta1
            beta2: beta2
            save_freq: save_freq
            do_warp: do_warp
            tile_size: tile_size
            weights_file: weights_file
            output: output
            score_out: score_out
        out: [classifier_weights,scores]
        hints:
            saber: 
                score_format: "F1: {score}"
                local: True
