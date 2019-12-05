cwlVersion: v1.0
class: CommandLineTool
hints:
    DockerRequirement:
        dockerPull: aplbrain/unets
baseCommand: python
arguments: ["/src/deploy_unet_docker.py"]
inputs:
  img_file:
    type: File
    inputBinding:
      position: 1
      prefix: --img_file
  lbl_file:
    type: File?
    inputBinding:
      position: 2
      prefix: --lbl_file
  weights_file:
    type: File
    inputBinding:
      prefix: --weights_file
      position: 3
  tile_size:
    type: int?
    inputBinding:
      prefix: --tile_size
      position: 4
  output:
    type: string
    inputBinding:
      prefix: --output
      position: 5

outputs:
  membrane_probability_map:
    type: File
    outputBinding:
      glob: $(inputs.output)