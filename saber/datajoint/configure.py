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

#Configuring datajoint
dj.config['database.host'] = '10.109.9.203:3306'
dj.config['database.user'] = 'root'
dj.config['database.password'] = 'tutorial'

#Connecting to datajoin
print(dj.conn())

schema = dj.schema('Xbrain', locals())

@schema #Points to the schema object above
#Data specifications:
class Experiment(dj.Imported):
    definition = """
    # Part of the brain where the data comes from
    experiment_id :  varchar(40)                   #Experiment id 
    ---
      workflow : varchar(10)               # Workflow manager used                                
      """

@schema
#experiment sessions specifications:
class Session(dj.Imported):
    definition = """
    # Centroid results
    -> Experiment                           # Table depends on Experiment
    session_date : date                                   
      """

@schema
#Workflow specifications
class Params(dj.Imported):
    definition = """
    #workflow parameters used
    -> Experiment                           # Table depend on Experiment
    input_data : varchar(128)
    p_threshold : float
    p_residual : float
    spheres_z : float
    dialations_z : float
    max_num_cells : float
    num_samp : int
    num_comp : int
    erodes_z : int
      """
@schema
class Results(dj.Imported):
    definition = """
    -> Experiment
    result_id : varchar(128)                # The result_id of the file related to this experiment
    results : int                     # Numpy array
    cells : int                             # The amount of cells found using the workflow
    """

#Defined instance to manipulate the database
experiment = Experiment() 
session = Session()
params = Params()
results = Results()

# Uncomment this to delete all tables
# experiment.drop()
# session.drop()
# params.drop()
# results.drop()

#Define All Data Variables
SESSION = datetime.datetime.today()
EXPERIMENT_ID = str(uuid.uuid4())
print("This is your experiment ID: " + EXPERIMENT_ID)

#Create unique experiment ID
experiment.insert1((EXPERIMENT_ID, 'airflow'))

# Grab the data from the workflow run
session_data = {
    'experiment_id' : EXPERIMENT_ID,
    'session_date' : SESSION
}
param_data = {
    'experiment_id' : EXPERIMENT_ID,
    'input_data' : INPUT,
    'p_threshold' : 0.2,
    'p_residual' : 0.47,
    'spheres_z' : 18,
    'dialations_z' : 8,
    'max_num_cells' : 500,
    'num_samp' : 500000,
    'num_comp' : 2,
    'erodes_z' : 1,
    'result_id' : 0,
    'cells' : 150
}
results_data + {
    'result_id' : OUTPUT,                
    'results' : OUTPUT_N,                     
    'cells' : CELLS,   
}

#Input data and match to the corresponding UUID of the experiment
session.insert1(session_data)
params.insert1(param_data)
results.insert1(results_data)
#Print joint tables for visualization
print(session * params * results)