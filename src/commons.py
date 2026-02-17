# -*- coding: utf-8 -*-

'''
Script:
    commons.py
Description:
    Useful auxiliary commons functions.
Author:
    Jose Miguel Rios Rubio
Creation date:
    02/11/2020
Last modified date:
    28/12/2022
Version:
    1.0.5
'''

###############################################################################
# Imported modules
###############################################################################

# Date and Time Library
from datetime import datetime

# Logging Library
import logging

# Operating System Library
from os import path, makedirs

# Persistent RAM data (save/restore "session")
from pickle import dump as pickle_dump
from pickle import load as pickle_load

# Error Traceback Library
from traceback import format_exc

# Data Types Hints Library
from typing import Union


###############################################################################
# Logger Setup
###############################################################################

logger = logging.getLogger(__name__)


###############################################################################
# Functions
###############################################################################

def get_unix_epoch():
    '''
    Get UNIX Epoch time (seconds sins 1970).
    '''
    epoch = 0
    try:
        date_epoch = datetime.utcfromtimestamp(0)
        epoch = int((datetime.today().utcnow() - date_epoch).total_seconds())
    except Exception:
        logger.error(format_exc())
    return epoch


def is_int(element):
    '''
    Check if the string is an integer number.
    '''
    try:
        int(element)
        return True
    except ValueError:
        return False


def add_lrm(str_to_modify: str):
    '''
    Add a Left to Right Mark (LRM) at provided string start.
    '''
    try:
        byte_array = bytearray(b"\xe2\x80\x8e")
        str_to_modify_bytes = str_to_modify.encode("utf-8")
        for char in str_to_modify_bytes:
            byte_array.append(char)
        str_to_modify = byte_array.decode("utf-8")
    except Exception:
        logger.error(format_exc())
    return str_to_modify


def rm_lrm(str_to_modify: str):
    '''
    Remove Left to Right Mark (LRM) from provided string start.
    '''
    try:
        if str_to_modify[0] == "\u200e":
            str_to_modify = str_to_modify[1:]
    except Exception:
        logger.error(format_exc())
    return str_to_modify


def create_parents_dirs(file_path: str):
    '''
    Create all parents directories from provided file path
    (mkdir -p $file_path).
    '''
    try:
        parent_dir_path = path.dirname(file_path)
        if not path.exists(parent_dir_path):
            makedirs(parent_dir_path, 0o775)
    except Exception:
        logger.error(format_exc())
        logger.error("Can't create parents directories of %s.", file_path)


def file_exists(file_path: str):
    '''
    Check if the given file exists.
    '''
    return path.exists(file_path)


def file_write(
        file_path: str,
        text: Union[str, list] = "",
        mode: str = "a"):
    '''
    Write a text or a list of text lines to plain text file.
    '''
    write_ok = False
    if text is None:
        return False
    # Create file path directories and determine if file exists
    create_parents_dirs(file_path)
    if not path.exists(file_path):
        logger.info("File %s not found, creating it...", file_path)
    # Try to Open and write to the file
    try:
        with open(file_path, mode, encoding="utf-8") as file:
            if isinstance(text, str):
                file.write(text)
            elif isinstance(text, list):
                for line in text:
                    file.write(f"{line}\n")
            write_ok = True
    except Exception:
        logger.error(format_exc())
        logger.error("Can't write to file %s", file_path)
    return write_ok


def file_read(file_path: str):
    '''
    Read content of a plain text file and return a list of each text line.
    '''
    list_read_lines = []
    try:
        with open(file_path, "r", encoding="utf8") as file:
            for line in file:
                if line is None:
                    continue
                if line in ["", "\r\n", "\r", "\n"]:
                    continue
                line = line.replace("\r", "")
                line = line.replace("\n", "")
                list_read_lines.append(line)
    except Exception:
        logger.error(format_exc())
        logger.error("Error when opening file %s", file_path)
    return list_read_lines


def list_remove_element(the_list: list, the_element):
    '''
    Safe remove an element from a list.
    '''
    try:
        if the_element not in the_list:
            return False
        i = the_list.index(the_element)
        del the_list[i]
    except Exception:
        # The element could not be in the list
        logger.error(format_exc())
        logger.error("Can't remove element from a list")
        return False
    return True


def pickle_save(pickle_file_path: str, data):
    '''
    Save data to pickle file.
    '''
    try:
        with open(pickle_file_path, "wb") as file:
            pickle_dump(data, file)
    except Exception:
        logger.error(format_exc())
        return False
    return True


def pickle_restore(pickle_file_path: str):
    '''
    Load data from pickle file.
    '''
    try:
        with open(pickle_file_path, "rb") as file:
            last_session_data = pickle_load(file)
    except Exception:
        logger.error(format_exc())
        return None
    return last_session_data
