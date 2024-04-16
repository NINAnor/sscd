# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 13:54:54 2021

@author: Bruno Caneco

Purpose: Main script to evaluate the current performance of Salmon Scale Circuli detector on fresh images. 

Brief pipeline description:
    (i) Convert annotations from pascal voc xml to text files 
    (ii) Convert detections from csv to text files
    (iii) Compute performance metrics
    (iv) draw plots comparing gt vs dets
    (v) delete generated txt files
    
    
Usage:

%run eval_detector.py \
    --img_dir \
    --ann_dir \
    --dets_csv \
    --outputs_dir \
    --dets_vs_anns_plots \
    --sep_plots
"""

# import built-in modules
import argparse
import os
import glob
import shutil
from time import time
from pathlib import Path
#import multiprocessing
import matplotlib.image as mpimg


# import installed packages
import logging
from tqdm import tqdm
import pandas as pd

# import local modules
from sscd_libs.helpers import (
    boolean_string,
    clean_output_dir,
    unpack_for_string,
    query_yes_no
    )

from sscd_libs.data_processing import pascal_to_evaltxt
from sscd_libs.detection import (
    write_detections_per_img,
    plot_detections
    )
from sscd_libs.evaluation import evaluate




# ------------------------------------------------------------------------------
def FileNotFound_logAndOut(msg):
    """
    log error, close logging and force stop
    """     
    logger.error(msg)
    logging.shutdown()
    raise FileNotFoundError(msg)
    #raise 


    

# ------------------------------------------------------------------------------
def main():

    
    # parse the command line arguments
    args_parser = argparse.ArgumentParser(
        description='*** Tool to perform evaluation of sscd performance on new images ***',
        formatter_class=argparse.MetavarTypeHelpFormatter)
    args_parser.add_argument(
        "--img_dir",
        required=True,
        type=str,
        help="Directory path containing the images used for the evaluation. Expects JPEG images"
    )
    args_parser.add_argument(
        "--anns_dir",
        required=True,
        type=str,
        help="Directory path containing the annotation files. Expects XML files with" 
            " annotations in Pascal VOC format, containing bounding boxes",
    )
    args_parser.add_argument(
        "--dets_csv",
        required=True,
        type=str,
        help="Filepath to CSV file containing detection bounding boxes, "
        "produced under the sscd.py module"
    )
    args_parser.add_argument(
        "--iou_threshould",
        required=False,
        type=float,
        default = 0.5,
        help="IOU threshold for evaluation, determining if a detection is TP or FP"
    )
    args_parser.add_argument(
        "--output_dir",
        required=True,
        type=str,
        help="directory path where evaluation outputs will be stored"
    )
    args_parser.add_argument(
        "--plot_dets_vs_anns",
        required=False,
        type=boolean_string,
        default = True,
        help="Option to generate image plots contrasting detections and annotations"
    )
    args_parser.add_argument(
        "--sep_plots",
        required=False,
        type=boolean_string,
        default = False,
        help="Option to generate separate image plots for detections and annotations. If False, "
        "draw both in the same plot"
    )
    args_parser.add_argument(
        "--get_details",
        required=False,
        type=boolean_string,
        default = False,
        help="Option to return datasets with evaulation details for detections and ground truths "
    )

        
    args = vars(args_parser.parse_args())   
    
    #breakpoint()
    # --- Start runtime timer
    run_start = time()
        
    # --- Clean output directory of all subdirectories and files from a previous run
    clean_output_dir(args["output_dir"])
    
        
    
    # --------------------------------- #
    # --      Initiate Logger       --- #
    # --------------------------------- #  

    os.makedirs(args["output_dir"], exist_ok=True)
    log_filename = os.path.join(args["output_dir"], "log_sscd_evaluation.log")
    
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
    
    
           
    
    # ------------------------------------------------- #
    # --  Retrieve image ID's from each data set    --- #
    # ------------------------------------------------- #  
    
    logger.info("Fetching image ID's from each dataset")
        
    # images
    
    img_filepaths = glob.glob(args["img_dir"] + os.path.sep + "*.jpg")
    if len(img_filepaths) == 0:
        FileNotFound_logAndOut("No JPG image files found in directory: {}".format(args["img_dir"]))
        
    img_ids = [Path(name).stem for name in img_filepaths]
        
    
    # annotations   
    # TODO: Handle case where already in txt format
    ann_filepaths = glob.glob(args["anns_dir"] + os.path.sep + "*.xml")
    ann_format = "xml"
    if len(ann_filepaths) == 0:
        ann_filepaths = glob.glob(args["anns_dir"] + os.path.sep + "*.txt")
        ann_format = "txt"
    if len(ann_filepaths) == 0:
        FileNotFound_logAndOut("No XML or TXT annotation files found in directory: {}".format(args["anns_dir"]))
        
    ann_ids =[Path(name).stem for name in ann_filepaths]
    
    
    # detections
    try:
        dets = pd.read_csv(args["dets_csv"])
    except FileNotFoundError:
        FileNotFound_logAndOut("No such file or directory: {}".format(args["dets_csv"]))
        
    det_ids = dets.img_id.unique().tolist()

    

    
    # --------------------------------- #
    # --   Check ID's congruency    --- #
    # --------------------------------- #  

    logger.info("Checking image ID's matching between detasets")

     # find unmatched ID's
    img_id_missing = [x for x in ann_ids if x not in set(img_ids)]
    ann_id_missing = [x for x in img_ids if x not in set(ann_ids)]
    det_id_missing = [x for x in img_ids if x not in set(det_ids)]
    
    # Raise error for missing images
    if len(img_id_missing) > 0:        
        img_missing = [x + ".jpg" for x in img_id_missing]        
        FileNotFound_logAndOut(
            "Missing the following image file(s):"
            f"\n\n\t{unpack_for_string(img_missing)}"
           "\n\n\tOne image per annotation file required, with matching file names "
           "(e.g. 'img01.xml' contains annotations for 'img01.jpg')"
           )
        
    # Raise error for missing detection data
    if len(det_id_missing) > 0:        
        det_missing = [x + ".jpg" for x in det_id_missing]        
        FileNotFound_logAndOut(
            "Missing detection data for the following image file(s):"
            f"\n\n\t{unpack_for_string(det_missing)}"
            "\n\n\tPlease ensure the above image(s) are included in the "
            "detection step before performing the evaluation"
            )
        
    
    # Prompt user with decision over missing annotation files, raising error if 
    # incongruence is unintentional, or carrying on otherwise
    if len(ann_id_missing) > 0:        
        ann_missing = [x + ".xml" for x in ann_id_missing]        
        logger.warning(
            "Missing the following annotation file(s):"
            f"\n\n\t{unpack_for_string(ann_missing)}"
            "\n\n\tDo you wish to continue with the evaluation? If yes, "
            "assumes no target object was found in the associated images during the "
            "labelling process."
            "\n\tAlternatively, either label the associated images or exclude "
            "them from evaluation.\n"
            )
        
        if query_yes_no("Continue with evaluation?") == 0:
            FileNotFound_logAndOut("Ending prematurely due to missing annotation file")

               
    
 
    
    # ------------------------------------------------------------------ #
    # --    Prepare detections and annotations data for evaluator     -- #
    # ------------------------------------------------------------------ #  
    
    logger.info("Preparing data for evaluation ")
    
    # --- Annotations (ground truth bounding boxes): convert from Pascal VOC xlm to txt files
    
    anns_temp_dir = args["anns_dir"]
    if ann_format == "xml":
        anns_temp_dir = os.path.join(args["output_dir"], "temp", "gt_temp")
        os.makedirs(anns_temp_dir, exist_ok=True)
        for ann_id in ann_ids:
            pascal_to_evaltxt(args["anns_dir"], ann_id, anns_temp_dir)
    
    # generate empty text files for missing xlm annotation files
    for ann_id in ann_id_missing:
        ann_filepath = os.path.join(anns_temp_dir, ann_id + ".txt")
        open(ann_filepath, 'w').close()
        

        
    # --- Detections: save detections in each image in separate txt files
    # image IDs in detection data being used in evaluation
    det_ids_eval = [x for x in img_ids if x in set(det_ids)]
    dets_eval = dets[dets['img_id'].isin(det_ids_eval)] # subset detection data
    dets_eval = dets_eval.drop(columns = ["detection_nr", "img_prop"]) # Remove irrelevant columns
    
    # set up temporary directory to hold detection files
    dets_temp_dir = os.path.join(args["output_dir"], "temp", "dets_temp")
    os.makedirs(dets_temp_dir, exist_ok=True)
    
    # write out detection bounding boxes in each image in separate files
    dets_eval.groupby("img_id").apply(write_detections_per_img, det_subdir = dets_temp_dir)
    
    
    
    # ---------------------------------------------------------------------------- #
    # --    Draw annotations and detections in images, if required by user      -- #
    # ---------------------------------------------------------------------------- #
    
    
    if(args["plot_dets_vs_anns"]):
        
        logger.info("Plotting images contrasting detections vs annotations")
        
        # Create directory to take detection images, if required
        dets_vs_anns_img_dir = os.path.join(args["output_dir"], "dets_vs_anns_plots")
        os.makedirs(dets_vs_anns_img_dir, exist_ok=True)

        for img_filepath, img_id in tqdm(zip(img_filepaths, img_ids), total = len(img_filepaths), 
                                         ascii=True, ncols=120):
                
            # read-in original img as a array of pixel intensities
            img_orig = mpimg.imread(img_filepath)
            
            # detections in current image
            img_dets = dets.query('img_id == @img_id')
            
            # read in annotation txt file for current image
            img_anns = pd.read_csv(os.path.join(anns_temp_dir, img_id + ".txt"), 
                                 header=None, sep = " ",
                                 names=["class_name", "xmin", "ymin", "xmax", "ymax"])
            
            # plot detections and, optionally, annotations
            plot_detections(
                img = img_orig, 
                dets = img_dets, 
                output_dir = dets_vs_anns_img_dir, 
                draw_ann = True, 
                anns = img_anns, 
                anns_sepPlot = args["sep_plots"], 
                plot_conf = True, 
                draw_det_num = True
                )
                        
            ## end of loop
       
    
    
    # ----------------------------------------------------- #
    # --               Perform evaluation                -- #
    # ----------------------------------------------------- #  
    
    logger.info("Performing evaluation and computing metrics\n") 
    
    #breakpoint()
    evaluate(
        gtFolder = anns_temp_dir, 
        detFolder = dets_temp_dir,
        savePath = args["output_dir"],
        iouThreshold = args["iou_threshould"],
        gtFormat = "xyrb",
        detFormat ="xyrb",
        gtCoordinates = "abs",
        detCoordinates = "abs",
        showPlot=True,
        #imgSize = (3904,64),
        get_details = args["get_details"]
        )

    logger.info("All outputs saved to %s", args["output_dir"]) 

    ## --- Summarise Run
    num_images = len(img_ids)   
    num_dets = len(dets_eval)
    
    
    # calculate runtime duration (mins)
    run_duration = round((time() - run_start)/60, 2)
     
    logger.info("Evaluation finished"
                "\n\n---------------------------------------------------------"
                f"\nRuntime duration: {run_duration} mins"
                f"\nImages processed: {num_images}"
               # f"\nAnnotations considered: {num_anns}"
                f"\nDetections evaluated: {num_dets}"
                "\n---------------------------------------------------------")   
        

    # Clean temporary folders
    clean_output_dir(os.path.join(args["output_dir"], "temp"))

    # Stop logging process
    logging.shutdown()
    


    
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    __spec__ = None
    main()
    
    
    
