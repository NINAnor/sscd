# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 19:42:58 2021

@author: Bruno Canecco

Purpose: Module with core worker functions for the detection process

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
    
    
    # Concatenate into a single dataframe
    detections_df = pd.concat([id_classes_scores, boxes_df], axis=1)     
    
    # add the proportion of image covered by each detection, if any present
    det_areas = (detections_df.xmax - detections_df.xmin)*(detections_df.ymax - detections_df.ymin)
    detections_df["img_prop"] = det_areas/(img_orig_wh[0]*img_orig_wh[1])   
       
    # calculate xcentre, sort data by it, and drop it, for consistency with previous version
    detections_df = detections_df.assign(xcentre = lambda x: (x.xmax + x.xmin)/2)
    detections_df.sort_values(by=['xcentre'], inplace = True, ignore_index =True)
    detections_df.drop('xcentre', axis = 1, inplace = True)
        
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
def plot_detections(img, dets, output_dir, draw_ann = False, anns = None, 
                    anns_sepPlot = False, plot_conf = True, draw_det_num = False, 
                    fig_w = None, fig_h = None):
    """
    Generate image plot(s) with detections, and optionally annotations, drawn in a target image

    Parameters
    ----------
    img : 3D numpy array
        target image decoded as an array of pixel intensities
    dets : pandas DataFrame
        object detections on target image. It MUST contain, at least,
        columns with class names, boxes boundaries and confidence scores named, respectively, 
        as 'class_name', 'xmin', 'ymin"', 'xmax', 'ymax, and 'score'. Expects boundaries 
        coordinates as absolute values w.r.t. the size of the target image
    output_dir : str
        poth to directory where the generated image plot will be saved to
    draw_ann : bool, optional
        Option to draw annotations in the image plot. The default is False.
    anns : pandas DataFrame, optional
        annotations on target image - only required if draw_ann is set to True. The default is None.
        It MUST contain, at least, columns for class names and boxes boundaries named, respectively, 
        as 'class_name', 'xmin', 'ymin"', 'xmax' and 'ymax. Expects boundaries 
        coordinates as absolute values w.r.t. the size of the target image
    anns_sepPlot : bool, optional
        Option to generate a separate image plot for annotations, as well as a reference image plot. 
        The default is False, which will draw annnotations and detections on the same image plot.
    plot_conf : bool, optional
        Option to add confidence scores to the plot. The default is True.
    draw_det_num : bool, optional
        Option to add detection (and annotation) counters to the plot, to help visual inspection. 
        The default is False.
    fig_w : float, optional
        figure width of the image plot. The default is 30.
    fig_h : TYPE, optional
        figure height of the image plot. The default is 30.

    Raises
    ------
    ValueError
        If 'draw_ann' is set to True, the DataFrame 'anns' must be provided.

    Returns
    -------
    None.

    """
    
    if draw_ann and anns is None:
        raise ValueError("Missing annotations data to plot against detections")
        logging.shutdown()
               
    # calculate centers, widths & heights of detections    
    dets = dets.assign(
        xcentre = lambda x: (x.xmax + x.xmin)/2, 
        ycentre = lambda x: (x.ymax + x.ymin)/2,
        width = lambda x: x.xmax - x.xmin,
        height = lambda x: x.ymax - x.ymin
        )  
    
    # sort output by xmin to plot detection counters in left-to-right order
    dets.sort_values(by=['xmin'], inplace = True, ignore_index=True)
    
     
    # Option to automatically set size of figure plot based on size of original image
    if fig_w is None or fig_h is None:
        fig_w = min(img.shape[1]*.15, 100)
        fig_h = min(img.shape[0]*.15, 100)
        
    # Create figure and axes
    fig = plt.figure(figsize = (fig_w, fig_h))

    # set subplot for image with detections
    ax0 = fig.add_subplot(3, 1, 3)
    ax0.imshow(img)
    ax0.axis('off')
        
    # draw bounding boxes, centers and confidence score of each detection
    for index, row in dets.iterrows():
         
        det_centre = (row["xcentre"], row["ycentre"])
            
        det_rect = patches.Rectangle(
            xy = (row["xmin"], row["ymin"]),
            width = row["width"],
            height = row["height"], 
            linewidth = 1.5,
            edgecolor = 'red',
            facecolor = (1, 0, 0, 0.1),
            fill = True)
            
        det_dot = patches.Circle(xy = det_centre, radius = 1, color = 'red')
            
        ax0.add_patch(det_rect)
        ax0.add_patch(det_dot)
        
        if plot_conf:
            ax0.text(det_centre[0], det_centre[1]+3, round(row["score"], 2), 
                    fontsize = 'small', fontstyle = "italic", c = 'white', 
                    ha = "center", va = "top")
            
        if draw_det_num: 
            ax0.text(det_centre[0], det_centre[1]-2, index+1, fontsize = 'small', 
                    c = "red", ha = "center", va = "bottom")
        # end of loop
    
    
    # Plot annotations        
    if draw_ann:            
                
        # calculate centers, widths & heights of annotations    
        anns = anns.assign(
            xcentre = lambda x: (x.xmax + x.xmin)/2, 
            ycentre = lambda x: (x.ymax + x.ymin)/2,
            width = lambda x: x.xmax - x.xmin,
            height = lambda x: x.ymax - x.ymin
            )  
        
        # sort output by xmin to plot annotations counters in left-to-right order
        anns.sort_values(by=['xmin'], inplace = True, ignore_index=True)
        
        # First, generate and store bbox elements in lists
        ann_bbxs_centres = []
        ann_bbxs_rects = []
        ann_bbxs_dots = []
        
        for index, row in anns.iterrows():
            
            ann_bbx_centre = (row["xcentre"], row["ycentre"])
            ann_bbxs_centres.append(ann_bbx_centre)

            ann_bbxs_rects.append(
                patches.Rectangle(
                    xy = (row["xmin"], row["ymin"]),
                    width = row["width"],
                    height = row["height"], 
                    linewidth = 1.5,
                    edgecolor = 'limegreen', 
                    facecolor = (43/255, 195/255, 61/255, 0.3), #'limegreen',
                    fill = True)
                )
            
            ann_bbxs_dots.append(
                patches.Circle(xy = ann_bbx_centre, radius = 0.5, color = 'limegreen')
                )         
            # end of loop
               
        # Secondly, add annotations bounding boxes in separate subplot or add them to first plot
        if anns_sepPlot:
                                
            # add subplot for the reference image
            ax1 = fig.add_subplot(3, 1, 2, sharex=ax0)
            ax1.imshow(img)
            ax1.axis('off')
                       
            # add subplot for the annotations image
            ax2 = fig.add_subplot(3, 1, 1, sharex=ax0)
            ax2.imshow(img)
            ax2.axis('off')
            
            for i in range(len(anns)):
                ax2.add_patch(ann_bbxs_rects[i])
                ax2.add_patch(ann_bbxs_dots[i])
                
                if draw_det_num: 
                    ax2.text(ann_bbxs_centres[i][0], ann_bbxs_centres[i][1]-2, i+1, fontsize = 'small', 
                             c = 'limegreen', ha = "center", va = "bottom")       
               
        else:
            for i in range(len(anns)):
                ax0.add_patch(ann_bbxs_rects[i])
                ax0.add_patch(ann_bbxs_dots[i])
        
    
    if draw_ann:
        imgfile_label = "dets_vs_anns"
    else:
        imgfile_label = "detections"

    plt.savefig(os.path.join(output_dir, dets.img_id.iloc[0] + imgfile_label +".jpg"),
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
           plot_dets = True, draw_det_num = False, 
           fig_w = 25, fig_h = 20):
    """
    TODO

    Parameters
    ----------
    img_dir : TYPE
        DESCRIPTION.
    det_dir : TYPE
        DESCRIPTION.
    weights : TYPE, optional
        DESCRIPTION. The default is None.
    classes_file : TYPE, optional
        DESCRIPTION. The default is None.
    input_width : TYPE, optional
        DESCRIPTION. The default is None.
    input_height : TYPE, optional
        DESCRIPTION. The default is None.
    yolo_score_threshold : TYPE, optional
        DESCRIPTION. The default is 0.5.
    yolo_max_boxes : TYPE, optional
        DESCRIPTION. The default is 100.
    dets_save_apart : TYPE, optional
        DESCRIPTION. The default is False.
    plot_dets : TYPE, optional
        DESCRIPTION. The default is True.
    draw_det_num : TYPE, optional
        DESCRIPTION. The default is False.
    fig_w : TYPE, optional
        DESCRIPTION. The default is 25.
    fig_h : TYPE, optional
        DESCRIPTION. The default is 20.

    Returns
    -------
    all_detections : TYPE
        DESCRIPTION.

    """
    
    
    #--- File management
    # Create directory to take detection images, if required
    if plot_dets:
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
        if plot_dets and img_detections_df.shape[0] > 0:
            plot_detections(img_orig, img_detections_df, det_img_dir, 
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