# -*- coding: utf-8 -*-

'''
Script:
    commons.py
Description:
    Useful auxiliar commons functions.
Author:
    Jose Rios Rubio
Creation date:
    02/11/2020
Last modified date:
    25/12/2020
Version:
    1.0.1
'''

################################################################################
### Imported modules

from os import path, remove, makedirs
from datetime import datetime

################################################################################
### Constants

DATE_EPOCH = datetime.utcfromtimestamp(0)

################################################################################
### Functions


def printts(to_print="", timestamp=True):
    '''printts with timestamp.'''
    print_without_ts = False
    # Normal print if timestamp is disabled
    if (not timestamp):
        print_without_ts = True
    else:
        # If to_print is text and not other thing
        if isinstance(to_print, str):
            # Normalize EOLs to new line
            to_print = to_print.replace("\r", "\n")
            # If no text provided or text just contain spaces or EOLs
            if to_print == "":
                print_without_ts = True
            elif (" " in to_print) and (len(set(to_print)) == 1):
                print_without_ts = True
            elif ("\n" in to_print) and (len(set(to_print)) == 1):
                print_without_ts = True
            else:
                # Normal print for all text start EOLs
                num_eol = -1
                for character in to_print:
                    if character == '\n':
                        print("")
                        num_eol = num_eol + 1
                    else:
                        break
                # Remove all text start EOLs (if any)
                if num_eol != -1:
                    to_print = to_print[num_eol+1:]
    if print_without_ts:
        print(to_print)
    else:
        # Get actual time and print with timestamp
        actual_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print("{}: {}".format(actual_date, to_print))


def get_unix_epoch():
    '''Get UNIX Epoch time (seconds sins 1970)'''
    epoch = 0
    try:
        epoch = int((datetime.today().utcnow() - DATE_EPOCH).total_seconds())
    except Exception as e:
        printts("{}".format(file_path, str(e)))
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
    barray = bytearray(b"\xe2\x80\x8e")
    str_to_modify = str_to_modify.encode("utf-8")
    for b in str_to_modify:
        barray.append(b)
    str_to_modify = barray.decode("utf-8")
    return str_to_modify


def create_parents_dirs(file_path):
    '''Create all parents directories from provided file path (mkdir -p $file_path).'''
    try:
        parentdirpath = path.dirname(file_path)
        if not path.exists(parentdirpath):
            makedirs(parentdirpath, 0o775)
    except Exception as e:
        printts("ERROR - Can't create parents directories of {}. {}".format(file_path, str(e)))


def file_write(file_path, text="", mode="a"):
    '''Write a text or a list of text lines to plain text file.'''
    # Create file path directories and determine if file exists
    create_parents_dirs(file_path)
    if not path.exists(file_path):
        printts("File {} not found, creating it...".format(file_path))
    # Try to Open and write to the file
    try:
        with open(file_path, mode, encoding="utf-8") as f:
            if type(text) is str:
                f.write(text)
            elif type(text) is list:
                for line in text:
                    f.write("{}\n".format(line))
    except Exception as e:
        printts("ERROR - Can't write to file {}. {}".format(file_path, str(e)))


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
    except Exception as e:
        printts("Error when opening file \"{}\". {}".format(file_path, str(e)))
    return list_read_lines


def list_remove_element(the_list, the_element):
    '''Safe remove an element from a list.'''
    try:
        i = the_list.index(the_element)
        del the_list[i]
    except Exception as e:
        # The element could not be in the list
        printts("ERROR - Can't remove element from a list. {}".format(str(e)))
        return False
    return True
