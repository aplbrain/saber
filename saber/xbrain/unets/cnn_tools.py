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

"""
Implements semantic segmentation for convnets using Keras.
"""
__author__ = 'mjp, Nov 2016'
__license__ = 'Apache 2.0'

import os
from keras.models import Model
from keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, Dropout
from keras.layers.merge import concatenate
from keras.optimizers import Adam, SGD
from keras import backend as K

from data_tools import *

import time
from datetime import datetime
import numpy as np
import tensorboard
import tensorflow as tf

from keras.callbacks import TensorBoard

def timed_collection(c, rate=60*2):
    """ Provides status on progress as one iterates through a collection.
    """
    start_time = time.time()
    last_chatter = -rate

    for idx, ci in enumerate(c):
        yield ci
        
        elapsed = time.time() - start_time
        if (elapsed) > last_chatter + rate:
            last_chatter = elapsed
            print('processed %d items in %0.2f minutes' % (idx+1, elapsed/60.))


def f1_score(y_true, y_hat):
    """ 
    """
    y_true_flat = y_true.flatten()
    y_hat_flat = y_hat.flatten()

    try:
        # default is to assume a Keras object
        y_true_flat = K.flatten(y_true)
        y_hat_flat = K.flatten(y_hat)
     
        intersection = K.sum(y_hat_flat * y_true_flat) 
        precision = intersection / K.sum(y_hat_flat)
        recall = intersection / K.sum(y_true_flat)
    except:
        intersection = np.sum(y_hat_flat * y_true_flat)
        precision = intersection / np.sum(y_hat_flat)
        recall = intersection / np.sum(y_true_flat)

    return 2 * precision * recall / (precision + recall)


def pixelwise_crossentropy_loss(y_true, y_hat):
    y_hat += 1e-8   # avoid issues with log
    ce = -y_true * K.log(y_hat) - (1. - y_true) * K.log(1 - y_hat)
    return K.mean(ce)


def pixelwise_crossentropy_loss_w(y_true, y_hat):
    y_hat += 1e-8   # avoid issues with log
    w = K.sum(y_true) / K.prod(K.shape(y_true))
    ce = -(1 - w) * y_true * K.log(y_hat) - w * (1. - y_true) * K.log(1 - y_hat)
    return K.mean(ce)


def pixelwise_crossentropy_loss_mc(y_true, y_hat):
    y_hat += 1e-8   # avoid issues with log
    w = K.sum(K.sum(K.sum(y_true, axis=0), axis=2), axis=3) / K.prod(K.shape(y_true)) / K.shape(y_true)[1]
    ce = -(1 - w) * y_true * K.log(y_hat) - w * (1. - y_true) * K.log(1 - y_hat)
    return K.mean(ce)


def create_unet(sz):
    """
      sz : a tuple specifying the input image size in the form:
           (# channels, # rows, # columns)
      References:
        1. Ronneberger et al. "U-Net: Convolutional Networks for Biomedical
           Image Segmentation." 2015. 
        2. https://github.com/jocicmarko/ultrasound-nerve-segmentation/blob/master/train.py
    """

    assert(len(sz) == 3)
    if not np.all(np.mod(sz[1:], 16) == 0):
        raise ValueError('This network assumes the input image dimensions are multiple of 2^4')

    # NOTES:
    #   o possibly change Deconvolution2D to UpSampling2D
    bm = 'same'

    inputs = Input(sz)
    conv1 = Conv2D(32, (3, 3), activation='relu', padding=bm)(inputs)
    conv1 = Conv2D(32, (3, 3), activation='relu', padding=bm)(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

    conv2 = Conv2D(64, (3, 3), activation='relu', padding=bm)(pool1)
    conv2 = Conv2D(64, (3, 3), activation='relu', padding=bm)(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

    conv3 = Conv2D(128, (3, 3), activation='relu', padding=bm)(pool2)
    conv3 = Conv2D(128, (3, 3), activation='relu', padding=bm)(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

    conv4 = Conv2D(256, (3, 3), activation='relu', padding=bm)(pool3)
    conv4 = Conv2D(256, (3, 3), activation='relu', padding=bm)(conv4)
    conv4 = Dropout(.5)(conv4)   # mjp
    pool4 = MaxPooling2D(pool_size=(2, 2))(conv4)

    conv5 = Conv2D(512, (3, 3), activation='relu', padding=bm)(pool4)
    conv5 = Conv2D(512, (3, 3), activation='relu', padding=bm)(conv5)

    up6 = concatenate([UpSampling2D(size=(2, 2))(conv5), conv4], axis=1)
    conv6 = Conv2D(256, (3, 3), activation='relu', padding=bm)(up6)
    conv6 = Conv2D(256, (3, 3), activation='relu', padding=bm)(conv6)

    up7 = concatenate([UpSampling2D(size=(2, 2))(conv6), conv3], axis=1)
    conv7 = Conv2D(128, (3, 3), activation='relu', padding=bm)(up7)
    conv7 = Conv2D(128, (3, 3), activation='relu', padding=bm)(conv7)

    up8 = concatenate([UpSampling2D(size=(2, 2))(conv7), conv2], axis=1)
    conv8 = Conv2D(64, (3, 3), activation='relu', padding=bm)(up8)
    conv8 = Conv2D(64, (3, 3), activation='relu', padding=bm)(conv8)

    up9 = concatenate([UpSampling2D(size=(2, 2))(conv8), conv1], axis=1)
    conv9 = Conv2D(32, (3, 3), activation='relu', padding=bm)(up9)
    conv9 = Conv2D(32, (3, 3), activation='relu', padding=bm)(conv9)

    conv10 = Conv2D(1, (1, 1), activation='sigmoid')(conv9)

    model = Model(inputs=inputs, outputs=conv10)

    return model


def train_model(X_train, Y_train, X_valid, Y_valid, model, output,
                n_epochs=30, n_mb_per_epoch=25, mb_size=30, save_freq=100,
                do_augment=False,args=None):
    """
    Note: these are not epochs in the usual sense, since we randomly sample
    the data set (vs methodically marching through it)                
    """
    logdir = "logs/scalars/" + datetime.now().strftime("%Y%m%d-%H%M%S")
    sz = model.input_shape[-2:]
    score_all = []
    best_score = 0
    callback = TensorBoard(logdir)
    callback.set_model(model)
    train_names = ['train_loss', 'train_f1']
    for ii in range(n_epochs):
        print('starting "epoch" %d (of %d)' % (ii, n_epochs))

        for jj in timed_collection(range(n_mb_per_epoch)):
            Xi, Yi = random_minibatch(X_train, Y_train, mb_size, sz=sz)
            loss, f1 = model.train_on_batch(Xi, Yi)
            write_log(callback, train_names, (loss,f1), jj)
            score_all.append(f1)


        # evaluate performance on validation data
        Yi_hat = deploy_model(X_valid, model, do_augment)
#        if ii % save_freq == 0:
#            np.savez(os.path.join(output[:-4], 'valid_epoch%04d' % ii),
#                     X=X_valid, Y=Y_valid, Y_hat=Yi_hat, s=score_all)
        
        f1_curr = f1_score(Y_valid,Yi_hat)
        print('f1 on validation data:    %0.3f' % f1_curr)
        print('recent train performance: %0.3f' % np.mean(score_all[-20:]))
        print('y_hat min, max, mean:     %0.2f / %0.2f / %0.2f' % (np.min(Yi_hat),
                                                                   np.max(Yi_hat),
                                                                   np.mean(Yi_hat)))
        if f1_curr > best_score:
            # save state
            fn_out = os.path.join(output)
            print('saving to : ' + fn_out)
            if ii % save_freq == 0:
                model.save_weights(fn_out)
            best_score = f1_curr
            if args:
                np.save(args.score_out,best_score)

        
    return best_score


def deploy_model(X, model, do_augment=False):
    """
    X : a tensor of dimensions (n_examples, n_channels, n_rows, n_cols)
    Note that n_examples will be used as the minibatch size.
    """
    # the only slight complication is that the spatial dimensions of X might
    # not be a multiple of the tile size.
    sz = model.input_shape[-2:]

    Y_hat = np.zeros(X.shape)

    for rr in range(0, X.shape[-2], sz[0]):
        ra = rr if rr+sz[0] < X.shape[-2] else X.shape[-2] - sz[0]
        rb = ra+sz[0]
        for cc in range(0, X.shape[-1], sz[1]):
            ca = cc if cc+sz[1] < X.shape[-1] else X.shape[-1] - sz[-1]
            cb = ca+sz[1]
            if do_augment:
                slices = X[:, :, ra:rb, ca:cb]
                for i in range(slices.shape[0]):
                    s = slices[i, ...]
                    sm1 = apply_symmetry(s, 4)
                    sm2 = apply_symmetry(s, 5)
                    stack = np.concatenate((s, sm1, sm2), axis=0)
                    stack = stack[:, np.newaxis, :, :]
                    new_stack = model.predict(stack) 
                    new_stack[1, ...] = apply_symmetry(new_stack[1, ...], 4)
                    new_stack[2, ...] = apply_symmetry(new_stack[2, ...], 5)
                    Y_hat[i, :, ra:rb, ca:cb] = np.mean(new_stack, axis=0)
            else:
                Y_hat[:, :, ra:rb, ca:cb] = model.predict(
                    X[:, :, ra:rb, ca:cb]
                    )

    return Y_hat

def write_log(callback, names, logs, batch_no):
    for name, value in zip(names, logs):
        summary = tf.Summary()
        summary_value = summary.value.add()
        summary_value.simple_value = value
        summary_value.tag = name
        callback.writer.add_summary(summary, batch_no)
        callback.writer.flush()