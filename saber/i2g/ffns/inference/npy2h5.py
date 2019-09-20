"""
Copyright 2018 The Johns Hopkins University Applied Physics Laboratory.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import numpy as np
import h5py

def convert(file, path, name):
    data = np.load(file)
    dtype = data.dtype
    if dtype == np.uint64:
        print("Converting to uint8 from " + str(dtype))
        dtype = np.uint8
    with h5py.File(path, 'w') as fh:
        fh.create_dataset(name, data=data, dtype=dtype)

