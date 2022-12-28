# -*- coding: utf-8 -*-

'''
Script:
    commons.py
Description:
    Useful auxiliar commons functions.
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
### Imported modules

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

###############################################################################
### Logger Setup

logger = logging.getLogger(__name__)

###############################################################################
### Functions

def get_unix_epoch():
    '''Get UNIX Epoch time (seconds sins 1970)'''
    epoch = 0
    try:
        date_epoch = datetime.utcfromtimestamp(0)
        epoch = int((datetime.today().utcnow() - date_epoch).total_seconds())
    except Exception:
        logger.error(format_exc())
    return epoch


def is_int(s):
    '''Check if the string is an integer number'''
    try:
        int(s)
        return True
    except ValueError:
        return False


def add_lrm(str_to_modify):
    '''Add a Left to Right Mark (LRM) at provided string start'''
    try:
        barray = bytearray(b"\xe2\x80\x8e")
        str_to_modify = str_to_modify.encode("utf-8")
        for b in str_to_modify:
            barray.append(b)
        str_to_modify = barray.decode("utf-8")
    except Exception:
        logger.error(format_exc())
    return str_to_modify


def rm_lrm(str_to_modify):
    '''Remove Left to Right Mark (LRM) from provided string start'''
    try:
        if str_to_modify[0] == "\u200e":
            str_to_modify = str_to_modify[1:]
    except Exception:
        logger.error(format_exc())
    return str_to_modify


def create_parents_dirs(file_path):
    '''Create all parents directories from provided file path (mkdir -p $file_path).'''
    try:
        parentdirpath = path.dirname(file_path)
        if not path.exists(parentdirpath):
            makedirs(parentdirpath, 0o775)
    except Exception:
        logger.error(format_exc())
        logger.error("Can't create parents directories of {%s}.", file_path)


def file_exists(file_path):
    '''Check if the given file exists'''
    if file_path is None:
        return False
    if not path.exists(file_path):
        return False
    return True


def file_write(file_path, text="", mode="a"):
    '''Write a text or a list of text lines to plain text file.'''
    # Create file path directories and determine if file exists
    create_parents_dirs(file_path)
    if not path.exists(file_path):
        logger.info("File {%s} not found, creating it...", file_path)
    # Try to Open and write to the file
    try:
        with open(file_path, mode, encoding="utf-8") as f:
            if type(text) is str:
                f.write(text)
            elif type(text) is list:
                for line in text:
                    f.write(f"{line}\n")
    except Exception:
        logger.error(format_exc())
        logger.error("Can't write to file {%s}", file_path)


def file_read(file_path):
    '''Read content of a plain text file and return a list of each text line.'''
    list_read_lines = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line is None:
                    continue
                if (line == "") or (line == "\r\n") or (line == "\r") or (line == "\n"):
                    continue
                line = line.replace("\r", "")
                line = line.replace("\n", "")
                list_read_lines.append(line)
    except Exception:
        logger.error(format_exc())
        logger.error("Error when opening file {%s}", file_path)
    return list_read_lines


def list_remove_element(the_list, the_element):
    '''Safe remove an element from a list.'''
    try:
        i = the_list.index(the_element)
        del the_list[i]
    except Exception as e:
        # The element could not be in the list
        logger.error(format_exc())
        logger.error("Can't remove element from a list")
        return False
    return True


def pickle_save(pickle_file_path, data):
    '''Save data to pickle file'''
    try:
        with open(pickle_file_path, "wb") as f:
            pickle_dump(data, f)
    except Exception:
        logger.error(format_exc())
        return False
    return True


def pickle_restore(pickle_file_path):
    '''Load data from pickle file'''
    try:
        with open(pickle_file_path, "rb") as f:
            last_session_data = pickle_load(f)
    except Exception:
        logger.error(format_exc())
        return None
    return last_session_data
