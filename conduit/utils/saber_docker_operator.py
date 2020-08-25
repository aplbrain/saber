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

import time
import parse

from airflow.operators.docker_operator import DockerOperator
from conduit.utils.datajoint_hook import DatajointHook, JobMetadata
from datajoint import DuplicateError


class SaberDockerOperator(DockerOperator):
    def __init__(self, *args, workflow_id, score_format="", **kwargs):
        super().__init__(*args, **kwargs)
        self.score_format = score_format
        self.workflow_id = workflow_id
        self.task_id = kwargs["task_id"]
        self.dj_hook = DatajointHook()

    def execute(self, *args, **kwargs):
        begin_time = time.time()
        super().execute(*args, **kwargs)
        task_time = time.time() - begin_time
        score = self._get_score()
        iteration = self.task_id.split(".")[1]
        real_task_id = self.task_id.split(".")[0]
        self.log.info(
            "Inserting {} {} {} {} {} into job metadata database".format(
                self.workflow_id, iteration, real_task_id, task_time, score
            )
        )
        self.dj_hook.insert1(
            {
                "iteration": iteration,
                "workflow_id": self.workflow_id,
                "job_id": real_task_id,
                "cost": task_time,
                "score": score,
            },
            JobMetadata,
        )

    def _get_score(self):

        if self.score_format:
            logEvents = self.cli.logs(container=self.container["Id"], stream=True)
            # Reads events from most recent to least recent (earliest), so the
            # first match is the most recent score. Perhaps change this?
            for logEvent in logEvents:
                parsed_event = parse.parse(self.score_format, logEvent.decode())
                if parsed_event and "score" in parsed_event.named:
                    return float(parsed_event["score"])
            self.log.info("Score format present but no score found in logs...")
        return None
