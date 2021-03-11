# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 18:13:27 2021


Module for miscellaneous utility functions

@author: Bruno Caneco
"""

import shutil
import os
from distutils.util import strtobool

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


# ------------------------------------------------------------------------------
def query_yes_no(question, default='no'):
    
    """
    hacked from https://gist.github.com/garrettdreyfus/8153571
    """
    
    if default is None:
        prompt = " [y/n] "
    elif default == 'yes':
        prompt = " [Y/n] "
    elif default == 'no':
        prompt = " [y/N] "
    else:
        raise ValueError(f"Unknown setting '{default}' for default.")

    while True:
        try:
            resp = input(question + prompt).strip().lower()
            if default is not None and resp == '':
                return default == 'yes'
            else:
                return strtobool(resp)
        except ValueError:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
    