

# SABER <img src="https://avatars2.githubusercontent.com/u/34253653?s=200&v=4" alt="APL Brain logo" width="80"/>

## What is in this branch?
This Branch includes the repository of detestron2,  Facebook AI Research's next generation library that provides state-of-the-art detection and segmentation algorithms. It supports a number of computer vision research projects and production applications in Facebook. Our goal is to study this repository and use its algorithms to help identify different parts of the brain. The attached link is a google colab that shows a demo of how detectron works with image data: https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5.
## Prerequisites
Detectron2 requires a GPU. If needed connect an AWS Instance. Below is the skeleton configuration file to connect through Visual Studio Code. 

Host aws-ec2 \
    HostName ec2-44-229-243-8.us-west-2.compute.amazonaws.com \
    User ubuntu \
    IdentityFile ~/aws-key/test-key-pair.pem

The following link explains detail the process behind the connection.

https://medium.com/@christyjacob4/using-vscode-remotely-on-an-ec2-instance-7822c4032cff

## Installation
Simply clone this repository and run
`docker-compose up -d` inside it!

## Execution of workflows

Please see our [wiki](https://github.com/aplbrain/saber/wiki) for more information!

## Data Access

Please see our [wiki](https://github.com/aplbrain/saber/wiki/Data-Access) for more information about public access to data for testing Electron Microscopy and X-ray Microtomography workflows. 

## Legal

Use or redistribution of the SABER system in source and/or binary forms, with or without modification, are permitted provided that the following conditions are met:
 
1. Redistributions of source code or binary forms must adhere to the terms and conditions of any applicable software licenses.
2. End-user documentation or notices, whether included as part of a redistribution or disseminated as part of a legal or scientific disclosure (e.g. publication) or advertisement, must include the following acknowledgement:  The SABER software system was designed and developed by the Johns Hopkins University Applied Physics Laboratory (JHU/APL). 
3. The names "SABER", "JHU/APL", "Johns Hopkins University", "Applied Physics Laboratory" must not be used to endorse or promote products derived from this software without prior written permission. For written permission, please contact BossAdmin@jhuapl.edu.
4. This source code and library is distributed in the hope that it will be useful, but is provided without any warranty of any kind.
