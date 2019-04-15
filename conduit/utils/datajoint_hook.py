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
import datetime
import uuid
from pathlib import Path
from airflow.hooks.base_hook import BaseHook
import re




# class DatajointHook():
#     def __init__(self, *args, **kwargs):
#         #Configuring datajoint
#         dj.config['database.host'] = '10.109.9.203:3306'
#         dj.config['database.user'] = 'root'
#         dj.config['database.password'] = 'tutorial'
#     def get_conn(self, host, user, password):
#         dj.config['database.host'] = host
#         dj.config['database.user'] = user
#         dj.config['database.password'] = password
#         log.info(dj.conn()))
dj.config['database.host'] = 'datajoint:3306'
dj.config['database.user'] = 'root'
dj.config['database.password'] = 'airflow'
dj.conn()
schema = dj.schema('airflow', locals())

@schema
class Workflow(dj.Manual):
    definition = """
    # Workflows
    workflow_id : varchar(40)
    ---
    workflow_name : varchar(40)
    """
@schema
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
# Hacky way to get a class? I hate datajoint


def create_dj_schema(d, wf_name, is_cwl=True):
    definition = """
    # Parameter table for workflow {}
    -> Workflow
    iteration : varchar(6)
    ---

    """.format(wf_name)
    for k,t in d.items():
        # Ignore saber keys
        tp = t.replace('?','')
        if not re.match('_saber_.*',k):
            try:
                djt = db_types[tp] if is_cwl else tp
            except KeyError:
                # Unsupport type, try string lmao
                djt = "varchar(64)"
            definition += "    {} = null : {}\n".format(k,djt)
    return type("{}Params".format(wf_name.title()), (dj.Manual,), dict(definition=definition))




    
    

db_types = {
    'int' : 'int',
    'boolean' : 'char(4)',
    'float' : 'float',
    'double' : 'double',
    'string' : 'varchar(64)',
    'File' : 'varchar(64)'
}




# @schema
# class WorkflowMetadata(dj.Imported):
#     definition = """
#     # 