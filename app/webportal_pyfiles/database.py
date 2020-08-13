#!/usr/bin/env python3

"""
All of the database management code for this app.
"""

import json
import uuid

class JobDatabase:

    def get_all_jobs(self):
        raise NotImplementedError()

    def get_job_by_id(self, id):
        raise NotImplementedError()

    def insert_job(self, job):
        raise NotImplementedError()

    def update_job(self, job_id, job):
        raise NotImplementedError()

# class JankyDatabase inherits JobDatabase
class JankyDatabase(JobDatabase):
    """
    A janky database implementation.
    """
    # fields:
    # string json_fname

    # constructor method
    def __init__(self, json_fname = "jobs.json"):
        self.json_fname = json_fname

    # loads the json file that contains the job names
    def get_all_jobs(self):
        with open(self.json_fname, 'r') as fh:
            return json.load(fh)

    # gets a particular job given the uuid
    def get_job_by_id(self, id):
        return self.get_all_jobs()[id]

    # job is a dict of format {param1: value1, param2: value2}
    # jobs is a dict of format {"uuid": job}
    def insert_job(self, job):
        jobs = self.get_all_jobs()
        job_id = str(uuid.uuid4())
        # add key: value to dict jobs
        jobs[job_id] = job
        # write to json file
        with open(self.json_fname, 'w') as fh:
            json.dump(jobs, fh)
        # return "uuid"
        return job_id

    # method update_job
    # param job_id: the uuid of datatype string
    # param job: datatype dict
    def update_job(self, job_id, job):
        jobs = self.get_all_jobs()
        # update key: value in dict jobs
        jobs[job_id] = job
        # write to json file
        with open(self.json_fname, 'w') as fh:
            return json.dump(jobs, fh)

# TODO:
# Reimplement database using (pick one):
# - MongoDB (schema not required)
# - sqlite3 (schema required)
# - SQL     (schema required)
