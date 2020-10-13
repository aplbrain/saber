#!/usr/bin/bash

# Clean docker containers
docker system prune -f 

# Remove job and experiment directories
rm -rf /opt/saber/experiment/*
rm -rf /opt/saber/jobs/*

# Re-initialize SABER with new database
docker-compose down
rm -rf ../volumes
docker-compose up -d

