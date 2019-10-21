#!/usr/bin/env python
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

import os
import yaml 

from datetime import datetime, timedelta

import json
import pickle
import logging
import time
import hashlib
import boto3
import re
import pathlib
import datajoint

from airflow import DAG
from airflow.operators.subdag_operator import SubDagOperator
from utils.datajoint_hook import Workflow, schema, create_dj_schema, JobMetadata, safe_toggle
from datajoint.errors import DuplicateError, DataJointError
import cwltool.main as cwltool
import parse

from utils.parameterization import parameterize
from utils.job_definitions import create_job_definition, generate_job_definition, make_tag, create_and_push_docker_image
from utils.command_list import *
from utils.awsbatch_operator import AWSBatchOperator
from utils.saber_docker_operator import SaberDockerOperator

log = logging.getLogger(__name__)
class CwlParser:
    def __init__(self, cwl, config, constant=False):
        '''
        Initializes the CWL parser

        parameters:
        ------
        cwl: str
            Filename of cwl file
        queue: str
            AWSbatch queue name
        constant: bool
            [Deprecated]
        '''

        self.default_args = {
            "depends_on_past": False,
            "start_date": datetime(2018, 2, 23),
            "max_retries": 300,
            
        }

        filename_prefix = cwl.split('.cwl')[0]
        self.workflow_name = os.path.split(filename_prefix)[-1]
        # For resolving paths relative to files
        self.cwl_fp = os.path.abspath(os.path.dirname(cwl))
        # Load cwl
        with open(cwl) as fp:
            self.cwl = yaml.load(fp)
        
        self.constant = constant
        self.steps = self.resolve_tools()
        self.job_def_arns = {}
        self.tags = {}
        self.config = config
        self.queue = self.config['job-queue']['jobQueueName']
        # Create AWS job defs and push images
        self.workflow_db = Workflow()
        self.job_param_db = schema(create_dj_schema(self.cwl['inputs'], self.workflow_name))()
        self.parameterization = [{}] 
        self.opti_iter = 0 
        try:
            if self.cwl['doc'] == 'local':
                self.local = True
            else:
                "Doc specified but not running locally."
        except KeyError:
            self.local = False

    def generate_volume_list(self, tool_yml, local_path):
        """
        input_files = []
        if len([tn for tn,t in tool_yml['inputs'].items() if t['type'] == 'File']) > 0:
            f = iteration_parameters['input']
            fs = f.split('/')
            volumes.append(':'.join([fs,fs]))
        """
        volumes = []
        if len(tool_yml['outputs']) > 0:
            volumes.append(local_path+':/volumes/data/local')
        return volumes
    
    def create_job_definitions(self):
        for stepname, tool in self.steps.items():
            log.info('Generating job definition for step {}'.format(stepname))
            tag = make_tag(stepname, tool, self.local)
            self.tags[stepname] = tag
            if self.local:
                print("WORKING LOCALLY- no job definitions generated")
            else:
                job_def = generate_job_definition(stepname, tool, tag)
                self.job_def_arns[stepname] = create_job_definition(job_def)['jobDefinitionArn']

    def build_docker_images(self):
        done_tags = []
        for stepname, tool in self.steps.items():
            tag = make_tag(stepname, tool, self.local)
            if tag not in done_tags:
                create_and_push_docker_image(tool, tag, self.local)
                done_tags.append(tag)

    def resolve_tools(self):
        '''
        Resolves the tools into yaml files from the cwl file
        '''
        tool_yamls = {}
        toollist = [(step_name, os.path.normpath(os.path.join(self.cwl_fp,step['run']))) for step_name, step in self.cwl['steps'].items()]
        for tool_name, tool in toollist:
            tool_yamls[tool_name] = {}
            with open(tool) as fp:
                tool_yaml = yaml.load(fp)
            tool_yamls[tool_name] = tool_yaml
        return tool_yamls

    def create_subdag(self, iteration, i, param_db_update_dict, job_params, job, wf_id, deps, dag=None):
        subdag_id = '{}_{}.{}'.format(self.workflow_name, wf_id, i) 
        parent_dag_id = '{}_{}'.format(self.workflow_name, wf_id)
        if dag == None:
            subdag = DAG(
                default_args = self.default_args,
                dag_id = subdag_id,
                schedule_interval = None
            )
        else: 
            subdag = dag
        subdag_steps = {}            
        for stepname, tool in self.steps.items():
            stepname_c = '{}.{}'.format(stepname,i)
            
            iteration_parameters = job_params[stepname].copy()
            if stepname in iteration:
                for key,value in iteration[stepname].items():
                    param_db_update_dict[self.cwl['steps'][stepname]['in'][key]] = value
                iteration_parameters.update(iteration[stepname])
            (in_string, out_string) = generate_io_strings(tool, wf_id, iteration_parameters,i)
            if self.local:
                iteration_parameters['_saber_home'] = wf_id
                iteration_parameters['_saber_stepname'] = '{}/{}'.format(wf_id,stepname_c)
            else: 
                iteration_parameters['_saber_home'] = '{}/{}'.format(job['_saber_bucket'], wf_id)
                iteration_parameters['_saber_stepname'] = '{}:{}/{}'.format(job['_saber_bucket'], wf_id,stepname_c)
            if in_string:
                iteration_parameters['_saber_input'] = in_string
            if out_string:
                iteration_parameters['_saber_output'] = out_string
            try:
                score_format = self.cwl['steps'][stepname]['hints']['saber']['score_format']
            except KeyError:
                score_format = ''
            try:
                is_local = self.cwl['steps'][stepname]['hints']['saber']['local']
            except KeyError:
                is_local = False
            try:
                step_job_queue = self.cwl['steps'][stepname]['hints']['saber']['queue']
            except KeyError:
                step_job_queue = self.queue
            try:
                file_path = self.cwl['steps'][stepname]['hints']['saber']['file_path']
                if not self.local:
                    file_path = '{}:{}'.format(job['_saber_bucket'], os.path.join(file_path, stepname_c))
            except KeyError:
                file_path = '' 
            
            log.debug('Score_format: {}'.format(score_format))
            command_list = generate_command_list(tool, iteration_parameters, self.cwl['steps'][stepname], self.local, file_path)
            if is_local:
                if not self.local:
                    creds = boto3.session.Session().get_credentials()
                    env_dict = {
                        'AWS_ACCESS_KEY_ID' : creds.access_key,
                        'AWS_SECRET_ACCESS_KEY' : creds.secret_key
                    }
                    t = SaberDockerOperator(
                        task_id=stepname_c,
                        workflow_id=parent_dag_id,
                        score_format=score_format,
                        image=self.tags[stepname],
                        environment=env_dict,
                        command=' '.join(sub_params(command_list, iteration_parameters)),
                        dag=subdag,
                        pool='Local'
                        )
                if self.local:
                    volumes = self.generate_volume_list(tool, file_path)
                    t = SaberDockerOperator(
                        task_id=stepname_c,
                        workflow_id=parent_dag_id,
                        score_format=score_format,
                        image=self.tags[stepname],
                        command=' '.join(sub_params(command_list, iteration_parameters)),
                        dag=subdag,
                        pool='Local',
                        volumes=volumes
                        )
            else:
                t = AWSBatchOperator(
                    task_id=stepname_c,
                    job_name=re.sub('[^A-Za-z0-9-_]+', "", "{}-{}".format(self.workflow_name,stepname_c)),
                    job_definition=self.job_def_arns[stepname],
                    overrides={
                        'command':command_list
                    },
                    job_parameters=iteration_parameters,
                    dag=subdag,
                    queue=step_job_queue,
                    workflow_id=parent_dag_id,
                    score_format=score_format
                    
                )
            subdag_steps[stepname] = t
        unique_keys = {
            'workflow_id' : parent_dag_id,
            'iteration' : i,
        }
        param_db_update_dict.update(unique_keys)
        try:
            self.job_param_db.insert1(param_db_update_dict)
        except DuplicateError:
            log.warning('Duplicate entry found for param db, updating')
            (self.job_param_db & unique_keys).delete()
            self.job_param_db.insert1(param_db_update_dict)
        for dep in deps:
            subdag_steps[dep[0]].set_upstream(subdag_steps[dep[1]])
        return subdag

    def set_parameterization(self, parameterization=[{}]):
        '''
        Sets the parameterization for the workflow
        
        Parameters
        ----------
        parameterization : iterable of dict
            Parameterization iterable with each iteration containing the
            parameters to be changed and their values.'''

        self.parameterization = parameterize(parameterization)
        
    def generate_dag(self,job,**kwargs):

        '''
        Generates an AWS airflow dag from CWL

        Parameters
        ----------
        job: str
            Name of the file (ex. job.yml)
        
        kwargs: dict
            Keyword arguments to pass to the DAG creation


        Returns
        -------
        DAG
        '''
        # Create the unique name of the workflow based on the dir containing 
        # the job file
        wf_id = os.path.basename(os.path.dirname(os.path.abspath(job)))
        with open(job) as fp:
            job = yaml.load(fp)


        dag_id = '{}_{}'.format(self.workflow_name, wf_id)
        self.dag_id = dag_id 
        default_args = {
            "depends_on_past": False,
            "start_date": datetime(2018, 2, 23),
            "max_retries": 300,
            
        }

        try:
            self.workflow_db.insert1({
                'workflow_id' : dag_id,
                'workflow_name' : self.workflow_name
            })
        except( DuplicateError,DataJointError):
            log.warning('Workflow database entry for {} already exists, reinserting'.format(self.workflow_name))
            # This is the dumbest way to delete an entry that I've ever seen
            # delstr = {'workflow_id' : dag_id}
            # (self.workflow_db & delstr).delete()
            # self.workflow_db.insert1({
            #     'workflow_id' : dag_id,
            #     'workflow_name' : self.workflow_name
                
            # },skip_duplicates=True)
            pass
        if self.cwl['class'] != 'Workflow':
            raise TypeError('CWL is not a workflow')
        dag = DAG(
            dag_id=dag_id, 
            default_args=self.default_args,
            schedule_interval=None
        )
        job_params, deps = self.resolve_args(job)
        if len(self.parameterization) > 1:
            log.info('Parameterization produces {} workflows, totaling {} jobs...'.format(len(self.parameterization), len(self.steps)*len(self.parameterization)))
        # If the parameter is a file, use the path
        param_db_update_dict = {}
        for param in self.cwl['inputs']:
            if type(job[param]) != dict:
                param_db_update_dict[param] = job[param]
            elif 'path' in job[param]:
                param_db_update_dict[param] = job[param]['path']
            else:
                raise ValueError('Unable to insert parameter {} into job parameter database'.format(param))

        
        try:
            use_subdag = self.cwl['hints']['saber']['use_subdag']
        except KeyError:
            use_subdag = True
        for i,iteration in enumerate(self.parameterization):
            if 'optimize' in self.parameterization[0].keys():
                    i = self.opti_iter
                    safe_toggle()
            if use_subdag:
                subdag = self.create_subdag(iteration, i, param_db_update_dict, job_params, job, wf_id, deps, dag=None)
                iteration_subdag_step = SubDagOperator(
                    subdag = subdag,
                    task_id = str(i),
                    dag = dag
                )
            else:
                dag = self.create_subdag(iteration, i, param_db_update_dict, job_params, job, wf_id, deps, dag=dag)


        return dag
    def resolve_args(self,job):
        '''
        Creates job parameters from job file

        params:
        ------
        job: dict
            A cwl job loaded directly from yaml
        
        returns:
        ------
        dict:
            A dictionary containing the parameters for each step, resolved to
            their actual values from the job file
        list of tuple:
            List of form (step, step_dependency)
        '''
        
        # Resolve dependencies
        output_deps = self.resolve_dependencies()
        deps = []
        step_params = {}
        # A map from inputs to actual values defined in job
        inputs = {}
        optional_params = []
        # Resolve inputs to job inputs
        for param,t in self.cwl['inputs'].items():
            if param in job:
            
                if type(job[param]) != dict:
                    # Raw value
                    # Must convert to string for AWS for some reason
                    inputs[param] = str(job[param])
                elif (type(job[param]) == dict) and (job[param]['class'] == 'File'):
                    inputs[param] = job[param]['path']
                else:
                    raise NotImplementedError('Job parameter value type {} not supported yet'.format(job[param]['class']))
            elif type(param) == dict and 'default' in param:
                # Using a default
                inputs[param] = str(param['default'])
            else:
                #Parameter is not in job, check if optional
                if '?' in self.cwl['inputs'][param]:
                    optional_params.append(param)
                else:
                    raise TypeError('Parameter {} is required by workflow, but not present in job description'.format(param))
        
        # Resolve step parameters
        # Redundant?
        step_params = {}
        for step_name,step in self.cwl['steps'].items():
            step_params[step_name] = {}
            for input_name,inp in step['in'].items():
                if type(inp) == dict and 'default' in inp:
                    step_params[step_name][input_name] = inp['default']
                elif inp in output_deps:
                    # Add dependency to dependency list of form (step, step_dependency)
                    dep = (step_name,inp.split('/')[0])
                    if dep not in deps:
                        deps.append(dep)
                    # Take from previous step's directory
                    if type(output_deps[inp]) == dict and 'default' in output_deps[inp]:
                        step_params[step_name][input_name] = '{}/{}'.format(inp.split('/')[0], output_deps[inp]['default'])
                    else:
                        step_params[step_name][input_name] = '{}/{}'.format(inp.split('/')[0], inputs[output_deps[inp]])
                    
                elif inp in inputs:
                    step_params[step_name][input_name] = inputs[inp]
                else:
                    if inp not in optional_params:
                        raise TypeError('Input {} not recognized'.format(inp))
        return step_params, deps

    def resolve_dependencies(self):
        '''
        Resolves dependencies (i.e. 'tool/output') to input name defined in job file
        '''
        resolved_outputs = {}
        
        for tool_name,tool_info in self.steps.items():
            log.debug('Resolving outputs for {}'.format(tool_name))
            if not len(tool_info['outputs']) == 0:
                for output_name, output in tool_info['outputs'].items():
                    log.debug('...for output {}'.format(output_name))
                    resolved_outputs['{}/{}'.format(tool_name, output_name)] = self.resolve_glob(
                        tool_name=tool_name, 
                        glob=output['outputBinding']['glob']
                        )
        return resolved_outputs

    def resolve_glob(self, tool_name, glob):
        '''
        Resolves a glob to an input parameter defined in the tool CWL

        Parameters
        ----------
        tool_name: str
            Name of the tool
        glob: str
            The glob to resolve. Should be either a system glob (i.e "output.txt") or
            a resolvable glob such as "$(input.outputname)"
        Returns:
        --------
        str:
            An input parameter from the tool CWL
        '''
        glob_parse = parse.parse('$({}.{})',glob)
        if not glob_parse:
            return glob
        else:
            if glob_parse[0] != 'inputs':
                raise NotImplementedError('References to non-inputs are not supported')
            # Glob with the form $(_._) means it must have a reference
            return self.cwl['steps'][tool_name]['in'][glob_parse[1]]

    def dag_write(self,dag):
        '''
        Very crude way of saving the DAG so airflow can access it.
        '''
        dag_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../dags/'))
        with open(os.path.join(dag_folder, 'template_dag'),'r') as fp:
            template_string = fp.read()
        with open(os.path.join(dag_folder, '{}_dag.pickle'.format(self.workflow_name)),'wb') as fp:
            pickle.dump(dag, fp)
        with open(os.path.join(dag_folder, '{}_dag.py'.format(self.workflow_name)),'w') as fp:
            fp.write(template_string.format(self.workflow_name))

    def collect_results(self):
        '''
        Prints the results of the workflow
        '''
        # Datajoint has not implemented unions yet, so it would be as simple as
        
        query = JobMetadata() * self.job_param_db
        return query.fetch(as_dict=True)
        # d1 = JobMetadata().fetch()
        # s2 = 
