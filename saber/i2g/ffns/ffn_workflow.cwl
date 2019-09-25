#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
inputs:
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
        run: ../ffns_seg.cwl
        in:
            input: raw_boss_pull/raw_pull_output
            seg_input: anno_boss_pull/anno_pull_output
            height:
    type: int?
    inputBinding:
      position: 2
      prefix: --height
  min_thres:
    type: float?
    inputBinding:
      position: 3
      prefix: --min_thres
  max_thres:
    type: float?
    inputBinding:
      position: 4
      prefix: --max_thres
  thres_step:
    type: float?
    inputBinding:
      position: 5
      prefix: --thres_step
  lom_radius:
    type: int?
    inputBinding:
      position: 6
      prefix: --lom_radius
  min_size:
    type: int?
    inputBinding:
      position: 7
      prefix: --min_size
  margin:
    type: int?
    inputBinding:
      position: 8
      prefix: --margin
  model_name:
    type: string
    inputBinding:
      position: 9
      prefix: --name
  depth:
    type: int?
    inputBinding:
      position: 10
      prefix: --depth  
  fov:
    type: int?
    inputBinding:
      position: 11
      prefix: --fov  
  deltas:
    type: int?
    inputBinding:
      position: 12
      prefix: --deltas  
  image_mean:
    type: int?
    inputBinding:
      position: 13
      prefix: --image_mean  
  image_std:
    type: int?
    inputBinding:
      position: 14
      prefix: --image_std  
  max_steps:
    type: int?
    inputBinding:
      position: 15
      prefix: --max_steps  
  output:
    type: string
    inputBinding:
      position: 16
       prefix: --output
        out: [classifier_weights]
        hints:
            saber: 
                score_format: "F1: {score}"
                local: True
