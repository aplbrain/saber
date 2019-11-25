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

import datajoint as dj
from datajoint import DuplicateError
import datetime
import uuid
from pathlib import Path
from airflow.hooks.base_hook import BaseHook
import re
import os
import contextlib
from contextlib import closing
import sys


class Workflow(dj.Manual):
    definition = """
    # Workflows
    workflow_id : varchar(40)
    ---
    workflow_name : varchar(40)
    """

class JobMetadata(dj.Manual):
    definition = """
    # Metadata table for optimization / statistics
    -> Workflow
    iteration : varchar(6)
    job_id : varchar(40)
    ---
    cost: float
    score = null : float
    
    """




def handle_key(key):
    """
    Handles keys to fit into DataJoint tables
    Returns false if saber key


    """
    assert isinstance(key, str)
    key = key.lower()
    if re.match('_saber_.*',key):
        return False
    if re.match("^[a-z][a-z0-9_]*$", key):
        return key
    else:
        raise ValueError('Key must start with a letter and only contain alphanumeric characters and underscores')
    
    


    
    

db_types = {
    'int' : 'int',
    'boolean' : 'char(4)',
    'float' : 'float',
    'double' : 'double',
    'string' : 'varchar(64)',
    'File' : 'varchar(64)'
}




class DatajointHook(BaseHook):
    
    def __init__(self, classdef=None, safe=True, config=None):
        self.safe = safe
        if config is None:
            self.config = {}
            self.config['host'] = 'datajoint:3306'
            self.config['user'] = 'root'
            self.config['password'] = 'airflow'
        else:
            self.config = config
        self.classdef = classdef
        self.context = {}
        with closing(self.get_conn()) as conn:
            self.create_table(conn, Workflow)
            self.create_table(conn, JobMetadata)
        
    def create_definition(self, d, wf_name, is_cwl=True):
        definition = """
        # Parameter table for workflow {}
        -> Workflow
        iteration : varchar(6)
        ---

        """.format(wf_name)
        for k,t in d.items():
            # Ignore saber keys
            tp = t.replace('?','')
            k = handle_key(k)
            if k:
                try:
                    djt = db_types[tp] if is_cwl else tp
                except KeyError:
                    # Unsupport type, try string lmao
                    djt = "varchar(64)"
                definition += "    {} = null : {}\n".format(k,djt)
        return type("{}Params".format(wf_name.title()), (dj.Manual,), dict(definition=definition))
    def create_table(self, conn, classdef=None):
        if self.classdef is None and classdef is None:
            raise AttributeError("Schema needs to be set. Create in constructor or by using create_definition")
        if classdef is None:
            classdef = self.classdef
                
        schema = dj.schema(schema_name='airflow', connection=conn, context=self.context)

        
        table = schema(classdef)()
        self.context[classdef.__name__] = table
        return table
    def insert1(self, row, classdef=None, skip_duplicates=True, **kwargs):
        if classdef is None:
            classdef = self.classdef
        with closing(self.get_conn()) as conn:
            table = self.create_table(conn, classdef=classdef)

            ret = table.insert1(row, skip_duplicates=skip_duplicates, **kwargs)
        return ret
    
    def get_conn(self):
        with open(os.devnull,'w') as devnull:
            with contextlib.redirect_stdout(devnull):
                conn = dj.conn(**self.config, reset=True)
        return conn
    def update(self, row, primary_keys={}, classdef=None,  **kwargs):
        
        if classdef is None:
            classdef = self.classdef
        with closing(self.get_conn()) as conn:
            table = self.create_table(conn, classdef=classdef)
            try: 
                ret = table.insert1(row, skip_duplicates=False, **kwargs)
            except DuplicateError:
                with dj.config(safemode=False):
                    (table & primary_keys).delete()
                ret = table.insert1(row, skip_duplicates=False, **kwargs)
        return ret
    def query(self, classdef=None)
        if classdef is None:
            classdef = self.classdef
        with closing(self.get_conn()) as conn:
            table = self.create_table(conn, classdef=classdef)
            
            jmdb = self.create_table(conn, JobMetadata)
            query = table*jmdb
        return query.fetch(as_dict=True)
            
    def init_workflow(self, id, name):

        self.insert1(dict(
            workflow_id=id,
            workflow_name=name
        ), classdef=Workflow)
    
    

