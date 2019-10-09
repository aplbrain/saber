#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
inputs:
    data: File
    cell_gt: File
    optimize_output_name: string
    detect_threshold: float?
    stop: float?
    initial_template_size: int?
    detect_dilation: int?
    max_cells: int?
    num_samp: int?
    num_comp: int?
    erode: int?
    metrics: int?

outputs:
    membrane_classify_output:
        type: File
        outputSource: membrane_classify/membrane_probability_map
    cell_detect_output:
        type: File
        outputSource: cell_detect/cell_detect_results
    metrics_output:
        type: File
        outputSource: optimize/metrics
steps:
    membrane_classify:
        run: ../tools/unsup_membrane_3D_nos3.cwl
        in:
            input: data
            output_name: optimize_output_name
            num_samp: num_samp
            num_comp: num_comp
            erode: erode
        out: [membrane_probability_map]
    cell_detect:
        run: ../tools/unsup_cell_detect_3D_nos3.cwl
        in:
            input: membrane_classify/membrane_probability_map
            output_name: optimize_output_name
            threshold: detect_threshold
            stop: stop
            initial_template_size: initial_template_size
            dilation: detect_dilation
            max_cells: max_cells
        out: [cell_detect_results]
    metrics:
        run: ../tools/unsup_metrics_3D_nos3.cwl
        in:
            input: cell_detect/cell_detect_results
            output_name: optimize_output_name
            groundtruth: cell_gt
        out: [metrics]
