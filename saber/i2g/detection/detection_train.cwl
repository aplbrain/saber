cwlVersion: v1.0
class: CommandLineTool
hints:
    DockerRequirement:
        dockerPull: aplbrain/i2gdetect_gpu
baseCommand: python2
arguments: ["train_pipeline.py"]
inputs:
  use_boss:
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

  chan_img:
    type: string?
    inputBinding:
      position: 8
      prefix: --chan_img
  
  chan_labels:
    type: string?
    inputBinding:
      position: 9
      prefix: --chan_labels
  
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
  
  resolution:
    type: int?
    inputBinding:
      prefix: --res
      position: 12

  xmin:
    type: int?
    inputBinding:
      prefix: --xmin
      position: 13

  xmax:
    type: int?
    inputBinding:
      prefix: --xmax
      position: 14

  ymin:
    type: int?
    inputBinding:
      prefix: --ymin
      position: 15
  
  ymax:
    type: int?
    inputBinding:
      prefix: --ymax
      position: 16
  
  zmin:
    type: int?
    inputBinding:
      prefix: --zmin
      position: 17
    
  zmax:
    type: int?
    inputBinding:
      prefix: --zmax
      position: 18

  train_pct:
    type: float?
    inputBinding:
      prefix: --train_pct
      position: 19

  n_epochs:
    type: int?
    inputBinding:
      prefix: --n_epochs
      position: 20
  
  mb_size:
    type: int?
    inputBinding:
      prefix: --mb_size
      position: 21
  
  n_mb_per_epoch:
    type: int?
    inputBinding:
      prefix: --n_mb_per_epoch
      position: 22
  
  learning_rate:
    type: float?
    inputBinding:
      prefix: --learning_rate
      position: 23

  beta1:
    type: float?
    inputBinding:
      prefix: --beta1
      position: 24

  beta2:
    type: float?
    inputBinding:
      prefix: --beta2
      position: 25

  save_freq:
    type: int?
    inputBinding:
      prefix: --save_freq
      position: 26

  do_warp:
    type: boolean?
    inputBinding:
      prefix: --do_warp
      position: 27

  tile_size:
    type: int?
    inputBinding:
      prefix: --tile_size
      position: 28

  weights_file:
    type: File?
    inputBinding:
      prefix: --weights_file
      position: 29
  
  output:
    type: string
    inputBinding:
      prefix: --output
      position: 30

outputs:
  detection_train_out:
    type: File
    outputBinding:
      glob: $(inputs.output)
