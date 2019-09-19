# Floodfill Docker

## Building the docker containers

```shell
docker build --rm -t ffn-base -f Dockerfile.base .
docker build --rm -t ffn-train -f Dockerfile.train .
docker build --rm -t ffn-inference -f Dockerfile.inference .
```

## Downloading data for use

Put an intern config in `~/.intern/intern.cfg`.

You may need:

```shell
pip install scipy scikit-image numpy tensorflow h5py pillow absl-py intern
``` 


```shell
mkdir data/

scripts/create-training-set bossdb://kasthuri2015/ac4/em bossdb://kasthuri2015/ac4/neuron 512:1024/512:1024/0:99 --boss_config_file /home/ubuntu/.intern/intern.cfg --raw_out data/raw --seg_out data/seg
```

## Convert data to hdf5 of the correct dtype and shape

```shell
scripts/npy2hdf5 raw data/raw.npy data/raw.h5
scripts/npy2hdf5 seg data/seg.npy data/seg.h5
```

## Train the model

```shell
sudo docker run --runtime=nvidia -it -v $(pwd)/data:/data -v $(pwd)/model:/model ffn-train
```

The model checkpoints will be saved to `$(pwd)/model`.

## Run inference

```shell
sudo docker run --runtime=nvidia -it -v $(pwd)/data:/data -v $(pwd)/model:/model -v $(pwd)/results:/results ffn-inference
```

## python driver test
docker run --rm -v $(pwd)/results:/ffn/output/ aplbrain/ffn-inference -c config.pbtxt -bb ['start { x:0 y:0 z:0 } size { x:64 y:64 z:63 }'] -o output/my_seg.npy
