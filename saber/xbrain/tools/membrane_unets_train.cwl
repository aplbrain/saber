#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
hints:
    DockerRequirement:
        dockerPull: aplbrain/unets
baseCommand: python 
arguments: [/src/train_unet_docker.py]
inputs:
    use_boss:
        type: int
        default: 1
        inputBinding:
            position: 1
            prefix: --use_boss
    img_file:
        type: File?
        inputBinding:      
            position: 2
            prefix: --img_file
    lbl_file:
        type: File?
        inputBinding:
            position: 3
            prefix: --lbl_file
    coord: 
        type: string?
        inputBinding:
            position: 4
            prefix: --coord
    token: 
        type: string?
        inputBinding:
            position: 5
            prefix: --token
    coll: 
        type: string?
        inputBinding:
            position: 6
            prefix: --coll
    exp: 
        type: string?
        inputBinding:
            position: 7
            prefix: --exp
    chan_labels: 
        type: string?
        inputBinding:
            position: 8
            prefix: --chan_labels
    chan_img:
        type: string?
        inputBinding:
            position: 9
            prefix: --chan_img
    dtype_img:
        type: string?
        inputBinding:
            position: 10
            prefix: --dtype_img
    dtype_lbl:
        type: string?
        inputBinding:
            position: 11
            prefix: --dtype_lbl
    res:
        type: int?
        default: 0
        inputBinding:
            position: 12
            prefix: --res
    xmin:
        type: int?
        inputBinding:
            position: 13
            prefix: --xmin
    xmax:
        type: int?
        inputBinding:
            position: 14
            prefix: --xmax
    ymin:
        type: int?
        inputBinding:
            position: 15
            prefix: --ymin
    ymax:
        type: int?
        inputBinding:
            position: 16
            prefix: --ymax
    zmin:
        type: int?
        inputBinding:
            position: 17
            prefix: --zmin
    zmax:
        type: int?
        inputBinding:
            position: 18
            prefix: --zmax
    train_pct:
        type: float?
        default: 0.5
        inputBinding:
            position: 19
            prefix: --train_pct
    n_epochs:
        type: int?
        default: 10
        inputBinding: 
            position: 20
            prefix: --n_epochs
    mb_size:
        type: int?
        default: 4
        inputBinding: 
            position: 21
            prefix: --mb_size
    n_mb_per_epoch:
        type: int?
        default: 3
        inputBinding: 
            position: 22
            prefix: --n_mb_per_epoch
    use_adam:
        type: boolean?
        default: False
        inputBinding:
            position: 23
            prefix: --use_adam
    learning_rate:
        type: float?
        default: 0.0001
        inputBinding: 
            position: 24
            prefix: --learning_rate
    momentum:
        type: float?
        default: 0.99
        inputBinding:
            position: 25
            prefix: --momentum
    decay: 
        type: float?
        default: 0.000001
        inputBinding:
            position: 26
            prefix: --decay
    beta1:
        type: float?
        default: 0.9
        inputBinding: 
            position: 27
            prefix: --beta1
    beta2:
        type: float?
        default: 0.999
        inputBinding: 
            position: 28
            prefix: --beta2
    save_freq:
        type: int?
        default: 50
        inputBinding: 
            position: 29
            prefix: --save_freq
    do_warp:
        type: boolean?
        default: False
        inputBinding: 
            position: 30
            prefix: --do_warp
    tile_size:
        type: int?
        default: 256
        inputBinding: 
            position: 31
            prefix: --tile_size   
    weights_file:
        type: File?
        inputBinding: 
            position: 32
            prefix: --weights_file
    output:
        type: string
        inputBinding:
            position: 33
            prefix: --output
    score_out:
        type: string
        inputBinding: 
            position: 34
            prefix: --score_out
outputs:
    classifier_weights:
        type: File
        outputBinding:
            glob: $(inputs.output)
    scores: 
        type: File
        outputBinding:
            glob: $(inputs.score_out)
