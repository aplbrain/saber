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
import json
import argparse 

np.random.seed(9999)

import image_handler as ih

from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *

from cnn_tools import *
from data_tools import *

K.set_image_data_format('channels_first') #replaces K.set_image_dim_ordering('th')



class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def parse_args(json_file=None):
    args = defaults

    if json_file:
        with open(json_file, 'r') as f:
            json_args = json.load(f)
        args.update(json_args)

    return Namespace(**args)


def get_boss_data(args):

    config = {"protocol": "https",
              "host": "api.bossdb.org",
              "token": args.token}
    rmt = BossRemote(config)
    print('[info] Downloading data from BOSS')
    chan = ChannelResource(args.chan_img,
                           args.coll,
                           args.exp,
                           'image',
                           datatype=args.dtype_img)

    # Get the image data from the BOSS
    x_train = rmt.get_cutout(chan, args.res,
                             [args.xmin,args.xmax],
                             [args.ymin,args.ymax],
                             [args.zmin,args.zmax])

    lchan = ChannelResource(args.chan_labels,
                            args.coll,
                            args.exp,
                            'annotation',
                            datatype=args.dtype_lbl)

    y_train = rmt.get_cutout(lchan, args.res,
                             [args.xmin,args.xmax],
                             [args.ymin,args.ymax],
                             [args.zmin,args.zmax])
    print('[info] Downloaded BOSS data')
    # Data must be [slices, chan, row, col] (i.e., [Z, chan, Y, X])
    x_train = x_train[:, np.newaxis, :, :].astype(np.float32)
    y_train = y_train[:, np.newaxis, :, :].astype(np.float32)

    # Pixel values must be in [0,1]
    x_train /= 255.
    y_train = (y_train > 0).astype('float32')

    return x_train, y_train


def get_file_data(args):

    file_type = args.img_file.split('.')[-1]
    if file_type == 'gz' or file_type == 'nii':
        x_train = ih.load_nii(args.img_file, data_type='uint8')
        y_train = ih.load_nii(args.lbl_file, data_type='uint8')

    elif file_type == 'npz':
        x_train = np.load(args.img_file)
        y_train = np.load(args.lbl_file)

    # Data must be [slices, chan, row, col] (i.e., [Z, chan, Y, X])
    x_train = x_train[:, np.newaxis, :, :].astype(np.float32)
    y_train = y_train[:, np.newaxis, :, :].astype(np.float32)

    # Pixel values must be in [0,1]
    x_train /= 255.
    y_train = (y_train > 0).astype('float32')

    return x_train, y_train


if __name__ == '__main__':
    # -------------------------------------------------------------------------

    parser = argparse.ArgumentParser(description='Training Unets for Probability Mapping')
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument(
            '--use_boss',
            type=int,
            required=True,
            help='False(0) to use img_file and lbl_file or True(1) to pull data from boss')
    parser.add_argument(
            '--img_file',
            required=False,
            help='Local image file'
            )
    parser.add_argument(
            '--lbl_file',
            required=False,
            help='Local label file'
            )
    parser.add_argument(
            '--coord',
            required=False,
            help='Coord frame for BOSS'
            )
    parser.add_argument(
            '--token',
            required=False,
            help='Token for BOSS'
            )
    parser.add_argument(
            '--coll',
            required=False,
            help='Collection Name for BOSS'
            )
    parser.add_argument(
            '--exp',
            required=False,
            help='Experiment Name for BOSS'
            )
    parser.add_argument(
            '--chan_labels',
            required=False,
            help='Label channel for BOSS'
            )
    parser.add_argument(
            '--chan_img',
            required=False,
            help='Raw img channel for BOSS'
            )
    parser.add_argument(
            '--dtype_img',
            required=False,
            help='Datatype for BOSS'
            )
    parser.add_argument(
            '--dtype_lbl',
            required=False,
            help='Datatype for BOSS annotation'
            )
    parser.add_argument(
            '--res',
            type=int,
            required=False,
            help='resolution for BOSS'
            )
    parser.add_argument(
            '--xmin',
            type=int,
            required=False,
            help='Xmin of range for BOSS'
            )
    parser.add_argument(
            '--xmax',
            type=int,
            required=False,
            help='Xmax of range for BOSS'
            )
    parser.add_argument(
            '--ymin',
            type=int,
            required=False,
            help='Ymin of range for BOSS'
            )
    parser.add_argument(
            '--ymax',
            type=int,
            required=False,
            help='Ymax of range for BOSS'
            )
    parser.add_argument(
            '--zmin',
            type=int,
            required=False,
            help='Zmin of range for BOSS'
            )
    parser.add_argument(
            '--zmax',
            type=int,
            required=False,
            help='Zmax of range for BOSS'
            )
    parser.add_argument(
            '--train_pct',
            required=False,
            type=float,
            default=0.5,
            help='Percentage of z slices to use as training'
            )
    parser.add_argument(
            '--n_epochs',
            required=False,
            type=int,
            default=10,
            help='Number of training epochs'
            )
    parser.add_argument(
            '--mb_size',
            required=False,
            type=int,
            default=4,
            help='Minibatch size'
            )
    parser.add_argument(
            '--n_mb_per_epoch',
            required=False,
            type=int,
            default=3,
            help='num mb per epoch'
            )
    parser.add_argument(
            '--learning_rate',
            required=False,
            type=float,
            default=0.0001,
            help='Adam or SGD learning rate for training'
            )
    parser.add_argument(
            '--use_adam',
            required=False,
            type=bool,
            default=False,
            help='Flag to use adam or sgd'
            )
    parser.add_argument(
            '--beta1',
            required=False,
            type=float,
            default=0.9,
            help='Adam first moment forgetting factor'
            )
    parser.add_argument(
            '--beta2',
            required=False,
            type=float,
            default=0.999,
            help='Adam second moment forgetting factor'
            )
    parser.add_argument(
            '--momentum',
            required=False,
            type=float,
            default=0.99,
            help='SGD momemntum value'
            )
    parser.add_argument(
            '--decay',
            required=False,
            type=float,
            default=0.000001,
            help='SGD decay value'
            )
    parser.add_argument(
            '--save_freq',
            required=False,
            type=int,
            default=50,
            help='How often to save'
            )
    parser.add_argument(
            '--do_warp',
            required=False,
            type=bool,
            default=False,
            help='Warp data?'
            )
    parser.add_argument(
            '--tile_size',
            required=False,
            type=int,
            default=256,
            help='Size of image chunks processed by network'
            )
    parser.add_argument(
            '--weights_file',
            required=False,
            help='Weights file to continue training'
            )
    parser.add_argument(
            '--score_out',
            required=True,
            help='File for output of final score'
    )
    parser.add_argument(
            '--output',
            required=True,
            help='Weights output file (hdf5)'
            )

    args = parser.parse_args()
    if args.use_boss:
        x_train, y_train = get_boss_data(args)
    else:
        x_train, y_train = get_file_data(args)

    tile_size = (args.tile_size,args.tile_size)
    train_pct = args.train_pct
    # -------------------------------------------------------------------------

    # Data must be [slices, chan, row, col] (i.e., [Z, chan, Y, X])
    # split into train and valid
    train_slices = range(int(train_pct * x_train.shape[0]))
    x_train = x_train[train_slices, ...]
    y_train = y_train[train_slices, ...]

    valid_slices = range(int(train_pct * x_train.shape[0]), x_train.shape[0])
    x_valid = x_train[valid_slices, ...]
    y_valid = y_train[valid_slices, ...]

    print('[info]: training data has shape:     %s' % str(x_train.shape))
    print('[info]: training labels has shape:   %s' % str(y_train.shape))
    print('[info]: validation data has shape:   %s' % str(x_valid.shape))
    print('[info]: validation labels has shape: %s' % str(y_valid.shape))
    print('[info]: tile size:                   %s' % str(tile_size))

    # train model
    tic = time.time()
    model = create_unet((1, tile_size[0], tile_size[1]))
    #if args.do_synapse:
    if args.use_adam:
        print('[info]: using adam optimizer')
        model.compile(optimizer=Adam(lr=args.learning_rate,beta_1=args.beta1,beta_2=args.beta2),
                        loss=pixelwise_crossentropy_loss_w,
                        metrics=[f1_score])
    else:
        print('[info]: using sgd optimizer')
        model.compile(optimizer=SGD(lr=args.learning_rate,decay=args.decay,momentum=args.momentum),
                        loss=pixelwise_crossentropy_loss_w,
                        metrics=[f1_score])
    #else:
    #    model.compile(optimizer=Adam(lr=args.learning_rate,beta_1=args.beta1,beta_2=args.beta2),
    #                  loss=pixelwise_crossentropy_loss,
    #                  metrics=[f1_score])

    if args.weights_file:
        if args.weights_file != "None":
            model.load_weights(args.weights_file)

    f1=train_model(x_train, y_train, x_valid, y_valid, model,
                args.output, do_augment=args.do_warp,
                n_epochs=args.n_epochs, mb_size=args.mb_size,
                n_mb_per_epoch=args.n_mb_per_epoch,
                save_freq=args.save_freq,args=args)

    print('[info]: total time to train model: %0.2f min' %
          ((time.time() - tic) / 60.))
    print("F1: {}".format(f1))
