# ”””
# Copyright 2018 The Johns Hopkins University Applied Physics Laboratory.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# “””

#FROM bgruening/galaxy-imaging
FROM bgruening/galaxy-stable

ENV GALAXY_CONFIG_BRAND="Computational Neuroscience"  
ENV ENABLE_TTS_INSTALL=True
RUN echo "root  ALL = (root) NOPASSWD: SETENV: /usr/bin/docker" >> /etc/sudoers
RUN echo "galaxy ALL = (root) NOPASSWD: SETENV: /usr/bin/docker" >> /etc/sudoers
# The following two lines are optional and can be given during runtime
# with the -e http_proxy='http://yourproxyIP:8080' parameter
#ENV http_proxy 'http://yourproxyIP:8080'
#ENV https_proxy 'http://yourproxyIP:8080'
# ENV GALAXY_DESTINATIONS_DEFAULT slurm_cluster_docker
WORKDIR /galaxy-central
RUN mkdir /galaxy-central/tools/DockerScripts/

#Imaging tools from docker-galaxy-imaging
# Install imaging tools
ADD imagingtoolbox_tools.yml $GALAXY_ROOT/tools.yaml
RUN install-tools $GALAXY_ROOT/tools.yaml && \
    /tool_deps/_conda/bin/conda clean --tarballs

# Adding the tool definitions to the container
ADD ./local_galaxy_tools/ /galaxy-central/tools/

# Install imaging tour
ADD tours/imaging.galaxy_ui.yaml $GALAXY_ROOT/config/plugins/tours/imaging.galaxy_ui.yaml

# Mark folders as imported from the host.
VOLUME ["/export/", "/data/", "/var/lib/docker"]

# Expose port 80 (webserver), 21 (FTP server), 8800 (Proxy)
EXPOSE :80
EXPOSE :21

#Install Workflow (not quite working)
# Add workflows to the Docker image
#ADD ./workflows/*.ga $GALAXY_ROOT/workflows/

# Download training data and populate the data library
#RUN startup_lite && \
#    sleep 30 && \
#    . $GALAXY_VIRTUAL_ENV/bin/activate && \
#    workflow-install --workflow_path $GALAXY_ROOT/workflows/ -g http://localhost:8080 -u $GALAXY_DEFAULT_ADMIN_USER -p $GALAXY_DEFAULT_ADMIN_PASSWORD 
