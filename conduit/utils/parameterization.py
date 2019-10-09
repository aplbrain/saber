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

import yaml
import numpy as np
import itertools
import random
from abc import ABC, abstractmethod

def parameterize(p):
    param_ranges = []
    for mp_name, metaparam in p.items():
        r = metaparam['range']
        if type(r) == dict:
            param_ranges.append(np.arange(**r))
        elif type(r) == list:
            param_ranges.append(r)
        else:
            raise TypeError("Range structure not valid for {}".format(mp_name))
    iterations = []
    for i in itertools.product(*param_ranges):
        iteration = {}
        for j,(mp_name, metaparam) in enumerate(p.items()):
            job = {}
            if set(metaparam['parameters'].keys()) == set(['min', 'max']):
                if set(metaparam['range'].keys()) == set(['start', 'stop', 'step']):
                    job[metaparam['parameters']['min']] = str(i[j])
                    job[metaparam['parameters']['max']] = str(min(i[j] + metaparam['range']['step'], metaparam['range']['stop']))
                else:
                    raise KeyError("In order to use min/max parameterization, you need to specify a range with start, stop and step")
            elif set(metaparam['parameters'].keys()) == set(['abs']):
                job[metaparam['parameters']['abs']] = str(i[j])
            else:
                raise KeyError("Parameters type(s) {} not valid".format(metaparam['parameters'].keys()))
            for stepname in metaparam['steps']:
                if stepname in iteration:
                    iteration[stepname].update(job)
                else:
                    iteration[stepname] = job
                
        iterations.append(iteration)
    return iterations

class Sampler(ABC):
    '''
    Abstract class for a sampler
    '''
    def __init__(self, parameterization_dict, job):
        self.job = job
        self.parameters = parameterization_dict
        
        super().__init__()
    @abstractmethod
    def update(self, results):
        pass
    
    @abstractmethod
    def sample(self):
        pass

class RandomSampler(Sampler):
    def __init__(self, parameterization_dict, job, max_iterations):
        self.param_grid = parameterize(parameterization_dict)
        self.max_iterations = max_iterations
        self.update(None)
        super().__init__(parameterization_dict, job)

    def update(self, results):
        self.next_job = random.choice(self.param_grid)
    
    def sample(self):
        for i in range(self.max_iterations):
            yield self.next_job

# New sampling methods can be added below!
    
