cwlVersion: v1.0
class: CommandLineTool
baseCommand: cat
inputs:
  file1:
    type: file
    inputBinding:
      position: 0
      prefix: --f1
  file2:
    type: file
    inputBinding:
      position: 0
      prefix: --f2
  file3:
    type: file
    inputBinding:
      position: 0
      prefix: --f3
stdout: output.txt
outputs:
  output:
    type: stdout
