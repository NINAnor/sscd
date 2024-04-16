# import built-in modules
import argparse
import os
import glob
import shutil
from time import time
from pathlib import Path


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


# ------------------------------------------------------------------------------
def main():

    base_dir = 'Z:\Adult_Salmon_Scales\Salmon_scale_circuli_detection\SSCD_data\detection_accuracy_analysis'
    ann_dir = os.path.join(base_dir,'circuli_anns_Bruno_original_90_padded_xml')
    out_dir = os.path.join(base_dir,'circuli_anns_Bruno_original_90_padded_txt')

    # annotations   
    ann_filepaths = glob.glob(ann_dir + os.path.sep + "*.xml")
    ann_ids =[Path(name).stem for name in ann_filepaths]
   

    # --- Annotations (ground truth bounding boxes): convert from Pascal VOC xlm to txt files
    anns_temp_dir = os.path.join(out_dir)
    os.makedirs(anns_temp_dir, exist_ok=True)
    
    for ann_id in ann_ids:
        pascal_to_evaltxt(ann_dir, ann_id, anns_temp_dir)

