"""
Unpacks pretrained (feature-extractor) darknet-53 weights into checkpoints. Checkpoint files can then be
loaded into the YOLOv3 model for training with transfer learning

Modified version from original YOLOv3 implementation, replacing absl.flags (not a fan!) with 
argparse for interfacing with command-line arguments

"""



#from absl import app, flags, logging
#from absl.flags import FLAGS
import numpy as np
from yolov3_tf2.models import YoloV3, YoloV3Tiny
from yolov3_tf2.utils import load_darknet_weights
import tensorflow as tf
import argparse
import logging


from sscd_libs.helpers import boolean_string

# ------------------------------------------------------------------------------
# set up a basic, global _logger which will write to the console
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s (%(asctime)s): %(message)s",
    datefmt="%Y-%m-%d  %H:%M:%S",
)
logger = logging.getLogger(__name__)


# # ---------------------------------------------------------------------------------
# # Create logger
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

# # Create STDERR handler
# handler = logging.StreamHandler(sys.stderr)
# # ch.setLevel(logging.DEBUG)

# # Create formatter and add it to the handler
# formatter = logging.Formatter('%(levelname)s (%(asctime)s): %(message)s',
#                               datefmt="%Y-%m-%d %H:%M:%S")
# handler.setFormatter(formatter)

# # Set STDERR handler as the only handler 
# logger.handlers = [handler]



def main():
    
    # parse the command line arguments
    args_parser = argparse.ArgumentParser(
        description='*** Tool to convert downloaded/compressed pretrained weights as checkpoint files***')
    args_parser.add_argument(
        "--weights_file",
        required=True,
        type=str,
        help='path to weights file'
    )
    args_parser.add_argument(
        "--output_file",
        required=True,
        type=str,
        help= "Path to output directory",
    )
    args_parser.add_argument(
        "--tiny",
        required=False,
        type=boolean_string,
        default = False,
        help="yolov3 or yolov3-tiny"
    )
    
    args_parser.add_argument(
        "--num_classes",
        required=False,
        type = int,
        default = 80,
        help="number of classes in the model"
    )

    args = vars(args_parser.parse_args())   
        
    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    if len(physical_devices) > 0:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)

    if args["tiny"]:
        yolo = YoloV3Tiny(classes=args["num_classes"])
    else:
        yolo = YoloV3(classes=args["num_classes"])
    yolo.summary()
    logger.info('model created')

    load_darknet_weights(yolo, args["weights_file"], args["tiny"])
    logger.info('weights loaded')

    img = np.random.random((1, 320, 320, 3)).astype(np.float32)
    output = yolo(img)
    logger.info('sanity check passed')

    yolo.save_weights(args["output_dir"])
    logger.info('weights saved')


if __name__ == '__main__':
    
    main()
