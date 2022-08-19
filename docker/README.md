
Below are the steps to building the docker image and running the bash script

cd docker/

# Build:
docker build --build-arg USER_ID=$UID -t detectron2:v0 .

#Launch:
sh run_docker.sh 