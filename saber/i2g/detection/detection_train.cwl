cwlVersion: v1.0
class: CommandLineTool
hints:
    DockerRequirement:
        dockerPull: aplbrain/i2gdetect_gpu
baseCommand: python
arguments: ["train_pipeline.py"]
inputs:
  useboss:
    type: int
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

  coord_name:
    type: string
    inputBinding:
      position: 4
      prefix: --coord  

  token:
    type: string?
    inputBinding:
      position: 5
      prefix: --token

  coll_name:
    type: string?
    inputBinding:
      position: 6
      prefix: --coll
    
  exp_name:
    type: string?
    inputBinding:
      position: 7
      prefix: --exp

  chan_name:
    type: string?
    inputBinding:
      position: 8
      prefix: --chan
  
  dtype_img:
    type: string?
    inputBinding:
      position: 9
      prefix: --dtype_img

  dtype_lbl:
    type: string?
    inputBinding:
      position: 9
      prefix: --dtype_lbl
  
  resolution:
    type: int?
    inputBinding:
      prefix: --res
      position: 10

  xmin:
    type: int?
    inputBinding:
      prefix: --xmin
      position: 11

  xmax:
    type: int?
    inputBinding:
      prefix: --xmax
      position: 13

  ymin:
    type: int?
    inputBinding:
      prefix: --ymin
      position: 14
  
  ymax:
    type: int?
    inputBinding:
      prefix: --ymax
      position: 15
  
  zmin:
    type: int?
    inputBinding:
      prefix: --zmin
      position: 16
    
  zmax:
    type: int?
    inputBinding:
      prefix: --zmax
      position: 17

  train_pct:
    type: float?
    inputBinding:
      prefix: --train_pct
      position: 18

  n_epochs:
    type: int?
    inputBinding:
      prefix: --n_epochs
      position: 19
  
  mb_size:
    type: int?
    inputBinding:
      prefix: --mb_size
      position: 20
  
  n_mb_per_epoch:
    type: int?
    inputBinding:
      prefix: --n_mb_per_epoch
      position: 21
  
  learning_rate:
    type: float?
    inputBinding:
      prefix: --learning_rate
      position: 22

  beta1:
    type: float?
    inputBinding:
      prefix: --beta1
      position: 23

  beta2:
    type: float?
    inputBinding:
      prefix: --beta2
      position: 24

  save_freq:
    type: int?
    inputBinding:
      prefix: --save_freq
      position: 25

  do_warp:
    type: boolean?
    inputBinding:
      prefix: --do_warp
      position: 26

  tile_size:
    type: int?
    inputBinding:
      prefix: --tile_size
      position: 27

  weights_file:
    type: File?
    inputBinding:
      prefix: --weights_file
      position: 28

outputs:
  detection_train_out:
    type: File
    outputBinding:
      glob: $(inputs.output)
