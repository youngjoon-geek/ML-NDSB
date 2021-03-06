import find_mxnet
import mxnet as mx
import logging
import argparse
import train_model
import time

# don't use -n and -s, which are resevered for the distributed training
parser = argparse.ArgumentParser(description='train an image classifer on Kaggle Data Science Bowl 1')
parser.add_argument('--network', type=str, default='dsb',
                    help = 'the cnn to use')
parser.add_argument('--data-dir', type=str, default="data48/",
                    help='the input data directory')
parser.add_argument('--model-prefix', type=str,default= "./models/sample_net",
                    help='the prefix of the model to load/save')
parser.add_argument('--lr', type=float, default=.01,
                    help='the initial learning rate')
parser.add_argument('--lr-factor', type=float, default=1,
                    help='times the lr with a factor for every lr-factor-epoch epoch')
parser.add_argument('--lr-factor-epoch', type=float, default=15,
                    help='the number of epoch to factor the lr, could be .5')
parser.add_argument('--clip-gradient', type=float, default=5.,
                    help='clip min/max gradient to prevent extreme value')
parser.add_argument('--num-epochs', type=int, default=100,
                    help='the number of training epochs')
parser.add_argument('--load-epoch', type=int,
                    help="load the model on an epoch using the model-prefix")
parser.add_argument('--batch-size', type=int, default=64,
                    help='the batch size')
parser.add_argument('--gpus', type=str, default='0',
                    help='the gpus will be used, e.g "0,1,2,3"')
parser.add_argument('--kv-store', type=str, default='local',
                    help='the kvstore type')
parser.add_argument('--num-examples', type=int, default=20000,
                    help='the number of training examples')
parser.add_argument('--num-classes', type=int, default=121,
                    help='the number of classes')
parser.add_argument('--log-file', type=str,
		    help='the name of log file')
parser.add_argument('--log-dir', type=str, default="/tmp/",
                    help='directory of the log file')
args = parser.parse_args()

args.save_model_prefix = args.model_prefix

# network
import importlib
net = importlib.import_module('symbol_' + args.network).get_symbol(args.num_classes)


# data
def get_iterator(args, kv):
    data_shape = (3, 36, 36)

    # train data iterator
    train = mx.io.ImageRecordIter(
        path_imgrec = args.data_dir + "tr.rec",
        mean_r      = 128,
        mean_g      = 128,
        mean_b      = 128,
        scale       = 0.0078125,
        max_aspect_ratio = 0.35,
        data_shape  = data_shape,
        batch_size  = args.batch_size,
        rand_crop   = True,
        rand_mirror = True,
    )

    # validate data iterator
    val = mx.io.ImageRecordIter(
        path_imgrec = args.data_dir + "va.rec",
        mean_r      = 128,
        mean_b      = 128,
        mean_g      = 128,
        scale       = 0.0078125,
        rand_crop   = False,
        rand_mirror = False,
        data_shape  = data_shape,
        batch_size  = args.batch_size)

    return (train, val)

# train
tic=time.time()
train_model.fit(args, net, get_iterator)
print "time elapsed to train model", time.time()-tic