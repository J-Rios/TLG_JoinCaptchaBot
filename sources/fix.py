#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
### Imported modules

from sys import exit as sys_exit
from os import path, listdir
from tsjson import TSjson
from constants import CONST

###############################################################################
### JSON File Read-Write Functions

def get_chat_config(json_file, param):
    '''Get specific stored chat configuration property'''
    if json_file is None:
        return None
    config_data = json_file.read()
    if (not config_data) or (param not in config_data):
        return None
    return config_data[param]


def save_config_property(json_file, param, value):
    '''Store actual chat configuration in file'''
    if json_file is None:
        return False
    config_data = json_file.read()
    if (not config_data) or (param not in config_data):
        return False
    if value != config_data[param]:
        config_data[param] = value
        json_file.write(config_data)
    return True

###############################################################################
### Fix Function

def fix():
    # Ignore if data directory not found
    if not path.exists(CONST["CHATS_DIR"]):
        print("Data directory not found")
        return False
    # Get all data subdirectories names (chats ID)
    files = listdir(CONST["CHATS_DIR"])
    for f_chat_id in files:
        config_file = "{}/{}/{}".format(CONST["CHATS_DIR"], f_chat_id,
                CONST["F_CONF"])
        # Ignore if config file doesn't exists
        if not path.exists(config_file):
            print("{} | Ignoring (Config file not found)".format(f_chat_id))
            continue
        # Read config file JSON data and update it
        config_json = TSjson(config_file)
        captcha_timeout = get_chat_config(config_json, "Captcha_Time")
        if captcha_timeout is None:
            print("{} | Ignoring (Captcha_Time not found)".format(f_chat_id))
            continue
        if captcha_timeout > 20: # Max config time was 20 min
            print("{} | Ignoring (timeout over 20 min!)".format(f_chat_id))
            continue
        new_captcha_timeout = captcha_timeout * 60
        if new_captcha_timeout > 600:
            new_captcha_timeout = 600
        if not save_config_property(config_json, "Captcha_Time",
        new_captcha_timeout):
            print("{} | Fail to write the new value".format(f_chat_id))
            continue
        print("{} | Captcha_Time {} -> {}".format(f_chat_id, captcha_timeout,
                new_captcha_timeout))
    return True

###############################################################################
### Main Function

def main():
    '''Main Function'''
    print("Fixing...")
    rc = fix()
    if not rc:
        print("Fix fail")
        sys_exit(1)
    print("Fix applied")
    sys_exit(0)


if __name__ == "__main__":
    main()
