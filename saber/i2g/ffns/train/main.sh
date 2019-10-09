echo "Computing partitions... (Go get a coffee.)"

python ./compute_partitions.py --input_volume /data/seg.h5:seg --output_volume /data/af.h5:af --thresholds 0.025,0.05,0.075,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9 --lom_radius 24,24,24 --min_size 10000

echo "Building coordinates file... (Go get lunch.)"
# Takes a very long time:
python build_coordinates.py --partition_volumes val:/data/af.h5:af --coordinate_output /data/tf_record_file --margin 24,24,24

echo "Training. (Go get a life!)"
python train.py --train_coords /data/tf_record_file --data_volumes val:/data/raw.h5:raw --label_volumes val:/data/seg.h5:seg --model_name convstack_3d.ConvStack3DFFNModel --model_args "{\"depth\": 12, \"fov_size\": [33, 33, 33], \"deltas\": [8, 8, 8]}" --image_mean 128 --image_stddev 33 --train_dir '/model' --max_steps 4000000
