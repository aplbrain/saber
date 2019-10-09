#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
inputs:
    # Shared
    _saber_bucket: string
    # Inputs for BOSS
    config: File?
    token: string?
    coll_name: string
    exp_name: string
    in_chan_name: string
    out_chan_name: string
    dtype_name: string
    out_dtype_name: string
    itype_name: string
    out_itype_name: string
    resolution: int?
    xmin: int?
    xmax: int?
    ymin: int?
    ymax: int?
    zmin: int?
    zmax: int?
    padding: int?
    onesided: int?
    pull_output_name: string
    coord_name: string
    # Inputs for steps
    
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

    map_output_name: string
    list_output_name: string
    centroid_volume_output_name: string
outputs:
    pull_output:
        type: File
        outputSource: boss_pull/pull_output
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
    boss_pull:
        run: ../../boss_access/boss_pull.cwl
        in:
            config: config
            token: token
            coll_name: coll_name
            exp_name: exp_name
            chan_name: in_chan_name
            dtype_name: dtype_name
            itype_name: itype_name
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            output_name: pull_output_name
            coord_name: coord_name
            bucket: bucket
            onesided: onesided
        out:
            [pull_output]
           
    membrane_classify:
        run: ../tools/membrane_classify.cwl
        in:
            input: boss_pull/pull_output
            output_name: membrane_classify_output_name
            classifier: classifier
            ram_amount: ram_amount
            num_threads: num_threads
            bucket: bucket
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
            # bucket: bucket
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
            bucket: bucket
        out: [vessel_segment_results]
    cell_split:
        run: ../tools/cell_split.cwl
        in:
            input: cell_detect/cell_detect_results
            map_output_name: map_output_name
            list_output_name: list_output_name
            centroid_volume_output_name: centroid_volume_output_name
        out:
            [cell_map, cell_list, centroid_volume]
    boss_push:
        run: ../../boss_access/boss_push.cwl
        in:
            token: token
            coll_name: coll_name
            exp_name: exp_name
            chan_name: out_chan_name
            dtype_name: out_dtype_name
            itype_name: out_itype_name
            resolution: resolution
            xmin: xmin
            xmax: xmax
            ymin: ymin
            ymax: ymax
            zmin: zmin
            zmax: zmax
            padding: padding
            input: cell_split/centroid_volume
            coord_name: coord_name
            bucket: bucket
            onesided: onesided
        out: []
        
