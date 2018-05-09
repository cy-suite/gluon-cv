# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# coding: utf-8
# pylint: disable= arguments-differ,missing-docstring
"""SENet, implemented in Gluon."""
from __future__ import division

__all__ = ['SENet', 'SEBlock', 'get_senet', 'senet_154']

import os
from mxnet import cpu
from mxnet.gluon import nn
from mxnet.gluon.block import HybridBlock

# Helpers

class SEBlock(HybridBlock):
    r"""SEBlock from `"Aggregated Residual Transformations for Deep Neural Network"
    <http://arxiv.org/abs/1611.05431>`_ paper.

    Parameters
    ----------
    cardinality: int
        Number of groups
    bottleneck_width: int
        Width of bottleneck block
    stride : int
        Stride size.
    downsample : bool, default False
        Whether to downsample the input.
    in_channels : int, default 0
        Number of input channels. Default is 0, to infer from the graph.
    """
    expansion = 2

    def __init__(self, cardinality, bottleneck_width, stride,
                 downsample=False, in_channels=0, use_se=True, **kwargs):
        super(SEBlock, self).__init__(**kwargs)
        group_width = cardinality * bottleneck_width

        self.body = nn.HybridSequential(prefix='')
        self.body.add(nn.Conv2D(group_width//2, kernel_size=1, use_bias=False,
                                in_channels=in_channels))
        self.body.add(nn.BatchNorm())
        self.body.add(nn.Activation('relu'))
        self.body.add(nn.Conv2D(group_width, kernel_size=3, strides=stride, padding=1,
                                use_bias=False))
        self.body.add(nn.BatchNorm())
        self.body.add(nn.Activation('relu'))
        self.body.add(nn.Conv2D(self.expansion*group_width, kernel_size=1, use_bias=False))
        self.body.add(nn.BatchNorm())

        if use_se:
            self.se = nn.HybridSequential(prefix='')
            self.se.add(nn.GlobalAvgPool2D())
            self.se.add(nn.Conv2D(self.expansion*group_width//16, kernel_size=1, use_bias=False))
            self.se.add(nn.Activation('relu'))
            self.se.add(nn.Conv2D(self.expansion*group_width, kernel_size=1, use_bias=False))
            self.se.add(nn.Activation('sigmoid'))
        else:
            self.se = None

        if downsample:
            self.downsample = nn.HybridSequential(prefix='')
            self.downsample.add(nn.Conv2D(self.expansion*group_width, kernel_size=3, strides=stride,
                                          use_bias=False, in_channels=in_channels))
            self.downsample.add(nn.BatchNorm())
        else:
            self.downsample = None

    def hybrid_forward(self, F, x):
        residual = x

        x = self.body(x)

        if self.se:
            w = self.se(x)
            x = F.broadcast_mul(x, w)

        if self.downsample:
            residual = self.downsample(residual)

        x = F.Activation(x + residual, act_type='relu')
        return x


# Nets
class SENet(HybridBlock):
    r"""ResNext model from
    `"Aggregated Residual Transformations for Deep Neural Network"
    <http://arxiv.org/abs/1611.05431>`_ paper.

    Parameters
    ----------
    layers : list of int
        Numbers of layers in each block
    cardinality: int
        Number of groups
    bottleneck_width: int
        Width of bottleneck block
    classes : int, default 1000
        Number of classification classes.
    """
    def __init__(self, layers, cardinality, bottleneck_width,
                 classes=1000, use_se=False, **kwargs):
        super(SENet, self).__init__(**kwargs)
        self.cardinality = cardinality
        self.bottleneck_width = bottleneck_width
        self.in_channels = 64

        with self.name_scope():
            self.features = nn.HybridSequential(prefix='')
            for i in range(3):
                self.features.add(nn.Conv2D(64, 3, 2, 3, use_bias=False))
            self.features.add(nn.BatchNorm())
            self.features.add(nn.Activation('relu'))
            self.features.add(nn.MaxPool2D(3, 2, 1))

            for i, num_layer in enumerate(layers):
                stride = 1 if i == 0 else 2
                self.features.add(self._make_layer(num_layer, stride, use_se, i+1))
            self.features.add(nn.AvgPool2D(7))
            self.features.add(nn.Dropout(0.2))

            total_expansion = SEBlock.expansion ** len(layers)
            self.output = nn.Dense(classes,
                                   in_units=cardinality*bottleneck_width*total_expansion)

    def _make_layer(self, num_layers, stride, use_se, stage_index):
        layer = nn.HybridSequential(prefix='stage%d_'%stage_index)
        channels = SEBlock.expansion * self.cardinality * self.bottleneck_width
        downsample = self.in_channels != channels
        with layer.name_scope():
            layer.add(SEBlock(self.cardinality, self.bottleneck_width,
                              stride, downsample or stride != 1,
                              in_channels=self.in_channels, use_se=use_se, prefix=''))
            for _ in range(num_layers-1):
                layer.add(SEBlock(self.cardinality, self.bottleneck_width, 1, False,
                                  in_channels=channels, use_se=use_se, prefix=''))

        self.in_channels = channels
        self.bottleneck_width *= 2
        return layer

    # pylint: disable=unused-argument
    def hybrid_forward(self, F, x):
        x = self.features(x)
        x = self.output(x)

        return x


# Specification
resnext_spec = {50: [3, 4, 6, 3],
                101: [3, 4, 23, 3],
                152: [3, 8, 36, 3]}


# Constructor
def get_senet(num_layers, cardinality=64, bottleneck_width=4,
              pretrained=False, ctx=cpu(),
              root=os.path.join('~', '.mxnet', 'models'), **kwargs):
    r"""ResNext model from `"Aggregated Residual Transformations for Deep Neural Network"
    <http://arxiv.org/abs/1611.05431>`_ paper.

    Parameters
    ----------
    num_layers : int
        Numbers of layers. Options are 50, 101.
    cardinality: int
        Number of groups
    bottleneck_width: int
        Width of bottleneck block
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    ctx : Context, default CPU
        The context in which to load the pretrained weights.
    root : str, default '~/.mxnet/models'
        Location for keeping the model parameters.
    """
    assert num_layers in resnext_spec, \
        "Invalid number of layers: %d. Options are %s"%(
            num_layers, str(resnext_spec.keys()))
    layers = resnext_spec[num_layers]
    net = SENet(layers, cardinality, bottleneck_width, **kwargs)
    if pretrained:
        from ..model_store import get_model_file
        net.load_params(get_model_file('resnext%d_%dx%d'%(num_layers, cardinality,
                                                          bottleneck_width),
                                       root=root), ctx=ctx)
    return net

def senet_154(**kwargs):
    r"""ResNext50 32x4d model from
    `"Aggregated Residual Transformations for Deep Neural Network"
    <http://arxiv.org/abs/1611.05431>`_ paper.

    Parameters
    ----------
    cardinality: int
        Number of groups
    bottleneck_width: int
        Width of bottleneck block
    pretrained : bool, default False
        Whether to load the pretrained weights for model.
    ctx : Context, default CPU
        The context in which to load the pretrained weights.
    root : str, default '~/.mxnet/models'
        Location for keeping the model parameters.
    """
    return get_senet(152, **kwargs)
