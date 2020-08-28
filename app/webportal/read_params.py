#!/usr/bin/env python3
import yaml #NOTE Should be `yaml` and not `pyyaml`

def cwl_input_params(cwl_filepath):
    # .strip() will get rid of whitespaces after filename

    """
    Parse cwl file and return a dictionary of input parameters.

    Arguments:
        cwl_filepath (string): the filepath to the .cwl file to be read

    Returns:
        cwl_inputs (dict): the dict with key : value, where
            key (string) : parameter name
            value (string) : cwl-compatible parameter datatype

    Raises:
        FileNotFoundError: if the specified `cwl_filepath` could not be located
    """

    try:
        with open(cwl_filepath.strip(), 'r') as cwl_file:
            cwl_dict = yaml.safe_load(cwl_file)
        cwl_inputs = cwl_dict['inputs']
        return cwl_inputs
    except FileNotFoundError:
        empty_dict = {}
        print('Unable to locate file or filepath: ' + cwl_filepath)
        return empty_dict
