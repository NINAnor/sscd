# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 19:42:58 2021

@author: dmp
"""

import os
import tensorflow as tf
import glob
import logging
from tqdm import tqdm
from pathlib import Path
import pandas as pd
import cv2
import numpy as np

from yolov3_tf2.models import YoloV3
from yolov3_tf2.dataset import transform_images


logger = logging.getLogger(__name__)

# Colours for detections annotations (BGR order)
bbox_col = (0, 0, 255)
txt_col = (221, 221, 221)



def bbox_textbox(img, text, offset, txt_bgr_col, txt_col):
    font_scale = 1.5
    font = cv2.FONT_HERSHEY_PLAIN

    # # set the rectangle background to white
    # rectangle_bgr = (255, 0, 0)
    # get the width and height of the text box
    (text_width, text_height) = cv2.getTextSize(text, font, fontScale=font_scale, thickness=1)[0]
    # set the text start position
    text_offset_x = offset[0]
    text_offset_y = offset[1]
    # make the coords of the box with a small padding of two pixels
    box_coords = ((text_offset_x, text_offset_y), 
                  (text_offset_x + text_width + 3, text_offset_y - text_height - 3)
                  )
    cv2.rectangle(img, box_coords[0], box_coords[1], txt_bgr_col, cv2.FILLED)
    
    img_textbox = cv2.putText(img, text, (text_offset_x, text_offset_y), font, 
                      fontScale=font_scale, color=txt_col, thickness=1)
    
    return img_textbox


def draw_detections(img, outputs, class_names, bbox_col, txt_col):
    
    #breakpoint()
    boxes, objectness, classes, nums = outputs
    boxes, objectness, classes, nums = boxes[0], objectness[0], classes[0], nums[0]
    wh = np.flip(img.shape[0:2])
    for i in range(nums):
        x1y1 = tuple((np.array(boxes[i][0:2]) * wh).astype(np.int32))
        x2y2 = tuple((np.array(boxes[i][2:4]) * wh).astype(np.int32))
        img = cv2.rectangle(img, x1y1, x2y2, bbox_col, 1)       
        img = bbox_textbox(img, '{}: {:.2f}'.format(
              class_names[int(classes[i])], objectness[i]), x1y1, bbox_col, txt_col)
        
        xcent = (x2y2[0]+x1y1[0])/2
        ycent = (x2y2[1]+x1y1[1])/2
        img = cv2.circle(img, (xcent.astype(np.int32), ycent.astype(np.int32)), radius=1, color=bbox_col, thickness=-1)
    return img




# def process_detections(boxes, scores, classes, nums, 
#                        img_id, img_raw_w, img_raw_h, class_names, det_dir,
#                        plot_detection=True):
    
#     detections = []
#     for i in range(nums[0]):
#         detection = {
#             "img_id": img_id,
#             "class_name": class_names[int(classes[0][i])],
#             "score" : scores[0][i].numpy(),
#             "xmin": int(boxes[0][i][0].numpy()*img_raw_w),
#             "ymin": int(boxes[0][i][1].numpy()*img_raw_h),
#             "xmax": int(boxes[0][i][2].numpy()*img_raw_w),
#             "ymax": int(boxes[0][i][3].numpy()*img_raw_h)
#                 }
#         detections.append(detection)
        
#     # write the detection boxes into a txt file, with boundaries as absolute values
#     # os.makedirs(detection_dir, exist_ok=True)
#     with open(os.path.join(det_dir, img_id + ".txt"), "w") as detection_file:
#         for detection in detections:
#             detection_file.write(
#                 f"{detection['class_name']} "
#                 f"{detection['score']} "
#                 f"{detection['xmin']} "
#                 f"{detection['ymin']} "
#                 f"{detection['xmax']} "
#                 f"{detection['ymax']}\n"
#                 )
        
#     if plot_detection:
#         img = cv2.cvtColor(img_raw.numpy(), cv2.COLOR_RGB2BGR)
#         img = draw_detections(img, (boxes, scores, classes, nums), class_names, 
#                               bbox_col, txt_col)
            
#         cv2.imwrite(os.path.join(detection_img_dir, img_id + "_detections.jpg"), img)
    
#     return(pd.DataFrame(detections))







def detect(img_dir, det_dir, det_img_dir, weights=None, classes_file=None, 
           input_width=None, input_height=None):
    
    """
    
    """
    
    # # --- prepare GPU infrastructure (if present)
    # physical_devices = tf.config.experimental.list_physical_devices('GPU')
    # for physical_device in physical_devices:
    #       tf.config.experimental.set_memory_growth(physical_device, True)
         
    #breakpoint()
    
    # --- setting up yoloV3's model structure
    # yolo = YoloV3(classes=1)
    yolo = YoloV3(width=input_width, height=input_height, classes=1)
    
    # --- load weights
    yolo.load_weights(weights).expect_partial()
    logger.info('weights loaded')
        
    # --- load object classes
    class_names = [c.strip() for c in open(classes_file).readlines()]
    logger.info('classes loaded')
    
    
    # --- get image filepaths
    img_filepaths = glob.glob(img_dir + "/*.jpg")
    
    # initiate data frame to store detections in all images
    all_detections = pd.DataFrame()
    
    logger.info('Starting detection in %d images', len(img_filepaths))
    
    #breakpoint()
    
    for img_filepath in tqdm(img_filepaths, ascii=True, ncols=120):
                
        img_id = Path(img_filepath).stem
        
        # Read-in img as a tensor
        img_raw = tf.image.decode_image(open(img_filepath, 'rb').read(), channels=3)
        img_raw_h, img_raw_w = img_raw.shape[0:2]
        
        # Image pre-processing
        img = tf.expand_dims(img_raw, 0)
        img = transform_images(img, input_height, input_width)
        
        # Predict
        boxes, scores, classes, nums = yolo(img)
        
        detections = []
        for i in range(nums[0]):
            detection = {
                "img_id": img_id,
                "class_name": class_names[int(classes[0][i])],
                "score" : scores[0][i].numpy(),
                "xmin": int(boxes[0][i][0].numpy()*img_raw_w),
                "ymin": int(boxes[0][i][1].numpy()*img_raw_h),
                "xmax": int(boxes[0][i][2].numpy()*img_raw_w),
                "ymax": int(boxes[0][i][3].numpy()*img_raw_h)
                }
            detections.append(detection)
        
        # breakpoint()
        
        # dets = yolo(img)
        # process_detections(dets, )
        
        # Append detection in current image to overal dataset
        all_detections = all_detections.append(pd.DataFrame(detections))
        
        # write the detection boxes into a txt file, with boundaries as absolute values
        # os.makedirs(detection_dir, exist_ok=True)
        with open(os.path.join(det_dir, img_id + ".txt"), "w") as detection_file:
            for detection in detections:
                detection_file.write(
                    f"{detection['class_name']} "
                    f"{detection['score']} "
                    f"{detection['xmin']} "
                    f"{detection['ymin']} "
                    f"{detection['xmax']} "
                    f"{detection['ymax']}\n"
                    )
                    
        # Colours for detections annotations (BGR order)
        bbox_col = (0, 0, 255)
        txt_col = (221, 221, 221)

        # plot
        img = cv2.cvtColor(img_raw.numpy(), cv2.COLOR_RGB2BGR)
        img = draw_detections(img, (boxes, scores, classes, nums), class_names, 
                              bbox_col, txt_col)
        
        # breakpoint()        
        cv2.imwrite(os.path.join(det_img_dir, img_id + "_detections.jpg"), img)
        
    
    #logger.info('Finished detections')
    
    # Write out dataframe with all detections
    all_detections.to_csv(os.path.join(det_dir, "detections_all_images.csv"), index_label="detection_nr")
   
    return 0