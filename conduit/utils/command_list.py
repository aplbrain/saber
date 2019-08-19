# Copyright 2019 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import parse
def generate_command_list(tool_yml,iteration_parameters, step, local=False, file_path = ''):
    '''
    Generates an AWS Batch command list from a tool YML

    Parameters:
    -----------
    tool_yml : dict
        Tool YML from file
    iteration_parameters: dict
        Job parameters for a particular step
    step : dict
        Step from CWL. Used to make sure that the input is enabled in the
        workflow
    file_path = path to store intermediate files (local or s3)
    
    Returns:
    --------
    list of str:
        Command list, where each string is a seperate string. Could be used as 
        input to a docker RUN cmd
    '''
    # Command list generation
    # Prepend to copy data from S3 (if any of the tool inputs are Files)
    if local:
        command_list = ['python3', '/app/localwrap', '--wf', 'Ref::_saber_home']
        # Only care about file inputs
        seperator ="," 
        input_files = iteration_parameters.get('_saber_input', [])
        if len(input_files) > 0:
            input_files = input_files.split(',')
            command_list.append('--input')
            command_list.append(seperator.join(input_files))

        # Append the data outputs to S3
        output_files = iteration_parameters.get('_saber_output', [])
        if len(output_files) > 0:
            output_files = output_files.split(',')
            command_list.append('--output')
            command_list.append(seperator.join(output_files))
    else:
        if file_path != '':
            command_list = ['python3', '/app/s3wrap', '--to', file_path, '--fr', 'Ref::_saber_home']
        else:
            command_list = ['python3', '/app/s3wrap', '--to', 'Ref::_saber_stepname', '--fr', 'Ref::_saber_home']
        # Only care about file inputs
        input_files = iteration_parameters.get('_saber_input', [])
        if len(input_files) > 0:
                command_list.append('--download')
                command_list.append('Ref::_saber_input')

        # Append the data outputs to S3
        output_files = iteration_parameters.get('_saber_output', [])
        if len(output_files) > 0:
                command_list.append('--upload')
                command_list.append('Ref::_saber_output')
    # Not really necessary to split but I dont see a use case where one would want a space in their command...
    command_list.extend(tool_yml['baseCommand'].split())
    command_list.extend([arg for arg in tool_yml['arguments']])
    
    # Create sorted input list to respect CWL input binding
    sorted_inps = [(inpn, inp) for inpn, inp in tool_yml['inputs'].items()]
    sorted_inps.sort(key=lambda x: x[1]['inputBinding']['position'])
    # Add to the command_list
    for inpn,inp in sorted_inps:
        if inpn in step['in']:
            command_list.append(inp['inputBinding']['prefix'])
            command_list.append('Ref::{}'.format(inpn))
    return command_list

def sub_params(command_list,params):
    '''
    Substitutes parameters from their references for use in local execution

    Parameters:
    -----------
    command_list : list of str
        Generated from above function
    params: dict
        Dictionary of form {parameter_name : parameter value}
    '''

    for i,command in enumerate(command_list):
        parsed_command = parse.parse('Ref::{p}',command )
        if parsed_command is not None:
            command_list[i] = params[parsed_command['p']]
    return command_list
def generate_io_strings(tool_yml, wf_hash, step_params,j):
        '''
        Generates IO strings for the S3 wrapper

        Params:
        ------
        tool_yml : dict
            Tool CWL from file
        wf_hash: str
            The unique ID of the workflow, based on job name
        step_params: dict
            The parameters of the step
        j: int
            The iteration (for parameterization)
        '''

        inp_string = []
        out_string = []
        if len(tool_yml['inputs']) > 0:
            input_files = dict([(tn,t) for tn,t in tool_yml['inputs'].items() if t['type'] == 'File' or t['type'] == 'File?'])
            for i in input_files:
                if i in step_params.keys():
                    s = step_params[i].split('/')
                    if len(s) > 1:
                        # Form input/file
                        # TODO make naming more consistent
                        s[0] = s[0] #dumb fix
                        s[0] += '.{}'.format(j)
                    inp_string.append('/'.join(s))
        if len(tool_yml['outputs']) > 0:
            output_files = dict([(tn,t) for tn,t in tool_yml['outputs'].items() if t['type'] == 'File'])
            out_string = []
            for t in output_files.values():
                glob = t['outputBinding']['glob']
                # Ad hoc glob resolution
                glob_parse = parse.parse('$({}.{})',glob)
                if not glob_parse:
                    # Just a filename, not a reference
                    out_string.append(glob)
                else:
                    out_string.append(step_params[glob_parse[1]])
            
        return (','.join(inp_string), ','.join(out_string))
