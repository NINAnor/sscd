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

# built-in modules
import argparse
import os
import glob
from pathlib import Path

# installed packages/libraries
from PIL import Image   # installed from pip, following https://pillow.readthedocs.io/en/latest/installation.html#basic-installation
from tqdm import tqdm



def convert_to_jpeg(input_imgs_dir, output_imgs_dir):
    
    """
    Converts images located within the directory into jpeg format.

    :param input_imgs_dir: path to directory where image files are located. 
        Input formats accepted: TIFF, PGN and JPG. 
        Jpeg files are simply copied to the output directory
    :param output_imgs_dir: path directory where jpeg image files should be written
    :return: 0 to indicate successful completion
    """
        
    # --- list image pathfiles in input directory
    types = ('*.tif', '*.png', '*.jpg') # file types accepted
    img_filepaths = []
    for ftype in types:
        img_filepaths.extend(glob.glob(input_imgs_dir + "/" + ftype))
        
    if len(img_filepaths) == 0:
        raise Exception('No images of type TIFF or PNG found in input folder')
    
    for f in tqdm(img_filepaths, ascii = True, ncols = 150,
                  desc = "Converting images files to jpeg format"):
        im = Image.open(f)
        name = Path(f).stem
        outfile = os.path.join(output_imgs_dir, name + '.jpg')
        im.save(outfile, 'JPEG', quality=95)
        
    return 0






def main():
    
    # parse the command line arguments
    args_parser = argparse.ArgumentParser()
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
        help="directory path where all outputs will be stored",
    )
        
    args = vars(args_parser.parse_args())
       
    
    
    # --- Create destination directories
    
    # scale jpeg images
    scales_jpegs_dir = os.path.join(args["output_dir"], "jpegs", "scales")
    os.makedirs(scales_jpegs_dir, exist_ok=True)
    
    # transect jpeg images
    transects_jpegs_dir = os.path.join(args["output_dir"], "jpegs", "transects")
    os.makedirs(transects_jpegs_dir, exist_ok=True)
    
    #breakpoint()
    # --- Convert image files to jpeg format and saving them in the destination directory
    convert_to_jpeg(args["img_dir"], scales_jpegs_dir)
    
    
    
    #tiff_to_jpeg(img_dir, scale_jpegs_dir, quality = quality)
    
    
    
# ------------------------------------------------------------------------------
if __name__ == "__main__":
   
    main()    
    
    
    
    
    