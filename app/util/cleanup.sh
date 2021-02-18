#!/usr/bin/env bash


# NOTE: This will delete all jobs and logs but keep experiments.

# Clean docker containers
docker system prune -f 

# Remove job and experiment directories
rm -rf /opt/saber/jobs/*

# Re-initialize SABER with new database
docker-compose down
rm -rf ../../volumes
docker-compose up -d

