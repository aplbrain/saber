#!/bin/bash
sudo docker run -p 8080:80 -p 8021:21 -p 8800:8800 -p 9002:9002 --privileged -e GALAXY_CONFIG_TOOL_CONFIG_FILE=config/my_tools.xml,config/basic_tools.xml,config/shed_tool_conf.xml -e GALAXY_CONFIG_FILE=config/galaxy.ini -e GALAXY_DOCKER_ENABLED=True -e GALAXY_LOGGING="full" -e GALAXY_DESTINATIONS_DEFAULT=slurm_cluster_docker -v /export/:/export/ -v /var/run/docker.sock:/var/run/docker.sock --name galaxywebapp --rm saber:galaxy

