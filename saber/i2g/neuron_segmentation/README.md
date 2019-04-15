Gala neural segmentation and agglomeration tool

docker build . -t i2g:gala

docker run i2g:gala python3 ./bin/gala-train -I --seed-cc-threshold 5 -o ./train-sample --experiment-name agglom ./example/prediction_precomputed.h5 ./example/groundtruth

Better:
docker run i2g:gala python3 ./bin/gala-segment -I --seed-cc-threshold 5 --output-dir ./train-sample --experiment-name agglom --classifier ./example/agglom.classifier_precomputed.h5 ./example/prediction_precomputed.h5

Try
docker run -v $(pwd):/data i2g:gala python3 ./driver.py -m 0 -o /data/trained_classifier.pkl --prob_file ./tests/example-data/train-p1.lzf.h5 --gt_file ./tests/example-data/train-gt.lzf.h5 --ws_file ./tests/example-data/train-ws.lzf.h5

docker run -v $(pwd):/data i2g:gala python3 ./driver.py -m 1 -o /data/annotations.npy --prob_file /data/membrane_output.npy --train_file /data/trained_classifier.pkl --seeds_cc_threshold 5 --agg_threshold 0.5

Now Try
docker run -v $(pwd):/data i2g:gala python3 ./driver.py -m 0 -o /data/trained_classifier.pkl --prob_file ./tests/example-data/train-p1.lzf.h5 --gt_file ./tests/example-data/train-gt.lzf.h5 --ws_file ./tests/example-data/train-ws.lzf.h5
docker run -v $(pwd):/data i2g:gala python3 ./driver.py -m 1 -o /data/annotations.npy --prob_file /data/membrane_output.npy --train_file /data/trained_classifier.pkl --seeds_cc_threshold 5 --agg_threshold 0.5



