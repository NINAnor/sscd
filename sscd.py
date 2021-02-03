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
    -

"""

# import built-in modules
import argparse
import os
import glob
from pathlib import Path
import concurrent.futures
import shutil


# import installed packages/libraries
from PIL import Image
from tqdm import tqdm


# import local modules
from sscd_libs.detection import detect




import logging
#import sys


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
def tiff_to_jpg(tiff_input_filepath, jpg_output_filepath):
    """
    Converts a tiff image to jpeg format.

    Parameters
    ----------
    tiff_input_filepath : str
        filepath to tiff image file to be converted.
    jpg_output_filepath : str
        filepath to write the jpeg image.
    
    """
    
    im = Image.open(tiff_input_filepath)
    im.save(jpg_output_filepath, 'JPEG', quality=95)
    
    
    
    
# ------------------------------------------------------------------------------
def images_tiff_to_jpeg(input_imgs_dir, output_imgs_dir):
    
    """
    Wrapper to convert tiff images located within the directory into jpeg format.
    
    Parameters
    ----------
    input_imgs_dir : str
        path to directory where image files are located. Input formats accepted: 
            TIFF, TIF and JPG. Jpeg files are simply copied to the output 
            directory
    output_imgs_dir : str
        path directory where jpeg image files should be written
        
        
    Returns
    -------
    0 to indicate successful completion
    
    """

    # --- list image pathfiles in input directory with tiff (or jpg) formats
    types = ('*.tif', '*.tiff', '*.jpg') # file types accepted
    img_input_fpaths = []
    for ftype in types:
        img_input_fpaths.extend(glob.glob(input_imgs_dir + "/" + ftype))
        
    # Raise exception if there are no valid images present in input directory
    if len(img_input_fpaths) == 0:
        #raise ValueError('No images of type TIFF or PNG found in input folder')
        raise Exception('No images of type TIFF found in input folder')
        
    # --- generate output filepaths for converted images
    img_output_fpaths = [os.path.join(output_imgs_dir, Path(name).stem + '.jpg') 
                         for name in img_input_fpaths]
    
    # use a ProcessPoolExecutor to convert the  images in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        
        logger.info("Converting %d images to jpeg format", len(img_input_fpaths))
        
        # use the executor to map the converting function to the iterable of input paths
        list(tqdm(executor.map(tiff_to_jpg, img_input_fpaths, img_output_fpaths),
                  total=len(img_input_fpaths), ascii = True, ncols = 120))
        
    return 0



# ------------------------------------------------------------------------------
def clean_output_dir(dir_path):
    
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
        dest= "img_dir",
        required=True,
        type=str,
        help="directory path containing scale image files. Expects .tif images",
    )
    args_parser.add_argument(
        "--output_dir",
        dest= "output_dir",
        required=True,
        type=str,
        help="directory path where outputs will be stored",
    )
    args_parser.add_argument(
        "--dets_separate_files",
        dest= "dets_separate_files",
        required=False,
        type=boolean_string,
        default = False,
        help="Require detections in each image to be saved in separate files",
    )
    args_parser.add_argument(
        "--plot_detections",
        dest= "plot_detections",
        required=False,
        type=boolean_string,
        default = True,
        help="Plot images with detections?",
    )
        
    args = vars(args_parser.parse_args())
    
    
    
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
    
    # # scale images with focus detections
    # if args["plot_detections"]:
    #     focus_detection_images_dir = os.path.join(focus_detections_dir, "detection_images")
    #     os.makedirs(focus_detection_images_dir, exist_ok=True)
    # else:
    #     focus_detection_images_dir = None
       
        
    # --------------------------------------- #
    # --    Circuli detection pipeline    --- #
    # --------------------------------------- #  
    
    ## - 1. Convert image files to jpeg format and write them to ~/<output_dir>/jpegs/scales
    images_tiff_to_jpeg(
        args["img_dir"], 
        scales_jpegs_dir
        )
       
    #breakpoint()
            
    ## - 2. Focus detection    
    logger.info("Gearing up focus detector")
    detect(img_dir = scales_jpegs_dir, 
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
    logger.info("Finished focus detection")

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    __spec__ = None
    main()    
    
    
    
    
    