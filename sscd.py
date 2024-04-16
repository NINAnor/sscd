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
    (v) Calculate circuli spacings in each transect
    
    
Usage:

%run sscd.py \
   --img_dir "./data/example_scales"\
   --output_dir "C:/SSCD_temp_outputs"\
   --transect_angles 0 45 90 135 180 \
   --dets_separate_files False\
   --draw_detections True\
   --transect_max_boxes 200
"""

# import built-in modules
import argparse
import os
import shutil
import glob
from time import time
#import multiprocessing

# import installed/3rd-party modules
import logging
from tqdm import tqdm
import pandas as pd


# import local modules
from sscd_libs.helpers import boolean_string

from sscd_libs.detection import detect 

from sscd_libs.data_processing import (
    images_tiff_to_jpeg,
    get_transects
    )

from sscd_libs.helpers import unpack_for_string



# ------------------------------------------------------------------------------
def clean_output_dir(dir_path):
        
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            print("Error: %s : %s" % (dir_path, e.strerror))




# ------------------------------------------------------------------------------
def focus_checks(focus_dets_df):
        
    # QA for circuli spacings - flag up detection anomalies
    
    # issues counter
    issues = 0
    
    # Raise error if multiple focus found in one image
    n_focus_image = focus_dets_df["img_id"].value_counts()
    multiple_focus = n_focus_image[n_focus_image > 1]
    if len(multiple_focus) > 0:
        
        mult_focus_img_id = multiple_focus.index.values.tolist()

        logger.exception("... Multiple focus detected in the following image(s): " 
                        f"\n\n\t{unpack_for_string(mult_focus_img_id)}"
                        "\n\n\tDo images contain multiple scales? "
                        "Currently, system only allows for one scale per image " 
                        "\n\tEnding run prematurely.\n\n")
        
        # Stop logging process
        logging.shutdown()
            
        raise RuntimeError("Multiple focus in image")
        
        
    
    # Warning when detection boxes cover more than a given proportion of the image
    det_prop_tolerance = 0.2  # 1/5 of the image (arbitrary at this stage. May need tunning with usage)
    large_dets = focus_dets_df[["img_id", "detection_nr", "score",
                                         "img_prop"]][focus_dets_df.img_prop > det_prop_tolerance]
    if len(large_dets) > 0:
                      
         logger.warning("... The size of some of the focus detections are unusually large "
                        f"(covering >{det_prop_tolerance*100}% of the image size):"                      
                       '\n\n\t'+ large_dets.to_string().replace('\n', '\n\t') +
                       "\n\n\tCheck focus detection images as something might have gone wrong "
                       "(e.g. unsuitable images; detection deterioration)\n\n")
         issues += 1
         
    
    # report if no issues found
    if issues == 0:
        logger.info("... no apparent issues")
         
    return 0





# ------------------------------------------------------------------------------
def circuli_checks(circuli_dets_df, circuli_max_boxes):
    
    # QA for circuli spacings - flag up detection anomalies
      
    # issues counter
    issues = 0
    
    # Cases with spacings greater than a given tolerance
    spacing_tolerance = 250   # 250 pixels
    large_spacings = circuli_dets_df[["img_id", "circulus_nr", "score",
                                         "spacing_px"]][circuli_dets_df.spacing_px > spacing_tolerance]
    
    if len(large_spacings) > 0:
        logger.warning(f"... Some of the extracted spacings are abnormally large (>{spacing_tolerance} pixels), "
                      "likely due to misdetections of debris on the scale's periphery:" 
                       '\n\n\t'+ large_spacings.to_string().replace('\n', '\n\t') +
                       "\n\n\tCheck circuli detection images to confirm debris misdetection."
                       "\n\tNOTE: Large spacings due to debris misdetections must be removed on post-processing\n\n")
        issues += 1
    
    
    # Warning when more than 20% of spacings are over the large spacing tolerance 
    # NOTE: 20% is arbitrary at this point. Should be tunned with more usage and better grasp of common problems
    prop_large_spacings = large_spacings.shape[0]/circuli_dets_df.shape[0]   
    if prop_large_spacings > 0.2:
        logger.warning("... Over 20% of extracted spacings are abnormally large. ", 
                       "Check circuli detection images as something might have gone wrong "
                       "(e.g. unsuitable images; detection deterioration)\n\n")
        issues += 1
    
    
    # Warning when more than 30% of spacings are <= 1 pixel
    # NOTE: 30% is arbitrary at this point. Should be tunned with more usage and better grasp of common problems
    prop_tiny_spacings = circuli_dets_df.query("spacing_px <= 1").shape[0]/circuli_dets_df.shape[0]   
    if prop_tiny_spacings > 0.3:
        logger.warning("...Over 30% of extracted spacings are abnormally small. ", 
                       "Check circuli detection images as something might have gone wrong "
                       "(e.g. unsuitable images; detection deterioration)\n\n")
        issues += 1

    
    # Warning when maximum number of detections in one image 
    hit_max_num_dets = circuli_dets_df[["img_id", "circulus_nr"]][circuli_dets_df.circulus_nr == circuli_max_boxes]    
    if len(hit_max_num_dets) > 0:
        logger.warning(f"... Current max number of detections permitted per transect ({circuli_max_boxes} boxes)"
                        "has been reached in the following images"
                        '\n\n\t'+ hit_max_num_dets.to_string().replace('\n', '\n\t') +
                        "\n\n\tCheck circuli detection images for visual inspection. "
                        "Cap on max number of circuli detections may need to be adjusted "
                        "to accomodate older individuals\n\n"
                        )   
        issues += 1
        
    
    # Warning when detection boxes cover more than a given proportion of the image
    det_prop_tolerance = 0.20  # 1/5 of the image (arbitrary at this stage. May need tunning with usage)
    large_dets = circuli_dets_df[["img_id", "circulus_nr", "score",
                                         "img_prop"]][circuli_dets_df.img_prop > det_prop_tolerance]
    
    if len(large_dets) > 0:
        
         logger.warning("... The size of some of the circuli detections are unusually large "
                        f"(covering >{det_prop_tolerance*100}% of the image size):"                      
                       '\n\n\t'+ large_dets.to_string().replace('\n', '\n\t') +
                       "\n\n\tCheck circuli detection images as something might have gone wrong "
                       "(e.g. unsuitable images; detection deterioration)\n\n")
         issues += 1
         
    
    # report if no issues found
    if issues == 0:
        logger.info("... no apparent issues")

    return 0
         

    
    
    





# ------------------------------------------------------------------------------
def main():
    
    # parse the command line arguments
    args_parser = argparse.ArgumentParser(
        description='*** DESCRIPTION TO DO ***',
        formatter_class=argparse.MetavarTypeHelpFormatter
        )
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
        "--plot_dets",
        #dest= "plot_detections",
        required=False,
        type=boolean_string,
        default = True,
        help="Option to generate image plots with detections, for visual inspection",
    )
    args_parser.add_argument(
        "--transect_max_boxes",
        required=False,
        type=int,
        default = 200,
        help="Maximum number of detections per transect image",
    )
        
    args = vars(args_parser.parse_args())
    
    
    # Start runtime timer
    run_start = time()
    
        
    # --- Clean output directory of all subdirectories and files from a previous run
    clean_output_dir(args["output_dir"])
           
    
    
    # --------------------------------------- #
    # --       Logger Configuration       --- #
    # --------------------------------------- #
    
    # set-up dir and log filename
    os.makedirs(args["output_dir"], exist_ok=True)
    log_filename = os.path.join(args["output_dir"], "log_sscd_detection.log")
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler(log_filename, mode = 'w')
    file_handler.setLevel(logging.INFO)

    # Set up logging to file and console
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s (%(asctime)s): %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=(console_handler, file_handler)
        )
    
    global logger
    logger = logging.getLogger(__name__)
    
    

    
    # --------------------------------------- #
    # --               Checks             --- #
    # --------------------------------------- #  
    
    # -- Check if weights are placed correctly
    # Focus detector
    if len(glob.glob("./data/yoloV3_checkpoints/focus_detector/*.index")) == 0:
        raise FileNotFoundError("Checkpoint files for focus detector not found."
                                "Please refer to the README.md file and follow instructions on how to set up yolo weights")
    elif len(glob.glob("./data/yoloV3_checkpoints/focus_detector/*.index")) > 1:
        raise IOError("Too many checkpoints found for the focus detector model (only one checkpoint expected)."
                      "Please refer to the README file and follow instructions on how to set up yolo weights")
        
    # circuli detector    
    if len(glob.glob("./data/yoloV3_checkpoints/circuli_detector/*.index")) == 0:
        raise FileNotFoundError("Checkpoint files for circuli detector not found."
                                "Please refer to the README.md file and follow instructions on how to set up yolo weights")
    elif len(glob.glob("./data/yoloV3_checkpoints/circuli_detector/*.index")) > 1:
        raise IOError("Too many checkpoints found for the circuli detector model (only one checkpoint expected)."
                      "Please refer to the README file and follow instructions on how to set up yolo weights")
    
    
    
    # --------------------------------- #
    # --      File Management       --- #
    # --------------------------------- #  

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
    
    # circuli detections
    circuli_detections_dir = os.path.join(args["output_dir"], "detections", "circuli")
    os.makedirs(circuli_detections_dir, exist_ok=True)
    
    

    
    # --------------------------------------- #
    # --          System pipeline         --- #
    # --------------------------------------- #  
    
    ## --- 1. Convert image files to jpeg format and write them to ~/<output_dir>/jpegs/scales
    images_tiff_to_jpeg(
        args["img_dir"], 
        scales_jpegs_dir
        )
       
            
    ## --- 2. Focus detection   
    logger.info("Gearing up focus detection")
    focus_dets = detect(img_dir = scales_jpegs_dir, 
            det_dir = focus_detections_dir, 
            weights = './data/yoloV3_checkpoints/focus_detector/yolov3_train_190.tf', 
            classes_file = './data/scales_label.names',
            input_width=1376, 
            input_height=1376,
            yolo_score_threshold = 0.5, 
            yolo_max_boxes = 100, 
            dets_save_apart = args["dets_separate_files"], 
            plot_dets = args["plot_dets"], 
            draw_det_num = False,
            fig_w = 65, 
            fig_h = 60
            )
    

    logger.info("Finished focus detection")
    logger.info("Focus detection outputs saved to %s", focus_detections_dir)
       
    # Drop instances with no focus detections
    focus_dets.dropna(subset = ["score"], inplace = True)
    
    # Only proceed to circuli detection if there is at least one focus detection
    if len(focus_dets) > 0:
    
        ## --- 3. Sanity checks on focus detections
        logger.info("Running sanity checks on focus detections...")
        focus_checks(focus_dets)
        
        
        ## --- 4. Generate transect images off the detected focus
        
        # convert to list of dictionaries (1 per focus detection)
        focus_dets_dicts = focus_dets.to_dict("records")
        
        logger.info("Extracting images of radial transects from focus in %d scales", len(focus_dets_dicts))
        for focus_bbx in tqdm(focus_dets_dicts, ascii=True, ncols=120):
            
            get_transects(focus_bbox = focus_bbx, 
                          transect_degrees = args["transect_angles"],
                          img_filepath = os.path.join(scales_jpegs_dir, focus_bbx['img_id'] + '.jpg'), 
                          output_dir = transects_jpegs_dir)
            
            ## end of for loop
        
        
        # report progress    
        logger.info("Finished extracting transect images")
        logger.info("Transect images saved to %s", transects_jpegs_dir)
        
        
        ## --- 5. Circuli detections (model for non-padded images, for conf thresh of 0.3)
        logger.info("Gearing up circuli detector")
        circuli_dets = detect(
            img_dir = transects_jpegs_dir, 
            det_dir = circuli_detections_dir, 
            weights = './data/yoloV3_checkpoints/circuli_detector/yolov3_train_22.tf', 
            classes_file = './data/scale_transects_label.names',
            input_width = 3904, 
            input_height = 64,
            yolo_score_threshold = 0.3, 
            yolo_max_boxes = args["transect_max_boxes"], 
            dets_save_apart = args["dets_separate_files"], 
            plot_dets = args["plot_dets"], 
            draw_det_num = True,
            fig_w = 100, 
            fig_h = 5
            )
            
        logger.info("Finished circuli detection")
        logger.info("Circuli detection outputs saved to %s", circuli_detections_dir)
        
        
        ## --- 6. Calculate circuli spacings 
        logger.info("Calculating intracirculus spacings (in pixels)")
        
        circuli_dets["x_center"] = (circuli_dets["xmin"]+circuli_dets["xmax"])/2
        circuli_dets["y_center"] = (circuli_dets["ymin"]+circuli_dets["ymax"])/2
        circuli_dets["spacing_px"] = circuli_dets.groupby('img_id', group_keys=False).apply(lambda x: x.x_center.diff())
        circuli_dets.rename(columns={"detection_nr": "circulus_nr"}, inplace = True)
        
        # Write out dataframe with all detections
        circuli_dets.to_csv(os.path.join(circuli_detections_dir, "circuli_spacings.csv"), index=False)
        
        ## --- 7. Sanity checks on circuli detections and spacings
        logger.info("Running sanity checks on circuli detections and spacings...")
        circuli_checks(circuli_dets, args["transect_max_boxes"])
        
        
        ## --- 8. Summary stats of circuli outputs
        circuli_summary_stats = circuli_dets[["score", "spacing_px"]].describe(percentiles = [0.05, .5, .95])
        circuli_summary_stats.rename(columns = {"score":"det_conf_score"}, inplace = True)
        circuli_summary_stats = circuli_summary_stats.round({"conf_score":4, "spacing_px":2})

    else:
            
        logger.warning("Focus detector failed to locate focus in any of the provided scale images - "
                       "system cannot proceed to the circuli detection stage")
        
        circuli_summary_stats = pd.DataFrame()
        
     
    
    ## --- 8. Summarise Run
        
    num_scales = len(glob.glob(scales_jpegs_dir + os.path.sep + "*.jpg"))
    num_transects = len(glob.glob(transects_jpegs_dir + os.path.sep + "*.jpg"))   
    
     # calculate runtime duration (mins)
    run_duration = round((time() - run_start)/60, 2)
    
    logger.info("Run finished!"
                "\n\n---------------------------------------------------------"
                f"\nRuntime duration: {run_duration} mins"
                "\n\nFocus detection"
                f"\n\tScale images processed: {num_scales}"
                f"\n\tFocus detected: \t{focus_dets.img_id.nunique()}"
                "\n\nCirculi detection"
                f"\n\tTransect images processed: {num_transects}"
                "\n\tSummary statistics:"
                "\n\t\t" + circuli_summary_stats.to_string().replace('\n', '\n\t\t') +
                "\n---------------------------------------------------------")
    
    # Stop logging process
    logging.shutdown()


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    __spec__ = None
    main()
    
    
    
    
