# Copyright 2019 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cnn_tools import *
from data_tools import *

from keras import backend as K
from keras.models import load_model

import os
import sys
import time
import numpy as np
import json
import argparse

np.random.seed(9999)

K.set_image_data_format('channels_first') #replaces K.set_image_dim_ordering('th')


def get_parser():
    parser = argparse.ArgumentParser(description='EM processing script')
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument(
            '-i',
            '--input',
            required=True,
            help='Input file')
    parser.add_argument(
            '-o',
            '--output',
            required=True,
            help='Output file')
    parser.add_argument(
            '-x',
            '--width',
            default=256,
            required=False,
            help='Image width')
    parser.add_argument(
            '-y',
            '--height',
            default=256,
            required=False,
            help='Image height')
    parser.add_argument('--z_step', dest='z_step', type=int, default=1,
                        help='Amount to step in Z when performing inference')
    parser.add_argument('--mode', dest='mode', type=str,
                        default='membrane',
                        help='Flag to toggle between mem/syn prediction')
    return parser

if __name__ == '__main__':
    # ----------------------------------------------------------------------
    parser = get_parser()
    args = parser.parse_args()

    x_test = np.load(args.input)
    # Data currently X,Y,Z
    x_test = np.transpose(x_test, (2, 1, 0))
    x_test = x_test[:, np.newaxis, :, :]

    # Data must be [slices, chan, row, col] (i.e. [Z, chan, Y, X])
    x_test = x_test.astype(np.float32)
    print('Input size {}'.format(x_test.shape))
    # Pixel values must be in [0,1]
    if x_test.max() > 1.0:
        x_test /= 255.

    tile_size = (args.width, args.height)
    z_step = args.z_step
    # ----------------------------------------------------------------------

    # Load model
    model = create_unet((1, int(args.width), int(args.height)))
    if args.mode == 'synapse':
        model.load_weights('/src/weights/synapse_weights.hdf5')
    elif args.mode == 'membrane':
        model.load_weights('/src/weights/membrane_weights.hdf5')
    else:
        print('invalid mode; please choose "synapse" or "membrane"')
    tic0 = time.time()
    tic = time.time()
    y_hat = np.zeros(x_test.shape)
    for i in range(0, x_test.shape[0], z_step):
        y_hat[i:i+z_step, ...] = deploy_model(x_test[i:i+z_step, ...], model)

    print('[info]: total time to deploy: {:0.2f} sec'.format(time.time() - tic))
    print('Total time to process entire volume: {}'.format(time.time() - tic0))

    # ----------------------------------------------------------------------
    print(y_hat.shape)
    y_hat = np.squeeze(np.transpose(y_hat, (3, 2, 0, 1)))
    y_hat = np.floor(y_hat*255)
    print(args.output)
    with open(args.output, 'wb') as f:
        np.save(f, y_hat)

