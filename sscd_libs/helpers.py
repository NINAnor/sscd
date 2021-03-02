# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 18:13:27 2021


Module for miscellaneous utility functions

@author: dmp
"""

import shutil
import os


# ------------------------------------------------------------------------------
def boolean_string(s):
    
    """
    dealing with args_parser issues when taking boolean variables as inputs
    """

    if s not in {'False', 'True'}:
        raise ValueError('Not a valid boolean string')
    return s == 'True'



# ------------------------------------------------------------------------------
def clean_output_dir(dir_path):
        
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            print("Error: %s : %s" % (dir_path, e.strerror))


# ------------------------------------------------------------------------------
def unpack_for_string(s, sep = '\n\t'):
    
    """    
    Little utility function to unpack list elements for use in logging messages 
    """
    
    return sep.join(str(x) for x in s)