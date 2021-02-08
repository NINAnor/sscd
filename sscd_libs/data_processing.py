# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 19:45:28 2021

@author: Bruno Caneco

TODO
"""

# import built-in modules
import os
import glob
from pathlib import Path
import concurrent.futures
import logging
# import installed packages/libraries
from PIL import Image
from tqdm import tqdm
import numpy as np
logger = logging.getLogger(__name__)
def tiff_to_jpg(tiff_input_filepath, jpg_output_filepath):
    """
    Converts a tiff image to jpeg format.

    Args
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
    
    Args
    -----
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



