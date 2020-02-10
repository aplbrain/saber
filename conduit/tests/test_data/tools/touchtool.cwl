cwlVersion: v1.0
class: CommandLineTool
baseCommand: touch
inputs:
  file1:
    type: string
    inputBinding:
      position: 0
  file2:
    type: string
    inputBinding:
      position: 0
  file3:
    type: string
    inputBinding:
      position: 0
outputs:
  output1:
    type: File
    outputBinding:
      glob: $(inputs.file1)
  output2:
    type: File
    outputBinding:
      glob: $(inputs.file2)
  output3:
    type: File
    outputBinding:
      glob: $(inputs.file3)

