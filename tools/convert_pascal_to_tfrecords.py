""" Convert PASCAL VOC XML-type dataset to TFRecords for Tensorflow object_detection.

Example usage:
    python convert_pascal_to_tfrecords.py \
    --images_dir "./data/scales_data_sample/images/"\
    --annotations_dir "./data/scales_data_sample/annotations/"\
    --image_set_file  "./data/scales_data_sample/image_sets/scales_train.txt"\
    --label_dict_file "./data/scales_data_sample/scales_label_dict.txt"\
    --output_file "./data/scales_data_sample/scales_train.tfrecord"\
    --drop_difficult_images True

-------------------------------------------------------------------
BC: Script put together from hacking a few scripts from gitHub, e.g.:
    (i) https://gist.github.com/iamtodor/787aafbd15b99bf15eaf5bc31271e235
    (ii) https://github.com/datitran/raccoon_dataset/blob/master/generate_tfrecord.py
    (iii) https://github.com/zzh8829/yolov3-tf2/blob/master/tools/voc2012.py
    (iv) https://github.com/tensorflow/models/blob/master/research/object_detection

"""

import argparse
import hashlib
import io
import logging
import os
import sys
import lxml.etree
from PIL import Image
import tensorflow as tf
import tqdm
import six
from pathlib import Path

from typing import List #Dict, , NamedTuple, Set


# ------------------------------------------------------------------------------
# -- Parse the command line arguments
args_parser = argparse.ArgumentParser(description = "Converting PascalVOC xlm annotation files to TFRecords",
                                      formatter_class=argparse.MetavarTypeHelpFormatter
                                      )
args_parser.add_argument(
    "--images_dir",
    required=True,
    type=str,
    help="path to directory containing image files",
)
args_parser.add_argument(
    "--annotations_dir",
    required=True,
    type=str,
    help="path to directory containing annotation files"
)
args_parser.add_argument(
    "--split_image_ids_file",
    required=True,
    type=str,
    help="path to file specifying image IDs on the split to be converted"
)
args_parser.add_argument(
    "--output_file",
    required=True,
    type=str,
    help="path to TFRecord file output"
)
# args_parser.add_argument(
#     "--label_dict_file",
#     required=True,
#     type=str,
#     help="file with dictionary of labels to indices represented by label map "
# )
args_parser.add_argument(
    "--label_names_file",
    required=True,
    type=str,
    help="NAMES file with label names, one per line"
)

args_parser.add_argument(
    "--drop_difficult_ann",
    type=str,
    default=False,
    choices = ["True", "False"],
    help="whether to drop annotations whose bounding boxes were difficult to delineate (default: False)"
)

args = vars(args_parser.parse_args())  # 'vars' converts Namespace containing args to dict
    

# ------------------------------------------------------------------------------
# parse XLM to dictionary
def parse_xml(xml):
    if not len(xml):
        return {xml.tag: xml.text}
    result = {}
    for child in xml:
        child_result = parse_xml(child)
        if child.tag != 'object':
            result[child.tag] = child_result[child.tag]
        else:
            if child.tag not in result:
                result[child.tag] = []
            result[child.tag].append(child_result[child.tag])
    return {xml.tag: result}

# ------------------------------------------------------------------------------
# Functions to convert a value to a type compatible with tf.Example

def int64_feature(
        value: int,
) -> tf.train.Feature:
    
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

# -----------------------
def int64_list_feature(
        value: List[int],
) -> tf.train.Feature:
    
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))

# -----------------------
def bytes_feature(
        value: str,
) -> tf.train.Feature:
    
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

# -----------------------
def bytes_list_feature(
        values: str,
) -> tf.train.Feature:
    """
    Returns a TF-Feature of bytes.
    :param values a string
    :return TF-Feature of bytes
    """
    def norm2bytes(value):
        return value.encode() if isinstance(value, str) and six.PY3 else value

    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[norm2bytes(values)]))

# ------------------------------
def string_bytes_list_feature(
        value: List[str],
) -> tf.train.Feature:

    return tf.train.Feature(bytes_list=tf.train.BytesList(value=value))

# -----------------------
def float_list_feature(
        value: List[float],
) -> tf.train.Feature:

    return tf.train.Feature(float_list=tf.train.FloatList(value=value))




# ------------------------------------------------------------------------------
def build_example(annotation, class_map, conversionArgs):
  
    """Convert XML derived dict to tf.Example proto.

    NOTE: function normalizes the bounding box coordinates provided by the raw data.

    Args:
    annotation: dict holding PASCAL XML fields for a single image (obtained by
      running 'parse_xml')
    class_map: A map from string label names to integers ids.
    conversionArgs: dict holding the convertion's main arguments including:
        - images_dir: Path to folder holding the images.
        - ignore_difficult_images: Whether to skip difficult instances in the
          dataset  (default: False).

    Returns:
    example: The converted tf.Example.

    Raises:
    ValueError: if the image pointed to by data['filename'] is not a valid JPEG
    """
       
    # Read the images as rgb
    img_path = os.path.join(conversionArgs["images_dir"], annotation['filename'])
    img_raw = open(img_path, 'rb').read()
    key = hashlib.sha256(img_raw).hexdigest()
        
    # check if images are encoded as jpegs
    img_raw_io = io.BytesIO(img_raw)
    image = Image.open(img_raw_io)
    if image.format != 'JPEG':
        raise ValueError('Image format not JPEG')
        
    width = int(annotation['size']['width'])
    height = int(annotation['size']['height'])

    xmin = []
    ymin = []
    xmax = []
    ymax = []
    classes = []
    classes_text = []
    truncated = []
    views = []
    difficult_obj = []
    if 'object' in annotation:
        for obj in annotation['object']:
            difficult = bool(int(obj['difficult']))
                                                
            if conversionArgs['drop_difficult_ann']=='True' and difficult:
                continue
               
            difficult_obj.append(int(difficult))
            # normalize the bounding box coordinates to within the range (0, 1)
            xmin.append(float(obj['bndbox']['xmin']) / width)
            ymin.append(float(obj['bndbox']['ymin']) / height)
            xmax.append(float(obj['bndbox']['xmax']) / width)
            ymax.append(float(obj['bndbox']['ymax']) / height)
            classes_text.append(obj['name'].encode('utf8'))
            classes.append(class_map[obj['name']])
            truncated.append(int(obj['truncated']))
            views.append(obj['pose'].encode('utf8'))

    #breakpoint()
    # BC: hack to exclude images without non-difficult bboxes - if option to drop 
    # difficult annotations is activated, images without "easy" annotations must
    # be exluded from the dataset (thus potentially inflating FPs in evaluation phase)
    if len(xmin) == 0:   
        example = None
    else:
        example = tf.train.Example(features=tf.train.Features(feature={
            'image/height': int64_feature(height),
            'image/width': int64_feature(width),
            'image/filename': bytes_list_feature(annotation['filename'].encode('utf8')), #bytes_feature(annotation['filename'].encode('utf8')),
            'image/source_id': bytes_feature(annotation['filename'].encode('utf8')),
            'image/key/sha256': bytes_feature(key.encode('utf8')),
            'image/encoded': bytes_feature(img_raw), #bytes_list_feature(img_raw), 
            'image/format': bytes_list_feature('jpeg'.encode('utf8')), #bytes_feature('jpeg'.encode('utf8')),
            'image/object/bbox/xmin': float_list_feature(xmin),
            'image/object/bbox/xmax': float_list_feature(xmax),
            'image/object/bbox/ymin': float_list_feature(ymin),
            'image/object/bbox/ymax': float_list_feature(ymax),
            'image/object/class/text': string_bytes_list_feature(classes_text),
            'image/object/class/label': int64_list_feature(classes),
            'image/object/difficult': int64_list_feature(difficult_obj),
            'image/object/truncated': int64_list_feature(truncated),
            'image/object/view': string_bytes_list_feature(views),
            }))
        
            
    return example


# ---------------------------------------------------------------------------------
# Create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create STDERR handler
handler = logging.StreamHandler(sys.stderr)
# ch.setLevel(logging.DEBUG)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(levelname)s (%(asctime)s): %(message)s',
                              datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

# Set STDERR handler as the only handler 
logger.handlers = [handler]



# ---------------------------------------------------------------------------------
def main():
        
    # Create parent directory, if 
    out_dir = Path(args['output_file']).parent
    Path(out_dir).mkdir(parents=True, exist_ok=True)
        
    # with open(args['label_dict_file'], 'r') as f: 
    #     content = f.read()
    #     label_map_dict = eval(content)
    # logger.info("Class mapping loaded: %s", label_map_dict)
    
    #breakpoint()
    label_map_dict = {name: idx for idx, name in enumerate(
        open(args['label_names_file']).read().splitlines())}
    logger.info("Class mapping loaded: %s", label_map_dict)

      
    image_list = open(args['split_image_ids_file']).read().splitlines()
    logger.info("Image list loaded: %d", len(image_list))
    
    writer = tf.io.TFRecordWriter(args['output_file'])
    
    exlc_ctr = 0
    for image in tqdm.tqdm(image_list, ascii = True, ncols = 120):
       
        name = os.path.splitext(image)[0]
        annotation_xml = os.path.join(args['annotations_dir'], name + '.xml')
        annotation_xml = lxml.etree.fromstring(open(annotation_xml).read())
        annotation = parse_xml(annotation_xml)['annotation']       
        tf_example = build_example(annotation, label_map_dict, args)
        if tf_example is None:
            exlc_ctr += 1
           # breakpoint()
            continue
        writer.write(tf_example.SerializeToString())
        
    writer.close()
    
    if exlc_ctr > 0:
        logger.info(f"Number of images excluded due to absence of non-dificult bounding boxes: {exlc_ctr}")
        
    logger.info("Number of images included in TFRecord dataset: %d", len(image_list) - exlc_ctr)
    
if __name__ == '__main__':
    main()
