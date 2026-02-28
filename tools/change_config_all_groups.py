#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    change_config_all_groups.py
Description:
    Change a config on all stored group configurations json files.
Usage:
    0. Be careful (considerate to make a backup of groups config)!
    1. Move this scipt to src/ directory
    2. Set the config key to modify (CONFIG_KEY)
    3. Set the target value to modify (CONFIG_VALUE_TO_MODIFY)
    4. Set the new value to apply (CONFIG_VALUE)
    5. Run the script
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
# Setup
###############################################################################

# Target configuration key to modify
CONFIG_KEY = "Captcha_Chars_Mode"

# Target value of the key to modify (use "ALL" to force the change no
# matter it current value)
CONFIG_VALUE = "nums"  # "ALL"

# New value to set
CONFIG_NEW_VALUE = "video"

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
        ("Allow_Unverify_Msg", CONST["INIT_ALLOW_UNVERIFY_MSG"]),
        ("RM_All_Msg", CONST["INIT_RM_ALL_MSG"]),
        ("Captcha_Chars_Mode", CONST["INIT_CAPTCHA_MODE"]),
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


def change_config(target_key, target_value, new_value):
    update_all = False
    if target_value == "ALL":
        update_all = True
        logger.info("Modifying all groups config to \"%s\": \"%s\"...",
                    target_key, new_value)
    else:
        logger.info("Modifying groups config \"%s\": \"%s\" -> \"%s\"...",
                    target_key, target_value, new_value)
    l_chat_id = get_groups_configs_chat_id()
    for chat_id in l_chat_id:
        # Read current config
        logger.info("")
        logger.info("[%s] Reading config", chat_id)
        fjson_config = get_config(chat_id)
        if not fjson_config:
            logger.error("[%s] Missing config", chat_id)
            return False
        cfg = fjson_config.read()
        missing_key = False
        if target_key not in cfg:
            logger.warning("[%s] Missing key \"%s\"", chat_id, target_key)
            missing_key = True
        # Add missing key-value to config
        if missing_key:
            cfg[target_key] = new_value
            success = fjson_config.write(cfg)
            if not success:
                logger.error("[%s] Fail to write config", chat_id)
                return False
            logger.info("[%s] Added:    \"%s\" : \"%s\"",
                        chat_id, target_key, new_value)
            continue
        logger.info("[%s] Config:  \"%s\" : \"%s\"",
                    chat_id, target_key, cfg[target_key])
        # Skip change (write) of groups that already has this value
        if cfg[target_key] == new_value:
            logger.info("[%s] Skip (already has this value)", chat_id)
            continue
        # Update config to new value
        if update_all:
            cfg[target_key] = new_value
            success = fjson_config.write(cfg)
            if not success:
                logger.error("[%s] Fail to write config", chat_id)
                return False
            else:
                logger.info("[%s] Update config")
                logger.info("[%s] Changed: \"%s\" : \"%s\"",
                            chat_id, target_key, new_value)
            continue
        # Skip groups that doesnt have the target value to change
        if cfg[target_key] != target_value:
            logger.info("[%s] Skip (not target value)", chat_id)
            continue
        # Update target value
        cfg[target_key] = new_value
        success = fjson_config.write(cfg)
        if not success:
            logger.error("[%s] Fail to write config", chat_id)
            return False
        else:
            logger.info("[%s] Changed: \"%s\" : \"%s\"",
                        chat_id, target_key, new_value)
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
    logger.info("")
    success = change_config(CONFIG_KEY, CONFIG_VALUE, CONFIG_NEW_VALUE)
    logger.info("")
    if success:
        logger.info("Success")
        success = 0
    else:
        logger.info("Fail / Abort")
        success = 1
    return success


###############################################################################
# Runnable Main Script Detection
###############################################################################

if __name__ == "__main__":
    return_code = main(len(sys_argv) - 1, sys_argv[1:])
    logger.info("Exit (%d)", return_code)
    logger.info("")
    sys_exit(return_code)
