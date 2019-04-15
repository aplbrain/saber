# XBrain Docker container
## Overview

This docker container contains the following tools necessary for the XBrain workflow

- Cell membrane classification
- Vessel segmentation
- Cell detection
- run pipeline for cell detection (classification followed by detection)

## Building
1. Navigate to this folder

    ```
    cd saber-private/workflows/xbrain
    ```
1. Build the docker container

    ```
    docker build -t xbrain
    ```
This requires a ilp file, which is a pretrained Ilastick classifier, in the ./classifier directory, relative to the xbrain dockerfile. This will be placed in the container at /classify/ for the tools to use

## Running
One can either run this docker container on a tool-by-tool basis, or you can launch an interactive terminal and access the tools via the command line. This is recommended, as you only have to attach volumes once.

```
docker run -it -v ./data:/data/ xbrain /bin/bash 
```

This will launch the container as an interactive terminal and bind `./data` on your local system to `/data/` in the container.
### Cell membrane classification

#### Usage

```
process-xbrain classify -i INPUT -o OUTPUT [--ram RAM] [--threads THREADS]
```

#### Options

##### input
Type: Numpy file

Description: A Nr x Nc x Nz numpy file that you wish to classify.

##### output
Type: Numpy file

Description: The name of the output file. The file will be a Nr x Nc x Nz x 3 numpy file.

#### ram

Type: Integer

Description: The maximum amount of RAM (in MB) used for classification. Will have no effect if larger than the amount dedicated to the container.

##### threads

Type: Integer

Description: Number of threads to use (-1 means number of CPUs available). Will also have no effect if larger than the amount dedicated to the container.

### Cell detection

#### Usage

```
process-xbrain detect -i INPUT -o OUTPUT [--threshold THRESHOLD] [--stop STOP] [--initial-template-size INITIAL_TEMPLATE_SIZE [--dilation DILATION] [--max-cells MAX_CELLS]
```


#### Options

##### input
Type: Numpy file

Description: A Nr x Nc x Nz x 3 numpy file containing a probability map in [:, :, :, 2] that contains the probability of each voxel being a cell body. The output of membrane classification is sufficient.

##### output
Type: Numpy file

Description: The name of the output file. This file will be a tuple of the form (centroids, cell_map). 

centroids is a D x 4 matrix, where D = number of detected cells. The (x,y,z) coordinate of each cell are in columns 1-3. The fourth column contains the correlation (ptest) between the template and probability map and thus represents our "confidence" in the estimate. The algorithm terminates when ptest<=stopping_criterion.

cell_map is a Nr x Nc x Nz matrix containing labeled detected cells (1,...,D)

##### threshold

Type: Integer

Description: Cell probability threshold. Probabilities below this threshold will be ignored.

##### stop

Type: Float

Description: Stopping criterion. Stopping criterion is a value between (0,1) (minimum normalized correlation between template and probability map) (Example = 0.47)

##### initial-template-size

Type: Integer

Description: Initial size of spherical template (to use in sweep)


##### dilation

Type: Integer

Description: Size to increase mask around each detected cell (zero out sphere of radius with initial_template_size+dilation_size around each centroid)

##### max-cells

Type: Integer

Description: Maximum number of cells to be detected. This is a alternative stopping criterion.

### Vessel segmentation

#### Usage

```
process-xbrain segment [-h] -i INPUT -o OUTPUT [--threshold THRESHOLD] [--dilation DILATION] [--minimum MINIMUM]
```

##### input
Type: Numpy file

Description: Description: A Nr x Nc x Nz x 3 numpy file containing a probability map in [:, :, :, 1] that contains the probability of each voxel being a vessel. The output of membrane classification is sufficient.

##### output
Type: Numpy file

Description: The name of the output file. The output file will be a binary image describing the locations of vessels.

##### threshold

Type: Integer

Description: Vessel probability threshold. Probabilities below this threshold will be ignored.


##### dilation

Type: Integer

Description: Sphere Structural Element diameter size.

##### minimum

Type: Integer

Description: Minimum size. Components smaller than this are removed from image.

### Run cell detection pipeline (runall)

#### Usage

```
process-xbrain runall -i INPUT -o OUTPUT [--ram RAM] [--threads THREADS] [--threshold THRESHOLD] [--stop STOP] [--initial-template-size INITIAL_TEMPLATE_SIZE [--dilation DILATION] [--max-cells MAX_CELLS]
```

##### input
Type: Numpy file

Description: A Nr x Nc x Nz numpy file that you wish to classify.

##### output
Type: Numpy file

Description: The name of the output file. The output file will be a binary image describing the locations of cell bodies.

#### ram

Type: Integer

Description: The maximum amount of RAM (in MB) used for classification. Will have no effect if larger than the amount dedicated to the container.

##### threads

Type: Integer

Description: Number of threads to use (-1 means number of CPUs available). Will also have no effect if larger than the amount dedicated to the container.

##### threshold

Type: Integer

Description: Cell probability threshold. Probabilities below this threshold will be ignored.

##### stop

Type: Float

Description: Stopping criterion. Stopping criterion is a value between (0,1) (minimum normalized correlation between template and probability map) (Example = 0.47)

##### initial-template-size

Type: Integer

Description: Initial size of spherical template (to use in sweep)


##### dilation

Type: Integer

Description: Size to increase mask around each detected cell (zero out sphere of radius with initial_template_size+dilation_size around each centroid)

##### max-cells

Type: Integer

Description: Maximum number of cells to be detected. This is a alternative stopping criterion.