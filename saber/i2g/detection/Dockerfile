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

FROM ermaker/keras

RUN apt-get clean
RUN apt-get update
RUN apt-get -y upgrade

RUN apt-get -y install build-essential

RUN apt-get -y install \
  libx11-dev \
  libblosc-dev \
  libblas-dev \
  liblapack-dev \
  wget

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

# Setup python packages
RUN pip3 install Theano
RUN pip3 install numpy
RUN pip3 install awscli
RUN pip3 install boto3

# Install intern
RUN pip3 install intern
RUN mkdir -p /src/weights
RUN wget --directory-prefix /src/weights https://raw.githubusercontent.com/aplbrain/emcv/master/unets/weights/kasthuri/synapse_weights.hdf5
RUN wget --directory-prefix /src/weights https://raw.githubusercontent.com/aplbrain/emcv/master/unets/weights/kasthuri/membrane_weights.hdf5
# Create workspace
# TODO: Re-org this to use git clone and S3
WORKDIR /src
COPY ./*.py /src/


ENV KERAS_BACKEND=theano
ENV PATH=/src:$PATH

RUN mkdir ~/.aws
ENTRYPOINT ["python", "deploy_pipeline.py"]
