cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  input_int:
    type: int?
    inputBinding:
      position: 0
      prefix: --int
  input_bool:
    type: boolean?
    inputBinding:
      position: 0
      prefix: --boolean
  input_float:
    type: float?
    inputBinding:
      position: 0
      prefix: --float
  input_double:
    type: double?
    inputBinding:
      position: 0
      prefix: --double
  input_file:
    type: File?
    inputBinding:
      position: 0
      prefix: --File
  input_string:
    type: string?
    inputBinding:
      position: 0
      prefix: --string
stdout: output.txt
outputs:
  output:
    type: stdout
