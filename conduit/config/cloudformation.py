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

from troposphere import GetAtt, Output, Parameter, Ref, Tags, Template
from troposphere.batch import (ComputeEnvironment, ComputeEnvironmentOrder,
                               ComputeResources, JobQueue)
from awacs.aws import Allow, Statement, Principal, Policy
from troposphere.ec2 import SecurityGroup, SecurityGroupRule
from troposphere.iam import Role, InstanceProfile
from awacs.sts import AssumeRole
import sys, os
import argparse

########
# Script to create a cloudformation template
# Primarily making use of the following repo: https://github.com/cloudtools/troposphere
########

def CF_config(args):
    t = Template()

    t.add_description("This AWS Cloudformation Template creates a stack necessary to run the SABER airflow pipeline.")

    #Set up iamRole
    iamRole = t.add_resource(Role(
        "ecsTaskWithS3",
        AssumeRolePolicyDocument= Policy( 
            Version= "2012-10-17",
            Statement= [
                Statement(
                    Effect=Allow,
                    Action=[AssumeRole],
                    Principal=Principal("Service", ["ecs-tasks.amazonaws.com"])
                )
            ]
        )
    ))

    Vpc = t.add_parameter(Parameter(
        'VpcId',
        ConstraintDescription='Must be a valid VPC ID. (Can be found here: https://console.aws.amazon.com/vpc/home?region=us-east-1#vpcs:sort=VpcId)',
        Type='String'
    ))

    PrivateSubnetA = t.add_parameter(Parameter(
        'SubnetId',
        ConstraintDescription="Must be a valid subnet Id wihthin same VPC id. (Can be found here: https://console.aws.amazon.com/vpc/home?region=us-east-1#subnets:search=vpc-6443921c;sort=State)",
        Type='String'
    ))

    keyname_param = t.add_parameter(Parameter(
        "KeyName",
        Description="Key pair name for EC2 managment",
        Type="String"
    ))

    sec_group = t.add_parameter(Parameter(
        "SecurityGroup",
        Description="Security Group to access Ec2 instances",
        Type="String"
    ))

    BatchServiceRole = t.add_resource(Role(
        'BatchServiceRole',
        Path='/',
        Policies=[],
        ManagedPolicyArns=[
            'arn:aws:iam::aws:policy/AmazonS3FullAccess',
            'arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole',
        ],
        AssumeRolePolicyDocument={'Statement': [{
            'Action': ['sts:AssumeRole'],
            'Effect': 'Allow',
            'Principal': {'Service': ['batch.amazonaws.com']}
        }]},
    ))

    BatchInstanceRole = t.add_resource(Role(
        'BatchInstanceRole',
        Path='/',
        Policies=[],
        ManagedPolicyArns=[
            'arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role'
        ],
        AssumeRolePolicyDocument={'Statement': [{
            'Action': ['sts:AssumeRole'],
            'Effect': 'Allow',
            'Principal': {'Service': ['ec2.amazonaws.com']}
        }]},
    ))

    BatchInstanceProfile = t.add_resource(InstanceProfile(
        'BatchInstanceProfile',
        Path="/",
        Roles=[Ref(BatchInstanceRole)],
    ))

    BatchSecurityGroup = t.add_resource(SecurityGroup(
        'BatchSecurityGroup',
        VpcId=Ref(Vpc), #Default Vpc
        GroupDescription='Enable access to Batch instances',
        Tags=Tags(Name='batch-sg'),
        SecurityGroupIngress=[
            # SecurityGroupRule(
            #     IpProtocol="tcp",
            #     FromPort="22",
            #     ToPort="22",
            #     CidrIp=Ref(sshlocation_param),
            # ),
        ]
    ))

    BatchComputeEnvironment = t.add_resource(ComputeEnvironment(
        'GeneralComputeEnvironment',
        Type='MANAGED',
        State='ENABLED',
        ServiceRole=Ref(BatchServiceRole),
        ComputeResources=ComputeResources(
            'GeneralComputeResources',
            Type='EC2',
            DesiredvCpus=0,
            MinvCpus=0,
            MaxvCpus=256,
            InstanceTypes=['optimal'],
            InstanceRole=Ref(BatchInstanceProfile),
            SecurityGroupIds=[GetAtt(BatchSecurityGroup, 'GroupId'), Ref(sec_group)],
            Subnets=[
                Ref(PrivateSubnetA)
            ],
            Ec2KeyPair=Ref(keyname_param)
        ),
        ComputeEnvironmentName="saber-batch-compute-environment"
    ))

    GPUBatchComputeEnvironment = t.add_resource(ComputeEnvironment(
        'GPUComputeEnvironment',
        Type='MANAGED',
        State='ENABLED',
        ServiceRole=Ref(BatchServiceRole),
        ComputeResources=ComputeResources(
            'GPUComputeResources',
            Type='EC2',
            DesiredvCpus=0,
            MinvCpus=0,
            MaxvCpus=512,
            ImageId="ami-0612e39997371a677",
            InstanceTypes=['p2.xlarge'],
            InstanceRole=Ref(BatchInstanceProfile),
            SecurityGroupIds=[GetAtt(BatchSecurityGroup, 'GroupId'), Ref(sec_group)],
            Subnets=[
                Ref(PrivateSubnetA)
            ],
            Ec2KeyPair=Ref(keyname_param)
        ),
        ComputeEnvironmentName="saber-batch-compute-environment-GPU-enabled"
    ))

    GPUJobQueue = t.add_resource(JobQueue(
        'GPUJobQueue',
        ComputeEnvironmentOrder=[
            ComputeEnvironmentOrder(
                ComputeEnvironment=Ref(GPUBatchComputeEnvironment),
                Order=1
            ),
        ],
        Priority=1,
        State='ENABLED',
        JobQueueName=args.job_queue_gpu
    ))

    GenJobQueue = t.add_resource(JobQueue(
        'GenJobQueue',
        ComputeEnvironmentOrder=[
            ComputeEnvironmentOrder(
                ComputeEnvironment=Ref(BatchComputeEnvironment),
                Order=1
            ),
        ],
        Priority=1,
        State='ENABLED',
        JobQueueName=args.job_queue_gen
    ))

    t.add_output([
        Output('BatchComputeEnvironment', Value=Ref(BatchComputeEnvironment)),
        Output('BatchSecurityGroup', Value=Ref(BatchSecurityGroup)),
        Output('ExampleJobQueue', Value=Ref(GenJobQueue)),
        Output('GPUComputeEnvironment', Value=Ref(BatchComputeEnvironment)),
        Output('ExampleJobQueueGPU', Value=Ref(GPUJobQueue))
    ])

    # Finally, write the template to a file
    template_fp = os.path.dirname(sys.argv[0])   
    with open(template_fp + '/' + args.template_file, 'w') as f:
        f.write(t.to_json())


if __name__ == '__main__':
    
    # Arguments
    parser = argparse.ArgumentParser(
        description='Creates a cloudformation template to deploy a stack on AWS.',
        epilog='EXAMPLE: ./cloudformation.py saber-job-queue saber-gpu-job-queue')
    parser.add_argument('job_queue_gen', help='Name of the general job queue')
    parser.add_argument('job_queue_gpu', help='Name of the gpu job queue')
    parser.add_argument('--template_file', '-f', default='saberAirflowGeneral.json', help='Name of template file (defaults to saberAirflowGeneral.json')
    args = parser.parse_args()

    CF_config(args)
