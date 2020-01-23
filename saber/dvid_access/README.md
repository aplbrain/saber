# BOSS Access Docker Container 

## Overview

This Docker container contains the tools necessary to push and pull data from the DVID Service. 

## Building

1. Navigate to this folder

    ```
    cd saber/saber/dvid-access/
    ```
1. Build the docker container

    ```
    docker build -t aplbrain/dvid-access .
    ```

## Running

One can either run this docker container as a standalone tool, or you can launch an interactive terminal and access the tools via the command line. This is recommended, as you only have to attach volumes once.

```
docker run -it -v ./data:/data/ aplbrain/dvid-access /bin/bash 
```

This will launch the container as an interactive terminal and bind `./data` on your local system to `/data/` in the container.