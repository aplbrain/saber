import unittest
import unittest.mock as mock
import conduit.utils.cwlparser as cwlparser
from airflow import DAG
from conduit.tests.testing_utils import load_data, resolve_filename, cd
import nose
import os

class TestCwlParser(unittest.TestCase):
    
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
        self.dj_patcher = mock.patch("conduit.utils.cwlparser.DatajointHook")
        self.dj_patcher.start()
        for pre in wf_prefixes:
            self.local_wfs[pre] = cwlparser.CwlParser(resolve_filename('local_workflows', f'{pre}_workflow.cwl'),config=fake_config)
            self.cloud_wfs[pre] = cwlparser.CwlParser(resolve_filename('cloud_workflows', f'{pre}_workflow.cwl'),config=fake_config)
        
        self.mi_job_fn = resolve_filename("jobs", "mi.yml")
        self.si_job_fn = resolve_filename("jobs", "si.yml")
        self.mi_job = load_data(self.mi_job_fn)
        self.si_job = load_data(self.si_job_fn)
    def tearDown(self):
        self.dj_patcher.stop()
    def test_resolve_tools(self):
        # Test cases:

        # 1. Single tool
        self.assertEqual(list(self.local_wfs['siso'].steps.keys()), ['step1'])
        self.assertEqual(list(self.local_wfs['si'].steps.keys()), ['step1'])
        self.assertEqual(list(self.local_wfs['so'].steps.keys()), ['step1'])
        # 2. Multiple tools
        self.assertEqual(list(self.local_wfs['simo'].steps.keys()), ['step1', 'step2', 'step3'])
        self.assertEqual(list(self.local_wfs['mi'].steps.keys()), ['step1', 'step2', 'step3'])
        self.assertEqual(list(self.local_wfs['miso'].steps.keys()), ['step1', 'step2', 'step3'])
        self.assertEqual(list(self.local_wfs['mimo'].steps.keys()), ['step1', 'step2', 'step3'])
        self.assertEqual(list(self.local_wfs['mo'].steps.keys()), ['step1', 'step2', 'step3'])

        # 3. Single tool (cloud)
        self.assertEqual(list(self.cloud_wfs['siso'].steps.keys()), ['step1'])
        self.assertEqual(list(self.cloud_wfs['si'].steps.keys()), ['step1'])
        self.assertEqual(list(self.cloud_wfs['so'].steps.keys()), ['step1'])
        # 4. Multiple tools (cloud)
        self.assertEqual(list(self.cloud_wfs['simo'].steps.keys()), ['step1', 'step2', 'step3'])
        self.assertEqual(list(self.cloud_wfs['mi'].steps.keys()), ['step1', 'step2', 'step3'])
        self.assertEqual(list(self.cloud_wfs['miso'].steps.keys()), ['step1', 'step2', 'step3'])
        self.assertEqual(list(self.cloud_wfs['mimo'].steps.keys()), ['step1', 'step2', 'step3'])
        self.assertEqual(list(self.cloud_wfs['mo'].steps.keys()), ['step1', 'step2', 'step3'])

        

    def test_generate_volume_list(self):
        # Test cases:
        # 1. Test no outputs
        # 2. Single output
        # 3. Multiple output
        for wf in self.local_wfs.values():
            for steps in wf.steps:
                self.assertEqual(wf.generate_volume_list(wf.steps['step1'],'./test_path'),['./test_path:/volumes/data/local'])
                # 4. Empty local path
                self.assertEqual(wf.generate_volume_list(wf.steps['step1'],''),[])

        # 1. Test no outputs (cloud)
        # 2. Single output (cloud)
        # 3. Multiple output (cloud)
        for wf in self.cloud_wfs.values():
            for steps in wf.steps:
                self.assertEqual(wf.generate_volume_list(wf.steps['step1'],'./test_path'),['./test_path:/volumes/data/local'])
                # 4. Empty local path
                self.assertEqual(wf.generate_volume_list(wf.steps['step1'],''),[])


        

    def test_create_job_definitions(self):
        # Test cases:
        # 1. Single tool
        # 2. Multiple tools
        # 3. Workflow CWL not in current directory
        def fake_tag(stepname, tool, local):
            return f"{stepname}_{local}"
        patcher1 = mock.patch('conduit.utils.cwlparser.create_job_definition', side_effect=lambda x: {'jobDefinitionArn': 'test'})
        patcher2 = mock.patch('conduit.utils.cwlparser.make_tag', side_effect=fake_tag)
        
        with patcher1, patcher2:
            for wf in self.local_wfs.values():
                wf.create_job_definitions()
                for stepname, step in wf.steps.items():
                    self.assertEquals(wf.tags[stepname], f"{stepname}_True")

            for wf in self.cloud_wfs.values():
                wf.create_job_definitions()
                for stepname, step in wf.steps.items():
                    self.assertEquals(wf.tags[stepname], f"{stepname}_False")
        
        
    def test_build_docker_images(self):
        # Tested in test_job_definitions.py
        pass
    def test_create_subdag(self):
        # Test cases:
        # 1. Single tool

        # 2. Multiple tools
        # 3. No iterations
        # 4. Multiple iterations
        # 5. Empty update dict

        pass

    def test_generate_dag(self):
        # Test cases:
        # 1. Single tool
        # 2. Multiple tools
        # 3. No iterations
        # 4. Multiple iterations
        # 5. Empty update dict
        # 6. Subdag = False
     
            
        for wf_name, wf in list(self.local_wfs.items()) + list(self.cloud_wfs.items()):
            patch1 = mock.patch.object(wf, 'create_subdag', spec=True, return_value=DAG(f'{wf_name}_workflow_jobs.0') )
            patch2 = mock.patch.object(wf, 'resolve_args', lambda x: ({}, []))

            
            subdag_config = {
                'saber' : {
                    'use_subdag' : False
                }
            }


            
            with patch1 as p1,patch2 as p2:
                wf_id = 'jobs'
                if "mi" in wf_name:
                    job = self.mi_job
                    job_fn = self.mi_job_fn
                    
                elif "si" in wf_name:
                    job = self.si_job
                    job_fn = self.si_job_fn
                else:
                    continue
                    # wf.generate_dag(job=resolve_filename("jobs", "empty.yml"))
                dag = wf.generate_dag(job=job_fn)
                param_db_update_dict = {}
                for param in wf.cwl['inputs']:
                    if type(job[param]) != dict:
                        param_db_update_dict[param] = job[param]
                    elif 'path' in job[param]:
                        param_db_update_dict[param] = job[param]['path']
                with mock.patch.dict(wf.cwl, subdag_config):
                    no_subdag_dag = wf.generate_dag(job=job_fn)
                    p1.assert_called_with({}, 0, param_db_update_dict, {}, job,  wf_id, [], dag=None)
                


                self.assertIsInstance(dag, DAG)
                self.assertEqual(len(dag.task_ids), 1)
                self.assertIsInstance(dag.subdags[0], DAG)
            
        pass
    def test_resolve_args(self):
        # Test cases:
        # 1. Single tool
        # 2. Multiple tools
        # 3. No iterations
        # 4. Multiple iterations
        # 5. Empty update dict
        
        for wf_name, wf in self.local_wfs.items():
            patch1 = mock.patch.object(wf, 'resolve_dependencies', return_value=self.dependency_generator(wf_name))
            if "mi" in wf_name:
                job = self.mi_job
                job_fn = self.mi_job_fn
                    
            elif "si" in wf_name:
                job = self.si_job
                job_fn = self.si_job_fn
            else:
                continue
                # wf.generate_dag(job=resolve_filename("jobs", "empty.yml"))
            with patch1:
                step_params, deps = wf.resolve_args(job)
            print(step_params, deps)
        pass
    def dependency_generator(self, wf_name):
            if 'mi' in wf_name or 'mo' in wf_name:
                return {
                    'step1/output' : 'output.txt',
                    'step2/output' : 'output.txt',
                    'step3/output' : 'output.txt'
                }
            else:
                return {}    
    def test_resolve_glob(self):
        # Test cases:
        # 1. Undefined tool
        # 2. Non-parseable glob
        # 3. Parseable but non-input glob
        # Just test resolve dependencies
        for wf_name, wf in self.local_wfs.items():
            self.assertDictEqual(wf.resolve_dependencies(), self.dependency_generator(wf_name))

        pass

if __name__ == "__main__":
    nose.main()
