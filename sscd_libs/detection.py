# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 19:42:58 2021

@author: Bruno Canecco

TODO

"""

# import standard libraries
import os
import glob
import logging
from pathlib import Path


# import installed/3rd-party modules
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from tqdm import tqdm
import numpy as np
import pandas as pd
import tensorflow as tf


# import local modules
from yolov3_tf2.models import YoloV3
from yolov3_tf2.dataset import transform_images

from sscd_libs.helpers import (
    unpack_for_string
    )


logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
def detections_as_df(detections_tf, img_orig_wh, img_id, class_names):
       
    """
    Combines the objects returned from the prediction step into a pandas DataFrame
    
    Args
    -----
    detections_tf : list
        list of objects returned from the prediction step, i.e. for each detection, 
        the bounding boxes coords, the confidence score and index of object class
        
    img_orig_wh: list   
        Width and height (in pixels) of the original image undergoing detection
            
    img_id : str
        Image ID, usually the name of the image file, without the file extension
        
    class_names : list
        Names of the object clases
        
    Returns
    -------
    DataFrame with detection data
    
    """
    
    boxes, scores, classes, nums = detections_tf
        
    # drop empty elements in arrays
    boxes, scores, classes, nums = boxes[0], scores[0], classes[0], nums[0]
    boxes, scores, classes = boxes[:nums], scores[:nums], classes[:nums]
    
    # convert classes index as integer
    classes = tf.cast(classes, tf.int16)
    # get classes names
    class_names = [class_names[i] for i in classes]
        
    # Convert bounding boxes limits from relative to absolute
    boxes_abs = boxes * np.tile(img_orig_wh, 2)
    # Round coords to integers
    boxes_abs = tf.cast(boxes_abs, tf.int32).numpy()
    
    # Convert from tensors to dataframe
    id_classes_scores = pd.DataFrame(
        {"img_id" : img_id,
         "class_name": class_names,
         "score": scores
          })
    boxes_df = pd.DataFrame(boxes_abs, columns = ["xmin", "ymin", "xmax", "ymax"])
    
    #breakpoint()
    
    # Concatenate into a single dataframe
    detections_df = pd.concat([id_classes_scores, boxes_df], axis=1)     
    
    # add the proportion of image covered by each detection, if any present
    det_areas = (detections_df.xmax - detections_df.xmin)*(detections_df.ymax - detections_df.ymin)
    detections_df["img_prop"] = det_areas/(img_orig_wh[0]*img_orig_wh[1])   

    # sort output by xmin
    detections_df.sort_values(by=['xmin'], inplace = True, ignore_index =True)
        
    # Add detection incremental counter
    detections_df.insert(loc = 1, column = "detection_nr", value =  detections_df.index + 1)
    
    # return DF with img_id and nans for remaining elements - usefull for keeping
    # record of images with no detections
    if len(detections_df) == 0:
        det_colnames = detections_df.columns.tolist()
        no_dets_fill = [img_id] + [np.nan]*(len(det_colnames)-1)
        detections_df = pd.DataFrame(dict(zip(det_colnames, no_dets_fill)), index = [0])
    
        
    return(detections_df)




# ------------------------------------------------------------------------------
def draw_detections(img, dets, output_dir, draw_gt = False, gtInSeparatePlot = False,
                    img_groundtruths = None, plot_conf = True, draw_det_num = False, 
                    fig_w = 30, fig_h = 30):
    
    """
    TODO
    
    Args
    ------
    img :
        
    Returns
    -------    
    
    """
    
    if draw_gt and img_groundtruths == None:
        raise ValueError("Missing ground truth data to plot against detections")
               
    # calculate centers, widths & heights of detections
    dets["xcenter"] = (dets["xmax"]+dets["xmin"])/2
    dets["ycenter"] = (dets["ymax"]+dets["ymin"])/2
    dets["width"] = dets["xmax"] - dets["xmin"]
    dets["height"] = dets["ymax"] - dets["ymin"]    
        
    # Create figure and axes
    fig, ax = plt.subplots(1, 1, figsize = (fig_w, fig_h))
     
    # set image for detections
    ax.imshow(img)
    ax.axis('off')
    
    # breakpoint()
    
    # draw bounding boxes, centers and confidence score of each detection
    for index, row in dets.iterrows():
         
        #det_center = ((row["xmax"]+row["xmin"])/2, (row["ymax"]+row["ymin"])/2)
        det_center = (row["xcenter"], row["ycenter"])
            
        det_rect = patches.Rectangle(xy = (row["xmin"], row["ymin"]),
                                     width = row["width"],
                                     height = row["height"], 
                                     linewidth = 2,
                                     edgecolor = 'red',
                                     facecolor = (1, 0, 0, 0.1),
                                     fill = True)
            
        det_dot = patches.Circle(xy = det_center, radius = 1, color = 'red')
            
        ax.add_patch(det_rect)
        ax.add_patch(det_dot)
        
        if plot_conf:
            ax.text(det_center[0], det_center[1]+3, round(row["score"], 2), 
                    fontsize = 'small', fontstyle = "italic", c = 'white', 
                    ha = "center", va = "top")
            
        if draw_det_num: 
            ax.text(det_center[0], det_center[1]-2, index+1, fontsize = 'small', 
                    c = "red", ha = "center", va = "bottom")
        

    plt.savefig(os.path.join(output_dir, dets["img_id"][0] + "_detections.jpg"),
                bbox_inches='tight', pad_inches=0)
        
    plt.close(fig)   

        
        


# ------------------------------------------------------------------------------
def write_detections_per_img(x, det_subdir):
    
    """    
    Write detections in each image in separate files
    
    Args
    -----
    x: pandas DataFrame. Data to be written out. It expects a column named "img_id", 
        specifying the ID of the image
            
    det_subdir: str. subdirectory comprising the detection files
        
    Returns
    -------    
    0 to indicate successful completion
    
    """
       
    # construct filepath as txt file
    det_filepath = os.path.join(det_subdir, x.img_id.iloc[0] + ".txt")
    
    # exclude image ID column
    #x.drop("img_id", axis = 1, inplace = True)
    out = x.drop("img_id", axis = 1)
    
    # write out
    #x.to_csv(det_filepath, header=None, index=None, sep=' ', mode='w')
    out.to_csv(det_filepath, header=False, index=False, sep=' ', mode='w')
       
    return 0
    




# ------------------------------------------------------------------------------
def detect(img_dir, det_dir, weights=None, classes_file=None, 
           input_width=None, input_height=None, 
           yolo_score_threshold = 0.5, yolo_max_boxes = 100, 
           dets_save_apart = False, 
           draw_dets = True, draw_det_num = False, 
           fig_w = 25, fig_h = 20):
    
    
    """
    TODO
    
    Args
    ----------
    img :
        
    Returns
    -------    
    
    """
    
    #--- File management
    # Create directory to take detection images, if required
    if draw_dets:
        det_img_dir = os.path.join(det_dir, "detection_images")
        os.makedirs(det_img_dir, exist_ok=True)

        
    # --- prepare GPU infrastructure (if present)
    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    for physical_device in physical_devices:
          tf.config.experimental.set_memory_growth(physical_device, True)
    
    # --- setting up yoloV3's model structure
    yolo = YoloV3(width=input_width, height=input_height, classes=1, 
                  yolo_max_boxes = yolo_max_boxes, 
                  yolo_score_threshold = yolo_score_threshold)
    
        
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
    
    all_detections = pd.DataFrame()
    no_detections_img_id = []
    no_detections_img = []
    
    for img_filepath in tqdm(img_filepaths, ascii=True, ncols=120):
        
        # read-in original img as a tensor
        img_orig = tf.image.decode_image(open(img_filepath, 'rb').read(), channels=3)
        
        # get original image dimensions (width x height)
        img_orig_wh = np.flip(img_orig.shape[0:2].as_list())
        
        # get image ID
        img_id = Path(img_filepath).stem
        
        # Image pre-processing for yoloV3 model
        img = tf.expand_dims(img_orig, 0)
        img = transform_images(img, input_height, input_width)
               
        # Predict in image
        img_detections_tf = yolo(img)
        
        # Convert detection data to dataframe
        img_detections_df = detections_as_df(img_detections_tf, img_orig_wh, 
                                                img_id, class_names)
        
        # append to overall dataset
        all_detections = all_detections.append(img_detections_df)
                            
        # drop rows with nan (i.e. return empty DF if no detections found), 
        # which is essential for ploting
        img_detections_df.dropna(subset = ["score"], inplace = True)
        
        # if requested, and if detections present, plot images with detections
        if draw_dets and img_detections_df.shape[0] > 0:
            draw_detections(img_orig, img_detections_df, det_img_dir, 
                            draw_det_num = draw_det_num,
                            fig_w = fig_w, fig_h = fig_w)
        
        # if no detections in image, store image pixel data and ID
        if img_detections_df.shape[0] == 0:
            no_detections_img_id.append(img_id)
            no_detections_img.append(img_orig)
        
    ## end of loop
       

    # Write out dataframe with all detections
    all_detections.to_csv(os.path.join(det_dir, "detections.csv"), index=False)
    
    
    # Reporting images with no detections
    if len(no_detections_img_id) > 0:
        
        no_det_img_dir = os.path.join(det_dir, "imgs_with_no_detections")
        os.makedirs(no_det_img_dir, exist_ok=True)
        
        # write image to specific folder for visual check
        for img_id, img_orig in zip(no_detections_img_id, no_detections_img):
            im = Image.fromarray(img_orig.numpy())
            im.save(os.path.join(no_det_img_dir, img_id + ".jpeg"), 'JPEG', quality=95)
                
        logger.warning(f"Failed to detect {unpack_for_string(class_names)} in {len(no_detections_img_id)} "
                       f"image(s):\n\n\t{unpack_for_string(no_detections_img_id)}"
                       f'\n\n\tImage(s) with no detections saved to {no_det_img_dir}\n\n')
      
    
    # option to save detections separately for each image id
    if dets_save_apart: 
        det_subdir = os.path.join(det_dir, "dets_img_id")
        os.makedirs(det_subdir, exist_ok=True)
        all_detections.groupby("img_id").apply(write_detections_per_img, det_subdir = det_subdir)
     
          
    return all_detections