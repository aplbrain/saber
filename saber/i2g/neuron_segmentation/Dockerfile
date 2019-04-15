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

FROM ubuntu

RUN apt-get update
RUN apt-get install -y \
    git \
    python3-dev \
    python3-pip
RUN git clone https://github.com/janelia-flyem/gala.git
COPY ./requirements.txt /gala/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install Cython numpy h5py
RUN cd gala && \
    pip3 install -r requirements.txt && \
    python3 setup.py install && \
    python3 setup.py build_ext --inplace && \
    cd -
COPY ./driver.py /gala/driver.py
COPY ./trained_classifier.pkl /gala/trained_classifier.pkl
WORKDIR /gala
RUN  apt-get install -y python python-pip
#ENTRYPOINT ["python3", "gala-train  -I --seed-cc-threshold 5 -o ./train-sample --experiment-name agglom ./example/prediction.h5 ./example/groundtruth"]
ENTRYPOINT ["python3", "driver.py" ]
