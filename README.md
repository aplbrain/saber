# saber
This is the SABER repository for computational neuroscience. The SABER project, funded by the NIH, aims to build reproducible and scalable imaging pipelines for computational neuroscientists. This project builds on modern tools such as the Galaxy project in bioinformatics and Apache Airflow. We aim to build a computational framework (conduit) for reproducible pipelines and to develop new image processing and optimization methods to accelerate scientific discovery.

This project is distributed under the Apache License, Version 2.0

Current release: 

The current public release is a platform for optimization and deployment of computational neuroscience pipelines using the galaxy project. We build on the Galaxy docker work (https://github.com/bgruening/docker-galaxy-stable) to provide a dockerized environment scientists can rapidly get up and running. We are developing canonical workflows and dockerized tools to premote reproducible science and benchmarking of algorithms. 

Requirements:
Working docker installation, administrator access for your sytem. Note that in the current configuration, exported files are stored at /export. This can be controlled by editing ./run_galaxy.sh

Installation:

1. cd $saber_home/conduit/galaxy
2. ./build_galaxy.sh (creates the saber:galaxy image)
3. ./run_galaxy.sh
4. Use a web browser to check out galaxy at localhost:8080

Ongoing work: 

The SABER team is actively developing two solutions for datasets at different scales: Apache Airflow and Galaxy. We will be updating this repository with these tools as we test and release them. The goal is to enable scalable neuroscience from a single desktop to large cloud computing solutions. 

We are also defining canonical tools and workflows for processing neuroscience data. These data include Electron Microscopy and Xray Microtomography imaging of neural tissue. These tools and workflows, along with guidance and tools for algorithms developers, will be integrated as well.

Demos: 

Installation of SABER galaxy: https://youtu.be/m32Yd5sBgzE

Optimizing a workflow in SABER galaxy: https://youtu.be/-x7VNWyT4MU

Deploying a workflow in SABER galaxy: https://youtu.be/AHYyVqt49Tk

Deploying a workflow in Apache Airflow and AWS Batch: https://youtu.be/643UUTbOgwk

