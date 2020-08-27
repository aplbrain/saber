#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
inputs:
    data: File
    classifier: File
    membrane_classify_output_name: string
    cell_detect_output_name: string
    vessel_segment_output_name: string
    ram_amount: int?
    num_threads: int?
    detect_threshold: float?
    stop: float?
    initial_template_size: int?
    detect_dilation: int?
    max_cells: int?
    segment_threshold: float?
    segment_dilation: int?
    minimum: int?
outputs:
    membrane_classify_output:
        type: File
        outputSource: membrane_classify/membrane_probability_map
    cell_detect_output:
        type: File
        outputSource: cell_detect/cell_detect_results
    vessel_segment_output:
        type: File
        outputSource: vessel_segment/vessel_segment_results

steps:
    membrane_classify:
        run: ../tools/membrane_classify.cwl
        in:
            input: data
            output_name: membrane_classify_output_name
            classifier: classifier
            ram_amount: ram_amount
            num_threads: num_threads
        out: [membrane_probability_map]
    cell_detect:
        run: ../tools/cell_detect.cwl
        in:
            input: membrane_classify/membrane_probability_map
            output_name: cell_detect_output_name
            classifier: classifier
            threshold: detect_threshold
            stop: stop
            initial_template_size: initial_template_size
            dilation: detect_dilation
            max_cells: max_cells
        out: [cell_detect_results]
    vessel_segment:
        run: ../tools/vessel_segment.cwl
        in:
            input: membrane_classify/membrane_probability_map
            output_name: vessel_segment_output_name
            classifier: classifier
            threshold: segment_threshold
            dilation: segment_dilation
            minimum: minimum
        out: [vessel_segment_results]
