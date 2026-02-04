#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    check_regex_url.py
Description:
    Check the regex URL detection.
'''

###############################################################################
# Standard Libraries
###############################################################################

# Logging Library
import logging

# Regular Expressions Library
import re

# System Library
from sys import argv as sys_argv
from sys import exit as sys_exit

# Error Traceback Library
from traceback import format_exc

# Constants Library
from constants import (
    SCRIPT_PATH, CONST, TEXT
)


###############################################################################
# Logger Setup
###############################################################################

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


###############################################################################
# Functions
###############################################################################

def load_urls_regex(file_path):
    '''Load URL detection Regex from IANA TLD list text file.'''
    tlds_str = ""
    list_file_lines = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if line is None:
                    continue
                if line in ["", "\r\n", "\r", "\n"]:
                    continue
                # Ignore lines that start with # (first header line of
                # IANA TLD list file)
                if line[0] == "#":
                    continue
                line = line.lower()
                line = line.replace("\r", "")
                line = line.replace("\n", "|")
                list_file_lines.append(line)
    except Exception:
        logger.error(format_exc())
        logger.error("Fail to open file \"%s\"", file_path)
    if len(list_file_lines) > 0:
        # Remove last '|' from last TLDs list item
        num_tlds = len(list_file_lines)
        last_tld = list_file_lines[num_tlds-1]
        if last_tld[-1] == '|':
            last_tld = last_tld[:-1]
            list_file_lines[num_tlds-1] = last_tld
        # Add all TLDs substring to the URL Regex
        tlds_str = "".join(list_file_lines)
    CONST["REGEX_URLS"] = CONST["REGEX_URLS"].format(tlds_str)


def print_regex():
    print("")
    print("-----------------------")
    print("")
    print(CONST["REGEX_URLS"])
    print("")


def check_url(text):
    has_url = re.findall(CONST["REGEX_URLS"], text)
    if has_url:
        print(f"{text} - URL")
    else:
        print(f"{text} - NOT URL")


###############################################################################
# Main Function
###############################################################################

def main(argc, argv):
    '''
    Main Function.
    '''
    print_regex()
    load_urls_regex(f'{SCRIPT_PATH}/{CONST["F_TLDS"]}')
    print_regex()
    check_url("hola.mundo")
    check_url("asdf.com")
    check_url("9.90")
    check_url("09.00")
    return 0


###############################################################################
# Runnable Main Script Detection
###############################################################################

if __name__ == "__main__":
    logger.info("Application start")
    return_code = main(len(sys_argv) - 1, sys_argv[1:])
    logger.info("Application exit (%d)", return_code)
    sys_exit(return_code)
