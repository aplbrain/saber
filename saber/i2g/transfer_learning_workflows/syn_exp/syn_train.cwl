#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
doc: local
inputs:
    use_boss: int
    img_file: File?
    lbl_file: File?
    train_pct: float?
    n_epochs: int?
    mb_size: int?
    n_mb_per_epoch: int?
    learning_rate: float?
    beta1: float?
    beta2: float?
    use_adam: boolean?
    save_freq: int?
    do_warp: boolean?
    tile_size: int?
    output: string
    score_out: string
outputs:
    train_output:
        type: File
        outputSource: optimize/classifier_weights
steps:
    optimize:
        run: ../../../xbrain/tools/membrane_unets_train.cwl
        in:
            use_boss: use_boss
            img_file: img_file
            lbl_file: lbl_file
            train_pct: train_pct
            n_epochs: n_epochs
            mb_size: mb_size
            n_mb_per_epoch: n_mb_per_epoch
            learning_rate: learning_rate
            beta1: beta1
            beta2: beta2
            use_adam: use_adam
            save_freq: save_freq
            do_warp: do_warp
            tile_size: tile_size
            output: output
            score_out: score_out
        out: [classifier_weights,scores]
        hints:
            saber: 
                score_format: "F1: {score}\n" 
                local: True
                file_path: /home/ubuntu/saber/volumes/data/local
