# -*- coding: utf-8 -*-

'''
Script:
    tsjson.py
Description:
    Thread-Safe JSON files read/write library.
Author:
    Jose Miguel Rios Rubio
Creation date:
    20/07/2017
Last modified date:
    30/12/2022
Version:
    1.3.0
'''

###############################################################################
### Standard Libraries

# Logging Library
import logging

# Operating System Library
from os import makedirs as os_makedirs
from os import path as os_path
from os import remove as os_remove
from os import stat as os_stat

# JSON Library
from json import dump as json_dump
from json import load as json_load

# Collections Data Types Library
from collections import OrderedDict

# Threads and Multi-tasks Library
from threading import Lock

# Error Traceback Library
from traceback import format_exc

###############################################################################
### Logger Setup

logger = logging.getLogger(__name__)

###############################################################################
### Thread-Safe JSON Class

class TSjson():
    '''
    Thread-Safe JSON files read/write class.
    '''

    def __init__(self, file_name):
        '''
        Class Constructor.
        It initializes the Mutex Lock element and get the file path.
        '''
        self.lock = Lock()
        self.file_name = file_name


    def read(self):
        '''
        Thread-Safe Read of JSON file.
        It locks the Mutex access to the file, checks if the file exists
        and is not empty, and then reads it content and try to parse as
        JSON data and store it in an OrderedDict element. At the end,
        the lock is released and the read and parsed JSON data is
        returned. If the process fails, it returns None.
        '''
        read = {}
        # Try to read the file
        try:
            with self.lock:
                # Check if file exists and is not empty
                if not os_path.exists(self.file_name):
                    return {}
                if not os_stat(self.file_name).st_size:
                    return {}
                # Read the file and parse to JSON
                with open(self.file_name, "r", encoding="utf-8") as file:
                    read = json_load(file, object_pairs_hook=OrderedDict)
        except Exception:
            logger.error(format_exc())
            logger.error("Fail to read JSON file %s", self.file_name)
            read = None
        return read


    def write(self, data):
        '''
        Thread-Safe Write of JSON file.
        It checks and creates all the needed directories to file path if
        any does not exists. Then it locks the Mutex access to the file,
        opens and overwrites the file with the provided JSON data.
        '''
        write_result_ok = False
        if not data:
            return False
        # Check for directory path and create all needed directories
        directory = os_path.dirname(self.file_name)
        if not os_path.exists(directory):
            os_makedirs(directory)
        # Try to write the file
        try:
            with self.lock:
                with open(self.file_name, "w", encoding="utf-8") as file:
                    json_dump(data, fp=file, ensure_ascii=False, indent=4)
                write_result_ok = True
        except Exception:
            logger.error(format_exc())
            logger.error("Fail to write JSON file %s", self.file_name)
        return write_result_ok


    def delete(self):
        '''
        Remove JSON file from filesystem.
        '''
        remove_ok = False
        try:
            with self.lock:
                if os_path.exists(self.file_name):
                    os_remove(self.file_name)
                remove_ok = True
        except Exception:
            logger.error(format_exc())
            logger.error("Fail to remove JSON file %s", self.file_name)
        return remove_ok
