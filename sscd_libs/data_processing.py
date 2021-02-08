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
import math

# import installed packages/libraries
from PIL import Image
from tqdm import tqdm
import numpy as np

# import local modules
from tools.diagonal_crop import crop

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
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



# ------------------------------------------------------------------------------
def pol2cart(radius, phi):
    x = radius * np.cos(phi)
    y = radius * np.sin(phi)
    
    return [x, y]


# # ------------------------------------------------------------------------------
# def get_transect_base_coords(focus_centre, transect_rad, transect_width):
     
#     """
#     Compute the coordinates of the transect's base point, defined as the upper left point of the 
#     area to be cropped before rotation. 
#     Approached using a polar to cartesian system conversion, using the focus centre as the pole, 
#     as the base's angle and distance to the focus centre are always known
    
#     """
    
#     # Get polar coordinates
#     # get angle (radians) of base point in the polar plane - always perpendicular to transect angle
#     base_rad = transect_rad + math.pi/2
#     # get radial distance of base point = distance to focus center, known to be half of the transect width
#     base_radius = transect_width/2
    
#     # Convert to cartesian coords (relative to the pole)
#     base_xy_0 = pol2cart(base_radius, base_rad)
    
#     # Project coords in the image's coordinate space
#     # Note: sign needs to inverted for y coord as y-axis is inverted in image's 
#     #       space (i.e. coord (0,0) is at the top left of image)
#     base_xy = (focus_centre[0] + base_xy_0[0], focus_centre[1] - base_xy_0[1])
    
#     return base_xy




def get_transect_base_coords(focus_centre, transect_rad, transect_width):
     
    """
    Compute the coordinates of the transect's base point, defined as the upper left point of the 
    area to be cropped before rotation. 
    Approached using a polar to cartesian system conversion, using the focus centre as the pole, 
    as the base's angle and distance to the focus centre are always known
    
    """
    
    # Get polar coordinates
    # get angle (radians) of base point in the polar plane - always perpendicular to transect angle
    # Note: need to work with inverted angles as the y-axis for images is inverted 
    # (i.e. coord (0,0) is at the top left of image)
    base_rad = (2*math.pi - transect_rad) - math.pi/2
    # get radial distance of base point = distance to focus center, known to be half of the transect width
    base_radius = transect_width/2
    
    # Convert to cartesian coords (relative to the pole)
    base_xy_0 = pol2cart(base_radius, base_rad)
    
    # Project coords in the image's coordinate space
    base_xy = (focus_centre[0] + base_xy_0[0], focus_centre[1] + base_xy_0[1])
    
    return base_xy



# ------------------------------------------------------------------------------
def line_x_rectangle(a, b, x_min, y_min, x_max, y_max):
    
    """
    Line Clipping follwing Liang-Barsky Algorithm
    
    source: https://twinee.fr/2020-03-24-Liang-Barsky/
    """
    
    # breakpoint()

    # Intersections of f(x) = ax + b with the rectangle. (x, y, axis)
    p1, p2 = (x_min, a * x_min + b, 'x'), (x_max, a * x_max + b, 'x'), 
    p3, p4 = ((y_min - b) / a, y_min, 'y'), ((y_max - b) / a, y_max, 'y')
    # Python sorts them using the first key
    p1, p2, p3, p4 = sorted([p1, p2, p3, p4])
    
    # # Check if there is an intersection, returns the points otherwise
    # if p1[2] == p2[2]:
    #     return None
    # return p2[:2], p3[:2]
    #
    # BC: Commented out above chunk as I'n not sure if it's correct... 
    # If the line sits above or below the rectangle, p1[2] != p2[2] and so the 
    # condition doesn't hold.
    # Actually, the condition is excluding the special case when the line crosses
    # exactly the opposite corners of the rectangle. In that case p1 == p2 and 
    # p3 == p4, so returning p2 and p3 should give the desired output
    # Warning: only returning p2 and p3 doesn't account for the no intersection case,
    # but on the context of transects in scales, where the focus is always inside
    # the image, there is always an intersection
    
    return p2[:2], p3[:2]


# ------------------------------------------------------------------------------
def get_transect_length(focus_centre, transect_rad, im_width, im_height):
    
    """
    TODO
    """
   
    trans_slope = math.tan(2*math.pi - transect_rad) 
    trans_yint = (focus_centre[1] - trans_slope*focus_centre[0])
    
    # Getting the points of intersection between the transect line and the image limits
    # Using the Liang-Barsky Algorithm, with transect is interpreted as a linear function.
    # Thus, we get 2 intersection points on opposite sides of the image - sorted from left to right
    if trans_slope == 0:
        trans_x_img = ((0,trans_yint), (im_width,trans_yint))
    else:
        trans_x_img = line_x_rectangle(
        a = trans_slope, 
        b = trans_yint, 
        x_min = 0, 
        y_min = 0,
        x_max = im_width, 
        y_max = im_height
        )
    
    #breakpoint()
    
    # select which intersection to use 
    # 1st intersection if transect in 2nd or 3rd quadrants, 
    # 2nd intersection otherwise
    if 1/2*math.pi <= transect_rad <= 3/2*math.pi:
        trans_int = trans_x_img[0]
        #trans_int = (trans_int[0], trans_int[1] + im_height)
    else:
        trans_int = trans_x_img[1]
        #trans_int = (trans_int[0], trans_int[1] - im_height)
    
    # compute transect length using pythagoras theorem
    trans_adj_lt = focus_centre[0] - trans_int[0]    
    trans_opp_lt = focus_centre[1] - trans_int[1]
    trans_lt = math.sqrt(trans_adj_lt**2 + trans_opp_lt**2)     
        
    return trans_lt
    



# ------------------------------------------------------------------------------
def get_transects(focus_bbox, transect_degrees, img_filepath, output_dir):
    """
    Extract, and store, images of radial transects off the scale's focus
    
    Args:
    -----
        focus_bbox: dict
            focus bounding box limits (absolute measurements)
        
        transect_degrees: list
            Transect's radial angle(s) (in degrees)
        
        img_filepath: str
            path to scale image
            
        output_dir: str
            path to folder where transect images will be stored
        
    Returns:
    --------
        empty (saves images to output_dir)
        
    """
    
    im = Image.open(img_filepath)
    im_width, im_height = im.size
    bb_xmin = focus_bbox["xmin"]
    bb_ymin = focus_bbox["ymin"]
    bb_xmax = focus_bbox["xmax"]
    bb_ymax = focus_bbox["ymax"]
    bb_xcentre = (bb_xmax + bb_xmin)/2
    bb_ycentre = (bb_ymin + bb_ymax)/2    
    focus_centre = (bb_xcentre, bb_ycentre)
    trans_width = min((bb_xmax-bb_xmin), (bb_ymax - bb_ymin))/2
        
    img_id = Path(img_filepath).stem

    #breakpoint()
    
    for angle_deg in transect_degrees:     
               
        angle_rad = math.radians(angle_deg)
        base = get_transect_base_coords(focus_centre, angle_rad, trans_width)
        trans_length = get_transect_length(focus_centre, angle_rad, im_width, im_height)
        cropped_im = crop(im, base, angle_rad, trans_width, trans_length)
        transect_outfile = os.path.join(output_dir, img_id + f'_{angle_deg}.jpg')
        cropped_im.save(transect_outfile, 'JPEG')
         


