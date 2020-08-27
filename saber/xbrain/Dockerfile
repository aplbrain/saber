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

FROM jupyter/scipy-notebook:17aba6048f44
RUN conda install --yes -c ilastik-forge/label/cf201901 ilastik-dependencies-no-solvers-no-gui \
     && conda clean -y --all
RUN conda install --yes --force libgfortran scipy \
    && conda clean -y --all

#For supervised only
# User must be responsible for supplying their own classifier 
# ADD ./classifier/xbrain_vessel_seg_v7.ilp /classifier/xbrain.ilp

RUN pip install --no-cache-dir mahotas
RUN pip install --no-cache-dir ndparse
RUN pip install --no-cache-dir nibabel
RUN pip install --no-cache-dir blosc==1.4.4
RUN mkdir app
RUN git clone https://github.com/jhuapl-boss/intern.git && cd intern && git checkout RemoteExtension && git pull && python3 setup.py install --user
ADD ./unsupervised_celldetect.py /app/unsupervised_celldetect.py
#Necessary to use for galaxy
ADD --chown=1000:100 ./xbrain.py ./process-xbrain.py ./split_cells.py  /app/
ENV PATH /app:$PATH
USER root
