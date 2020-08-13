#!/usr/bin/env python3

def write_input_params(input_params, yml_filepath):
    """
    Write input parameters into specified filename.

    Arguments:
        input_params (dict): the dict with key : value, where
            key (string) : parameter name
            value (string) : user-inputted parameter value
        yml_filepath (string): the filepath to the .yml file to write into,
            where default filename = "job.yml"

    Returns:
        None

    Raises:
        FileNotFoundError: if the specified `yml_filepath` could not be located
    """

    # .strip() will get rid of whitespaces after filename
    try:
        file = open(yml_filepath.strip(), 'w+')
        for k, v in input_params.items():
            line = k + ": " + v + "\n"
            file.write(line)
        file.close()
        return None
    except FileNotFoundError:
        print('Unable to locate file or filepath: ' + yml_filepath)
        return None
