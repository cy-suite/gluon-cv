"""Training Your First Classification Model on CIFAR10
===================================================

```CIFAR10`` <https://www.cs.toronto.edu/~kriz/cifar.html>`__ is a
labeled dataset of tiny (32x32) images, collected by Alex Krizhevsky,
Vinod Nair, and Geoffrey Hinton. It is widely used as a benchmark in
computer vision research.

|image-cifar10|

In this tutorial, we will demonstrate how to use ``Gluon`` to train a
model from scratch and reproduce the performance from papers.
Specifically, we offer a script to prepare the ``CIFAR10`` dataset and
train a ``ResNet`` model at
`scripts/classification/cifar/train.py <https://github.com/dmlc/gluon-vision/blob/master/scripts/classification/cifar/train.py>`__.

In the following content, we will demonstrate how to

-  How well can our model predict
-  train a model
-  plot the training history

Demo and Benchmark
------------------

Before busying with training and parameter tuning, you may want to get
an idea of what the result may look like.

Here we provide you a script,
```demo.py`` <https://github.com/hetong007/gluon-vision/blob/master/scripts/classification/cifar/demo.py>`__,
to load a pre-trained model from us and predict on any image on your
disk.

This is an airplane:

|image0|

Right click and save the image, we can then make prediction by

::

    python demo.py --model cifar_resnet110_v2 --input-pic plane.jpg

And the model thinks that

::

    The input picture is classified to be [airplane], with probability 0.517.

Feel free to feed in your own image to see how well it does the job.
Keep in mind that ``CIFAR10`` is relatively small and has only 10
classes. Models trained on ``CIFAR10`` only recognize objects from those
10 classes, therefore it may surprise you if we feed one image to the model which doesn't belong to any of the 10 classes

|image1|

::

    python demo.py --model cifar_resnet110_v2 --input-pic mt_baker.jpg

The result is:

::

    The input picture is classified to be [airplane], with probability 0.857.

To experience a more real world friendly demo, please checkout models
trained on `ImageNet <>`__.

Train Your First Model
----------------------

In the demo, we have used a pretrained model. So how did we train it?

We trained the models with
```train.py`` <https://github.com/hetong007/gluon-vision/blob/master/scripts/classification/cifar/train.py>`__.
It takes a bunch of parameters to control the model training process. To
start, you can try the following command:

::

    python train.py --num-epochs 240 --mode hybrid --num-gpus 1 -j 8 --batch-size 128\
        --wd 0.0001 --lr 0.1 --lr-decay 0.1 --lr-decay-epoch 80,160 --model cifar_resnet20_v1

This command trains a ``ResNet20_V2`` model for 240 epochs on one GPU.
The batch size is 128. We decay the learning rate by a factor of 10 at the 80-th and 160-th epoch.
The script prints information for each epoch so that we can have a sense
of the progress and watchout for any unexpected issues.

::

    INFO:root:[Epoch 0] train=0.367448 val=0.460800 loss=1.735358 time: 12.739688
    INFO:root:[Epoch 1] train=0.492027 val=0.524600 loss=1.409553 time: 12.500988
    INFO:root:[Epoch 2] train=0.556891 val=0.640400 loss=1.241357 time: 12.994388
    INFO:root:[Epoch 3] train=0.595152 val=0.658900 loss=1.145049 time: 12.342926
    INFO:root:[Epoch 4] train=0.620733 val=0.680900 loss=1.075090 time: 13.098537
    INFO:root:[Epoch 5] train=0.640966 val=0.700200 loss=1.017329 time: 12.360461
    ...

The dataset and the model are relatively small, thus it won’t take you
too long to train the model. If you don't have a GPU yet, you can still try to
train with your CPU with MKLDNN. One can install MXNet with MKLDNN with


::

    pip install --pre mxnet-mkl


After the installation, one can run the following command:

::

    python train.py --num-epochs 240 --mode hybrid --num-gpus 0 -j 1 --batch-size 128\
        --wd 0.0001 --lr 0.1 --lr-decay 0.1 --lr-decay-epoch 80,160 --model cifar_resnet20_v1

Here we change the values of ``--num-gpus`` to 0 and ``-j`` to 1, to only use CPU for training and use one thread
for data loader.

This is a brief comparison of performance on our side :

-  13 seconds with one V100 GPU per epoch, and 8 CPU threads.
-  70 seconds with one 8-thread CPU per epoch, with MKLDNN enabled.

With limited computational power, it is good in practice to firstly test
a few epochs to ensure everything works, then leave it running for a
night, and wake up to see the result :)

After the training, the accuracy is expect to be around 91%. To get a
better accuracy, we can train a ``ResNet110_V2`` model instead by
``--model cifar_resnet110_v2``, at the cost of around 4 times of the
training time. With ``ResNet110_V2``, we expect the accuracy to be
around 94%.

Don’t Overfit
-------------

The training of a deep learning model is usually a trial-and-error
process. A good way to review the result is to have a plot:

This is a plot generated from the following command:

|image2|

We see that the training error is much lower than validation error.
This is a clear message of overfitting.  Actually this is the plot for
a training process without data augmentation.

By adding data augmentation back, we can expect the following plot:

|image3|

and observe that training and validation errors share the same trend,
while training error is a little bit higher than the validation error.

Model Zoo
---------

We train various models and store them on cloud as a “zoo of the
models”. Users can pick the model with regards to the accuracy and model
complexity.

Here’s what we have for ``CIFAR10`` so far:

+---------------------------+----------+
| Model                     | Accuracy |
+===========================+==========+
| ``CIFAR_ResNet20_v1``     | 0.9160   |
+---------------------------+----------+
| ``CIFAR_ResNet56_v1``     | 0.9387   |
+---------------------------+----------+
| ``CIFAR_ResNet110_v1``    | 0.9471   |
+---------------------------+----------+
| ``CIFAR_ResNet20_v2``     | 0.9130   |
+---------------------------+----------+
| ``CIFAR_ResNet56_v2``     | 0.9413   |
+---------------------------+----------+
| ``CIFAR_ResNet110_v2``    | 0.9464   |
+---------------------------+----------+
| ``CIFAR_WideResNet16_10`` | 0.9614   |
+---------------------------+----------+
| ``CIFAR_WideResNet28_10`` | 0.9667   |
+---------------------------+----------+
| ``CIFAR_WideResNet40_8``  | 0.9673   |
+---------------------------+----------+

Most of them are more accurate than the claims in the original papers.
The reason is that we incorporate a technique called
```Mix-Up`` <https://arxiv.org/abs/1710.09412>`__ to improve the
performance without changing the network structure.

Specifically, we train the ``cifar_resnet`` models with:

::

    python train_mixup.py --num-epochs 450 --mode hybrid --num-gpus 2 -j 32\
        --batch-size 64 --wd 0.0001 --lr 0.1 --lr-decay 0.1 --lr-decay-epoch 150,250\
        --model cifar_resnet20_v1

and the ``cifar_wideresnet`` models with:

::

    python train_mixup.py --num-epochs 500 --mode hybrid --num-gpus 2 -j 32\
        --batch-size 64 --wd 0.0001 --lr 0.1 --lr-decay 0.1 --lr-decay-epoch 100,200,300\
        --model cifar_wideresnet16_10

Next Step
---------

Congratulations! You’ve just finished reading our first tutorial. We
have a lot more others to help you learn more and get familiar with
``gluonvision``.

If you would like to dig deeper in the topic of ``CIFAR10`` training,
feel free to read `the next tutorial on ``CIFAR10`` <>`__.

Or, if you would like to try a more powerful demo, i.e. models trained
on ImageNet, please read `xxx <>`__.

.. |image-cifar10| image:: https://raw.githubusercontent.com/dmlc/web-data/master/gluonvision/classification/cifar10.png
.. |image0| image:: https://raw.githubusercontent.com/dmlc/web-data/master/gluonvision/classification/plane-draw.jpeg
.. |image1| image:: https://raw.githubusercontent.com/dmlc/web-data/master/gluonvision/classification/mt_baker.jpg
.. |image2| image:: https://raw.githubusercontent.com/dmlc/web-data/master/gluonvision/classification/overfitting.png
.. |image3| image:: https://raw.githubusercontent.com/dmlc/web-data/master/gluonvision/classification/normal_training.png

"""
from __future__ import division

import argparse, time, logging, random, math

import numpy as np
import mxnet as mx
import matplotlib.pyplot as plt

from mxnet import gluon, nd, image
from mxnet.gluon.data.vision import transforms

from gluonvision.model_zoo import get_model

parser = argparse.ArgumentParser(description='Predict CIFAR10 classes from a given image')
parser.add_argument('--model', type=str, required=True,
                    help='name of the model to use')
parser.add_argument('--saved-params', type=str, default='',
                    help='path to the saved model parameters')
parser.add_argument('--input-pic', type=str, required=True,
                    help='path to the input picture')
opt = parser.parse_args()

classes = 10
class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']

context = [mx.cpu()]

# Load Model
model_name = opt.model
pretrained = True if opt.saved_params == '' else False
kwargs = {'classes': classes, 'pretrained': pretrained}
net = get_model(model_name, **kwargs)

if not pretrained:
    net.load_params(opt.saved_params, ctx = context)

# Load Images
with open(opt.input_pic, 'rb') as f:
    img = image.imdecode(f.read())

# Transform
transform_fn = transforms.Compose([
    transforms.Resize(32),
    transforms.CenterCrop(32),
    transforms.ToTensor(),
    transforms.Normalize([0.4914, 0.4822, 0.4465], [0.2023, 0.1994, 0.2010])
])

img_transformed = nd.zeros((1, 3, 32, 32))
img_transformed[0,:,:,:] = transform_fn(img)
pred = net(img_transformed)

ind = nd.argmax(pred, axis=1).astype('int')
print('The input picture is classified to be [%s], with probability %.3f.'%
      (class_names[ind.asscalar()], nd.softmax(pred)[0][ind].asscalar()))
