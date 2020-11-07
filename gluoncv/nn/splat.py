# pylint: disable=arguments-differ,line-too-long,missing-docstring,missing-module-docstring
import mxnet as mx
from mxnet.gluon import nn
from mxnet.gluon.nn import Conv2D, HybridBlock, BatchNorm, Activation
from mxnet import use_np # pylint: disable=unused-import
mx.npx.set_np()

__all__ = ['SplitAttentionConv']


class SplitAttentionConv(HybridBlock):
    # pylint: disable=keyword-arg-before-vararg
    def __init__(self, channels, kernel_size, strides=(1, 1), padding=(0, 0),
                 dilation=(1, 1), groups=1, radix=2, in_channels=None, r=2,
                 norm_layer=BatchNorm, norm_kwargs=None, drop_ratio=0,
                 *args, **kwargs):
        super(SplitAttentionConv, self).__init__()
        norm_kwargs = norm_kwargs if norm_kwargs is not None else {}
        inter_channels = max(in_channels*radix//2//r, 32)
        self.radix = radix
        self.cardinality = groups
        self.conv = Conv2D(channels*radix, kernel_size, strides, padding, dilation,
                           groups=groups*radix, *args, in_channels=in_channels, **kwargs)
        self.use_bn = norm_layer is not None
        if self.use_bn:
            self.bn = norm_layer(in_channels=channels*radix, **norm_kwargs)
        self.relu = Activation('relu')
        self.fc1 = Conv2D(inter_channels, 1, in_channels=channels, groups=self.cardinality)
        if self.use_bn:
            self.bn1 = norm_layer(in_channels=inter_channels, **norm_kwargs)
        self.relu1 = Activation('relu')
        if drop_ratio > 0:
            self.drop = nn.Dropout(drop_ratio)
        else:
            self.drop = None
        self.fc2 = Conv2D(channels*radix, 1, in_channels=inter_channels, groups=self.cardinality)
        self.channels = channels

    def forward(self, x):
        x = self.conv(x)
        if self.use_bn:
            x = self.bn(x)
        x = self.relu(x)
        if self.radix > 1:
            x_expand_dims = mx.np.expand_dims(x, axis=1)
            splited = mx.np.reshape(x_expand_dims,
                                    (x_expand_dims.shape[0], self.radix, self.channels,
                                     x_expand_dims.shape[3], x_expand_dims.shape[4]))
            gap = mx.np.sum(splited, axis=1)
        else:
            gap = x
        gap = mx.nd.contrib.AdaptiveAvgPooling2D(gap.as_nd_ndarray(), 1).as_np_ndarray()
        gap = self.fc1(gap)
        if self.use_bn:
            gap = self.bn1(gap)
        atten = self.relu1(gap)
        if self.drop:
            atten = self.drop(atten)
        atten = self.fc2(atten)
        atten = atten.reshape((atten.shape[0], self.cardinality, self.radix, -1)).swapaxes(1, 2)
        if self.radix > 1:
            atten = mx.npx.softmax(atten, axis=1)
            atten = atten.reshape((atten.shape[0], self.radix, -1, 1, 1))
        else:
            atten = mx.npx.sigmoid(atten).reshape((0, -1, 1, 1))
        if self.radix > 1:
            outs = atten * splited
            out = mx.np.sum(outs, axis=1)
        else:
            out = atten * x
        return out
