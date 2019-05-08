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

import boto3
import json
import glob
import os
import logging
import yaml
import docker
import base64 
from urllib.parse import urlparse
import tarfile

import tempfile
try:
    from BytesIO import BytesIO
    from StringIO import StringIO
except ImportError:
    from io import BytesIO
    from io import StringIO

def docker_auth():
    '''
    Autheticates the AWS ECR registry
    
    Returns:
    --------
    dict: 
        JSON response from the server
    '''
    ecr_client = boto3.client('ecr')
    auth_response = ecr_client.get_authorization_token()['authorizationData']
    if len(auth_response) > 1:
        log.warning('Multiple authorizations for AWS ECR detected, using first one')
    auth_response = auth_response[0]
    return auth_response

def docker_registry_login():
    '''
    Gets the docker registry name from the auth response

    Returns:
    --------
    str : 
        docker registry
    '''
    auth_response = docker_auth()
    docker_registry = urlparse(auth_response['proxyEndpoint']).netloc
    return docker_registry

def docker_login():
    '''
    Logs into the docker registry to push images

    Returns:
    --------
    docker.client
    '''
    auth_response = docker_auth()
    auth_token = base64.b64decode(auth_response['authorizationToken'])
    auth_token = auth_token.decode('ascii').split(':')

    docker_client = docker.from_env()
    login_response = docker_client.login(
        username=auth_token[0],
        password=auth_token[1],
        registry=auth_response['proxyEndpoint'],
        reauth=True
    )
    if 'Status' in login_response:
        log.info(login_response['Status'])
        return docker_client
    else:
        log.error("ERROR")
        log.error(login_response)
        raise RuntimeError('Docker login failed')

def extract(d, keys,exclude=False):
    '''
    Helper function to extract keys and values from dictionary
    
    Parameters
    ----------
    d : dict
        Dictionary from which to extract keys
    keys : list of keys
        List of keys to exclude or include
    exclude : boolean
        If true, excludes the given keys from the returned dictionary
    Returns
    -------
    dict : Dict with extracted keys and values
    '''
    if exclude:
        return dict((k, d[k]) for k in d if k not in keys)
    else:
        return dict((k, d[k]) for k in keys if k in d)
def make_build_context(docker_image_name):
    '''
    Makes a build context for the wrapped docker image

    Parameters:
    -----------
    docker_image_name : str
        Name of the docker image
    
    Returns:
    --------
    tempfile.NamedTemporaryFile : 
        Temporary dockerfile for build
    '''
    s3fd = os.open(os.path.join(os.path.dirname(__file__),'../scripts/s3wrap'), os.O_RDONLY)
    s3fp_info = tarfile.TarInfo('s3wrap')
    s3fp_info.size = os.fstat(s3fd).st_size
    dockerfile = BytesIO()
    log.debug('Docker image name: {}'.format(docker_image_name))
    dockerfile.write('FROM {}\n'.format(docker_image_name).encode())
    with open(os.path.join(os.path.dirname(__file__),'../config/dockerfile_template'), 'r') as template_file:
        for line in template_file.readlines():
            dockerfile.write(line.encode())
    dockerfile.seek(0)


    # Make build context
    f = tempfile.NamedTemporaryFile()
    t = tarfile.open(mode='w', fileobj=f)
    s3fp = os.fdopen(s3fd, mode='rb')
    dfinfo = tarfile.TarInfo('Dockerfile')
    dfinfo.size = len(dockerfile.getvalue())
    t.addfile(dfinfo, dockerfile)
    t.addfile(s3fp_info, s3fp)
    t.close()
    s3fp.close()
    f.seek(0)
    return f

def get_original_docker_name(tool_yml):
    '''
    Gets the original docker name from a tool CWL

    Parameters:
    -----------
    tool_yml : dict
        Tool CWL from file
    
    Returns:
    --------
    str:
        Original docker name
    '''
    try:   
        orig_docker_image_name = tool_yml['hints']['DockerRequirement']['dockerPull']
    except KeyError:
        raise NotImplementedError('Non-docker based tools are not supported')

    return orig_docker_image_name
def make_tag(tool_name, tool_yml, local):
    '''
    Makes a tag form the tool name and tool CWL
    Parameters:
    -----------
    tool_name: str
        Name of the tool
    tool_yml : dict
        Tool CWL from file
    
    Returns:
    --------
    str:
        Docker image tag of the form "registry/original_name:s3"
    '''
    orig_docker_image_name = get_original_docker_name(tool_yml)
    docker_image_name_s = orig_docker_image_name.split('/')
    if not local:
        auth_response = docker_auth()
    # Seperate out docker repo name
    if len(docker_image_name_s) == 3:
        # Includes repository name
        docker_repo_name = docker_image_name_s[0]
        docker_image_name = '/'.join(docker_image_name_s[1:])
    else:
        docker_image_name = orig_docker_image_name
        docker_repo_name = ''
    docker_tag_s = docker_image_name.split(':')
    short_docker_image_name = docker_tag_s[0]
    # if auth_response['proxyEndpoint'] != docker_repo_name:
    #     log.warning('Docker repo does not match AWS docker repo')
    if not local:
        docker_registry = docker_registry_login()
        tag = '{}/{}:s3'.format(docker_registry, short_docker_image_name)
    if local:
        tag = short_docker_image_name
    return tag


def create_and_push_docker_image(tool_yml, tag, local):
    '''
    Creates and pushes a docker image from the created context

    Parameters:
    -----------
    tool_yml : dict
        Tool CWL from file
    tag : str
        Tag generated from make_tag()
    
    Returns:
    --------
    str:
        Tag from input
    
    '''
    orig_docker_image_name = get_original_docker_name(tool_yml)
    dockerfile_tar = make_build_context(orig_docker_image_name)
    if not local:
        docker_client = docker_login()
    if local: 
        docker_client = docker.from_env()
    try:
        im, bgen = docker_client.images.build(
            fileobj=dockerfile_tar, 
            rm=True, 
            pull=True, 
            tag=tag,
            custom_context=True)
    except docker.errors.BuildError as e:
        log.warn('Error building image "{}", trying with local image...'.format(e))
        dockerfile_tar = make_build_context(orig_docker_image_name)

        im, bgen = docker_client.images.build(
            fileobj=dockerfile_tar, 
            rm=True, 
            pull=False, 
            tag=tag,
            custom_context=True)
    prev_line = ''
    for line in bgen:
        if 'stream' in line and line['stream'] != prev_line:
            log.info(line['stream'])
            prev_line = line['stream']
    prev_line = ''
    if not local:
        for line in docker_client.images.push(tag, stream=True, decode=True):
            if 'status' in line and line['status'] != prev_line:
                log.info(line['status'])
                prev_line = line['status']
    return tag
def generate_job_definition(tool_name, tool_yml, tag):
    '''
    Generates an AWS batch job definition containing the running requirements
    and image. Does NOT include a command, as this is added as an override.
    This was done because AWS will throw an error if the job submitted does not
    have all the parameters of the command in the job definition

    Parameters:
    -----------
    tool_name : str
        Name of the tool
    tool_yml : dict
        Tool CWL from file
    tag : str
        Tag of the docker image on the AWS ECR registry.
    
    Returns:
    --------
    dict : 
        Job definition in the format described by AWS
        See: https://docs.aws.amazon.com/batch/latest/userguide/job-definition-template.html

    '''

    # Load template from configs
    with open(os.path.join(os.path.dirname(__file__),'../config/aws_config.yml' )) as fp:
        job_definition = yaml.load(fp)['job-definitions']

    job_definition['containerProperties']['image'] = tag
    
    
    job_definition['containerProperties']['command'] = []
    job_definition['jobDefinitionName'] = tool_name.replace('_','-')
    try:
        job_definition['containerProperties']['memory'] = tool_yml['requirements']['ResourceRequirement']['ramMin']
    except KeyError:
        log.warning('No memory resource requirements specified, using default of {}'.format(job_definition['containerProperties']['memory']))
        
    try:
        job_definition['containerProperties']['vcpus'] = tool_yml['requirements']['ResourceRequirement']['coresMin']
    except KeyError:
        log.warning('No vCPU resource requirements specified, using default of {}'.format(job_definition['containerProperties']['vcpus']))

    return job_definition
def create_job_definitions():
    '''
    Creates job definitions from json files in ./job-definitions/

    Returns
    -------
    list
        List of response dicts of form 
        {
            'jobDefinitionName': 'string',
            'jobDefinitionArn': 'string',
            'revision': 123
        }
            
    '''

    
    ret = []

    job_definition_files = glob.glob(
        os.path.join(os.path.dirname(__file__),'../config/job-definitions/*.json')
        )
    for job_definition_file in job_definition_files:
        with open(job_definition_file) as fp:
            job_definition = json.load(fp)
        ret.append(create_job_definition(job_definition))
    return ret

def create_job_definition(job_definition):
    ''' 
    Registers a job definition with AWS, checking if it was already defined.

    Parameters
    ----------
    job_definition : dict
        Parsed JSON dict describing the job defintition. Should match the
        description here: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/batch.html#Batch.Client.register_job_definition
    
    Returns
    -------
    dict : 
        The response of the form:
        {
            jobDefinitionName: str,
            jobDefinitionArn: str,
            revision: int
        }
    '''
    log.debug('Describing job definition from job {}'.format(job_definition['jobDefinitionName']))
    check_response = client.describe_job_definitions(
            jobDefinitionName=job_definition['jobDefinitionName'],
            status='ACTIVE'
        )
    
    if check_response['jobDefinitions'] == []:
        log.info('Creating job definition for job {}...'.format(job_definition['jobDefinitionName']))
        ret = client.register_job_definition(
            **job_definition
        )
    else:
        for i,c_check_reponse in enumerate(check_response['jobDefinitions']):
            c_check_response = extract(
                d=c_check_reponse, 
                keys=['jobDefinitionArn','status','revision'], 
                exclude=True
            )
            if c_check_response == job_definition:
                log.warning('Job definition exists for job {} and matches revision {}. Continuing...'.format(job_definition['jobDefinitionName'],check_response['jobDefinitions'][i]['revision'] ))
                ret = extract(
                    d=check_response['jobDefinitions'][i],
                    keys=['jobDefinitionName','jobDefinitionArn','revision']
                )
                return ret

        log.warning('Job definition exists for job {}, but does not match file. Creating new revision...'.format(job_definition['jobDefinitionName']))
        ret = extract(
            d=client.register_job_definition(
                **job_definition
                ),
            keys=['jobDefinitionName','jobDefinitionArn','revision']
            )        
    return ret
try:
    client = boto3.client('batch')
except:
    print('Local Execution only (no S3)')
if __name__ == "__main__":
    logging.basicConfig()
    log = logging.getLogger(__name__)
    create_job_definitions()
else:
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    

