# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 18:54:54 2021

@author: Bruno Caneco

Purpose: Main script to run the Salmon Scale Circuli detector via a command-line interface. 

Brief pipeline description:
    (i) Convert scale image's format to jepgs
    (ii) Detect focus location on each scale image
    (iii) Extract scale transect images at different angles from detected focus
    (iv) Detect circuli bands locations on transect images
    
    
Usage:

%run sscd.py \
    --img_dir "/MSS_Scales_depot/circuli_detection/inputs/transects_imgs_to_label/" \
    TODO

"""

# import built-in modules
import argparse
import os
import shutil
import glob
#import multiprocessing

# import local modules
from sscd_libs.detection import detect
from sscd_libs.data_processing import (
    images_tiff_to_jpeg,
    get_transects
    )

import logging


from tqdm import tqdm



# ------------------------------------------------------------------------------
# set up a basic, global _logger which will write to the console
logging.basicConfig(
    level=logging.INFO,
    #filename='sscd.log', filemode='w',
    format='%(levelname)s (%(asctime)s): %(message)s',
    #format= '%(levelname)s:%(module)s (%(asctime)s): %(message)s ',
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)




# ------------------------------------------------------------------------------
def clean_output_dir(dir_path):
        
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            print("Error: %s : %s" % (dir_path, e.strerror))



# ------------------------------------------------------------------------------
def boolean_string(s):
    if s not in {'False', 'True'}:
        raise ValueError('Not a valid boolean string')
    return s == 'True'



# ------------------------------------------------------------------------------
def main():
    
    # parse the command line arguments
    args_parser = argparse.ArgumentParser(
        description='*** DESCRIPTION TO DO ***')
    args_parser.add_argument(
        "--img_dir",
        #dest= "img_dir",
        required=True,
        type=str,
        help="directory path containing scale image files. Expects .tif images",
    )
    args_parser.add_argument(
        "--output_dir",
        #dest= "output_dir",
        required=True,
        type=str,
        help="directory path where outputs will be stored",
    )
    args_parser.add_argument(
        "--transect_angles",
        #dest= "transect_angles",
        required=False,
        type=int,
        nargs='+',
        default = [0, 45, 90, 135, 180],
        help="choice of angle(s) for radial transects relative to focus, in degrees",
    )
    args_parser.add_argument(
        "--dets_separate_files",
        #dest= "dets_separate_files",
        required=False,
        type=boolean_string,
        default = False,
        help="Require detections in each image to be saved in separate files",
    )
    args_parser.add_argument(
        "--plot_detections",
        #dest= "plot_detections",
        required=False,
        type=boolean_string,
        default = True,
        help="Plot images with detections?",
    )
        
    args = vars(args_parser.parse_args())
    
    
    #breakpoint()
    
    
    # --------------------------------------- #
    # --               Checks             --- #
    # --------------------------------------- #  
    
    # -- Check if weights are placed correctly
    # Focus detector
    if len(glob.glob("./data/yoloV3_checkpoints/focus_detector/*.index")) == 0:
        raise FileNotFoundError("Checkpoint files for focus detector not found."
                                "Please check README.md file and follow instructions on how to set up yolo weights")
    elif len(glob.glob("./data/yoloV3_checkpoints/focus_detector/*.index")) > 1:
        raise IOError("Too many checkpoints found for the focus detector model (only one checkpoint expected)."
                      "Please check README file and follow instructions on how to set up yolo weights")
        
    # circuli detector    
    if len(glob.glob("./data/yoloV3_checkpoints/circuli_detector/*.index")) == 0:
        raise FileNotFoundError("Checkpoint files for circuli detector not found."
                                "Please check README.md file and follow instructions on how to set up yolo weights")
    elif len(glob.glob("./data/yoloV3_checkpoints/circuli_detector/*.index")) > 1:
        raise IOError("Too many checkpoints found for the circuli detector model ((only one checkpoint expected)."
                      "Please check README file and follow instructions on how to set up yolo weights")
    
    
    
    # --------------------------------- #
    # --      File Management       --- #
    # --------------------------------- #  
    
    # --- Clean output directory of all subdirectories and files from a previous run
    clean_output_dir(args["output_dir"])
           
    # -- Create destination directories
    # scale jpeg images
    scales_jpegs_dir = os.path.join(args["output_dir"], "jpegs", "scales")
    os.makedirs(scales_jpegs_dir, exist_ok=True)
    
    # transect jpeg images
    transects_jpegs_dir = os.path.join(args["output_dir"], "jpegs", "transects")
    os.makedirs(transects_jpegs_dir, exist_ok=True)
    
    # focus detections
    focus_detections_dir = os.path.join(args["output_dir"], "detections", "focus")
    os.makedirs(focus_detections_dir, exist_ok=True)
    
    circuli_detections_dir = os.path.join(args["output_dir"], "detections", "circuli")
    os.makedirs(circuli_detections_dir, exist_ok=True)
    
    

    
    # --------------------------------------- #
    # --    Circuli detection pipeline    --- #
    # --------------------------------------- #  
    
    ## --- 1. Convert image files to jpeg format and write them to ~/<output_dir>/jpegs/scales
    images_tiff_to_jpeg(
        args["img_dir"], 
        scales_jpegs_dir
        )
       
    #breakpoint()
            
    ## --- 2. Focus detection   
    logger.info("Starting focus detection")
    focus_dets = detect(img_dir = scales_jpegs_dir, 
            det_dir = focus_detections_dir, 
            #det_img_dir = focus_detection_images_dir,
            weights = './data/yoloV3_checkpoints/focus_detector/yolov3_train_190.tf', 
            classes_file = './data/scales_label.names',
            input_width=1376, 
            input_height=1376,
            dets_save_apart = args["dets_separate_files"], 
            plot_dets = args["plot_detections"], 
            fig_w = 35, 
            fig_h = 30
            )
    
    # focus_dets = multiprocessing.Process(target=detect, args = (
    #                                        scales_jpegs_dir, 
    #                                        focus_detections_dir, 
    #                                        './data/yoloV3_checkpoints/focus_detector/yolov3_train_190.tf', 
    #                                        './data/scales_label.names',
    #                                        1376, 
    #                                        1376,
    #                                        args["dets_separate_files"], 
    #                                        args["plot_detections"], 
    #                                        35, 
    #                                        30))
    
    # focus_dets.start()
    # focus_dets.join()
    
    
    logger.info("Finished focus detection")
    logger.info("Focus detection outputs saved to %s", focus_detections_dir)
    
    
    ## --- 3. Extract transect images off the detected focus
    
    # convert to list of dictionaries (1 per focus detection)
    focus_dets_dicts = focus_dets.to_dict("records")
    
    logger.info("Extracting images of radial transects from focus in %d scales", len(focus_dets_dicts))
    for focus_bbx in tqdm(focus_dets_dicts, ascii=True, ncols=120):
        
        get_transects(focus_bbox = focus_bbx, 
                      transect_degrees = args["transect_angles"],
                      img_filepath = os.path.join(scales_jpegs_dir, focus_bbx['img_id'] + '.jpg'), 
                      output_dir = transects_jpegs_dir)
    
    logger.info("Finished extracting transect images")
    logger.info("Transect images saved to %s", transects_jpegs_dir)
    
    
    ## --- 4. Circuli detections (model for non-padded images, for conf thresh of 0.3)
    logger.info("Gearing up circuli detector")
    circuli_dets = detect(
        img_dir = transects_jpegs_dir, 
        det_dir = circuli_detections_dir, 
        weights = './data/yoloV3_checkpoints/circuli_detector/yolov3_train_22.tf', 
        classes_file = './data/scale_transects_label.names',
        input_width = 3904, 
        input_height = 64,
        yolo_score_threshold = 0.3, 
        yolo_max_boxes = 150, 
        dets_save_apart = args["dets_separate_files"], 
        plot_dets = args["plot_detections"], 
        fig_w = 100, 
        fig_h = 5
        )
    
    logger.info("Finished circuli detection")
    logger.info("Circuli detection outputs saved to %s", circuli_detections_dir)
    
    
    ## --- 5. Calculate circuli spacings 
    
    #breakpoint()
    
    circuli_dets["x_center"] = (circuli_dets["xmin"]+circuli_dets["xmax"])/2
    circuli_dets["y_center"] = (circuli_dets["ymin"]+circuli_dets["ymax"])/2
    circuli_dets["spacing_px"] = circuli_dets.groupby('img_id', group_keys=False).apply(lambda x: x.x_center.diff())
    circuli_dets['circuli_nr'] = circuli_dets.groupby('img_id').cumcount()
    
    # Write out dataframe with all detections
    circuli_dets.to_csv(os.path.join(circuli_detections_dir, "circuli_spacings.csv"), index_label="detection_nr")

    # TODO: QA for circuli spacings - Add some summary statistics and metrics to flag up detection deterioration

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    __spec__ = None
    main()    
    
    
    
    
    