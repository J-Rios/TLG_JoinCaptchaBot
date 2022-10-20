#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    join_captcha_bot.py
Description:
    Telegram Bot that send a captcha for each new user who join a group, and
    remove them if they can not solve the captcha in a specified time.
Author:
    Jose Miguel Rios Rubio
Creation date:
    09/09/2018
Last modified date:
    15/10/2022
Version:
    1.27.0
'''

###############################################################################
### Imported modules

from platform import system as os_system

from signal import signal, SIGTERM, SIGINT
if os_system() != "Windows":
    from signal import SIGUSR1

import logging
import re

from sys import exit
from os import kill, getpid, path, remove, makedirs, listdir
from shutil import rmtree
from time import time, sleep
from threading import Thread
from collections import OrderedDict
from random import choice, randint
from json import dumps as json_dumps

from tsjson import TSjson
from multicolorcaptcha import CaptchaGenerator

from telegram import (
    Update, Chat, InputMediaPhoto, InlineKeyboardButton,
    InlineKeyboardMarkup, Poll
)

from telegram.ext import (
    CallbackContext, Updater, CommandHandler,
    ChatMemberHandler, MessageHandler, Filters,
    CallbackQueryHandler, PollAnswerHandler, Defaults
)

from telegram.utils.helpers import (
    escape_markdown
)

from telegram.error import (
    TelegramError, Unauthorized, BadRequest,
    TimedOut, NetworkError
)

from commons import (
    printts, is_int, add_lrm, file_exists, file_write, file_read,
    list_remove_element, get_unix_epoch, pickle_save, pickle_restore
)

from tlgbotutils import (
    tlg_send_msg, tlg_send_image, tlg_send_poll, tlg_stop_poll,
    tlg_answer_callback_query, tlg_delete_msg, tlg_edit_msg_media,
    tlg_ban_user, tlg_kick_user, tlg_user_is_admin, tlg_leave_chat,
    tlg_restrict_user, tlg_unrestrict_user, tlg_is_valid_user_id_or_alias,
    tlg_is_valid_group, tlg_alias_in_string, tlg_extract_members_status_change,
    tlg_get_msg, tlg_is_a_channel_msg_on_discussion_group, tlg_get_user_name,
    tlg_has_new_member_join_group
)

from constants import (
    SCRIPT_PATH, CONST, TEXT
)

###############################################################################
### Globals

updater = None
files_config_list = []
to_delete_in_time_messages_list = []
new_users = {}
connections = {}
th_0 = None
th_1 = None
force_exit = False

# Create Captcha Generator object of specified size (2 -> 640x360)
CaptchaGen = CaptchaGenerator(2)

###############################################################################
### Setup Bot Logger

log_level=logging.INFO
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)

###############################################################################
### Termination Signals Handler For Program Process

def signal_handler(signal,  frame):
    '''Termination signals (SIGINT, SIGTERM) handler for program process'''
    global force_exit
    global updater
    global th_0
    global th_1
    force_exit = True
    printts("Termination signal received. Releasing resources...")
    # Close the Bot instance (it wait for updater, dispatcher and other internals threads to end)
    if updater is not None:
        printts("Closing Bot...")
        updater.stop()
    # Launch threads to acquire all messages and users files mutex to ensure that them are closed
    # (make sure to close the script when no read/write operation on files)
    if files_config_list:
        printts("Closing resource files...")
        th_list = []
        for chat_config_file in files_config_list:
            t = Thread(target=th_close_resource_file, args=(chat_config_file["File"],))
            th_list.append(t)
            t.start()
        # Wait for all threads to end
        for th in th_list:
            if th.is_alive():
                th.join()
    # Wait to end threads
    printts("Waiting th_0 end...")
    if th_0 is not None:
        if th_0.is_alive():
            th_0.join()
    printts("Waiting th_1 end...")
    if th_1 is not None:
        if th_1.is_alive():
            th_1.join()
    # Save current session data
    save_session()
    # Close the program
    printts("All resources released.")
    printts("Exit 0")
    exit(0)


def th_close_resource_file(file_to_close):
    '''Threaded function to close resource files in parallel when closing Bot Script.'''
    file_to_close.lock.acquire()


### Signals attachment

signal(SIGTERM, signal_handler) # SIGTERM (kill pid) to signal_handler
signal(SIGINT, signal_handler)  # SIGINT (Ctrl+C) to signal_handler
if os_system() != "Windows":
    signal(SIGUSR1, signal_handler) # SIGUSR1 (self-send) to signal_handler

###############################################################################
### JSON Chat Config File Functions

def get_default_config_data():
    '''Get default config data structure'''
    config_data = OrderedDict(
    [
        ("Title", CONST["INIT_TITLE"]),
        ("Link", CONST["INIT_LINK"]),
        ("Language", CONST["INIT_LANG"]),
        ("Enabled", CONST["INIT_ENABLE"]),
        ("URL_Enabled", CONST["INIT_URL_ENABLE"]),
        ("RM_All_Msg", CONST["INIT_RM_ALL_MSG"]),
        ("Captcha_Chars_Mode", CONST["INIT_CAPTCHA_CHARS_MODE"]),
        ("Captcha_Time", CONST["INIT_CAPTCHA_TIME"]),
        ("Captcha_Difficulty_Level", CONST["INIT_CAPTCHA_DIFFICULTY_LEVEL"]),
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


def save_config_property(chat_id, param, value):
    '''Store actual chat configuration in file'''
    fjson_config = get_chat_config_file(chat_id)
    config_data = fjson_config.read()
    if not config_data:
        config_data = get_default_config_data()
    if (param in config_data) and (value == config_data[param]):
        return
    config_data[param] = value
    fjson_config.write(config_data)


def get_chat_config(chat_id, param):
    '''Get specific stored chat configuration property'''
    file = get_chat_config_file(chat_id)
    if file:
        config_data = file.read()
        if (not config_data) or (param not in config_data):
            config_data = get_default_config_data()
            save_config_property(chat_id, param, config_data[param])
    else:
        config_data = get_default_config_data()
        save_config_property(chat_id, param, config_data[param])
    return config_data[param]


def get_all_chat_config(chat_id):
    '''Get specific stored chat configuration property'''
    file = get_chat_config_file(chat_id)
    if file:
        config_data = file.read()
        if (not config_data):
            config_data = get_default_config_data()
    else:
        config_data = get_default_config_data()
    return config_data


def get_chat_config_file(chat_id):
    '''Determine chat config file from the list by ID. Get the file if exists or create it if not'''
    global files_config_list
    file = OrderedDict([("ID", chat_id), ("File", None)])
    found = False
    if files_config_list:
        for chat_file in files_config_list:
            if chat_file["ID"] == chat_id:
                file = chat_file
                found = True
                break
        if not found:
            chat_config_file_name = "{}/{}/{}".format(CONST["CHATS_DIR"], chat_id, CONST["F_CONF"])
            file["ID"] = chat_id
            file["File"] = TSjson(chat_config_file_name)
            files_config_list.append(file)
    else:
        chat_config_file_name = "{}/{}/{}".format(CONST["CHATS_DIR"], chat_id, CONST["F_CONF"])
        file["ID"] = chat_id
        file["File"] = TSjson(chat_config_file_name)
        files_config_list.append(file)
    return file["File"]

###############################################################################
### Telegram Related Functions

def tlg_send_msg_type_chat(bot, chat_type, chat_id, text,
        **kwargs_for_send_message):
    '''Send a telegram message normal or schedule to self-destruct depending
    of chat type (private chat - normal; group - selfdestruct).'''
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, text, **kwargs_for_send_message)
    else:
        tlg_send_selfdestruct_msg(bot, chat_id, text,
                **kwargs_for_send_message)


def tlg_send_selfdestruct_msg(bot, chat_id, message,
        **kwargs_for_send_message):
    '''tlg_send_selfdestruct_msg_in() with default delete time'''
    return tlg_send_selfdestruct_msg_in(bot, chat_id, message,
            CONST["T_DEL_MSG"], **kwargs_for_send_message)


def tlg_send_selfdestruct_msg_in(bot, chat_id, message, time_delete_sec,
        **kwargs_for_send_message):
    '''Send a telegram message that will be auto-delete in specified time'''
    sent_result = tlg_send_msg(bot, chat_id, message,
            **kwargs_for_send_message)
    if sent_result["msg"] is None:
        return None
    tlg_msg_to_selfdestruct_in(sent_result["msg"], time_delete_sec)
    return sent_result["msg"].message_id


def tlg_msg_to_selfdestruct(message):
    '''tlg_msg_to_selfdestruct_in() with default delete time'''
    tlg_msg_to_selfdestruct_in(message, CONST["T_DEL_MSG"])


def tlg_msg_to_selfdestruct_in(message, time_delete_sec):
    '''Add a telegram message to be auto-delete in specified time'''
    global to_delete_in_time_messages_list
    # Check if provided message has all necessary attributes
    if message is None:
        return False
    if not hasattr(message, "chat_id"):
        return False
    if not hasattr(message, "message_id"):
        return False
    if not hasattr(message, "from_user"):
        return False
    else:
        if not hasattr(message.from_user, "id"):
            return False
    # Get sent message ID and calculate delete time
    chat_id = message.chat_id
    user_id = message.from_user.id
    msg_id = message.message_id
    t0 = time()
    # Add sent message data to to-delete messages list
    sent_msg_data = OrderedDict([("Chat_id", None), ("User_id", None),
            ("Msg_id", None), ("time", None), ("delete_time", None)])
    sent_msg_data["Chat_id"] = chat_id
    sent_msg_data["User_id"] = user_id
    sent_msg_data["Msg_id"] = msg_id
    sent_msg_data["time"] = t0
    sent_msg_data["delete_time"] = time_delete_sec
    to_delete_in_time_messages_list.append(sent_msg_data)
    return True

###############################################################################
### General Functions

def save_session():
    '''Backup current execution data'''
    # Let's backup to file
    data = {
        "to_delete_in_time_messages_list": to_delete_in_time_messages_list,
        "new_users": new_users,
        "connections": connections
    }
    if not pickle_save(CONST["F_SESSION"], data):
        printts("Fail to save current session data")
        return False
    printts("Current session data saved")
    return True


def restore_session():
    '''Load last execution data'''
    global to_delete_in_time_messages_list
    global new_users
    global connections
    # Check if session file exists
    if not file_exists(CONST["F_SESSION"]):
        return False
    # Get data from session file
    last_session_data = pickle_restore(CONST["F_SESSION"])
    if last_session_data is None:
        printts("Fail to restore last session data")
        return False
    # Load last session data to current RAM
    connections = last_session_data["connections"]
    new_users = last_session_data["new_users"]
    to_delete_in_time_messages_list = \
            last_session_data["to_delete_in_time_messages_list"]
    # Renew time to kick users
    for chat_id in new_users:
        for user_id in new_users[chat_id]:
            # Some rand to avoid all requests sent at same time
            t0 = time() + randint(0, 10)
            new_users[chat_id][user_id]["join_data"]["join_time"] = t0
    # Renew time to remove messages
    i = 0
    while i < len(to_delete_in_time_messages_list):
        # Some rand to avoid all requests sent at same time
        t0 = time() + randint(0, 10)
        to_delete_in_time_messages_list[i]["time"] = t0
        i = i + 1
    printts("Last session data restored")
    return True


def initialize_resources():
    '''Initialize resources by populating files list with chats found files'''
    global files_config_list
    # Remove old captcha directory and create it again
    if path.exists(CONST["CAPTCHAS_DIR"]):
        rmtree(CONST["CAPTCHAS_DIR"])
    makedirs(CONST["CAPTCHAS_DIR"])
    # Create allowed users file if it does not exists
    if not path.exists(CONST["F_ALLOWED_USERS"]):
        file_write(CONST["F_ALLOWED_USERS"], "")
    # Create banned groups file if it does not exists
    if not path.exists(CONST["F_BAN_GROUPS"]):
        file_write(CONST["F_BAN_GROUPS"], "")
    # Create allowed groups file if it does not exists
    if CONST["BOT_PRIVATE"]:
        if not path.exists(CONST["F_ALLOWED_GROUPS"]):
            file_write(CONST["F_ALLOWED_GROUPS"], "")
    # Create data directory if it does not exists
    if not path.exists(CONST["CHATS_DIR"]):
        makedirs(CONST["CHATS_DIR"])
    else:
        # If chats directory exists, check all subdirectories names (chats ID)
        files = listdir(CONST["CHATS_DIR"])
        for f_chat_id in files:
            # Populate config files list
            file_path = "{}/{}/{}".format(CONST["CHATS_DIR"], f_chat_id, CONST["F_CONF"])
            files_config_list.append(OrderedDict([("ID", f_chat_id),
                ("File", TSjson(file_path))]))
            # Create default configuration file if it does not exists
            if not path.exists(file_path):
                default_conf = get_default_config_data()
                for key, value in default_conf.items():
                    save_config_property(f_chat_id, key, value)
    # Load and generate URL detector regex from TLD list file
    load_urls_regex("{}/{}".format(SCRIPT_PATH, CONST["F_TLDS"]))
    # Load all languages texts
    load_texts_languages()


def load_urls_regex(file_path):
    '''Load URL detection Regex from IANA TLD list text file.'''
    tlds_str = ""
    list_file_lines = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line is None:
                    continue
                if (line == "") or (line == "\r\n") or (line == "\r") or (line == "\n"):
                    continue
                # Ignore lines that start with # (first header line of IANA TLD list file)
                if line[0] == "#":
                    continue
                line = line.lower()
                line = line.replace("\r", "")
                line = line.replace("\n", "|")
                list_file_lines.append(line)
    except Exception as e:
        printts("Error opening file \"{}\". {}".format(file_path, str(e)))
    if len(list_file_lines) > 0:
        tlds_str = "".join(list_file_lines)
    CONST["REGEX_URLS"] = CONST["REGEX_URLS"].format(tlds_str)


def load_texts_languages():
    '''Load all texts from each language file.'''
    # Initialize all languages to english texts by default, so if
    # some language file miss some field, the english text is used
    lang_file = "{}/{}.json".format(CONST["LANG_DIR"], CONST["INIT_LANG"].lower())
    json_init_lang_texts = TSjson(lang_file).read()
    if (json_init_lang_texts is None) or (json_init_lang_texts == {}):
        printts("Error loading language \"{}\" from {}. Language file not found or bad JSON "
                "syntax.".format(CONST["INIT_LANG"].lower(), lang_file))
        printts("Exit.\n")
        exit(0)
    for lang_iso_code in TEXT:
        TEXT[lang_iso_code] = json_init_lang_texts.copy()
    # Load supported languages texts
    for lang_iso_code in TEXT:
        lang_file = "{}/{}.json".format(CONST["LANG_DIR"], lang_iso_code.lower())
        json_lang_file = TSjson(lang_file)
        json_lang_texts = json_lang_file.read()
        if (json_lang_texts is None) or (json_lang_texts == {}):
            printts("Error loading language \"{}\" from {}. Language file not found or bad JSON "
                    "syntax.".format(lang_iso_code, lang_file))
            printts("Exit.\n")
            exit(0)
        for text in json_lang_texts:
            TEXT[lang_iso_code][text] = json_lang_texts[text]
    # Check if there is some missing text in any language
    for lang_iso_code in TEXT:
        lang_iso_code = lang_iso_code.lower()
        lang_file = "{}/{}.json".format(CONST["LANG_DIR"], lang_iso_code)
        json_lang_file = TSjson(lang_file)
        json_lang_texts = json_lang_file.read()
        for text in json_init_lang_texts:
            if text not in json_lang_texts:
                printts("Warning: text \"{}\" missing from language file \"{}\".json".format(
                text, lang_iso_code))


def create_image_captcha(chat_id, file_name, difficult_level, captcha_mode):
    '''Generate an image captcha from pseudo numbers'''
    # If it doesn't exists, create captchas folder to store generated captchas
    img_dir_path = "{}/{}".format(CONST["CAPTCHAS_DIR"], chat_id)
    img_file_path = "{}/{}.png".format(img_dir_path, file_name)
    if not path.exists(CONST["CAPTCHAS_DIR"]):
        makedirs(CONST["CAPTCHAS_DIR"])
    else:
        if not path.exists(img_dir_path):
            makedirs(img_dir_path)
        else:
            # If the captcha file exists remove it
            if path.exists(img_file_path):
                remove(img_file_path)
    # Generate and save the captcha with a random background
    # mono-color or multi-color
    captcha_result = {
        "image": img_file_path,
        "characters": "",
        "equation_str": "",
        "equation_result": ""
    }
    if captcha_mode == "math":
        captcha = CaptchaGen.gen_math_captcha_image(2, bool(randint(0, 1)))
        captcha_result["equation_str"] = captcha["equation_str"]
        captcha_result["equation_result"] = captcha["equation_result"]
    else:
        captcha = CaptchaGen.gen_captcha_image(difficult_level, captcha_mode,
                bool(randint(0, 1)))
        captcha_result["characters"] = captcha["characters"]
    captcha["image"].save(img_file_path, "png")
    return captcha_result


def num_config_poll_options(poll_options):
    '''Check how many poll options are configured.'''
    configured_options = 0
    for i in range(0, CONST["MAX_POLL_OPTIONS"]):
        if poll_options[i] != "":
            configured_options = configured_options + 1
    return configured_options


def is_user_in_ignored_list(chat_id, user):
    '''Check if user is in ignored users list.'''
    ignored_users = get_chat_config(chat_id, "Ignore_List")
    if user.id in ignored_users:
        return True
    if user.username is not None:
        user_alias = "@{}".format(user.username)
        if user_alias in ignored_users:
            return True
    return False


def is_user_in_allowed_list(user):
    '''Check if user is in global allowed list.'''
    l_white_users = file_read(CONST["F_ALLOWED_USERS"])
    if user.id in l_white_users:
        return True
    if user.username is not None:
        user_alias = "@{}".format(user.username)
        if user_alias in l_white_users:
            return True
    return False


def is_group_in_allowed_list(chat_id):
    '''Check if group is in allowed list.'''
    # True if Bot is Public
    if not CONST["BOT_PRIVATE"]:
        return True
    l_allowed_groups = file_read(CONST["F_ALLOWED_GROUPS"])
    if str(chat_id) in l_allowed_groups:
        return True
    return False


def is_group_in_banned_list(chat_id):
    '''Check if group is in banned list.'''
    l_banned_groups = file_read(CONST["F_BAN_GROUPS"])
    if str(chat_id) in l_banned_groups:
        return True
    return False


def allowed_in_this_group(bot, chat, member_added_by):
    '''Check if Bot is allowed to be used in a Chat.'''
    if not is_group_in_allowed_list(chat.id):
        printts("Warning: Bot added to not allowed group.")
        from_user_name = ""
        if member_added_by.name is not None:
            from_user_name = member_added_by.name
        else:
            from_user_name = member_added_by.full_name
        chat_link = ""
        if chat.username:
            chat_link = "@{}".format(chat.username)
        printts("{}, {}, {}, {}".format(chat.id, from_user_name, chat.title,
                chat_link))
        msg_text = CONST["NOT_ALLOW_GROUP"].format(CONST["BOT_OWNER"], chat.id,
                CONST["REPOSITORY"])
        tlg_send_msg(bot, chat.id, msg_text)
        return False
    if is_group_in_banned_list(chat.id):
        printts("[{}] Warning: Bot added to banned group".format(chat.id))
        return False
    return True


def get_update_user_lang(update_user_data):
    '''Get user language-code from Telegram Update user data and return
    Bot supported language (english if not supported).'''
    lang = getattr(update_user_data, "language_code", "EN")
    if lang is None:
        lang = "EN"
    lang = lang.upper()
    if lang not in TEXT:
        lang = "EN"
    return lang


def is_captcha_num_solve(captcha_mode, msg_text, solve_num):
    '''Check if number send by user solves a num/hex/ascii/math captcha.
    - For "math", the message must be the exact math equation result number.
    - For other mode, the message must contains the numbers.'''
    if captcha_mode == "math":
        if msg_text == solve_num:
            return True
    else:
        if solve_num.lower() in msg_text.lower():
            return True
    return False


def should_manage_captcha(update, bot):
    '''Check if the Bot should manage a Captcha process to this Group and
    Member. It checks if the group is allowed to use the Bot, checks if the
    member is not an Administrator neither a member added by an Admin, or an
    added Bot, and checks if the Member is not in any of the allowed users
    lists.'''
    chat = update.chat_member.chat
    join_user = update.chat_member.new_chat_member.user
    member_added_by = update.chat_member.from_user
    # Check if Group is not allowed to be used by the Bot
    if not allowed_in_this_group(bot, chat, member_added_by):
        tlg_leave_chat(bot, chat.id)
        return False
    # Ignore Admins
    if tlg_user_is_admin(bot, join_user.id, chat.id):
        printts("[{}] User is an admin.".format(chat.id))
        printts("Skipping the captcha process.")
        return False
    # Ignore Members added by an Admin
    if tlg_user_is_admin(bot, member_added_by.id, chat.id):
        printts("[{}] User has been added by an admin.".format(chat.id))
        printts("Skipping the captcha process.")
        return False
    # Ignore if the member that has been join the group is a Bot
    if join_user.is_bot:
        printts("[{}] User is a Bot.".format(chat.id))
        printts("Skipping the captcha process.")
        return False
    # Ignore if the member that has joined is in chat ignore list
    if is_user_in_ignored_list(chat.id, join_user):
        printts("[{}] User is in ignore list.".format(chat.id))
        printts("Skipping the captcha process.")
        return False
    if is_user_in_allowed_list(join_user):
        printts("[{}] User is in global allowed list.".format(chat.id))
        printts("Skipping the captcha process.")
        return False
    return True


def captcha_fail_kick_ban_member(bot, chat_id, user_id, max_join_retries):
    '''Kick/Ban a new member that has fail to solve the captcha.'''
    global new_users
    # Get parameters
    lang = get_chat_config(chat_id, "Language")
    rm_result_msg = get_chat_config(chat_id, "Rm_Result_Msg")
    user_name = new_users[chat_id][user_id]["join_data"]["user_name"]
    join_retries = new_users[chat_id][user_id]["join_data"]["join_retries"]
    # Kick if user has fail to solve the captcha less than "max_join_retries"
    if join_retries < max_join_retries:
        printts("[{}] Captcha not solved, kicking {} ({})...".format(chat_id,
                user_name, user_id))
        # Try to kick the user
        kick_result = tlg_kick_user(bot, chat_id, user_id)
        if kick_result["error"] == "":
            # Kick success
            msg_text = TEXT[lang]["NEW_USER_KICK"].format(user_name)
            # Increase join retries
            join_retries = join_retries + 1
            printts("[{}] Increased join_retries to {}".format(chat_id, join_retries))
            # Send kicked message
            if rm_result_msg:
                tlg_send_selfdestruct_msg_in(bot, chat_id, msg_text, CONST["T_FAST_DEL_MSG"])
            else:
                tlg_send_msg(bot, chat_id, msg_text)
        else:
            # Kick fail
            printts("[{}] Unable to kick".format(chat_id))
            if (kick_result["error"] == "The user has left the group") or \
                    (kick_result["error"] == "The user was already kicked"):
                # The user is not in the chat
                msg_text = TEXT[lang]["NEW_USER_KICK_NOT_IN_CHAT"].format(user_name)
                if rm_result_msg:
                    tlg_send_selfdestruct_msg_in(bot, chat_id, msg_text, CONST["T_FAST_DEL_MSG"])
                else:
                    tlg_send_msg(bot, chat_id, msg_text)
            elif kick_result["error"] == "Not enough rights to restrict/unrestrict chat member":
                # Bot has no privileges to kick
                msg_text = TEXT[lang]["NEW_USER_KICK_NOT_RIGHTS"].format(user_name)
                # Send no rights for kick message without auto-remove
                tlg_send_msg(bot, chat_id, msg_text)
            else:
                # For other reason, the Bot can't ban
                msg_text = TEXT[lang]["BOT_CANT_KICK"].format(user_name)
                if rm_result_msg:
                    tlg_send_selfdestruct_msg_in(bot, chat_id, msg_text, CONST["T_FAST_DEL_MSG"])
                else:
                    tlg_send_msg(bot, chat_id, msg_text)
    # Ban if user has join "max_join_retries" times without solving the captcha
    else:
        printts("[{}] Captcha not solved, banning {} ({})...".format(chat_id,
                user_name, user_id))
        # Try to ban the user and notify Admins
        ban_result = tlg_ban_user(bot, chat_id, user_id)
        if ban_result["error"] == "":
            # Ban success
            msg_text = TEXT[lang]["NEW_USER_BAN"].format(
                    user_name, max_join_retries)
        else:
            # Ban fail
            if ban_result["error"] == "User not found":
                # The user is not in the chat
                msg_text = TEXT[lang]["NEW_USER_BAN_NOT_IN_CHAT"].format(
                        user_name, max_join_retries)
            elif ban_result["error"] == "Not enough rights to restrict/unrestrict chat member":
                # Bot has no privileges to ban
                msg_text = TEXT[lang]["NEW_USER_BAN_NOT_RIGHTS"].format(
                        user_name, max_join_retries)
            else:
                # For other reason, the Bot can't ban
                msg_text = TEXT[lang]["BOT_CANT_BAN"].format(
                        user_name, max_join_retries)
        # Send ban notify message
        printts("[{}] {}".format(chat_id, msg_text))
        if rm_result_msg:
            tlg_send_selfdestruct_msg(bot, chat_id, msg_text)
        else:
            tlg_send_msg(bot, chat_id, msg_text)
    # Update user info (join_retries & kick_ban)
    new_users[chat_id][user_id]["join_data"]["kicked_ban"] = True
    new_users[chat_id][user_id]["join_data"]["join_retries"] = join_retries
    # Remove join messages
    printts("[{}] Removing messages from user {}...".format(chat_id, user_name))
    join_msg = new_users[chat_id][user_id]["join_msg"]
    if join_msg is not None:
        tlg_delete_msg(bot, chat_id, join_msg)
    for msg in new_users[chat_id][user_id]["msg_to_rm"]:
        tlg_delete_msg(bot, chat_id, msg)
    new_users[chat_id][user_id]["msg_to_rm"].clear()
    for msg in new_users[chat_id][user_id]["msg_to_rm_on_kick"]:
        tlg_delete_msg(bot, chat_id, msg)
    new_users[chat_id][user_id]["msg_to_rm_on_kick"].clear()
    # Delete user join info if was ban
    if join_retries >= 5:
        del new_users[chat_id][user_id]
    printts("[{}] Kick/Ban process completed".format(chat_id))
    printts(" ")

###############################################################################
### Received Telegram not-command messages handlers

def chat_bot_status_change(update: Update, context: CallbackContext):
    '''Get Bot chats status changes (Bot added to group/channel,
    started/stopped conversation in private chat, etc.) event handler.'''
    # Check Bot changes
    result = tlg_extract_members_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result
    # Get chat data
    bot = context.bot
    chat = update.effective_chat
    caused_by_user = update.effective_user
    # Private Chat
    if chat.type == Chat.PRIVATE:
        return
        # Bot private conversation started
        #if not was_member and is_member:
        #    # ...
        # Bot private conversation blocked
        #elif was_member and not is_member:
        #    # ...
        #else:
        #    return
    # Groups
    elif chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        # Bot added to group
        if not was_member and is_member:
            # Get the language of the Telegram client software the Admin
            # that has added the Bot has, to assume this is the chat language
            # and configure Bot language of this chat
            admin_language = ""
            language_code = getattr(caused_by_user, "language_code", None)
            if language_code:
                admin_language = language_code[0:2].upper()
            if admin_language not in TEXT:
                admin_language = CONST["INIT_LANG"]
            save_config_property(chat.id, "Language", admin_language)
            # Get and save chat data
            if chat.title:
                save_config_property(chat.id, "Title", chat.title)
            if chat.username:
                chat_link = "@{}".format(chat.username)
                save_config_property(chat.id, "Link", chat_link)
            # Check if Group is not allowed to be used by the Bot
            if not allowed_in_this_group(bot, chat, caused_by_user):
                tlg_leave_chat(bot, chat.id)
                return
            # Send bot join message
            tlg_send_msg(bot, chat.id, TEXT[admin_language]["START"])
            return
        # Bot leave/removed from group
        elif was_member and not is_member:
            # Bot leave the group
            if caused_by_user.id == bot.id:
                # Bot left the group by itself
                print("[{}] Bot leave the group".format(chat.id))
            # Bot removed from group
            else:
                print("[{}] Bot removed from group by {}".format(
                        chat.id, caused_by_user.username))
            return
        else:
            return
    # Channels
    else:
        # Bot added to channel
        if not was_member and is_member:
            # Leave it (Bot don't allowed to be used in Channels)
            printts("Bot try to be added to a channel")
            tlg_send_msg(bot, chat.id, CONST["BOT_LEAVE_CHANNEL"])
            tlg_leave_chat(bot, chat.id)
            return
        # Bot leave/removed channel
        else:
            return


def chat_member_status_change(update: Update, context: CallbackContext):
    '''Get Members chats status changes (user join/leave/added/removed to/from
    group/channel) event handler. Note: if Bot is not an Admin, "chat_member"
    update won't be received.'''
    global new_users
    bot = context.bot
    # Ignore if it is not a new member join
    if not tlg_has_new_member_join_group(update.chat_member):
        return
    # Get Chat data
    chat = update.chat_member.chat
    join_user = update.chat_member.new_chat_member.user
    chat_id = chat.id
    # Get User ID and Name
    join_user_id = join_user.id
    join_user_name = tlg_get_user_name(join_user, 35)
    printts("[{}] New join detected: {} ({})".format(chat_id,
            join_user_name, join_user_id))
    # Get and update chat data
    chat_title = chat.title
    if chat_title:
        save_config_property(chat_id, "Title", chat_title)
    # Add an unicode Left to Right Mark (LRM) to chat title (fix for
    # arabic, hebrew, etc.)
    chat_title = add_lrm(chat_title)
    chat_link = chat.username
    if chat_link:
        chat_link = "@{}".format(chat_link)
        save_config_property(chat_id, "Link", chat_link)
    # Check if the Bot should manage a Captcha process to this Group and Member
    if not should_manage_captcha(update, bot):
        return
    # Check and remove previous join messages of that user (if any)
    if chat_id in new_users:
        if join_user_id in new_users[chat_id]:
            if "msg_to_rm" in new_users[chat_id][join_user_id]:
                for msg in new_users[chat_id][join_user_id]["msg_to_rm"]:
                    tlg_delete_msg(bot, chat_id, msg)
                new_users[chat_id][join_user_id]["msg_to_rm"].clear()
    # Ignore if the captcha protection is not enable in this chat
    captcha_enable = get_chat_config(chat_id, "Enabled")
    if not captcha_enable:
        printts("[{}] Captcha is not enabled in this chat".format(chat_id))
        return
    # Determine configured language and captcha settings
    lang = get_chat_config(chat_id, "Language")
    captcha_level = get_chat_config(chat_id, "Captcha_Difficulty_Level")
    captcha_mode = get_chat_config(chat_id, "Captcha_Chars_Mode")
    captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
    if captcha_timeout < CONST["T_SECONDS_IN_MIN"]:
        timeout_str = "{} sec".format(captcha_timeout)
    else:
        timeout_str = "{} min".format(int(captcha_timeout / CONST["T_SECONDS_IN_MIN"]))
    send_problem = False
    captcha_num = ""
    if captcha_mode == "random":
        captcha_mode = choice(["nums", "math", "poll"])
        # If Captcha Mode Poll is not configured use another mode
        if captcha_mode == "poll":
            poll_question = get_chat_config(chat_id, "Poll_Q")
            poll_options = get_chat_config(chat_id, "Poll_A")
            poll_correct_option = get_chat_config(chat_id, "Poll_C_A")
            if (poll_question == "") or \
            (num_config_poll_options(poll_options) < 2) or \
            (poll_correct_option == 0):
                captcha_mode = choice(["nums", "math"])
    if captcha_mode == "button":
        # Send a button-only challenge
        challenge_text = TEXT[lang]["NEW_USER_BUTTON_MODE"].format(join_user_name,
                chat_title, timeout_str)
        # Prepare inline keyboard button to let user pass
        keyboard = [[InlineKeyboardButton(TEXT[lang]["PASS_BTN_TEXT"],
                callback_data="button_captcha {}".format(join_user_id))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        printts("[{}] Sending captcha message to {}: [button]".format(chat_id, join_user_name))
        sent_result = tlg_send_msg(bot, chat_id, challenge_text,
                reply_markup=reply_markup, timeout=40)
        if sent_result["msg"] is None:
            send_problem = True
    elif captcha_mode == "poll":
        poll_question = get_chat_config(chat_id, "Poll_Q")
        poll_options = get_chat_config(chat_id, "Poll_A")
        poll_correct_option = get_chat_config(chat_id, "Poll_C_A")
        if (poll_question == "") or (num_config_poll_options(poll_options) < 2) \
        or (poll_correct_option == 0):
            tlg_send_selfdestruct_msg_in(bot, chat_id, TEXT[lang]["POLL_NEW_USER_NOT_CONFIG"], \
                    CONST["T_FAST_DEL_MSG"])
            return
        # Remove empty strings from options list
        poll_options = list(filter(None, poll_options))
        # Send request to solve the poll text message
        poll_request_msg_text = TEXT[lang]["POLL_NEW_USER"].format(join_user_name,
            chat_title, timeout_str)
        sent_result = tlg_send_selfdestruct_msg(bot, chat_id, poll_request_msg_text)
        solve_poll_request_msg_id = None
        if sent_result is not None:
            solve_poll_request_msg_id = sent_result
        # Send the Poll
        sent_result = tlg_send_poll(bot, chat_id, poll_question, poll_options,
                poll_correct_option-1, captcha_timeout, False, Poll.QUIZ)
        if sent_result["msg"] is None:
            send_problem = True
        else:
            # Save some info about the poll the bot_data for
            # later use in receive_quiz_answer
            poll_id = sent_result["msg"].poll.id
            poll_msg_id = sent_result["msg"].message_id
            poll_data = {
                poll_id:
                {
                    "chat_id": chat_id,
                    "poll_msg_id": poll_msg_id,
                    "user_id": join_user_id,
                    "correct_option": poll_correct_option
                }
            }
            context.bot_data.update(poll_data)
    else: # Image captcha
        # Generate a pseudorandom captcha send it to telegram group and
        # program message
        captcha = create_image_captcha(chat_id, join_user_id, captcha_level, \
                captcha_mode)
        if captcha_mode == "math":
            captcha_num = captcha["equation_result"]
            printts("[{}] Sending captcha message to {}: {}={}...".format( \
                    chat_id, join_user_name, captcha["equation_str"], \
                    captcha["equation_result"]))
            # Note: Img caption must be <= 1024 chars
            img_caption = TEXT[lang]["NEW_USER_MATH_CAPTION"].format( \
                    join_user_name, chat_title, timeout_str)
        else:
            captcha_num = captcha["characters"]
            printts("[{}] Sending captcha message to {}: {}...".format( \
                    chat_id, join_user_name, captcha_num))
            # Note: Img caption must be <= 1024 chars
            img_caption = TEXT[lang]["NEW_USER_IMG_CAPTION"].format( \
                    join_user_name, chat_title, timeout_str)
        # Prepare inline keyboard button to let user request another captcha
        keyboard = [[InlineKeyboardButton(TEXT[lang]["OTHER_CAPTCHA_BTN_TEXT"],
                callback_data="image_captcha {}".format(join_user_id))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send the image
        sent_result = tlg_send_image(bot, chat_id, \
                open(captcha["image"],"rb"), img_caption, \
                reply_markup=reply_markup)
        if sent_result["msg"] is None:
            send_problem = True
        # Remove sent captcha image file from file system
        if path.exists(captcha["image"]):
            remove(captcha["image"])
    if not send_problem:
        # Add sent captcha message to self-destruct list
        if sent_result["msg"] is not None:
            tlg_msg_to_selfdestruct_in(sent_result["msg"], captcha_timeout+10)
        # Default user join data
        join_data = \
        {
            "user_name": join_user_name,
            "captcha_num": captcha_num,
            "captcha_mode": captcha_mode,
            "join_time": time(),
            "captcha_timeout": captcha_timeout,
            "join_retries": 1,
            "kicked_ban": False
        }
        # Create dict keys for new user
        if chat_id not in new_users:
            new_users[chat_id] = {}
        if join_user_id not in new_users[chat_id]:
            new_users[chat_id][join_user_id] = {}
        if "join_data" not in new_users[chat_id][join_user_id]:
            new_users[chat_id][join_user_id]["join_data"] = {}
        if "join_msg" not in new_users[chat_id][join_user_id]:
            new_users[chat_id][join_user_id]["join_msg"] = None
        if "msg_to_rm" not in new_users[chat_id][join_user_id]:
            new_users[chat_id][join_user_id]["msg_to_rm"] = []
        if "msg_to_rm_on_kick" not in new_users[chat_id][join_user_id]:
            new_users[chat_id][join_user_id]["msg_to_rm_on_kick"] = []
        # Check if this user was before in the chat without solve the captcha
        # and restore previous join_retries
        if len(new_users[chat_id][join_user_id]["join_data"]) != 0:
            join_data["join_retries"] = new_users[chat_id][join_user_id]["join_data"]["join_retries"]
        # Add new user join data and messages to be removed
        new_users[chat_id][join_user_id]["join_data"] = join_data
        if update.message:
            new_users[chat_id][join_user_id]["join_msg"] = update.message.message_id
        if sent_result["msg"]:
            new_users[chat_id][join_user_id]["msg_to_rm"].append(sent_result["msg"].message_id)
        if (captcha_mode == "poll") and (solve_poll_request_msg_id is not None):
            new_users[chat_id][join_user_id]["msg_to_rm"].append(solve_poll_request_msg_id)
        # Restrict user to deny send any kind of message until captcha is solve
        # Allow send text messages for image based captchas (nums and maths)
        if (captcha_mode == "nums") or (captcha_mode == "math"):
            # Restrict user to only allow send text messages
            tlg_restrict_user(bot, chat_id, join_user_id, send_msg=True,
                send_media=False, send_stickers_gifs=False, insert_links=False,
                send_polls=False, invite_members=False, pin_messages=False,
                change_group_info=False)
        else:
            tlg_restrict_user(bot, chat_id, join_user_id, send_msg=False,
                send_media=False, send_stickers_gifs=False, insert_links=False,
                send_polls=False, invite_members=False, pin_messages=False,
                change_group_info=False)
        printts("[{}] Captcha send process completed.".format(chat_id))
        printts(" ")


def msg_user_joined_group(update: Update, context: CallbackContext):
    '''New member join the group event handler'''
    global new_users
    # Get message data
    chat_id = None
    update_msg = tlg_get_msg(update)
    if update_msg is not None:
        chat_id = getattr(update_msg, "chat_id", None)
    if (update_msg is None) or (chat_id is None):
        print("Warning: Received an unexpected update.")
        print(update)
        return
    msg_id = getattr(update_msg, "message_id", None)
    if msg_id is None:
        return
    new_chat_members = getattr(update_msg, "new_chat_members", None)
    if new_chat_members is None:
        return
    # For each new user that join or has been added
    for join_user in new_chat_members:
        # Ignore if the chat is not expected
        if chat_id not in new_users:
            continue
        # Ignore if user is not expected
        if join_user.id not in new_users[chat_id]:
            continue
        # If user has join the group, add the "USER joined the group"
        # message ID to new user data to be removed
        new_users[chat_id][join_user.id]["join_msg"] = msg_id


def msg_notext(update: Update, context: CallbackContext):
    '''All non-text messages handler.'''
    bot = context.bot
    # Get message data
    chat = None
    chat_id = None
    update_msg = None
    update_msg = tlg_get_msg(update)
    if update_msg is not None:
        chat = getattr(update_msg, "chat", None)
        chat_id = getattr(update_msg, "chat_id", None)
    if (update_msg is None) or (chat is None) or (chat_id is None):
        print("Warning: Received an unexpected update.")
        print(update)
        return
    # Ignore if message comes from a private chat
    if chat.type == "private":
        return
    # Ignore if message comes from a channel
    if chat.type == "channel":
        return
    # Ignore if message is a channel post automatically forwarded to the
    # connected discussion group
    if tlg_is_a_channel_msg_on_discussion_group(update_msg):
        return
    # Ignore if captcha protection is not enable in this chat
    captcha_enable = get_chat_config(chat_id, "Enabled")
    if not captcha_enable:
        return
    # Ignore if msg not from a new user that needs to solve the captcha
    user_id = update_msg.from_user.id
    if chat_id not in new_users:
        return
    if user_id not in new_users[chat_id]:
        return
    # Get username, if has an alias, just use the alias
    user_name = update_msg.from_user.full_name
    if update_msg.from_user.username is not None:
        user_name = "@{}".format(update_msg.from_user.username)
    # Remove send message and notify that not text messages are not allowed until solve captcha
    msg_id = update_msg.message_id
    printts("[{}] Removing non-text message sent by {}".format(chat_id, user_name))
    tlg_delete_msg(bot, chat_id, msg_id)
    lang = get_chat_config(chat_id, "Language")
    bot_msg = TEXT[lang]["NOT_TEXT_MSG_ALLOWED"].format(user_name)
    tlg_send_selfdestruct_msg_in(bot, chat_id, bot_msg, CONST["T_FAST_DEL_MSG"])


def msg_nocmd(update: Update, context: CallbackContext):
    '''Non-command text messages handler'''
    global new_users
    bot = context.bot
    # Get message data
    chat = None
    chat_id = None
    update_msg = None
    update_msg = tlg_get_msg(update)
    if update_msg is not None:
        chat = getattr(update_msg, "chat", None)
        chat_id = getattr(update_msg, "chat_id", None)
    if (update_msg is None) or (chat is None) or (chat_id is None):
        print("Warning: Received an unexpected update.")
        print(update)
        return
    # Ignore if message comes from a private chat
    if chat.type == "private":
        return
    # Ignore if message comes from a channel
    if chat.type == "channel":
        return
    # Ignore if message is a channel post automatically forwarded to the
    # connected discussion group
    if tlg_is_a_channel_msg_on_discussion_group(update_msg):
        return
    # Ignore if captcha protection is not enable in this chat
    captcha_enable = get_chat_config(chat_id, "Enabled")
    if not captcha_enable:
        return
    # If message doesn't has text, check for caption fields (for no text msgs
    # and forward ones)
    msg_text = getattr(update_msg, "text", None)
    if msg_text is None:
        msg_text = getattr(update_msg, "caption_html", None)
    if msg_text is None:
        msg_text = getattr(update_msg, "caption", None)
    # Check if message has a text link (embedded url in text) and get it
    msg_entities = getattr(update_msg, "entities", None)
    if msg_entities is None:
        msg_entities = []
    for entity in msg_entities:
        url = getattr(entity, "url", None)
        if url is not None:
            if url != "":
                if msg_text is None:
                    msg_text = url
                else:
                    msg_text = "{} [{}]".format(msg_text, url)
                break
    # Get others message data
    user_id = update_msg.from_user.id
    msg_id = update_msg.message_id
    # Get and update chat data
    chat_title = chat.title
    if chat_title:
        save_config_property(chat_id, "Title", chat_title)
    chat_link = chat.username
    if chat_link:
        chat_link = "@{}".format(chat_link)
        save_config_property(chat_id, "Link", chat_link)
    user_name = update_msg.from_user.full_name
    # If has an alias, just use the alias
    if update_msg.from_user.username is not None:
        user_name = "@{}".format(update_msg.from_user.username)
    # Set default text message if not received
    if msg_text is None:
        msg_text = "[Not a text message]"
    # Check if group is configured to deny users send URLs, and remove URLs msg
    url_enable = get_chat_config(chat_id, "URL_Enabled")
    if not url_enable:
        # Ignore if message comes from an Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if is_admin:
            return
        # Get Chat configured language
        lang = get_chat_config(chat_id, "Language")
        # Check for Spam (check if the message contains any URL)
        has_url = re.findall(CONST["REGEX_URLS"], msg_text)
        if has_url:
            # Try to remove the message and notify detection
            delete_result = tlg_delete_msg(bot, chat_id, msg_id)
            if delete_result["error"] == "":
                bot_msg = TEXT[lang]["URL_MSG_NOT_ALLOWED_DETECTED"].format(user_name)
                tlg_send_selfdestruct_msg_in(bot, chat_id, bot_msg, CONST["T_FAST_DEL_MSG"])
    # Ignore if message is not from a new user that has not completed the captcha yet
    if chat_id not in new_users:
        return
    if user_id not in new_users[chat_id]:
        return
    # Get Chat settings
    lang = get_chat_config(chat_id, "Language")
    rm_result_msg = get_chat_config(chat_id, "Rm_Result_Msg")
    captcha_mode = new_users[chat_id][user_id]["join_data"]["captcha_mode"]
    # Check for forwarded messages and delete it
    forward_from = getattr(update_msg, "forward_from", None)
    forward_from_chat = getattr(update_msg, "forward_from_chat", None)
    if (forward_from is not None) or (forward_from_chat is not None):
        printts("[{}] Spammer detected: {}.".format(chat_id, user_name))
        printts("[{}] Removing forwarded msg: {}.".format(chat_id, msg_text))
        delete_result = tlg_delete_msg(bot, chat_id, msg_id)
        if delete_result["error"] == "":
            printts("Message removed.")
        elif delete_result["error"] == "Message can't be deleted":
            printts("No rights to remove msg.")
        else:
            printts("Message can't be deleted.")
        return
    # Check for Spam (check if the message contains any URL or alias)
    has_url = re.findall(CONST["REGEX_URLS"], msg_text)
    has_alias = tlg_alias_in_string(msg_text)
    if has_url or has_alias:
        printts("[{}] Spammer detected: {}.".format(chat_id, user_name))
        printts("[{}] Removing spam message: {}.".format(chat_id, msg_text))
        # Try to remove the message and notify detection
        delete_result = tlg_delete_msg(bot, chat_id, msg_id)
        if delete_result["error"] == "":
            bot_msg = TEXT[lang]["SPAM_DETECTED_RM"].format(user_name)
            tlg_send_selfdestruct_msg_in(bot, chat_id, bot_msg, CONST["T_FAST_DEL_MSG"])
        # Check if message cant be removed due to not delete msg privileges
        elif delete_result["error"] == "Message can't be deleted":
            bot_msg = TEXT[lang]["SPAM_DETECTED_NOT_RM"].format(user_name)
            tlg_send_selfdestruct_msg_in(bot, chat_id, bot_msg, CONST["T_FAST_DEL_MSG"])
        else:
            printts("Message can't be deleted.")
        return
    # Check group config regarding if all messages of user must be removed when kick
    rm_all_msg = get_chat_config(chat_id, "RM_All_Msg")
    if rm_all_msg:
        new_users[chat_id][user_id]["msg_to_rm_on_kick"].append(msg_id)
    # End here if no image captcha mode
    if captcha_mode not in { "nums", "hex", "ascii", "math" }:
        return
    printts("[{}] Received captcha reply from {}: {}".format(chat_id, user_name, msg_text))
    # Check if the expected captcha solve number is in the message
    solve_num = new_users[chat_id][user_id]["join_data"]["captcha_num"]
    if is_captcha_num_solve(captcha_mode, msg_text, solve_num):
        printts("[{}] Captcha solved by {}".format(chat_id, user_name))
        # Remove all restrictions on the user
        tlg_unrestrict_user(bot, chat_id, user_id)
        # Remove join messages
        for msg in new_users[chat_id][user_id]["msg_to_rm"]:
            tlg_delete_msg(bot, chat_id, msg)
        new_users[chat_id][user_id]["msg_to_rm"].clear()
        new_users[chat_id][user_id]["msg_to_rm_on_kick"].clear()
        del new_users[chat_id][user_id]
        # Remove user captcha numbers message
        tlg_delete_msg(bot, chat_id, msg_id)
        # Send message solve message
        bot_msg = TEXT[lang]["CAPTCHA_SOLVED"].format(user_name)
        if rm_result_msg:
            tlg_send_selfdestruct_msg_in(bot, chat_id, bot_msg, CONST["T_FAST_DEL_MSG"])
        else:
            tlg_send_msg(bot, chat_id, bot_msg)
        # Check for custom welcome message and send it
        welcome_msg = get_chat_config(chat_id, "Welcome_Msg").format(escape_markdown(user_name, 2))
        if welcome_msg != "-":
            # Send the message as Markdown
            rm_welcome_msg = get_chat_config(chat_id, "Rm_Welcome_Msg")
            if rm_welcome_msg:
                welcome_msg_time = get_chat_config(chat_id, "Welcome_Time")
                sent_result = tlg_send_selfdestruct_msg_in(bot, chat_id, welcome_msg,
                        welcome_msg_time, parse_mode="MARKDOWN")
            else:
                sent_result = tlg_send_msg(bot, chat_id, welcome_msg, "MARKDOWN")
            if sent_result is None:
                printts("[{}] Error: Can't send the welcome message.".format(chat_id))
        # Check for send just text message option and apply user restrictions
        restrict_non_text_msgs = get_chat_config(chat_id, "Restrict_Non_Text")
        # Restrict for 1 day
        if restrict_non_text_msgs == 1:
            tomorrow_epoch = get_unix_epoch() + CONST["T_RESTRICT_NO_TEXT_MSG"]
            tlg_restrict_user(bot, chat_id, user_id, send_msg=True, send_media=False,
                send_stickers_gifs=False, insert_links=False, send_polls=False,
                invite_members=False, pin_messages=False, change_group_info=False,
                until_date=tomorrow_epoch)
        # Restrict forever
        elif restrict_non_text_msgs == 2:
            tlg_restrict_user(bot, chat_id, user_id, send_msg=True, send_media=False,
                send_stickers_gifs=False, insert_links=False, send_polls=False,
                invite_members=False, pin_messages=False, change_group_info=False)
    # The provided message doesn't has the valid captcha number
    else:
        # Check if the message is for a math equation captcha
        if (captcha_mode == "math"):
            clueless_user = False
            # Check if message is just 4 numbers
            if is_int(msg_text) and (len(msg_text) == 4):
                clueless_user = True
            # Check if message is "NN+NN" or "NN-NN"
            elif (len(msg_text) == 5) and (is_int(msg_text[:2])) and \
            (is_int(msg_text[3:])) and (msg_text[2] in ["+", "-"]):
                clueless_user = True
            # Tell the user that is wrong
            if clueless_user:
                sent_msg_id = tlg_send_selfdestruct_msg_in(bot, chat_id, \
                        TEXT[lang]["CAPTCHA_INCORRECT_MATH"], CONST["T_FAST_DEL_MSG"])
                new_users[chat_id][user_id]["msg_to_rm"].append(sent_msg_id)
                new_users[chat_id][user_id]["msg_to_rm"].append(msg_id)
        # If "nums", "hex" or "ascii" captcha
        else:
            # Check if the message has 4 chars
            if len(msg_text) == 4:
                sent_msg_id = tlg_send_selfdestruct_msg_in(bot, chat_id, \
                        TEXT[lang]["CAPTCHA_INCORRECT_0"], CONST["T_FAST_DEL_MSG"])
                new_users[chat_id][user_id]["msg_to_rm"].append(sent_msg_id)
                new_users[chat_id][user_id]["msg_to_rm"].append(msg_id)
            # Check if the message was just a 4 numbers msg
            elif is_int(msg_text):
                sent_msg_id = tlg_send_selfdestruct_msg_in(bot, chat_id, \
                        TEXT[lang]["CAPTCHA_INCORRECT_1"], CONST["T_FAST_DEL_MSG"])
                new_users[chat_id][user_id]["msg_to_rm"].append(sent_msg_id)
                new_users[chat_id][user_id]["msg_to_rm"].append(msg_id)
    printts("[{}] Captcha reply process completed.".format(chat_id))
    printts(" ")


def receive_poll_answer(update: Update, context: CallbackContext):
    '''User poll vote received'''
    global new_users
    bot = context.bot
    active_polls = context.bot_data
    poll_id = update.poll_answer.poll_id
    from_user = update.poll_answer.user
    option_answer = update.poll_answer.option_ids[0] + 1
    msg_text = "User {} select poll option {}".format(from_user.username, option_answer)
    print(msg_text)
    # Ignore any Poll vote that comes from unexpected poll
    if poll_id not in active_polls:
        return
    poll_data = active_polls[poll_id]
    # Ignore Poll votes that doesn't come from expected user in captcha process
    if from_user.id != poll_data["user_id"]:
        return
    # Handle poll vote
    chat_id = poll_data["chat_id"]
    user_id = poll_data["user_id"]
    poll_msg_id = poll_data["poll_msg_id"]
    poll_correct_option = poll_data["correct_option"]
    # The vote come from expected user, let's stop the Poll
    tlg_stop_poll(bot, chat_id, poll_msg_id)
    # Get user name (if has an alias, just use the alias)
    user_name = from_user.full_name
    if from_user.username is not None:
        user_name = "@{}".format(from_user.username)
    # Get chat settings
    lang = get_chat_config(chat_id, "Language")
    rm_result_msg = get_chat_config(chat_id, "Rm_Result_Msg")
    rm_welcome_msg = get_chat_config(chat_id, "Rm_Welcome_Msg")
    welcome_msg = get_chat_config(chat_id, "Welcome_Msg").format(escape_markdown(user_name, 2))
    restrict_non_text_msgs = get_chat_config(chat_id, "Restrict_Non_Text")
    # Wait 3s to let poll animation be shown
    sleep(3)
    # Remove previous join messages
    for msg in new_users[chat_id][user_id]["msg_to_rm"]:
        tlg_delete_msg(bot, chat_id, msg)
    new_users[chat_id][user_id]["msg_to_rm"].clear()
    # Check if user vote the correct option
    if option_answer == poll_correct_option:
        printts("[{}] User {} solved a poll challenge.".format(chat_id, user_name))
        # Remove all restrictions on the user
        tlg_unrestrict_user(bot, chat_id, user_id)
        # Send captcha solved message
        bot_msg = TEXT[lang]["CAPTCHA_SOLVED"].format(user_name)
        if rm_result_msg:
            tlg_send_selfdestruct_msg_in(bot, chat_id, bot_msg, CONST["T_FAST_DEL_MSG"])
        else:
            tlg_send_msg(bot, chat_id, bot_msg)
        del new_users[chat_id][user_id]
        # Check for custom welcome message and send it
        if welcome_msg != "-":
            if rm_welcome_msg:
                welcome_msg_time = get_chat_config(chat_id, "Welcome_Time")
                sent_result = tlg_send_selfdestruct_msg_in(bot, chat_id, welcome_msg,
                        welcome_msg_time, parse_mode="MARKDOWN")
            else:
                sent_result = tlg_send_msg(bot, chat_id, welcome_msg, "MARKDOWN")
            if sent_result is None:
                printts("[{}] Error: Can't send the welcome message.".format(chat_id))
        # Check for send just text message option and apply user restrictions
        if restrict_non_text_msgs == 1: # Restrict for 1 day
            tomorrow_epoch = get_unix_epoch() + CONST["T_RESTRICT_NO_TEXT_MSG"]
            tlg_restrict_user(bot, chat_id, user_id, send_msg=True, send_media=False,
                send_stickers_gifs=False, insert_links=False, send_polls=False,
                invite_members=False, pin_messages=False, change_group_info=False,
                until_date=tomorrow_epoch)
        elif restrict_non_text_msgs == 2: # Restrict forever
            tlg_restrict_user(bot, chat_id, user_id, send_msg=True, send_media=False,
                send_stickers_gifs=False, insert_links=False, send_polls=False,
                invite_members=False, pin_messages=False, change_group_info=False)
    else:
        # Notify captcha fail
        printts("[{}] User {} fail a poll challenge.".format(chat_id, user_name))
        bot_msg = TEXT[lang]["CAPTCHA_POLL_FAIL"].format(user_name)
        sent_msg_id = None
        if rm_result_msg:
            sent_result = tlg_send_msg(bot, chat_id, bot_msg)
            if sent_result["msg"] is not None:
                sent_msg_id = sent_result["msg"].message_id
        else:
            tlg_send_msg(bot, chat_id, bot_msg)
        # Wait 10s
        sleep(10)
        # Try to kick the user
        captcha_fail_kick_ban_member(bot, chat_id, user_id,
                CONST["MAX_FAIL_BAN_POLL"])
    printts("[{}] Poll captcha process completed.".format(chat_id))
    printts(" ")


def key_inline_keyboard(update: Update, context: CallbackContext):
    '''Inline Keyboard button pressed handler'''
    bot = context.bot
    query = update.callback_query
    # Confirm query received
    query_ans_result = tlg_answer_callback_query(bot, query)
    if query_ans_result["error"] != "":
        return
    # Convert query provided data into list
    button_data = query.data.split(" ")
    # Ignore if the query data unexpected or comes from an unexpected user
    if (len(button_data) < 2) or (button_data[1] != str(query.from_user.id)):
        return
    # Get type of inline keyboard button pressed and user ID associated to that button
    key_pressed = button_data[0]
    # Check and handle "request new img captcha" or "button captcha challenge" buttons
    if "image_captcha" in key_pressed:
        button_request_captcha(bot, query)
    elif "button_captcha" in key_pressed:
        button_request_pass(bot, query)


def button_request_captcha(bot, query):
    '''Button "Another captcha" pressed handler'''
    global new_users
    # Get query data
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    msg_id = query.message.message_id
    user_name = query.from_user.full_name
    # If has an alias, just use the alias
    if query.from_user.username is not None:
        user_name = "@{}".format(query.from_user.username)
    chat_title = query.message.chat.title
    # Add an unicode Left to Right Mark (LRM) to chat title
    # (fix for arabic, hebrew, etc.)
    chat_title = add_lrm(chat_title)
    # Ignore if message is not from a new user that has not
    # completed the captcha yet
    if chat_id not in new_users:
        return
    if user_id not in new_users[chat_id]:
        return
    # Get chat language
    lang = get_chat_config(chat_id, "Language")
    printts("[{}] User {} requested a new captcha.".format(chat_id, user_name))
    # Prepare inline keyboard button to let user request another captcha
    keyboard = [[InlineKeyboardButton(TEXT[lang]["OTHER_CAPTCHA_BTN_TEXT"],
            callback_data="image_captcha {}".format(str(query.from_user.id)))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Get captcha timeout
    captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
    if captcha_timeout < CONST["T_SECONDS_IN_MIN"]:
        timeout_str = "{} sec".format(captcha_timeout)
    else:
        timeout_min = int(captcha_timeout / CONST["T_SECONDS_IN_MIN"])
        timeout_str = "{} min".format(timeout_min)
    # Get current chat configurations
    captcha_level = get_chat_config(chat_id, "Captcha_Difficulty_Level")
    captcha_mode = new_users[chat_id][user_id]["join_data"]["captcha_mode"]
    # Use nums mode if captcha_mode was changed while captcha was in progress
    if captcha_mode not in { "nums", "hex", "ascii", "math" }:
        captcha_mode = "nums"
    # Generate a new captcha and edit previous captcha image message
    captcha = create_image_captcha(chat_id, user_id, captcha_level, \
            captcha_mode)
    if captcha_mode == "math":
        captcha_num = captcha["equation_result"]
        printts("[{}] Sending new captcha msg: {} = {}...".format(chat_id, \
                captcha["equation_str"], captcha_num))
        img_caption = TEXT[lang]["NEW_USER_MATH_CAPTION"].format(user_name, \
            chat_title, timeout_str)
    else:
        captcha_num = captcha["characters"]
        printts("[{}] Sending new captcha msg: {}...".format( \
                chat_id, captcha_num))
        img_caption = TEXT[lang]["NEW_USER_IMG_CAPTION"].format(user_name, \
            chat_title, timeout_str)
    input_media = InputMediaPhoto(media=open(captcha["image"], "rb"), \
            caption=img_caption)
    edit_result = tlg_edit_msg_media(bot, chat_id, msg_id, media=input_media, \
            reply_markup=reply_markup, timeout=20)
    if edit_result["error"] == "":
        # Set and modified to new expected captcha number
        new_users[chat_id][user_id]["join_data"]["captcha_num"] = captcha_num
        # Remove sent captcha image file from file system
        if path.exists(captcha["image"]):
            remove(captcha["image"])
    printts("[{}] New captcha request process completed.".format(chat_id))
    printts(" ")


def button_request_pass(bot, query):
    '''Button "I'm not a bot" pressed handler'''
    global new_users
    # Get query data
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    user_name = query.from_user.full_name
    # If has an alias, just use the alias
    if query.from_user.username is not None:
        user_name = "@{}".format(query.from_user.username)
    chat_title = query.message.chat.title
    # Add an unicode Left to Right Mark (LRM) to chat title (fix for arabic, hebrew, etc.)
    chat_title = add_lrm(chat_title)
    # Ignore if request doesn't come from a new user in captcha process
    if chat_id not in new_users:
        return
    if user_id not in new_users[chat_id]:
        return
    # Get chat settings
    lang = get_chat_config(chat_id, "Language")
    rm_result_msg = get_chat_config(chat_id, "Rm_Result_Msg")
    # Remove previous join messages
    for msg in new_users[chat_id][user_id]["msg_to_rm"]:
        tlg_delete_msg(bot, chat_id, msg)
    # Remove user from captcha process
    del new_users[chat_id][user_id]
    # Send message solve message
    printts("[{}] User {} solved a button-only challenge.".format(chat_id, user_name))
    # Remove all restrictions on the user
    tlg_unrestrict_user(bot, chat_id, user_id)
    # Send captcha solved message
    bot_msg = TEXT[lang]["CAPTCHA_SOLVED"].format(user_name)
    if rm_result_msg:
        tlg_send_selfdestruct_msg_in(bot, chat_id, bot_msg, CONST["T_FAST_DEL_MSG"])
    else:
        tlg_send_msg(bot, chat_id, bot_msg)
    # Check for custom welcome message and send it
    welcome_msg = get_chat_config(chat_id, "Welcome_Msg").format(escape_markdown(user_name, 2))
    if welcome_msg != "-":
        # Send the message as Markdown
        rm_welcome_msg = get_chat_config(chat_id, "Rm_Welcome_Msg")
        if rm_welcome_msg:
            welcome_msg_time = get_chat_config(chat_id, "Welcome_Time")
            sent_result = tlg_send_selfdestruct_msg_in(bot, chat_id, welcome_msg,
                    welcome_msg_time, parse_mode="MARKDOWN")
        else:
            sent_result = tlg_send_msg(bot, chat_id, welcome_msg, "MARKDOWN")
        if sent_result is None:
            printts("[{}] Error: Can't send the welcome message.".format(chat_id))
    # Check for send just text message option and apply user restrictions
    restrict_non_text_msgs = get_chat_config(chat_id, "Restrict_Non_Text")
    # Restrict for 1 day
    if restrict_non_text_msgs == 1:
        tomorrow_epoch = get_unix_epoch() + CONST["T_RESTRICT_NO_TEXT_MSG"]
        tlg_restrict_user(bot, chat_id, user_id, send_msg=True, send_media=False,
            send_stickers_gifs=False, insert_links=False, send_polls=False,
            invite_members=False, pin_messages=False, change_group_info=False,
            until_date=tomorrow_epoch)
    # Restrict forever
    elif restrict_non_text_msgs == 2:
        tlg_restrict_user(bot, chat_id, user_id, send_msg=True, send_media=False,
            send_stickers_gifs=False, insert_links=False, send_polls=False,
            invite_members=False, pin_messages=False, change_group_info=False)
    printts("[{}] Button-only challenge pass request process completed.".format(chat_id))
    printts(" ")

###############################################################################
### Received Telegram command messages handlers

def cmd_start(update: Update, context: CallbackContext):
    '''Command /start message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, TEXT[lang]["START"])
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        user_id = update_msg.from_user.id
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Send the response message
        lang = get_chat_config(chat_id, "Language")
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["START"])


def cmd_help(update: Update, context: CallbackContext):
    '''Command /help message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, TEXT[lang]["HELP"])
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        user_id = update_msg.from_user.id
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Send the response message
        lang = get_chat_config(chat_id, "Language")
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["HELP"])


def cmd_commands(update: Update, context: CallbackContext):
    '''Command /commands message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, TEXT[lang]["COMMANDS"])
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        user_id = update_msg.from_user.id
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Send the response message
        lang = get_chat_config(chat_id, "Language")
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["COMMANDS"])


def cmd_connect(update: Update, context: CallbackContext):
    '''Command /connect message handler'''
    global connections
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    user_id = update_msg.from_user.id
    user_alias = update_msg.from_user.username
    if user_alias is not None:
        user_alias = "@{}".format(user_alias)
    lang = get_update_user_lang(update_msg.from_user)
    # Ignore if command is not in private chat
    if chat_type != "private":
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Send just allowed in private chat message
        lang = get_chat_config(chat_id, "Language")
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["CMD_JUST_IN_PRIVATE"])
        return
    # Check for group chat ID
    if len(args) == 0:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["CONNECT_USAGE"])
        return
    group_id = args[0]
    # Add "-" if not present
    if group_id[0] != "-":
        group_id = "-{}".format(group_id)
    if not tlg_is_valid_group(group_id):
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["INVALID_GROUP_ID"])
        return
    # Check if requested by the Bot owner or an Admin of the group
    if (str(user_id) != CONST["BOT_OWNER"]) and \
    (user_alias != CONST["BOT_OWNER"]):
        is_admin = tlg_user_is_admin(bot, user_id, group_id)
        if (is_admin is None) or (is_admin == False):
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CONNECT_JUST_ADMIN"])
            return
    # Connection
    group_lang = get_chat_config(group_id, "Language")
    connections[user_id] = { "group_id": group_id, "lang": group_lang }
    tlg_send_msg_type_chat(bot, chat_type, chat_id,
            TEXT[lang]["CONNECT_OK"].format(group_id))


def cmd_disconnect(update: Update, context: CallbackContext):
    '''Command /disconnect message handler'''
    global connections
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    user_id = update_msg.from_user.id
    lang = get_update_user_lang(update_msg.from_user)
    # Ignore if command is not in private chat
    if chat_type != "private":
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Send just allowed in private chat message
        lang = get_chat_config(chat_id, "Language")
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["CMD_JUST_IN_PRIVATE"])
        return
    # Check if User is connected to some group
    if user_id not in connections:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["DISCONNECT_NOT_CONNECTED"])
        return
    # Disconnection
    lang = connections[user_id]["lang"]
    group_id = connections[user_id]["group_id"]
    del connections[user_id]
    tlg_send_msg_type_chat(bot, chat_type, chat_id,
            TEXT[lang]["DISCONNECT_OK"].format(group_id))


def cmd_checkcfg(update: Update, context: CallbackContext):
    '''Command /checkcfg message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Get all group configs
    group_cfg = get_all_chat_config(group_id)
    group_cfg = json_dumps(group_cfg, indent=4, sort_keys=True)
    tlg_send_msg_type_chat(bot, chat_type, chat_id,
            TEXT[lang]["CHECK_CFG"].format(escape_markdown(group_cfg, 2)),
            parse_mode="MARKDOWN")


def cmd_language(update: Update, context: CallbackContext):
    '''Command /language message handler'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if len(args) == 0:
        msg_text = TEXT[lang]["LANG_NOT_ARG"].format(
                CONST["SUPPORTED_LANGS_CMDS"])
        tlg_send_msg_type_chat(bot, chat_type, chat_id, msg_text)
        return
    # Get and configure chat to provided language
    lang_provided = args[0].upper()
    if lang_provided in TEXT:
        if lang_provided != lang:
            lang = lang_provided
            save_config_property(group_id, "Language", lang)
            if (chat_type == "private") and (user_id in connections):
                connections[user_id]["lang"] = lang
            msg_text = TEXT[lang]["LANG_CHANGE"]
        else:
            msg_text = TEXT[lang]["LANG_SAME"].format(
                    CONST["SUPPORTED_LANGS_CMDS"])
    else:
        msg_text = TEXT[lang]["LANG_BAD_LANG"].format(
                CONST["SUPPORTED_LANGS_CMDS"])
    tlg_send_msg_type_chat(bot, chat_type, chat_id, msg_text)


def cmd_time(update: Update, context: CallbackContext):
    '''Command /time message handler'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["TIME_NOT_ARG"])
        return
    # Check if provided time argument is not a number
    if not is_int(args[0]):
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["TIME_NOT_NUM"])
        return
    # Get time arguments
    new_time = int(args[0])
    min_sec = "min"
    if len(args) > 1:
        min_sec = args[1].lower()
    # Check if time format is not minutes or seconds
    # Convert time value to seconds if min format
    if min_sec in ["m", "min", "mins", "minutes"]:
        min_sec = "min"
        new_time_str = "{} min".format(new_time)
        new_time = new_time * CONST["T_SECONDS_IN_MIN"]
    elif min_sec in ["s", "sec", "secs", "seconds"]:
        min_sec = "sec"
        new_time_str = "{} sec".format(new_time)
    else:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["TIME_NOT_ARG"])
        return
    # Check if time value is out of limits
    if new_time < 10: # Lees than 10s
        msg_text = TEXT[lang]["TIME_OUT_RANGE"].format( \
                CONST["MAX_CONFIG_CAPTCHA_TIME"])
        tlg_send_msg_type_chat(bot, chat_type, chat_id, msg_text)
        return
    if new_time > CONST["MAX_CONFIG_CAPTCHA_TIME"] * CONST["T_SECONDS_IN_MIN"]:
        msg_text = TEXT[lang]["TIME_OUT_RANGE"].format( \
                CONST["MAX_CONFIG_CAPTCHA_TIME"])
        tlg_send_msg_type_chat(bot, chat_type, chat_id, msg_text)
        return
    # Set the new captcha time
    save_config_property(group_id, "Captcha_Time", new_time)
    msg_text = TEXT[lang]["TIME_CHANGE"].format(new_time_str)
    tlg_send_msg_type_chat(bot, chat_type, chat_id, msg_text)


def cmd_difficulty(update: Update, context: CallbackContext):
    '''Command /difficulty message handler'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["DIFFICULTY_NOT_ARG"])
        return
    # Get and configure chat to provided captcha difficulty
    if is_int(args[0]):
        new_difficulty = int(args[0])
        if new_difficulty < 1:
            new_difficulty = 1
        if new_difficulty > 5:
            new_difficulty = 5
        save_config_property(group_id, "Captcha_Difficulty_Level",
                new_difficulty)
        bot_msg = TEXT[lang]["DIFFICULTY_CHANGE"].format(new_difficulty)
    else:
        bot_msg = TEXT[lang]["DIFFICULTY_NOT_NUM"]
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_captcha_mode(update: Update, context: CallbackContext):
    '''Command /captcha_mode message handler'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["CAPTCHA_MODE_NOT_ARG"])
        return
    # Get and configure chat to provided captcha mode
    new_captcha_mode = args[0].lower()
    if new_captcha_mode in {
    "poll", "button", "nums", "hex", "ascii", "math", "random" }:
        save_config_property(group_id, "Captcha_Chars_Mode", new_captcha_mode)
        bot_msg = TEXT[lang]["CAPTCHA_MODE_CHANGE"].format(new_captcha_mode)
    else:
        bot_msg = TEXT[lang]["CAPTCHA_MODE_INVALID"]
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_welcome_msg(update: Update, context: CallbackContext):
    '''Command /welcome_msg message handler'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["WELCOME_MSG_SET_NOT_ARG"])
        return
    # Get welcome message in markdown and remove "/Welcome_msg " text from it
    welcome_msg = update.message.text_markdown_v2[14:]
    welcome_msg = welcome_msg.replace("{", "{{")
    welcome_msg = welcome_msg.replace("}", "}}")
    welcome_msg = welcome_msg.replace("$user", "{0}")
    welcome_msg = welcome_msg[:CONST["MAX_WELCOME_MSG_LENGTH"]]
    if welcome_msg == "disable":
        welcome_msg = '-'
        bot_msg = TEXT[lang]["WELCOME_MSG_UNSET"]
    else:
        bot_msg = TEXT[lang]["WELCOME_MSG_SET"]
    save_config_property(group_id, "Welcome_Msg", welcome_msg)
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_welcome_msg_time(update: Update, context: CallbackContext):
    '''Command /welcome_msg_time message handler'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["WELCOME_TIME_NOT_ARG"])
        return
    # Check if provided time argument is not a number
    if not is_int(args[0]):
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["TIME_NOT_NUM"])
        return
    # Get time arguments
    new_time = int(args[0])
    min_sec = "min"
    if len(args) > 1:
        min_sec = args[1].lower()
    # Check if time format is not minutes or seconds
    # Convert time value to seconds if min format
    if min_sec in ["m", "min", "mins", "minutes"]:
        min_sec = "min"
        new_time_str = "{} min".format(new_time)
        new_time = new_time * CONST["T_SECONDS_IN_MIN"]
    elif min_sec in ["s", "sec", "secs", "seconds"]:
        min_sec = "sec"
        new_time_str = "{} sec".format(new_time)
    else:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["WELCOME_TIME_NOT_ARG"])
        return
    # Check if time value is out of limits
    if new_time < 10: # Lees than 10s
        msg_text = TEXT[lang]["TIME_OUT_RANGE"].format( \
                CONST["MAX_CONFIG_CAPTCHA_TIME"])
        tlg_send_msg_type_chat(bot, chat_type, chat_id, msg_text)
        return
    if new_time > CONST["MAX_CONFIG_CAPTCHA_TIME"] * CONST["T_SECONDS_IN_MIN"]:
        msg_text = TEXT[lang]["TIME_OUT_RANGE"].format( \
                CONST["MAX_CONFIG_CAPTCHA_TIME"])
        tlg_send_msg_type_chat(bot, chat_type, chat_id, msg_text)
        return
    # Set the new captcha time
    save_config_property(group_id, "Welcome_Time", new_time)
    msg_text = TEXT[lang]["WELCOME_TIME_CHANGE"].format(new_time_str)
    tlg_send_msg_type_chat(bot, chat_type, chat_id, msg_text)


def cmd_captcha_poll(update: Update, context: CallbackContext):
    '''Command /captcha_poll message handler'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Format command usage text
    text_cmd_usage = TEXT[lang]["CAPTCHA_POLL_USAGE"].format(
            CONST["MAX_POLL_QUESTION_LENGTH"],
            CONST["MAX_POLL_OPTION_LENGTH"],
            CONST["MAX_POLL_OPTIONS"])
    # Check if no argument was provided with the command
    if len(args) < 2:
        tlg_send_msg_type_chat(bot, chat_type, chat_id, text_cmd_usage)
        return
    # Get poll message command
    poll_cmd = args[0]
    print("poll_cmd: {}".format(poll_cmd))
    if poll_cmd not in ["question", "option", "correct_option"]:
        tlg_send_msg_type_chat(bot, chat_type, chat_id, text_cmd_usage)
        return
    if poll_cmd == "question":
        # get Poll Question
        poll_question = " ".join(args[1:])
        print("poll_question: {}".format(poll_question))
        if len(poll_question) > CONST["MAX_POLL_QUESTION_LENGTH"]:
            poll_question = poll_question[:CONST["MAX_POLL_QUESTION_LENGTH"]]
        # Save Poll Question
        save_config_property(group_id, "Poll_Q", poll_question)
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["POLL_QUESTION_CONFIGURED"])
    elif poll_cmd == "correct_option":
        # get Poll correct option and check if is a number
        option_num = args[1]
        if not is_int(option_num):
            tlg_send_msg_type_chat(bot, chat_type, chat_id, text_cmd_usage)
            return
        option_num = int(option_num)
        # Check if correct option number is configured
        if (option_num < 1) or (option_num > CONST["MAX_POLL_OPTIONS"]):
            tlg_send_msg_type_chat(bot, chat_type, chat_id, text_cmd_usage)
            return
        poll_options = get_chat_config(group_id, "Poll_A")
        if option_num > num_config_poll_options(poll_options):
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["POLL_CORRECT_OPTION_NOT_CONFIGURED"].format(
                    option_num))
            return
        # Save Poll correct option number
        save_config_property(group_id, "Poll_C_A", option_num)
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["POLL_CORRECT_OPTION_CONFIGURED"].format(
                option_num))
    elif poll_cmd == "option":
        # Check if option argument is valid
        if len(args) < 3:
            tlg_send_msg_type_chat(bot, chat_type, chat_id, text_cmd_usage)
            return
        option_num = args[1]
        print("option_num: {}".format(option_num))
        if not is_int(option_num):
            tlg_send_msg_type_chat(bot, chat_type, chat_id, text_cmd_usage)
            return
        option_num = int(option_num)
        if (option_num < 1) or (option_num > CONST["MAX_POLL_OPTIONS"]):
            tlg_send_msg_type_chat(bot, chat_type, chat_id, text_cmd_usage)
            return
        option_num = option_num - 1
        # Resize poll options list if missing options slots
        poll_options = get_chat_config(group_id, "Poll_A")
        if len(poll_options) < CONST["MAX_POLL_OPTIONS"]:
            missing_options = CONST["MAX_POLL_OPTIONS"] - len(poll_options)
            for _ in range(missing_options, CONST["MAX_POLL_OPTIONS"]):
                poll_options.append("")
        # Modify option number if previous option is not defined
        for i in range(0, CONST["MAX_POLL_OPTIONS"]):
            if (poll_options[i] == "") and (i < option_num):
                option_num = i
                break
        # Parse provided Poll option text to configure and limit length
        poll_option = " ".join(args[2:])
        print("poll_option: {}".format(poll_option))
        if len(poll_option) > CONST["MAX_POLL_OPTION_LENGTH"]:
            poll_option = poll_option[:CONST["MAX_POLL_OPTION_LENGTH"]]
        # Check if requested an option remove and remove it
        if poll_option.lower() == "remove":
            del poll_options[option_num]
            poll_options.append("")
        else:
            poll_options[option_num] = poll_option
        # Save Poll option
        save_config_property(group_id, "Poll_A", poll_options)
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["POLL_OPTION_CONFIGURED"].format(option_num+1))


def cmd_restrict_non_text(update: Update, context: CallbackContext):
    '''Command /restrict_non_text message handler'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["RESTRICT_NON_TEXT_MSG_NOT_ARG"])
        return
    # Check for valid expected argument values
    restrict_non_text_msgs = args[0]
    if restrict_non_text_msgs != "enable" and restrict_non_text_msgs != "disable":
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["RESTRICT_NON_TEXT_MSG_NOT_ARG"])
        return
    # Check for forever restriction argument
    restrict_forever = False
    if (len(args) > 1) and (args[1] == "forever"):
        restrict_forever = True
    # Enable/Disable just text messages option
    if restrict_non_text_msgs == "enable":
        if restrict_forever:
            save_config_property(group_id, "Restrict_Non_Text", 2)
        else:
            save_config_property(group_id, "Restrict_Non_Text", 1)
        bot_msg = TEXT[lang]["RESTRICT_NON_TEXT_MSG_ENABLED"]
    else:
        save_config_property(group_id, "Restrict_Non_Text", 0)
        bot_msg = TEXT[lang]["RESTRICT_NON_TEXT_MSG_DISABLED"]
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_add_ignore(update: Update, context: CallbackContext):
    '''Command /add_ignore message handler'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["IGNORE_LIST_ADD_NOT_ARG"])
        return
    # Check and add user ID/alias form ignore list
    user_id_alias = args[0]
    if tlg_is_valid_user_id_or_alias(user_id_alias):
        ignore_list = get_chat_config(group_id, "Ignore_List")
        # Ignore list limit enforcement
        if len(ignore_list) < CONST["IGNORE_LIST_MAX"]:
            if user_id_alias not in ignore_list:
                ignore_list.append(user_id_alias)
                save_config_property(group_id, "Ignore_List", ignore_list)
                bot_msg = TEXT[lang]["IGNORE_LIST_ADD_SUCCESS"]
            else:
                bot_msg = TEXT[lang]["IGNORE_LIST_ADD_DUPLICATED"]
        else:
            bot_msg = TEXT[lang]["IGNORE_LIST_ADD_LIMIT_EXCEEDED"]
    else:
        bot_msg = TEXT[lang]["IGNORE_LIST_ADD_INVALID"]
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_remove_ignore(update: Update, context: CallbackContext):
    '''Command /remove_ignore message handler'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["IGNORE_LIST_REMOVE_NOT_ARG"])
        return
    # Check and remove user ID/alias form ignore list
    ignore_list = get_chat_config(group_id, "Ignore_List")
    user_id_alias = args[0]
    if list_remove_element(ignore_list, user_id_alias):
        save_config_property(group_id, "Ignore_List", ignore_list)
        bot_msg = TEXT[lang]["IGNORE_LIST_REMOVE_SUCCESS"]
    else:
        bot_msg = TEXT[lang]["IGNORE_LIST_REMOVE_NOT_IN_LIST"]
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_ignore_list(update: Update, context: CallbackContext):
    '''Command /ignore_list message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Get and show Ignore list
    ignore_list = get_chat_config(group_id, "Ignore_List")
    if not ignore_list:
        bot_msg = TEXT[lang]["IGNORE_LIST_EMPTY"]
    else:
        bot_msg = "\n".join([str(x) for x in ignore_list])
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_remove_solve_kick_msg(update: Update, context: CallbackContext):
    '''Command /remove_solve_kick_msg message handler'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["RM_SOLVE_KICK_MSG"])
        return
    # Get remove solve/kick messages config to set
    yes_or_no = args[0].lower()
    if yes_or_no == "yes":
        save_config_property(group_id, "Rm_Result_Msg", True)
        bot_msg = TEXT[lang]["RM_SOLVE_KICK_MSG_YES"]
    elif yes_or_no == "no":
        save_config_property(group_id, "Rm_Result_Msg", False)
        bot_msg = TEXT[lang]["RM_SOLVE_KICK_MSG_NO"]
    else:
        bot_msg = TEXT[lang]["RM_SOLVE_KICK_MSG"]
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_remove_welcome_msg(update: Update, context: CallbackContext):
    '''Command /remove_welcome_msg message handler'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_msg_type_chat(bot, chat_type, chat_id,
                TEXT[lang]["RM_WELCOME_MSG"])
        return
    # Get remove welcome messages config to set
    yes_or_no = args[0].lower()
    if yes_or_no == "yes":
        save_config_property(group_id, "Rm_Welcome_Msg", True)
        bot_msg = TEXT[lang]["RM_WELCOME_MSG_YES"]
    elif yes_or_no == "no":
        save_config_property(group_id, "Rm_Welcome_Msg", False)
        bot_msg = TEXT[lang]["RM_WELCOME_MSG_NO"]
    else:
        bot_msg = TEXT[lang]["RM_WELCOME_MSG"]
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_remove_all_msg_kick_on(update: Update, context: CallbackContext):
    '''Command /remove_all_msg_kick_on message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check and enable users send URLs in the chat
    enable = get_chat_config(group_id, "RM_All_Msg")
    if enable:
        bot_msg = TEXT[lang]["CONFIG_ALREADY_SET"]
    else:
        enable = True
        save_config_property(group_id, "RM_All_Msg", enable)
        bot_msg = TEXT[lang]["RM_ALL_MSGS_AFTER_KICK_ON"]
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_remove_all_msg_kick_off(update: Update, context: CallbackContext):
    '''Command /remove_all_msg_kick_off message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check and enable users send URLs in the chat
    enable = get_chat_config(group_id, "RM_All_Msg")
    if not enable:
        bot_msg = TEXT[lang]["CONFIG_ALREADY_UNSET"]
    else:
        enable = False
        save_config_property(group_id, "RM_All_Msg", enable)
        bot_msg = TEXT[lang]["RM_ALL_MSGS_AFTER_KICK_OFF"]
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_url_enable(update: Update, context: CallbackContext):
    '''Command /url_enable message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check and enable users send URLs in the chat
    enable = get_chat_config(group_id, "URL_Enabled")
    if enable:
        bot_msg = TEXT[lang]["CONFIG_ALREADY_SET"]
    else:
        enable = True
        save_config_property(group_id, "URL_Enabled", enable)
        bot_msg = TEXT[lang]["URL_ENABLE"]
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_url_disable(update: Update, context: CallbackContext):
    '''Command /url_disable message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        if user_id not in connections:
            tlg_send_msg_type_chat(bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check and disable users send URLs in the chat
    enable = get_chat_config(group_id, "URL_Enabled")
    if not enable:
        bot_msg = TEXT[lang]["CONFIG_ALREADY_UNSET"]
    else:
        enable = False
        save_config_property(group_id, "URL_Enabled", enable)
        bot_msg = TEXT[lang]["URL_DISABLE"]
    tlg_send_msg_type_chat(bot, chat_type, chat_id, bot_msg)


def cmd_enable(update: Update, context: CallbackContext):
    '''Command /enable message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Remove command message automatically after a while
    tlg_msg_to_selfdestruct(update_msg)
    # Ignore if not requested by a group Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if (is_admin is None) or (is_admin == False):
        return
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check and enable captcha protection in the chat
    enable = get_chat_config(chat_id, "Enabled")
    if enable:
        bot_msg = TEXT[lang]["ALREADY_ENABLE"]
    else:
        enable = True
        save_config_property(chat_id, "Enabled", enable)
        bot_msg = TEXT[lang]["ENABLE"]
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_disable(update: Update, context: CallbackContext):
    '''Command /disable message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user_id = update_msg.from_user.id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Remove command message automatically after a while
    tlg_msg_to_selfdestruct(update_msg)
    # Ignore if not requested by a group Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if (is_admin is None) or (is_admin == False):
        return
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check and disable captcha protection in the chat
    enable = get_chat_config(chat_id, "Enabled")
    if not enable:
        bot_msg = TEXT[lang]["ALREADY_DISABLE"]
    else:
        enable = False
        save_config_property(chat_id, "Enabled", enable)
        bot_msg = TEXT[lang]["DISABLE"]
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_chatid(update: Update, context: CallbackContext):
    '''Command /chatid message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    if chat_type == "private":
        msg_text = "Your Chat ID:\n—————————\n{}".format(chat_id)
        tlg_send_msg(bot, chat_id, msg_text)
    else:
        msg_text = "Group Chat ID:\n—————————\n{}".format(chat_id)
        tlg_msg_to_selfdestruct(update_msg)
        tlg_send_selfdestruct_msg(bot, chat_id, msg_text)


def cmd_version(update: Update, context: CallbackContext):
    '''Command /version message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    user_id = update_msg.from_user.id
    lang = get_update_user_lang(update_msg.from_user)
    if chat_type == "private":
        msg_text = TEXT[lang]["VERSION"].format(CONST["VERSION"])
        tlg_send_msg(bot, chat_id, msg_text)
    else:
        # Remove command message automatically after a while
        tlg_msg_to_selfdestruct(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if (is_admin is None) or (is_admin == False):
            return
        # Send the message
        lang = get_chat_config(chat_id, "Language")
        msg_text = TEXT[lang]["VERSION"].format(CONST["VERSION"])
        tlg_send_selfdestruct_msg(bot, chat_id, msg_text)


def cmd_about(update: Update, context: CallbackContext):
    '''Command /about handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    if chat_type != "private":
        lang = get_chat_config(chat_id, "Language")
    msg_text = TEXT[lang]["ABOUT_MSG"].format(CONST["DEVELOPER"],
            CONST["REPOSITORY"], CONST["DEV_DONATION_ADDR"])
    tlg_send_msg(bot, chat_id, msg_text)


def cmd_captcha(update: Update, context: CallbackContext):
    '''Command /captcha message handler. Useful to test.
    Just Bot Owner can use it.'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user = update_msg.from_user
    user_id = user.id
    user_alias = ""
    if user.username is not None:
        user_alias = "@{}".format(user.username)
    # Remove command message automatically after a while
    tlg_msg_to_selfdestruct(update_msg)
    # Check if command was execute by Bot owner
    if (str(user_id) != CONST["BOT_OWNER"]) and \
    (user_alias != CONST["BOT_OWNER"]):
        tlg_send_selfdestruct_msg(bot, chat_id, CONST["CMD_JUST_ALLOW_OWNER"])
        return
    # Generate a random difficulty captcha
    difficulty = randint(1, 5)
    captcha_mode = choice(["nums", "hex", "ascii", "math"])
    captcha = create_image_captcha(chat_id, user_id, difficulty, captcha_mode)
    if captcha_mode == "math":
        captcha_code = "{} = {}".format(captcha["equation_str"], \
                captcha["equation_result"])
    else:
        captcha_code = captcha["characters"]
    printts("[{}] Sending captcha msg: {}".format(chat_id, captcha_code))
    # Note: Img caption must be <= 1024 chars
    img_caption = "Captcha Level: {}\nCaptcha Mode: {}\n" \
            "Captcha Code: {}".format(difficulty, captcha_mode, captcha_code)
    tlg_send_image(bot, chat_id, open(captcha["image"],"rb"), img_caption)
    # Remove sent captcha image file from file system
    if path.exists(captcha["image"]):
        remove(captcha["image"])


def cmd_allowuserlist(update: Update, context: CallbackContext):
    '''Command /allowuserlist message handler. To Global allowed list blind users.
    Just Bot Owner can use it.'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user = update_msg.from_user
    user_id = user.id
    user_alias = ""
    if user.username is not None:
        user_alias = "@{}".format(user.username)
    lang = get_update_user_lang(update_msg.from_user)
    # Check if command was execute by Bot owner
    if (str(user_id) != CONST["BOT_OWNER"]) and (user_alias != CONST["BOT_OWNER"]):
        tlg_send_selfdestruct_msg(bot, chat_id, CONST["CMD_JUST_ALLOW_OWNER"])
        return
    # Check if no argument was provided with the command
    if len(args) == 0:
        # Show Actual Global allowed list Users
        l_white_users = file_read(CONST["F_ALLOWED_USERS"])
        bot_msg = "\n".join([str(user) for user in l_white_users])
        bot_msg = "Global Allowed Users List:\n--------------------\n{}".format(bot_msg)
        tlg_send_msg(bot, chat_id, bot_msg)
        tlg_send_msg(bot, chat_id, CONST["ALLOWUSERLIST_USAGE"])
        return
    else:
        if len(args) <= 1:
            tlg_send_msg(bot, chat_id, CONST["ALLOWUSERLIST_USAGE"])
            return
        if (args[0] != "add") and (args[0] != "rm"):
            tlg_send_msg(bot, chat_id, CONST["ALLOWUSERLIST_USAGE"])
            return
        add_rm = args[0]
        user = args[1]
        l_white_users = file_read(CONST["F_ALLOWED_USERS"])
        if add_rm == "add":
            if not tlg_is_valid_user_id_or_alias(user):
                tlg_send_msg(bot, chat_id, "Invalid User ID/Alias.")
                return
            if user not in l_white_users:
                file_write(CONST["F_ALLOWED_USERS"], "{}\n".format(user))
                tlg_send_msg(bot, chat_id, "User added to Global allowed list.")
            else:
                tlg_send_msg(bot, chat_id, "The User is already in Global allowed list.")
            return
        if add_rm == "rm":
            if not tlg_is_valid_user_id_or_alias(user):
                tlg_send_msg(bot, chat_id, "Invalid User ID/Alias.")
                return
            if list_remove_element(l_white_users, user):
                file_write(CONST["F_ALLOWED_USERS"], l_white_users, "w")
                tlg_send_msg(bot, chat_id, "User removed from Global allowed list.")
            else:
                tlg_send_msg(bot, chat_id, "The User is not in Global allowed list.")


def cmd_allowgroup(update: Update, context: CallbackContext):
    '''Command /allowgroup message handler. To allow Bot usage in groups when Bot is private.
    Just Bot Owner can use it.'''
    bot = context.bot
    args = context.args
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    user = update_msg.from_user
    user_id = user.id
    user_alias = ""
    if user.username is not None:
        user_alias = "@{}".format(user.username)
    lang = get_update_user_lang(update_msg.from_user)
    # Check if command was execute by Bot owner
    if (str(user_id) != CONST["BOT_OWNER"]) and (user_alias != CONST["BOT_OWNER"]):
        tlg_send_selfdestruct_msg(bot, chat_id, CONST["CMD_JUST_ALLOW_OWNER"])
        return
    # Check if no argument was provided with the command
    if len(args) == 0:
        # Show Actual Allowed Groups
        l_allowed_groups = file_read(CONST["F_ALLOWED_GROUPS"])
        bot_msg = "\n".join([str(group) for group in l_allowed_groups])
        bot_msg = "Allowed Groups:\n--------------------\n{}".format(bot_msg)
        tlg_send_msg(bot, chat_id, bot_msg)
        tlg_send_msg(bot, chat_id, CONST["ALLOWGROUP_USAGE"])
        return
    else:
        if len(args) <= 1:
            tlg_send_msg(bot, chat_id, CONST["ALLOWGROUP_USAGE"])
            return
        if (args[0] != "add") and (args[0] != "rm"):
            tlg_send_msg(bot, chat_id, CONST["ALLOWGROUP_USAGE"])
            return
        add_rm = args[0]
        group = args[1]
        l_allowed_groups = file_read(CONST["F_ALLOWED_GROUPS"])
        if add_rm == "add":
            if not tlg_is_valid_group(group):
                tlg_send_msg(bot, chat_id, "Invalid Group ID.")
                return
            if group not in l_allowed_groups:
                file_write(CONST["F_ALLOWED_GROUPS"], "{}\n".format(group))
                tlg_send_msg(bot, chat_id, "Group added to allowed list.")
            else:
                tlg_send_msg(bot, chat_id, "The group is already in the allowed list.")
            return
        if add_rm == "rm":
            if not tlg_is_valid_group(group):
                tlg_send_msg(bot, chat_id, "Invalid Group ID.")
                return
            if list_remove_element(l_allowed_groups, group):
                file_write(CONST["F_ALLOWED_GROUPS"], l_allowed_groups, "w")
                tlg_send_msg(bot, chat_id, "Group removed from allowed list.")
            else:
                tlg_send_msg(bot, chat_id, "The group is not in allowed list.")

###############################################################################
### Bot automatic remove sent messages thread

def th_selfdestruct_messages(bot):
    '''Handle remove messages sent by the Bot with the timed self-delete function'''
    global to_delete_in_time_messages_list
    while not force_exit:
        # Thread sleep for each iteration
        sleep(0.01)
        # Check each Bot sent message
        i = 0
        while i < len(to_delete_in_time_messages_list):
            # Check for break iterating if script must exit
            if force_exit:
                return
            sent_msg = to_delete_in_time_messages_list[i]
            # Sleep each 100 iterations
            i = i + 1
            if (i > 1) and ((i % 1000) == 0):
                sleep(0.01)
            # Check if delete time has arrive for this message
            if time() - sent_msg["time"] < sent_msg["delete_time"]:
                continue
            # Delete message
            printts("[{}] Scheduled deletion time for message: {}".format(
                    sent_msg["Chat_id"], sent_msg["Msg_id"]))
            delete_result = tlg_delete_msg(bot, sent_msg["Chat_id"], sent_msg["Msg_id"])
            # The bot has no privileges to delete messages
            if delete_result["error"] == "Message can't be deleted":
                lang = get_chat_config(sent_msg["Chat_id"], "Language")
                sent_result = tlg_send_msg(bot, sent_msg["Chat_id"],
                        TEXT[lang]["CANT_DEL_MSG"], reply_to_message_id=sent_msg["Msg_id"])
                if sent_result["msg"] is not None:
                    tlg_msg_to_selfdestruct(sent_result["msg"])
            list_remove_element(to_delete_in_time_messages_list, sent_msg)
            sleep(0.01)

###############################################################################
### Handle time to kick users thread

def th_time_to_kick_not_verify_users(bot):
    '''Check if the time for ban new users that has not completed the captcha has arrived'''
    global new_users
    while not force_exit:
        # Thread sleep for each iteration
        sleep(0.01)
        # Get all id from users in captcha process (shallow copy to list)
        users_id = []
        chats_id_list = list(new_users.keys()).copy()
        for chat_id in chats_id_list:
            users_id_list = list(new_users[chat_id].keys()).copy()
            for user_id in users_id_list:
                if user_id not in users_id:
                    users_id.append(user_id)
        # For each user id check for time to kick in each chat
        i = 0
        for user_id in users_id:
            for chat_id in chats_id_list:
                # Sleep each 1000 iterations
                i = i + 1
                if i > 1000:
                    i = 0
                    sleep(0.01)
                # Check for end thread when iterating if script must exit
                if force_exit:
                    return
                # Ignore if user is not in this chat
                if user_id not in new_users[chat_id]:
                    continue
                try:
                    user_join_time = new_users[chat_id][user_id]["join_data"]["join_time"]
                    captcha_timeout = new_users[chat_id][user_id]["join_data"]["captcha_timeout"]
                    if new_users[chat_id][user_id]["join_data"]["kicked_ban"]:
                        # Remove from new users list the remaining kicked users that have not solve
                        # the captcha in 30 mins (user ban just happen if a user try to join the group
                        # and fail to solve the captcha 5 times in the past 30 mins)
                        if time() - user_join_time < captcha_timeout + 1800:
                            continue
                        printts("Removing kicked user {} after 10 mins".format(user_id))
                        del new_users[chat_id][user_id]
                    else:
                        # If time for kick/ban has not arrived yet
                        if time() - user_join_time < captcha_timeout:
                            continue
                        user_name = new_users[chat_id][user_id]["join_data"]["user_name"]
                        printts("[{}] Captcha reply timed out for user {}.".format(chat_id, user_name))
                        captcha_fail_kick_ban_member(bot, chat_id, user_id,
                                CONST["MAX_FAIL_BAN"])
                        sleep(0.01)
                except Exception as e:
                    printts("Error handling kick/ban:\n{}".format(str(e)))

###############################################################################
### Telegram Errors Callback

def tlg_error_callback(update, context):
    '''Telegram errors handler.'''
    try:
        raise context.error
    except Unauthorized:
        printts("TLG Error: Unauthorized")
    except BadRequest:
        printts("TLG Error: Bad Request")
    except TimedOut:
        printts("TLG Error: Timeout (slow connection issue)")
    except NetworkError:
        printts("TLG Error: network problem")
    except TelegramError as e:
        printts("TLG Error: {}".format(str(e)))

###############################################################################
### Main Function

def main():
    '''Main Function'''
    global updater
    global th_0
    global th_1
    # Check if Bot Token has been set or has default value
    if CONST["TOKEN"] == "XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX":
        printts("Error: Bot Token has not been set.")
        printts("Please add your Bot Token to settings.py file.")
        printts("Exit.\n")
        exit(0)
    # Check if Bot owner has been set in Private Bot mode
    if (CONST["BOT_OWNER"] == "XXXXXXXXX") and CONST["BOT_PRIVATE"]:
        printts("Error: Bot Owner has not been set for Private Bot.")
        printts("Please add the Bot Owner to settings.py file.")
        printts("Exit.\n")
        exit(0)
    printts("Bot started.")
    # Initialize resources by populating files list and configs with chats found files
    initialize_resources()
    printts("Resources initialized.")
    restore_session()
    # Set messages to be sent silently by default
    msgs_defaults = Defaults(disable_notification=True)
    # Create an event handler (updater) for a Bot with the given Token and get the dispatcher
    updater = Updater(CONST["TOKEN"], workers=12, defaults=msgs_defaults)
    dp = updater.dispatcher
    # Set Telegram errors handler
    dp.add_error_handler(tlg_error_callback)
    # Set to dispatcher all expected commands messages handler
    dp.add_handler(CommandHandler("start", cmd_start))
    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("commands", cmd_commands))
    dp.add_handler(CommandHandler("checkcfg", cmd_checkcfg))
    dp.add_handler(CommandHandler("connect", cmd_connect, pass_args=True))
    dp.add_handler(CommandHandler("disconnect", cmd_disconnect))
    dp.add_handler(CommandHandler("language", cmd_language, pass_args=True))
    dp.add_handler(CommandHandler("time", cmd_time, pass_args=True))
    dp.add_handler(CommandHandler("difficulty", cmd_difficulty, pass_args=True))
    dp.add_handler(CommandHandler("captcha_mode", cmd_captcha_mode, pass_args=True))
    dp.add_handler(CommandHandler("welcome_msg", cmd_welcome_msg, pass_args=True))
    dp.add_handler(CommandHandler("welcome_msg_time", cmd_welcome_msg_time, pass_args=True))
    dp.add_handler(CommandHandler("captcha_poll", cmd_captcha_poll, pass_args=True))
    dp.add_handler(CommandHandler("restrict_non_text", cmd_restrict_non_text, pass_args=True))
    dp.add_handler(CommandHandler("add_ignore", cmd_add_ignore, pass_args=True))
    dp.add_handler(CommandHandler("remove_ignore", cmd_remove_ignore, pass_args=True))
    dp.add_handler(CommandHandler("ignore_list", cmd_ignore_list))
    dp.add_handler(CommandHandler("remove_solve_kick_msg", cmd_remove_solve_kick_msg, pass_args=True))
    dp.add_handler(CommandHandler("remove_welcome_msg", cmd_remove_welcome_msg, pass_args=True))
    dp.add_handler(CommandHandler("remove_all_msg_kick_on", cmd_remove_all_msg_kick_on))
    dp.add_handler(CommandHandler("remove_all_msg_kick_off", cmd_remove_all_msg_kick_off))
    dp.add_handler(CommandHandler("url_enable", cmd_url_enable))
    dp.add_handler(CommandHandler("url_disable", cmd_url_disable))
    dp.add_handler(CommandHandler("enable", cmd_enable))
    dp.add_handler(CommandHandler("disable", cmd_disable))
    dp.add_handler(CommandHandler("chatid", cmd_chatid))
    dp.add_handler(CommandHandler("version", cmd_version))
    dp.add_handler(CommandHandler("about", cmd_about))
    if (CONST["BOT_OWNER"] != "XXXXXXXXX"):
        dp.add_handler(CommandHandler("captcha", cmd_captcha))
        dp.add_handler(CommandHandler("allowuserlist", cmd_allowuserlist, pass_args=True))
    if (CONST["BOT_OWNER"] != "XXXXXXXXX") and CONST["BOT_PRIVATE"]:
        dp.add_handler(CommandHandler("allowgroup", cmd_allowgroup, pass_args=True))
    # Set to dispatcher a not-command text messages handler
    dp.add_handler(MessageHandler(Filters.text, msg_nocmd, run_async=True))
    # Set to dispatcher not text messages handler
    dp.add_handler(MessageHandler(Filters.photo | Filters.audio | Filters.voice |
            Filters.video | Filters.sticker | Filters.document | Filters.location |
            Filters.contact, msg_notext))
    # Set to dispatcher a new member join the group and member left the group events handlers
    dp.add_handler(ChatMemberHandler(chat_bot_status_change, ChatMemberHandler.MY_CHAT_MEMBER))
    dp.add_handler(ChatMemberHandler(chat_member_status_change, ChatMemberHandler.ANY_CHAT_MEMBER))
    # Set to dispatcher "USER joined the group" messages event handlers
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, msg_user_joined_group))
    # Set to dispatcher inline keyboard callback handler for new captcha request and
    # button captcha challenge
    dp.add_handler(CallbackQueryHandler(key_inline_keyboard))
    # Set to dispatcher users poll vote handler
    dp.add_handler(PollAnswerHandler(receive_poll_answer, run_async=True))
    # Launch the Bot ignoring pending messages (clean=True) and get all updates (allowed_uptades=[])
    if CONST["WEBHOOK_HOST"] == "None":
        printts("Setup Bot for Polling.")
        updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
    else:
        printts("Setup Bot for Webhook.")
        updater.start_webhook(
            drop_pending_updates=True, listen="0.0.0.0", port=CONST["WEBHOOK_PORT"], url_path=CONST["TOKEN"],
            key=CONST["WEBHOOK_CERT_PRIV_KEY"], cert=CONST["WEBHOOK_CERT"],
            webhook_url="https://{}:{}/{}".format(CONST["WEBHOOK_HOST"], CONST["WEBHOOK_PORT"],
            CONST["TOKEN"]), allowed_updates=Update.ALL_TYPES
        )
    printts("Bot setup completed. Bot is now running.")
    # Launch delete mesages and kick users threads
    th_0 = Thread(target=th_selfdestruct_messages, args=(updater.bot,))
    th_1 = Thread(target=th_time_to_kick_not_verify_users, args=(updater.bot,))
    th_0.name = "th_selfdestruct_messages"
    th_1.name = "th_time_to_kick_not_verify_users"
    th_0.start()
    sleep(0.05)
    th_1.start()
    # Set main thread to idle
    # Using Bot idle() catch external signals instead our signal handler
    updater.idle()
    print("Bot Threads end")
    if os_system() == "Windows":
        kill(getpid(), SIGTERM)
    else:
        kill(getpid(), SIGUSR1)
    sleep(1)
    printts("Exit 1")
    exit(1)


if __name__ == "__main__":
    main()
