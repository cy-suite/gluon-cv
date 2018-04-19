Vision Model Zoo
================

The GluonVision Model Zoo,
similar to its upstream `Gluon Model Zoo
<https://mxnet.incubator.apache.org/api/python/gluon/model_zoo.html>`_,
provides pre-defined and pre-trained models to help bootstrap computer vision related applications.

Model Zoo API
-------------

.. code-block:: python

    from gluonvision import model_zoo
    cifar_resnet20 = model_zoo.get_model('cifar_resnet20_v1', pretrained=True)
    # a fully pretrained ssd model
    ssd0 = model_zoo.get_model('ssd_300_vgg16_atrous_voc', pretrained=True)
    # load ssd model with pretrained feature extractors
    ssd1 = model_zoo.get_model('ssd_512_vgg16_atrous_voc', pretrained_base=True)
    # load ssd from scratch
    ssd2 = model_zoo.get_model('ssd_512_resnet50_v1_voc', pretrained_base=False)

We recommend using `model_zoo.get_model` for loading pre-defined models, because it provides
name check and suggest you what models are available now.

However, you can still load models by directly instantiate it like

.. code-block:: python

    from gluonvision import model_zoo
    cifar_resnet20 = model_zoo.cifar_resnet20_v1(pretrained=True)


Available models
----------------

We are still in early development stage, more models will be made available for download.

Image Classification
~~~~~~~~~~~~~~~~~~~~

The following table summarizes the available models and there performances in additional to
`Gluon Model Zoo
<https://mxnet.incubator.apache.org/api/python/gluon/model_zoo.html>`_.

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

Object Detection
~~~~~~~~~~~~~~~~

The following table summarizes the available models and there performances for object detection.

+-------------------------------------+----------+---------+-------+
| Model                               | Dataset  | Input   | Perf  |
+=====================================+==========+=========+=======+
| ssd_300_vgg16_atrous_voc [Liu16]_   | VOC07+12 | 300x300 | 77.6  |
+-------------------------------------+----------+---------+-------+
| ssd_512_vgg16_atrous_voc [Liu16]_   | VOC07+12 | 512x512 |       |
+-------------------------------------+----------+---------+-------+
| ssd_512_resnet50_v1_voc [Liu16]_    | VOC07+12 | 512x512 | 80.1  |
+-------------------------------------+----------+---------+-------+

.. [Liu16] Wei Liu, Dragomir Anguelov, Dumitru Erhan,
       Christian Szegedy, Scott Reed, Cheng-Yang Fu, Alexander C. Berg.
       SSD: Single Shot MultiBox Detector. ECCV 2016.


Semantic Segmentation
~~~~~~~~~~~~~~~~~~~~~

Table of pre-trained models, performances and the training commands:

.. comment (models :math:`^\ast` denotes pre-trained on COCO):

.. role:: raw-html(raw)
   :format: html

+-------------------+--------------+------------+-----------+-----------+-----------+----------------------------------------------------------------------------------------------+
| Name              | Method       | Backbone   | Dataset   | Note      | mIoU      | Command                                                                                      |
+===================+==============+============+===========+===========+===========+==============================================================================================+
| fcn_resnet50_voc  | FCN [Long15]_| ResNet50   | PASCAL12  | stride 8  | 69.4_     | :raw-html:`<a href="javascript:toggleblock('cmd_fcn_50')" class="toggleblock">cmd</a>`       |
+-------------------+--------------+------------+-----------+-----------+-----------+----------------------------------------------------------------------------------------------+
| fcn_resnet101_voc | FCN [Long15]_| ResNet101  | PASCAL12  | stride 8  | 70.9_     | :raw-html:`<a href="javascript:toggleblock('cmd_fcn_101')" class="toggleblock">cmd</a>`      |
+-------------------+--------------+------------+-----------+-----------+-----------+----------------------------------------------------------------------------------------------+

.. _69.4:  http://host.robots.ox.ac.uk:8080/anonymous/TC12D2.html
.. _70.9:  http://host.robots.ox.ac.uk:8080/anonymous/FTIQXJ.html

.. raw:: html

    <code xml:space="preserve" id="cmd_fcn_50" style="display: none; text-align: left; white-space: pre-wrap">
    # First training on augmented set
    CUDA_VISIBLE_DEVICES=0,1,2,3 python train.py --dataset pascal_aug --model fcn --backbone resnet50 --lr 0.001 --syncbn --checkname mycheckpoint
    # Finetuning on original set
    CUDA_VISIBLE_DEVICES=0,1,2,3 python train.py --dataset pascal_voc --model fcn --backbone resnet50 --lr 0.0001 --syncbn --checkname mycheckpoint --resume runs/pascal_aug/fcn/mycheckpoint/checkpoint.params
    </code>

    <code xml:space="preserve" id="cmd_fcn_101" style="display: none; text-align: left; white-space: pre-wrap">
    # First training on augmented set
    CUDA_VISIBLE_DEVICES=0,1,2,3 python train.py --dataset pascal_aug --model fcn --backbone resnet101 --lr 0.001 --syncbn --checkname mycheckpoint
    # Finetuning on original set
    CUDA_VISIBLE_DEVICES=0,1,2,3 python train.py --dataset pascal_voc --model fcn --backbone resnet101 --lr 0.0001 --syncbn --checkname mycheckpoint --resume runs/pascal_aug/fcn/mycheckpoint/checkpoint.params
    </code>

.. [Long15] Long, Jonathan, Evan Shelhamer, and Trevor Darrell. \
    "Fully convolutional networks for semantic segmentation." \
    Proceedings of the IEEE conference on computer vision and pattern recognition. 2015.
