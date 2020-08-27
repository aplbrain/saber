# SABER Floodfill Networks

## Building the docker containers

```shell
docker build --rm -t ffn-base -f Dockerfile.base .
docker build --rm -t aplbrain/ffn-inference -f Dockerfile.inference .
```

## python driver test
docker run --rm -v $(pwd)/results:/ffn/output/ aplbrain/ffn-inference -c config.pbtxt -bb ['start { x:0 y:0 z:0 } size { x:64 y:64 z:63 }'] -o output/my_seg.npy
