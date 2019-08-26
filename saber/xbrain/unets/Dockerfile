# Copyright 2018 The Johns Hopkins University Applied Physics Laboratory.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM kaixhin/cuda-theano:8.0

# Install dependencies
RUN apt-get update && apt-get install -y \
  libhdf5-dev \
  python-h5py \
  python-yaml \
  python3-pip \
  vim

RUN pip install --upgrade pip
# Upgrade six
RUN pip install --upgrade six

# Clone Keras repo and move into it
#RUN cd /root && git clone https://github.com/fchollet/keras.git && cd keras && \
#  # Install
#  python setup.py install
RUN pip install --ignore-installed keras
#==1.2.2
#RUN pip install --ignore-installed pygpu
#added 

# Install intern
RUN pip install --ignore-installed intern
#RUN pip install awscli
#RUN pip install boto3
RUN pip install --ignore-installed SimpleITK

#Default python2 doesn't include enum34
RUN pip install enum34

#Theano needs numpy ver < 1.16.0 to work
RUN pip install numpy==1.15.4 

# Create workspace
# TODO: Re-org this to use git clone and S3
WORKDIR /src
#COPY ./weights/*.hdf5 /src/weights/
#COPY ./aws-batch/setup/startup.sh /src/
#COPY ./*.json /src/
COPY ./*.py /src/

ENV KERAS_BACKEND=theano
ENV PATH=/src:$PATH

ENV THEANO_FLAGS="device=cuda0"
#ENV THEANO_FLAGS='device=cuda,lib.cnmem=1'

CMD ["python", "train_unet_docker.py"]
