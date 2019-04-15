# BOSS Access Docker Container 

## Overview

This Docker container contains the tools necessary to push and pull data from the Block Object Storage Service (BOSS). 

## Building

1. Navigate to this folder

    ```
    cd saber-private/workflows/boss_access
    ```
1. Build the docker container

    ```
    docker build -t boss-access
    ```

## Running

One can either run this docker container as a standalone tool, or you can launch an interactive terminal and access the tools via the command line. This is recommended, as you only have to attach volumes once.

```
docker run -it -v ./data:/data/ boss-access /bin/bash 
```

This will launch the container as an interactive terminal and bind `./data` on your local system to `/data/` in the container.

### Pulling data

#### Usage

```
boss_access.py pull (-c CONFIG | -t TOKEN) [-b BUCKET] --coll COLL --exp EXP --chan CHAN --coord COORD --dtype DTYPE --itype ITYPE [--res RES] [--xmin XMIN][--xmax XMAX] [--ymin YMIN] [--ymax YMAX] [--zmin ZMIN] [--zmax ZMAX] [--padding PADDING] -o OUTPUT [--s3-only]
```
#### Options

##### config

Type: Configuration file

Description: Configuration file for BOSS

##### token

Type: String

Description: BOSS API Token

##### bucket

Type: String

Description: S3 Bucket to save to. If unset, only a local file will be saved.

##### coll

Type: String

Description: BOSS collection from which to download from.

##### exp

Type: String

Description: BOSS experiment from which to download from.

##### coord

Type: String

Description: Coordinate system to use when downloading from the BOSS.

##### dtype

Type: numpy data type

Description: Datatype to recieve data in when downloading, or to use when uploading. Ex. uint8

##### itype

Type: "annotation" or "image"

Description: Image type to get.

##### res

Type: int

Description: Resolution. Unused.

##### x/y/z min/max

Type: int

Description: Bounds for volume.

##### padding

Type: int

Description: How much padding to use. Padding is applied to pulled images and stripped from pushed images.

##### Output

Type: File

Description: Output filename

##### s3-only

Type: Flag

Description: If set, no local file will be saved and the resulting cutout will be uploaded to S3. 

### Pushing data

#### Usage

```
boss_access.py push (-c CONFIG | -t TOKEN) [-b BUCKET] --coll COLL --exp EXP --chan CHAN --coord COORD --dtype DTYPE --itype ITYPE [--res RES] [--xmin XMIN][--xmax XMAX] [--ymin YMIN] [--ymax YMAX] [--zmin ZMIN] [--zmax ZMAX] [--padding PADDING] -o OUTPUT [--s3-only]
```
#### Options

##### config

Type: Configuration file

Description: Configuration file for BOSS

##### token

Type: String

Description: BOSS API Token

##### bucket

Type: String

Description: S3 Bucket to load from. If unset, a local file specified by --input will be used.

##### coll

Type: String

Description: BOSS collection from which to upload to.

##### exp

Type: String

Description: BOSS experiment from which to upload to.

##### coord

Type: String

Description: Coordinate system to use when uploading to the BOSS.

##### dtype

Type: numpy data type

Description: Datatype to to use when uploading. Ex. uint8

##### itype

Type: "annotation" or "image"

Description: Image type to set.

##### res

Type: int

Description: Resolution. Unused.

##### x/y/z min/max

Type: int

Description: Bounds for volume.

##### padding

Type: int

Description: How much padding to use. Padding is applied to pulled images and stripped from pushed images.

##### Input

Type: File

Description: Input filename


