import subprocess
import json
import time
import io
import random
import numpy as np

from database import JankyDatabase
from read_params import cwl_input_params
from find_file import find_file_mod

import conduit

#cwl_location
def conduit_commands(cwl, job):

    subprocess.Popen("cd ~/saber/saber/boss_access/")
    subprocess.Popen("docker build -t aplbrain/boss-access .")
    subprocess.Popen("docker exec -it saber_cwl_parser_1 /bin/bash")
    subprocess.Popen("cd saber/boss_access/boss_test")
    subprocess.Popen("conduit build dummy_workflow.cwl job_params.yml")
    subprocess.Popen("conduit parse dummy_workflow.cwl job_params.yml")

  #command = "cwl-runner " + request.form['cwlFilename'] + " final_output.yaml"
    #subprocess.call(command, shell = True)



