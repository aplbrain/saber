#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
inputs:
    data: File
    classifier: File?
    cell_gt: File
    optimize_output_name: string
    ram_amount: int?
    num_threads: int?
    detect_threshold: float?
    stop: float?
    initial_template_size: int?
    detect_dilation: int?
    max_cells: int?
    
outputs:
    metrics_output:
        type: File
        outputSource: optimize/metrics
steps:
    optimize:
        run: ../tools/optimize_supervised.cwl
        in:
            input: data
            output_name: optimize_output_name
            classifier: classifier
            cell_gt_input: cell_gt
            ram_amount: ram_amount
            num_threads: num_threads
            threshold: detect_threshold
            stop: stop
            initial_template_size: initial_template_size
            dilation: detect_dilation
            max_cells: max_cells
        out: [metrics]
