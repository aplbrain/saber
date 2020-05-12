import unittest
import unittest.mock as mock
from conduit.utils.command_list import generate_command_list, generate_io_strings, sub_params
from conduit.utils.cwlparser import CwlParser
from conduit.tests.testing_utils import load_data, resolve_filename, cd, dependency_generator 
import yaml

class TestCommandlist(unittest.TestCase):
    # TODO needs to be class
    
    def setUp(self):
        wf_prefixes = [
            'si',
            'siso',
            'simo',
            'so',
            'mi',
            'miso',
            'mimo',
            'mo'

        ]

        fake_config = {
            'job-queue':{
                'jobQueueName' : ""
            }
        }
        
        self.local_wfs = {}
        self.cloud_wfs = {}
        self.tool_dict = {}
        self.dj_patcher = mock.patch("conduit.utils.cwlparser.DatajointHook")
        self.dj_patcher.start()
        for pre in wf_prefixes:
            self.local_wfs[pre] = CwlParser(resolve_filename('local_workflows', f'{pre}_workflow.cwl'),config=fake_config)
            self.cloud_wfs[pre] = CwlParser(resolve_filename('cloud_workflows', f'{pre}_workflow.cwl'),config=fake_config)
            self.tool_dict[pre] = self.local_wfs[pre].resolve_tools()
        
        self.mi_job_fn = resolve_filename("jobs", "mi.yml")
        self.si_job_fn = resolve_filename("jobs", "si.yml")
        self.mi_job = load_data(self.mi_job_fn)
        self.si_job = load_data(self.si_job_fn)
    def test_generate_command_list_SISO(self):
            # Test cases:
            # 1. Single input, single output (SISO) tool
            # 2. Multi input, multi output (MIMO) tool
            # 3. MIMO tool with local
            # 4. MIMO tool with iteration parameters
            # 5. MIMO tool with no file path
            # 6. MIMO tool with file path
        key = "siso"
        tool_yml = self.tool_dict[key]['step1']
        parsers = (self.local_wfs[key], self.cloud_wfs[key])
        for parser in parsers:
            iteration_parameters, _ = parser.resolve_args(self.si_job)
            step = parser.cwl['steps']['step1']
            if parser.local:
                command_list = generate_command_list(tool_yml, iteration_parameters, step, local=True, file_path="./test_path")
                expected_command_list = ['python3', '/app/localwrap', '--wf', 'Ref::_saber_stepname', '--use_cache', 'False', 'echo', '--int', 'Ref::input_int']
                assert(command_list==expected_command_list)
            else:
                command_list = generate_command_list(tool_yml, iteration_parameters, step, local=False, file_path=None)
                expected_command_list = ['python3', '/app/s3wrap', '--to', 'Ref::_saber_stepname', '--fr', 'Ref::_saber_home', '--use_cache', 'False', 'echo', '--int', 'Ref::input_int']
                assert(command_list==expected_command_list)

    def test_generate_command_list_MIMO(self):
        key = "mimo"
        tool_yml = self.tool_dict[key]
        parsers = (self.local_wfs[key], self.cloud_wfs[key])
        for parser in parsers:
            dep_patch = mock.patch.object(parser, 'resolve_args', return_value=dependency_generator(key))
            with dep_patch:
                iteration_parameters = parser.resolve_args(self.mi_job)
            for i in tool_yml:
                step = parser.cwl['steps'][i]
                if parser.local:
                    command_list = generate_command_list(tool_yml[i], iteration_parameters, step, local=True, file_path="./test_path")
                    assert(command_list[0:6]==['python3', '/app/localwrap', '--wf', 'Ref::_saber_stepname', '--use_cache', 'False'])
                else:
                    command_list = generate_command_list(tool_yml[i], iteration_parameters, step, local=False, file_path=None)
                    assert(command_list[0:6]==['python3', '/app/s3wrap', '--to', 'Ref::_saber_stepname', '--fr', 'Ref::_saber_home'])
                if i == "step1":
                    assert(command_list[-7:]==['echo', '--int', 'Ref::input_int', '--boolean', 'Ref::input_bool', '--float', 'Ref::input_float'])
                elif i == "step2":
                    assert(command_list[-7:]==['echo', '--boolean', 'Ref::input_bool', '--float', 'Ref::input_float', '--File', 'Ref::input_file'])
                else:
                    assert(command_list[-5:]==['cat', '--f1', 'Ref::file1', '--f2', 'Ref::file2'])
                


    def test_sub_params(self):
        # Test cases:
        # 1. Single input
        # 2. Multi input
        # 3. Edge case
        si_cl = ['python3', '/app/localwrap', '--wf', 'Ref::_saber_stepname', '--use_cache', 'False', 'echo', '--int', 'Ref::input_int']
        self.si_job["_saber_stepname"] = "si_workflow/step1"
        si_sub_params = sub_params(si_cl, self.si_job)
        assert(si_sub_params == ['python3', '/app/localwrap', '--wf', 'si_workflow/step1', '--use_cache', 'False', 'echo', '--int', 0])

        mi_cl = ['python3', '/app/localwrap', '--wf', 'Ref::_saber_stepname', '--use_cache', 'False', 
        'echo', '--boolean', 'Ref::input_bool', '--float', 'Ref::input_float', '--File', 'Ref::input_file']
        self.mi_job["_saber_stepname"] = "mi_workflow/step2"
        mi_sub_params = sub_params(mi_cl, self.mi_job)
        expected_mi_sub_parmas = ['python3', '/app/localwrap', '--wf', 'mi_workflow/step2', '--use_cache', 'False', 
        'echo', '--boolean', True, '--float', False, '--File', {'path': 'tools/mi_workflow.cwl', 'class': 'File'}]
        assert(mi_sub_params==expected_mi_sub_parmas)

    def test_generate_io_strings(self):
        # Test cases:
        # 1. Empty input
        # 2. Single input
        # 3. Multi input
        # 4. Edge case
        key = 'mimo'
        tool_yml = self.tool_dict[key]['step3']
        parser = self.local_wfs[key]
        step = parser.cwl['steps']['step3']
        wf_hash = "test_workflow/"+key
        print(tool_yml) 
        print(step)
        print(generate_io_strings(tool_yml, wf_hash, step, 0))
    