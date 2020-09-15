from sacred import Experiment, Ingredient

from ..common import logging

yolo3 = Ingredient('yolo3')
train = Ingredient('train')
validation = Ingredient('validation')


@yolo3.config
def yolo3_default():
    # Base network name which serves as feature extraction base.
    backbone = 'darknet53'
    # List of convolution layer channels which is going to be appended to the
    # base network feature extractor. If `name` is `None`, this is ignored.
    filters = [512, 256, 128]
    # The anchor setting.
    anchors = [[10, 13, 16, 30, 33, 23], [30, 61, 62, 45, 59, 119], [116, 90, 156, 198, 373, 326]]
    # Strides of feature map.
    strides = [8, 16, 32]
    # Input data shape for evaluation, use 320, 416, 608...
    # Training is with random shapes from (320 to 608).
    data_shape = 416
    # Use synchronize BN across devices.
    syncbn = False
    # Use fixed size(data-shape) throughout the training, which will be faster
    # and require less memory. However, final model will be slightly worse.
    no_random_shape = False
    # Use MXNet AMP for mixed precision training.
    amp = False
    # Whether to enable custom model.
    custom_model = True


@train.config
def train_cfg():
    # Training mini-batch size
    batch_size = 32
    # Training epochs.
    epochs = 200
    # Starting epoch for resuming, default is 0 for new training.
    # You can specify it to 100 for example to start from 100 epoch.
    start_epoch = 0
    # Learning rate.
    lr = 0.001
    # learning rate scheduler mode. options are step, poly and cosine.
    lr_mode = 'step'
    # decay rate of learning rate.
    lr_decay = 0.1
    # interval for periodic learning rate decays.
    lr_decay_period = 0
    # epochs at which learning rate decays.
    lr_decay_epoch = (160, 180)
    # starting warmup learning rate.
    warmup_lr = 0.0
    # number of warmup epochs.
    warmup_epochs = 0
    # SGD momentum.
    momentum = 0.9
    # Weight decay.
    wd = 0.0005
    # Logging mini-batch interval.
    log_interval = 100
    # Random seed to be fixed.
    seed = 233
    # Training images. Use -1 to automatically get the number.
    num_samples = -1
    # whether to remove weight decay on bias, and beta/gamma for batchnorm layers.
    no_wd = False
    # whether to enable mixup.
    mixup = False
    # Disable mixup training if enabled in the last N epochs.
    no_mixup_epochs = 20
    # Use label smoothing.
    label_smooth = False


@validation.config
def valid_cfg():
    # Epoch interval for validation, increase the number
    # will reduce the training time if validation is slow.
    val_interval = 1


ex = Experiment('yolo3_default', ingredients=[logging, train, validation, yolo3])


@ex.config
def default_configs():
    # Training dataset. eg. 'coco', 'voc', 'voc_tiny'
    dataset = 'voc_tiny'
    # Path of the directory where the dataset is located.
    dataset_root = '~/.mxnet/datasets/'
    # Number of data workers, you can use larger number to
    # accelerate data loading, if you CPU and GPUs are powerful.
    num_workers = 4
    # Training with GPUs, you can specify (1,3) for example.
    gpus = (0, 1, 2, 3)
    # Resume from previously saved parameters if not None.
    # For example, you can resume from ./yolo3_xxx_0123.params
    resume = ''
    # Saving parameter prefix.
    save_prefix = ''
    # Saving parameters epoch interval, best model will always be saved.
    save_interval = 10
    # Use MXNet Horovod for distributed training. Must be run with OpenMPI.
    horovod = False
