# Blob Detect Tool
Author: Daniel Xenes  
Takes a volume_thresholded volume (binary volume) and finds blobs in it (hopefully cell bodies).

Inputs:
    input - (str) binary map input file
    max - (float) maximum area to be counted 
    min - (float) minimum area to be counted
    outfil - (str) output file name

outputs:

    MxN Array containing centroids where 
        M is number of blobs and 
        N is ndim of input array 

## How to use

`docker run aplbrain/blob_detect -i INPUT_FILE --min MINIMUM --max MAXIMUM --outfile OUTPUT_FILE`

Input files must be numpy .npy files.