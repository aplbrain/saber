# BOSS Access Docker Container 

## Overview

This Docker container contains the tools necessary to push and pull data from the Block Object Storage Service (BOSS). 

## Building

1. Navigate to this folder

    ```bash
    cd saber/boss_access
    ```
2. Build the docker image in your current directory

    ```bash
    docker build -t <image_name> .
    ```

## Running

To run this docker container

```bash
docker run --name <container_name> -it -v $(pwd)/data:/data/ <image_name> /bin/bash
```

This will launch the container as an interactive terminal and bind `./data` on your local system to `/data/` in the container.

### Pulling data

#### Usage

```bash
boss_access.py pull (-c CONFIG | -t TOKEN) --coll COLL --exp EXP --chan CHAN [--res RES] [--xmin XMIN][--xmax XMAX] [--ymin YMIN] [--ymax YMAX] [--zmin ZMIN] [--zmax ZMAX] -o OUTPUT
```
#### Options

##### config

Type: Configuration file

Description: Configuration file for BOSS

##### token

Type: String

Description: BOSS API Token

##### coll

Type: String

Description: BOSS collection from which to download from.

##### exp

Type: String

Description: BOSS experiment from which to download from.

##### res

Type: int

Description: Resolution. Unused.

##### x/y/z min/max

Type: int

Description: Bounds for volume.

##### Output

Type: File

Description: Output filename

### Pushing data

#### Usage

```bash
boss_access.py push (-c CONFIG | -t TOKEN) --coll COLL --exp EXP --chan CHAN [--res RES] [--xmin XMIN][--xmax XMAX] [--ymin YMIN] [--ymax YMAX] [--zmin ZMIN] [--zmax ZMAX] --type TYPE -i INPUT
```
#### Options

##### config

Type: Configuration file

Description: Configuration file for BOSS

##### token

Type: String

Description: BOSS API Token

##### coll

Type: String

Description: BOSS collection from which to upload to.

##### exp

Type: String

Description: BOSS experiment from which to upload to.

##### res

Type: int

Description: Resolution. Unused.

##### x/y/z min/max

Type: int

Description: Bounds for volume.

##### type

Type: "annotation" or "image"

Description: Image type to set.

##### Input

Type: File

Description: Input filename


