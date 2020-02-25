"""
Copyright 2018 The Johns Hopkins University Applied Physics Laboratory.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
import time
import numpy as np
import argparse 

import image_handler as ih

from cnn_tools import *
from data_tools import *

K.set_image_data_format('channels_first') #replaces K.set_image_dim_ordering('th')


if __name__ == '__main__':
    # -------------------------------------------------------------------------

    parser = argparse.ArgumentParser(description='Deploying Unets for Probability Mapping')
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument(
            '--img_file',
            required=True,
            help='Local image file'
            )
    parser.add_argument(
            '--lbl_file',
            required=False,
            help='Groundtruth image file'
            )
    parser.add_argument(
            '--weights_file',
            required=True,
            help='Weights file to deploy'
            )
    parser.add_argument(
            '--tile_size',
            required=False,
            type=int,
            default=256,
            help='Size of image chunks processed by network'
            )
    parser.add_argument(
            '--output',
            required=True,
            help='Inference output file (npy)'
            )
    
    args = parser.parse_args()
    y_data = np.load(args.img_file) # X, Y, Z
    y_data = np.transpose(y_data) # Z, Y, X
    print('Input data has shape: {}'.format(y_data.shape))
    y_data = y_data[:, np.newaxis, :, :].astype(np.float32) #Z, chan, Y, X
    y_data /= 255.
    tile_size = [args.tile_size, args.tile_size]
    model = create_unet((1, tile_size[0], tile_size[1]))
    model.load_weights(args.weights_file)
    print('Deploying model...')
    y_hat = deploy_model(y_data, model)
    np.save(args.output, y_hat)

    if args.lbl_file:
        y_true = np.load(args.lbl_file) # X, Y, Z
        y_true = np.transpose(y_true)
        print('Groundtruth data has shape: {}'.format(y_true.shape))
        y_true = y_true[:, np.newaxis, :, :].astype(np.float32) #Z, chan, Y, X
        f1 = f1_score(y_true, y_hat)
        print("F1: {}".format(f1))