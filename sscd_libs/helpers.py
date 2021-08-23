# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 18:13:27 2021


Module for miscellaneous utility functions

@author: Bruno Caneco
"""

import shutil
import os
from distutils.util import strtobool
import requests 
from tqdm import tqdm

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
            
            



# ------------------------------------------------------------------------------
def download_url(url, save_filepath, chunk_size=1024):
    """
    Download file from a url path

    Parameters
    ----------
    url : str
        the url address to file of interest
    save_path : str
        local path to downloaded file
    chunk_size : int, optional
        DESCRIPTION. size of chunk to download in each iteration The default is 128.

    Returns
    -------
    None.

    """
    
    # Streaming, so we can iterate over the response
    r = requests.get(url, stream=True)
    
    #breakpoint()
    
    file_size_bytes = int(r.headers.get("content-length", 0))

    #niter = int(file_size/chunk_size)
    pbar = tqdm(total=file_size_bytes, position=0, leave=True, ascii=True, 
                desc = "Downloading file", unit = "iB", unit_scale = True) #, ncols=120,
    
    with open(save_filepath, 'wb') as file:
        for chunk in r.iter_content(chunk_size=chunk_size):
            pbar.update(len(chunk))
            file.write(chunk)
    
    pbar.close()
                
    