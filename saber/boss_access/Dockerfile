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

#Use an official Python runtime as a parent image
FROM python:3.6

# Install any needed packages specified in requirements.txt
RUN pip install numpy
RUN pip install scikit-image
RUN pip install scipy boto3

# RUN git clone https://github.com/jhuapl-boss/intern.git && cd intern && git checkout RemoteExtension && git pull && python3 setup.py install --user
RUN pip install intern

RUN mkdir /app
COPY ./boss_access.py /app/
RUN chown -R 1000:100 /app/
ENV PATH /app:$PATH
WORKDIR /app

