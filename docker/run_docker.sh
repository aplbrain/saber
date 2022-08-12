#! /bin/zsh

# creates a container based on the commands from detectron2 
# dockerfile and imports the intern algorithm to call in 
# the bossdb data

# Also the file will bind mount to a test file with the 
# google colab collaboration custom dataset by replacing
# with the bossdb data set

# trim trailing / from argument so autocomplete to directories can be used
NAME="test.py"

# create the container so that it keeps itself alive, automatically cleans up
# on exit, and bind mounts the repo
 docker run \
    -dt \
    --rm \
    --gpus all\
    --name "$NAME"\
    --mount type=bind,source=/home/ubuntu/saber/files/"$NAME",target=/home/appuser/detectron2/"$NAME" \
    --mount type=bind,source=/home/ubuntu/saber/files/test2.py,target=/home/appuser/detectron2/test2.py \
    --mount type=bind,source=/home/ubuntu/saber/files/demo.py,target=/home/appuser/detectron2/demo.py \
     --mount type=bind,source=/home/ubuntu/saber/files/via_region_data.json,target=/home/appuser/detectron2/via_region_data.json \
    --mount type=bind,source=/home/ubuntu/saber/kasthuri_challenge,target=/home/appuser/kasthuri \
    detectron2:v0

# remove the repo from catkin workspace if it already exists
# start an interactive terminal
docker exec -it "$NAME" /bin/bash
# automatically stop the container on exit
docker stop "$NAME"