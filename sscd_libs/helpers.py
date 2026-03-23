# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 18:13:27 2021


Module for miscellaneous utility functions

@author: Bruno Caneco
"""

import shutil
import os
import requests
from tqdm import tqdm


# ------------------------------------------------------------------------------
def _strtobool(val):
    """Convert a string representation of truth to True or False."""
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"Invalid truth value {val!r}")


# ------------------------------------------------------------------------------
def boolean_string(s):
    """dealing with args_parser issues when taking boolean variables as inputs"""
    if s not in {"False", "True"}:
        raise ValueError("Not a valid boolean string")
    return s == "True"


# ------------------------------------------------------------------------------
def clean_output_dir(dir_path):
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            print("Error: %s : %s" % (dir_path, e.strerror))


# ------------------------------------------------------------------------------
def unpack_for_string(s, sep="\n\t"):
    """
    Little utility function to unpack list elements for use in logging messages
    """
    return sep.join(str(x) for x in s)


# ------------------------------------------------------------------------------
def query_yes_no(question, default="no"):
    """
    hacked from https://gist.github.com/garrettdreyfus/8153571
    """
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError(f"Unknown setting '{default}' for default.")

    while True:
        try:
            resp = input(question + prompt).strip().lower()
            if default is not None and resp == "":
                return default == "yes"
            else:
                return _strtobool(resp)
        except ValueError:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


# ------------------------------------------------------------------------------
def download_url(url, save_filepath, chunk_size=8192):
    """
    Download a file from a URL to a local path, with a progress bar.

    Parameters
    ----------
    url : str
        URL of the file to download.
    save_filepath : str
        Local path where the downloaded file will be saved.
    chunk_size : int, optional
        Size in bytes of each streamed chunk. Default is 8192.

    Raises
    ------
    ValueError
        If the server returns an HTML response instead of binary data,
        which typically indicates an error page or redirect rather than
        the expected file.
    requests.HTTPError
        If the server returns a non-2xx HTTP status code.
    """
    r = requests.get(url, stream=True)
    r.raise_for_status()

    content_type = r.headers.get("content-type", "")
    if "text/html" in content_type:
        raise ValueError(
            f"Expected a binary file but got an HTML response from {url!r}. "
            "The URL may be incorrect, require authentication, or be a "
            "folder/preview link rather than a direct download link."
        )

    file_size_bytes = int(r.headers.get("content-length", 0))

    pbar = tqdm(
        total=file_size_bytes,
        position=0,
        leave=True,
        ascii=True,
        desc="Downloading",
        unit="iB",
        unit_scale=True,
    )

    with open(save_filepath, "wb") as file:
        for chunk in r.iter_content(chunk_size=chunk_size):
            pbar.update(len(chunk))
            file.write(chunk)

    pbar.close()
