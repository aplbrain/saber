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
python boss_access.py pull (-c CONFIG | -t TOKEN) --coll COLL --exp EXP --chan CHAN [--res RES] [--xmin XMIN][--xmax XMAX] [--ymin YMIN] [--ymax YMAX] [--zmin ZMIN] [--zmax ZMAX] [--order ORDER] -o OUTPUT
```
#### Options

##### config

Type: Configuration file

Description: Configuration file for BOSS

##### token

Type: String

Description: BOSS API Token

##### host (Optional)

Type: String

Description: Name of boss host (Ex. api.bossdb.io)

Default: api.bossdb.io

##### coll

Type: String

Description: BOSS collection from which to download from

##### exp

Type: String

Description: BOSS experiment from which to download from

##### res

Type: int

Description: Resolution

##### x/y/z min/max

Type: int

Description: Bounds for volume

##### order (Optional)

Tyoe: String

Description: xyz or zyx order for data download

Default: 'zyx'

##### Output

Type: File

Description: Output filename

#### Example

```bash
python boss_access.py pull -t public --coll kuan_phelps2020 --ex drosophila_brain_120nm --chan drBrain_120nm_rec --res 0 --xmin 1000 --xmax 1500 --ymin 1000 --ymax 1500 --zmin 50 --zmax 60 -o /data/kuan_phelps_120.npy
```

### Pushing data

#### Usage

```bash
python boss_access.py push (-c CONFIG | -t TOKEN) --coll COLL --exp EXP --chan CHAN [--res RES] [--xmin XMIN][--xmax XMAX] [--ymin YMIN] [--ymax YMAX] [--zmin ZMIN] [--zmax ZMAX] [--order ORDER] --dtype DTYPE [--source SOURCE] -i INPUT
```
#### Options

##### config

Type: Configuration file

Description: Configuration file for BOSS

##### host (Optional)

Type: String

Description: Name of boss host (Ex. api.bossdb.io)

Default: 'api.bossdb.io'

##### token

Type: String

Description: BOSS API Token

##### coll

Type: String

Description: BOSS collection from which to upload to

##### exp

Type: String

Description: BOSS experiment from which to upload to

##### res

Type: int

Description: Resolution

##### x/y/z min/max

Type: int

Description: Bounds for volume

##### order

Tyoe: String

Description: order of your data (xyz or zyx) for data upload

Default: xyz

##### dtype

Type: numpy data type

Description: Datatype to receive data in when downloading, or to use when uploading (Ex. uint8)

##### Input

Type: File

Description: Input filename

