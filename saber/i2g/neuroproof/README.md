## Example Commands

Try:

`docker run -v $(pwd):/app aplbrain/neuroproof python3 ./driver.py -m 0 -o my_classifier.xml --pred_file ./test_data/boundary_prediction.h5 --gt_file ./test_data/groundtruth.h5 --ws_file ./test_data/oversegmented_stack_labels.h5`