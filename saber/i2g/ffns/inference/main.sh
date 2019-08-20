
# TODO: auto-infer size
# TODO: Auto-update pbtxt file

mkdir /latest-model
export LATEST=`./get-latest-checkpoint`
cp /model/model.ckpt-$LATEST* /latest-model

python run_inference.py --inference_request="$(cat ./config.pbtxt)" --bounding_box 'start { x:0 y:0 z:0 } size { x:1024 y:1024 z:150 }'
