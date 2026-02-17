#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    change_config_all_groups.py
Description:
    Change a config on all stored group configurations json files.
Usage:
    0. Be careful!
    1. Move this scipt to src/ directory
    2. Set the config key-value to modify (CONFIG_KEY & CONFIG_VALUE)
    3. Run the script
'''

###############################################################################
# Standard Libraries
###############################################################################

# Logging Library
import logging

# Operating System Library
import os

# Collections Data Types Library
from collections import OrderedDict

# System Library
from sys import argv as sys_argv
from sys import exit as sys_exit

# Error Traceback Library
from traceback import format_exc


###############################################################################
# Local Libraries
###############################################################################

# Constants Library
from constants import (
    CONST, CMD
)

# Thread-Safe JSON Library
from tsjson import TSjson


###############################################################################
# Logger Setup
###############################################################################

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


###############################################################################
# JSON Chat Config File Functions
###############################################################################

def get_default_config_data():
    '''
    Get default config data structure.
    '''
    config_data = OrderedDict([
        ("Title", CONST["INIT_TITLE"]),
        ("Link", CONST["INIT_LINK"]),
        ("Language", CONST["INIT_LANG"]),
        ("BiLang", CONST["INIT_BILANG"]),
        ("Enabled", CONST["INIT_ENABLE"]),
        ("URL_Enabled", CONST["INIT_URL_ENABLE"]),
        ("RM_All_Msg", CONST["INIT_RM_ALL_MSG"]),
        ("Captcha_Chars_Mode", CONST["INIT_CAPTCHA_CHARS_MODE"]),
        ("Captcha_Time", CONST["INIT_CAPTCHA_TIME"]),
        ("Captcha_Difficulty_Level", CONST["INIT_CAPTCHA_DIFFICULTY_LEVEL"]),
        ("Fail_Restriction", CMD["RESTRICTION"]["KICK"]),
        ("Restrict_Non_Text", CONST["INIT_RESTRICT_NON_TEXT_MSG"]),
        ("Rm_Result_Msg", CONST["INIT_RM_RESULT_MSG"]),
        ("Rm_Welcome_Msg", CONST["INIT_RM_WELCOME_MSG"]),
        ("Poll_Q", ""),
        ("Poll_A", []),
        ("Poll_C_A", 0),
        ("Welcome_Msg", "-"),
        ("Welcome_Time", CONST["T_DEL_WELCOME_MSG"]),
        ("Ignore_List", [])
    ])
    # Feed Captcha Poll Options with empty answers for expected max num
    for _ in range(0, CONST["MAX_POLL_OPTIONS"]):
        config_data["Poll_A"].append("")
    return config_data


def get_config(chat_id):
    path_cfg_file = f"{CONST["CHATS_DIR"]}/{chat_id}/{CONST["F_CONF"]}"
    fjson_config = TSjson(path_cfg_file)
    config_data = fjson_config.read()
    if not config_data:
        # config_data = get_default_config_data()
        # fjson_config.write(config_data)
        return None
    return fjson_config


def get_groups_configs_chat_id():
    list_chat_id = [
        file_name for file_name in os.listdir(CONST["CHATS_DIR"])
        if os.path.isdir(os.path.join(CONST["CHATS_DIR"], file_name))
    ]
    return list_chat_id


def change_config(cfg_key, cfg_value):
    l_chat_id = get_groups_configs_chat_id()
    for chat_id in l_chat_id:
        # Read current config
        logger.info("Reading config of %s", chat_id)
        fjson_config = get_config(chat_id)
        if not fjson_config:
            logger.error("Missing config at %s", chat_id)
            return False
        cfg = fjson_config.read()
        missing_key = False
        if cfg_key not in cfg:
            logger.warning("Missing key \"%s\" at config %s", cfg_key, chat_id)
            missing_key = True
        # Apply new value to config
        success = False
        if not missing_key:
            if cfg[cfg_key] == cfg_value:
                success = True
        if not success:
            cfg[cfg_key] = cfg_value
            success = fjson_config.write(cfg)
        if not success:
            logger.error("Fail to write config of %s", chat_id)
            return False
        if missing_key:
            logger.info("Added config of %s: \"%s\" : %s",
                        chat_id, cfg_key, cfg_value)
        else:
            logger.info("Updated config of %s: \"%s\" : %s",
                        chat_id, cfg_key, cfg_value)
    return True


###############################################################################
# Main Function
###############################################################################

def main(argc, argv):
    '''
    Main Function.
    '''
    # Disable unused arguments
    del argc
    del argv
    # Change Configuration on all json files
    CONFIG_KEY = "RM_All_Msg"
    CONFIG_VALUE = True
    success = change_config(CONFIG_KEY, CONFIG_VALUE)
    if success:
        success = 0
    else:
        success = 1
    return success


###############################################################################
# Runnable Main Script Detection
###############################################################################

if __name__ == "__main__":
    return_code = main(len(sys_argv) - 1, sys_argv[1:])
    logger.info("Exit (%d)", return_code)
    sys_exit(return_code)
