#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    join_captcha_bot.py
Description:
    Telegram Bot that send a captcha for each new user who join a group,
    and remove them if they can not solve the captcha in a specified
    time.
Author:
    Jose Miguel Rios Rubio
Creation date:
    09/09/2018
Last modified date:
    06/07/2024
Version:
    1.31.2
'''

###############################################################################
# Standard Libraries
###############################################################################

# Logging Library
import logging

# Asynchronous Input-Output Concurrency Library
from asyncio import create_task as asyncio_create_task
from asyncio import sleep as asyncio_sleep

# Collections Data Types Library
from collections import OrderedDict

# JSON Library
from json import dumps as json_dumps

# Operating System Library
from os import path, remove, makedirs, listdir

# Random Library
from random import choice, randint

# Regular Expressions Library
import re

# High Level Files Utils Library
from shutil import rmtree

# System Library
from sys import argv as sys_argv
from sys import exit as sys_exit

# Time Library
from time import time

# Error Traceback Library
from traceback import format_exc

# Built-in Data Types Library
from types import CoroutineType

# Data Types Library
from typing import Optional


###############################################################################
# Third-Party Libraries
###############################################################################

# Image Captcha Generator Library
from multicolorcaptcha import CaptchaGenerator

# Python-Telegram_Bot Core Library
from telegram import (
    Update, Chat, InputMediaPhoto, InlineKeyboardButton,
    InlineKeyboardMarkup, Poll
)

# Python-Telegram_Bot Extension Library
from telegram.ext import (
    Application, CallbackQueryHandler, ChatMemberHandler, ContextTypes,
    Defaults, filters, MessageHandler, PollAnswerHandler,
)

# Python-Telegram_Bot Helpers Library
from telegram.helpers import (
    escape_markdown
)

# Python-Telegram_Bot Error Library
from telegram.error import (
    BadRequest, ChatMigrated, Conflict, Forbidden, InvalidToken, NetworkError,
    PassportDecryptionError, RetryAfter, TelegramError, TimedOut
)


###############################################################################
# Local Libraries
###############################################################################

# Telegram Bot Ease Library
from tlgbotutils import (
    tlg_add_cmd, tlg_send_msg, tlg_send_image, tlg_send_poll, tlg_stop_poll,
    tlg_answer_callback_query, tlg_delete_msg, tlg_edit_msg_media,
    tlg_ban_user, tlg_kick_user, tlg_user_is_admin, tlg_leave_chat,
    tlg_restrict_user, tlg_unrestrict_user, tlg_is_valid_user_id_or_alias,
    tlg_is_valid_group, tlg_alias_in_string, tlg_extract_members_status_change,
    tlg_get_msg, tlg_is_a_channel_msg_on_discussion_group, tlg_get_user_name,
    tlg_member_has_join_group, tlg_member_has_left_group, tlg_get_msg_topic
)

# Commons Library
from commons import (
    is_int, add_lrm, file_exists, file_write, file_read,
    list_remove_element, get_unix_epoch, pickle_save, pickle_restore
)

# Constants Library
from constants import (
    SCRIPT_PATH, CONST, TEXT, CMD
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
# Globals
###############################################################################

class Globals():
    '''Global Elements Container.'''

    files_config_list: list = []
    to_delete_in_time_messages_list: list = []
    new_users: dict = {}
    connections: dict = {}
    async_captcha_timeout: Optional[CoroutineType] = None
    async_auto_delete_messages: Optional[CoroutineType] = None
    force_exit: bool = False


###############################################################################
# Objects Instantiation
###############################################################################

# Global Data Elements
Global = Globals()

# Create Captcha Generator object of specified size (2 -> 640x360)
CaptchaGen = CaptchaGenerator(2)


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


def save_config_property(chat_id, param, value):
    '''
    Store actual chat configuration in file.
    '''
    fjson_config = get_chat_config_file(chat_id)
    config_data = fjson_config.read()
    if not config_data:
        config_data = get_default_config_data()
    if (param in config_data) and (value == config_data[param]):
        return
    config_data[param] = value
    fjson_config.write(config_data)


def get_chat_config(chat_id, param):
    '''
    Get specific stored chat configuration property.
    '''
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
    '''
    Get specific stored chat configuration property.
    '''
    file = get_chat_config_file(chat_id)
    if file:
        config_data = file.read()
        if not config_data:
            config_data = get_default_config_data()
    else:
        config_data = get_default_config_data()
    return config_data


def get_chat_config_file(chat_id):
    '''
    Determine chat config file from the list by ID. Get the file if
    exists or create it if not.
    '''
    file = OrderedDict([("ID", chat_id), ("File", None)])
    found = False
    if Global.files_config_list:
        for chat_file in Global.files_config_list:
            if chat_file["ID"] == chat_id:
                file = chat_file
                found = True
                break
        if not found:
            chat_config_file_name = \
                    f'{CONST["CHATS_DIR"]}/{chat_id}/{CONST["F_CONF"]}'
            file["ID"] = chat_id
            file["File"] = TSjson(chat_config_file_name)
            Global.files_config_list.append(file)
    else:
        chat_config_file_name = \
                f'{CONST["CHATS_DIR"]}/{chat_id}/{CONST["F_CONF"]}'
        file["ID"] = chat_id
        file["File"] = TSjson(chat_config_file_name)
        Global.files_config_list.append(file)
    return file["File"]


###############################################################################
# Telegram Related Functions
###############################################################################

async def tlg_send_msg_type_chat(
        bot, chat_type, chat_id, text, **kwargs_for_send_message):
    '''
    Send a telegram message normal or schedule to auto-delete
    depending of chat type (private chat - normal;
    group - selfdestruct).
    '''
    if chat_type == "private":
        await tlg_send_msg(bot, chat_id, text, **kwargs_for_send_message)
    else:
        await tlg_send_autodelete_msg(
                bot, chat_id, text, **kwargs_for_send_message)


async def tlg_send_autodelete_msg(
        bot,
        chat_id,
        message,
        time_delete_sec=CONST["T_DEL_MSG"],
        **kwargs_for_send_message
        ):
    '''
    Send a telegram message that will be auto-delete in specified time.
    '''
    sent_result = await tlg_send_msg(
            bot, chat_id, message, **kwargs_for_send_message)
    if sent_result["msg"] is None:
        return None
    tlg_autodelete_msg(sent_result["msg"], time_delete_sec)
    return sent_result["msg"].message_id


def tlg_autodelete_msg(message, time_delete_sec=CONST["T_DEL_MSG"]):
    '''
    Add a telegram message to be auto-delete in specified time.
    '''
    # Check if provided message has all necessary attributes
    if message is None:
        return False
    if not hasattr(message, "chat_id"):
        return False
    if not hasattr(message, "message_id"):
        return False
    if not hasattr(message, "from_user"):
        return False
    if not hasattr(message.from_user, "id"):
        return False
    # Get sent message ID and calculate delete time
    chat_id = message.chat_id
    user_id = message.from_user.id
    msg_id = message.message_id
    _t0 = time()
    # Add sent message data to to-delete messages list
    sent_msg_data = OrderedDict(
        [
            ("Chat_id", None), ("User_id", None), ("Msg_id", None),
            ("time", None), ("delete_time", None)
        ]
    )
    sent_msg_data["Chat_id"] = chat_id
    sent_msg_data["User_id"] = user_id
    sent_msg_data["Msg_id"] = msg_id
    sent_msg_data["time"] = _t0
    sent_msg_data["delete_time"] = time_delete_sec
    Global.to_delete_in_time_messages_list.append(sent_msg_data)
    return True


async def bot_send_msg(bot, chat_id, msg_text, rm_result_msg):
    '''
    Send a normal or an auto-delete Telegram message depending of
    rm_result_msg argument.
    '''
    if rm_result_msg:
        await tlg_send_autodelete_msg(
                bot, chat_id, msg_text, CONST["T_FAST_DEL_MSG"])
    else:
        await tlg_send_msg(bot, chat_id, msg_text)


###############################################################################
# General Functions
###############################################################################

def save_session():
    '''
    Backup current execution data.
    '''
    # Let's backup to file
    data = {
        "to_delete_in_time_messages_list":
            Global.to_delete_in_time_messages_list,
        "new_users": Global.new_users,
        "connections": Global.connections
    }
    if not pickle_save(CONST["F_SESSION"], data):
        logger.error("Fail to save current session data")
        return False
    logger.info("Current session data saved")
    return True


def restore_session():
    '''
    Load last execution data.
    '''
    # Check if session file exists
    if not file_exists(CONST["F_SESSION"]):
        return False
    # Get data from session file
    last_session_data = pickle_restore(CONST["F_SESSION"])
    if last_session_data is None:
        logger.error("Fail to restore last session data")
        return False
    # Load last session data to current RAM
    Global.connections = last_session_data["connections"]
    Global.new_users = last_session_data["new_users"]
    Global.to_delete_in_time_messages_list = \
        last_session_data["to_delete_in_time_messages_list"]
    # Renew time to kick users
    for chat_id in Global.new_users:
        for user_id in Global.new_users[chat_id]:
            # Some rand to avoid all requests sent at same time
            _t0 = time() + randint(0, 10)
            Global.new_users[chat_id][user_id]["join_data"]["join_time"] = _t0
    # Renew time to remove messages
    i = 0
    while i < len(Global.to_delete_in_time_messages_list):
        # Some rand to avoid all requests sent at same time
        _t0 = time() + randint(0, 10)
        Global.to_delete_in_time_messages_list[i]["time"] = _t0
        i = i + 1
    logger.info("Last session data restored")
    return True


def initialize_resources():
    '''
    Initialize resources by populating files list with chats found
    files.
    '''
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
        # If chats directory exists, check all subdirs names (chats ID)
        files = listdir(CONST["CHATS_DIR"])
        for f_chat_id in files:
            # Populate config files list
            file_path = f'{CONST["CHATS_DIR"]}/{f_chat_id}/{CONST["F_CONF"]}'
            Global.files_config_list.append(
                    OrderedDict(
                            [("ID", f_chat_id), ("File", TSjson(file_path))]))
            # Create default configuration file if it does not exists
            if not path.exists(file_path):
                default_conf = get_default_config_data()
                for key, value in default_conf.items():
                    save_config_property(f_chat_id, key, value)
    # Load and generate URL detector regex from TLD list file
    load_urls_regex(f'{SCRIPT_PATH}/{CONST["F_TLDS"]}')
    # Load all languages texts
    load_texts_languages()
    logger.info("Resources initialized.")


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
        # Remove last '|' from TLDs list item
        num_tlds = len(list_file_lines)
        last_tld = list_file_lines[num_tlds-1]
        if last_tld[-1] == '|':
            last_tld = last_tld[:-1]
            list_file_lines[num_tlds-1] = last_tld
        # Add all TLDs substring to the URL Regex
        tlds_str = "".join(list_file_lines)
    CONST["REGEX_URLS"] = CONST["REGEX_URLS"].format(tlds_str)


def load_texts_languages():
    '''
    Load all texts from each language file.
    '''
    # Initialize all languages to english texts by default, so if
    # some language file miss some field, the english text is used
    lang_file = f'{CONST["LANG_DIR"]}/{CONST["INIT_LANG"].lower()}.json'
    json_init_lang_texts = TSjson(lang_file).read()
    if (json_init_lang_texts is None) or (json_init_lang_texts == {}):
        logger.error(
                "Loading language \"%s\" from %s. Language file not "
                "found or bad JSON syntax.",
                CONST["INIT_LANG"].lower(), lang_file)
        logger.info("Exit.\n")
        sys_exit(0)
    for lang_iso_code, _ in TEXT.items():
        TEXT[lang_iso_code] = json_init_lang_texts.copy()
    # Load supported languages texts
    for lang_iso_code, _ in TEXT.items():
        lang_file = f'{CONST["LANG_DIR"]}/{lang_iso_code.lower()}.json'
        json_lang_file = TSjson(lang_file)
        json_lang_texts = json_lang_file.read()
        if (json_lang_texts is None) or (json_lang_texts == {}):
            logger.error(
                    "Loading language \"%s\" from %s. "
                    "Language file not found or bad JSON syntax.",
                    lang_iso_code, lang_file)
            logger.info("Exit.\n")
            sys_exit(0)
        TEXT[lang_iso_code] = json_lang_texts
    # Check if there is some missing text in any language
    for lang_iso_code in TEXT:
        lang_iso_code = lang_iso_code.lower()
        lang_file = f'{CONST["LANG_DIR"]}/{lang_iso_code}.json'
        json_lang_file = TSjson(lang_file)
        json_lang_texts = json_lang_file.read()
        for text in json_init_lang_texts:
            if text not in json_lang_texts:
                logger.warning(
                        "Text \"%s\" missing from language file \"%s\".json",
                        text, lang_iso_code)


def create_image_captcha(chat_id, file_name, difficult_level, captcha_mode):
    '''
    Generate an image captcha from pseudo numbers.
    '''
    # If it doesn't exists, create captchas folder to store them
    img_dir_path = f'{CONST["CAPTCHAS_DIR"]}/{chat_id}'
    img_file_path = f'{img_dir_path}/{file_name}.png'
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
        captcha = CaptchaGen.gen_captcha_image(
            difficult_level, captcha_mode, bool(randint(0, 1)))
        captcha_result["characters"] = captcha["characters"]
    captcha["image"].save(img_file_path, "png")
    return captcha_result


def num_config_poll_options(poll_options):
    '''
    Check how many poll options are configured.
    '''
    configured_options = 0
    for i in range(0, CONST["MAX_POLL_OPTIONS"]):
        if poll_options[i] != "":
            configured_options = configured_options + 1
    return configured_options


def is_user_in_ignored_list(chat_id, user):
    '''
    Check if user is in ignored users list.
    '''
    ignored_users = get_chat_config(chat_id, "Ignore_List")
    if user.id in ignored_users:
        return True
    if user.username is not None:
        user_alias = f"@{user.username}"
        if user_alias in ignored_users:
            return True
    return False


def is_user_in_allowed_list(user):
    '''
    Check if user is in global allowed list.
    '''
    l_white_users = file_read(CONST["F_ALLOWED_USERS"])
    if user.id in l_white_users:
        return True
    if user.username is not None:
        user_alias = f"@{user.username}"
        if user_alias in l_white_users:
            return True
    return False


def is_group_in_allowed_list(chat_id):
    '''
    Check if group is in allowed list.
    '''
    # True if Bot is Public
    if not CONST["BOT_PRIVATE"]:
        return True
    l_allowed_groups = file_read(CONST["F_ALLOWED_GROUPS"])
    if str(chat_id) in l_allowed_groups:
        return True
    return False


def is_group_in_banned_list(chat_id):
    '''
    Check if group is in banned list.
    '''
    l_banned_groups = file_read(CONST["F_BAN_GROUPS"])
    if str(chat_id) in l_banned_groups:
        return True
    return False


async def allowed_in_this_group(bot, chat, member_added_by):
    '''
    Check if Bot is allowed to be used in a Chat.
    '''
    if not is_group_in_allowed_list(chat.id):
        logger.warning("Bot added to not allowed group.")
        from_user_name = ""
        if member_added_by.name is not None:
            from_user_name = member_added_by.name
        else:
            from_user_name = member_added_by.full_name
        chat_link = ""
        if chat.username:
            chat_link = f"@{chat.username}"
        logger.info(
                "%s, %s, %s, %s",
                chat.id, from_user_name, chat.title, chat_link)
        msg_text = CONST["NOT_ALLOW_GROUP"].format(
                CONST["BOT_OWNER"], chat.id, CONST["REPOSITORY"])
        await tlg_send_msg(bot, chat.id, msg_text)
        return False
    if is_group_in_banned_list(chat.id):
        logger.warning("[%d] Bot added to banned group", chat.id)
        return False
    return True


def get_update_user_lang(update_user_data):
    '''
    Get user language-code from Telegram Update user data and return
    Bot supported language (english if not supported).
    '''
    lang = getattr(update_user_data, "language_code", "EN")
    if lang is None:
        lang = "EN"
    lang = lang.upper()
    if lang not in TEXT:
        lang = "EN"
    return lang


def is_captcha_num_solve(captcha_mode, msg_text, solve_num):
    '''
    Check if number send by user solves a num/hex/ascii/math captcha.
    - For "math", the message must be the exact math equation result
    number.
    - For other mode, the message must contains the numbers.
    '''
    if captcha_mode == "math":
        if msg_text == solve_num:
            return True
    else:
        if solve_num.lower() in msg_text.lower():
            return True
        # Check if the message is the valid number but with spaces
        if len(msg_text) == len("1 2 3 4"):
            solve_num_with_spaces = " ".join(solve_num)
            if solve_num_with_spaces.lower() == msg_text.lower():
                return True
    return False


async def should_manage_captcha(update, bot):
    '''
    Check if the Bot should manage a Captcha process to this Group and
    Member. It checks if the group is allowed to use the Bot, checks if
    the member is not an Administrator neither a member added by an
    Admin, or an added Bot, and checks if the Member is not in any of
    the allowed users lists.
    '''
    chat = update.chat_member.chat
    join_user = update.chat_member.new_chat_member.user
    member_added_by = update.chat_member.from_user
    # Check if Group is not allowed to be used by the Bot
    if not await allowed_in_this_group(bot, chat, member_added_by):
        await tlg_leave_chat(bot, chat.id)
        return False
    # Ignore Admins
    if await tlg_user_is_admin(bot, chat.id, join_user.id):
        logger.info("[%d] User is an admin.", chat.id)
        logger.info("Skipping the captcha process.")
        return False
    # Ignore Members added by an Admin
    if await tlg_user_is_admin(bot, chat.id, member_added_by.id):
        logger.info("[%d] User has been added by an admin.", chat.id)
        logger.info("Skipping the captcha process.")
        return False
    # Ignore if the member that has been join the group is a Bot
    if join_user.is_bot:
        logger.info("[%d] User is a Bot.", chat.id)
        logger.info("Skipping the captcha process.")
        return False
    # Ignore if the member that has joined is in chat ignore list
    if is_user_in_ignored_list(chat.id, join_user):
        logger.info("[%d] User is in ignore list.", chat.id)
        logger.info("Skipping the captcha process.")
        return False
    if is_user_in_allowed_list(join_user):
        logger.info("[%d] User is in global allowed list.", chat.id)
        logger.info("Skipping the captcha process.")
        return False
    return True


async def restrict_user_mute(bot, chat_id, user_id, until_date=None):
    '''Restrict an user in order to deny it send any kind of message.'''
    restrict_success = await tlg_restrict_user(
        bot, chat_id, user_id,
        send_msg=False,
        send_media=False,
        send_polls=False,
        send_stickers_gifs=False,
        insert_links=False,
        change_group_info=False,
        invite_members=False,
        pin_messages=False,
        manage_topics=False,
        until_date=until_date)
    return restrict_success


async def restrict_user_media(bot, chat_id, user_id, until_date=None):
    '''Restrict an user in order to deny it send media messages.'''
    restrict_success = await tlg_restrict_user(
        bot, chat_id, user_id,
        send_msg=True,
        send_media=False,
        send_polls=False,
        send_stickers_gifs=False,
        insert_links=False,
        change_group_info=False,
        invite_members=False,
        pin_messages=False,
        manage_topics=False,
        until_date=until_date)
    return restrict_success


async def captcha_fail_member_mute(bot, chat_id, user_id, user_name):
    '''
    Restrict the user to deny send any kind of message for 24h.
    '''
    lang = get_chat_config(chat_id, "Language")
    user_name = Global.new_users[chat_id][user_id]["join_data"]["user_name"]
    mute_until_24h = get_unix_epoch() + CONST["T_SECONDS_IN_A_DAY"]
    logger.info("[%s] Captcha Fail - Mute - %s (%s)",
                chat_id, user_name, user_id)
    success = await restrict_user_mute(bot, chat_id, user_id, mute_until_24h)
    if success:
        msg_text = TEXT[lang]["CAPTCHA_FAIL_MUTE"].format(user_name)
        if lang != "EN":
            bilang = get_chat_config(chat_id, "BiLang")
            if bilang:
                en_text = TEXT["EN"]["CAPTCHA_FAIL_MUTE"].format(user_name)
                msg_text = f"{msg_text}\n\n{en_text}"
    else:
        msg_text = TEXT[lang]["CAPTCHA_FAIL_CANT_RESTRICT"].format(user_name)
    rm_result_msg = get_chat_config(chat_id, "Rm_Result_Msg")
    await bot_send_msg(bot, chat_id, msg_text, rm_result_msg)


async def captcha_fail_member_no_media(bot, chat_id, user_id, user_name):
    '''
    Restrict the user to deny send media messages (images, video, audio,
    etc.) for 24h.
    '''
    lang = get_chat_config(chat_id, "Language")
    mute_until_24h = get_unix_epoch() + CONST["T_SECONDS_IN_A_DAY"]
    logger.info("[%s] Captcha Fail - Media - %s (%s)",
                chat_id, user_name, user_id)
    success = await restrict_user_media(bot, chat_id, user_id, mute_until_24h)
    if success:
        msg_text = TEXT[lang]["CAPTCHA_FAIL_NO_MEDIA"].format(user_name)
        if lang != "EN":
            bilang = get_chat_config(chat_id, "BiLang")
            if bilang:
                en_text = TEXT["EN"]["CAPTCHA_FAIL_NO_MEDIA"].format(user_name)
                msg_text = f"{msg_text}\n\n{en_text}"
    else:
        msg_text = TEXT[lang]["CAPTCHA_FAIL_CANT_RESTRICT"].format(user_name)
    rm_result_msg = get_chat_config(chat_id, "Rm_Result_Msg")
    await bot_send_msg(bot, chat_id, msg_text, rm_result_msg)


async def captcha_fail_member_kick(bot, chat_id, user_id, user_name):
    '''
    Kick or Ban the user from the group.
    '''
    banned = False
    # Get parameters
    lang = get_chat_config(chat_id, "Language")
    rm_result_msg = get_chat_config(chat_id, "Rm_Result_Msg")
    captcha_mode = get_chat_config(chat_id, "Captcha_Chars_Mode")
    # Set Max user captcha consecutive retries before Ban
    max_join_retries = CONST["MAX_FAIL_BAN"]
    if captcha_mode == "poll":
        max_join_retries = CONST["MAX_FAIL_BAN_POLL"]
    join_retries = \
        Global.new_users[chat_id][user_id]["join_data"]["join_retries"]
    logger.info("[%s] %s join_retries: %d", chat_id, user_id, join_retries)
    # Kick if user has fail to solve the captcha less than
    # "max_join_retries"
    if join_retries < max_join_retries:
        logger.info("[%s] Captcha Fail - Kick - %s (%s)",
                    chat_id, user_name, user_id)
        # Try to kick the user
        kick_result = await tlg_kick_user(bot, chat_id, user_id)
        if kick_result["error"] == "":
            # Kick success
            join_retries = join_retries + 1
            msg_text = TEXT[lang]["CAPTCHA_FAIL_KICK"].format(user_name)
            if lang != "EN":
                bilang = get_chat_config(chat_id, "BiLang")
                if bilang:
                    en_text = TEXT["EN"]["CAPTCHA_FAIL_KICK"].format(user_name)
                    msg_text = f"{msg_text}\n\n{en_text}"
            await bot_send_msg(bot, chat_id, msg_text, rm_result_msg)
        else:
            # Kick fail
            logger.info("[%s] Unable to kick", chat_id)
            if ((kick_result["error"] == "The user has left the group") or
                    (kick_result["error"] == "The user was already kicked")):
                # The user is not in the chat
                msg_text = TEXT[lang]["NEW_USER_KICK_NOT_IN_CHAT"].format(
                        user_name)
                await bot_send_msg(bot, chat_id, msg_text, rm_result_msg)
            elif kick_result["error"] == \
                    "Not enough rights to restrict/unrestrict chat member":
                # Bot has no privileges to kick
                msg_text = TEXT[lang]["NEW_USER_KICK_NOT_RIGHTS"].format(
                        user_name)
                # Send no rights for kick message without auto-remove
                await bot_send_msg(bot, chat_id, msg_text, False)
            else:
                # For other reason, the Bot can't ban
                msg_text = TEXT[lang]["BOT_CANT_KICK"].format(user_name)
                await bot_send_msg(bot, chat_id, msg_text, rm_result_msg)
    # Ban if user has join "max_join_retries" times without solving
    # the captcha
    else:
        logger.info("[%s] Captcha Fail - Ban - %s (%s)",
                    chat_id, user_name, user_id)
        # Try to ban the user and notify Admins
        ban_result = await tlg_ban_user(bot, chat_id, user_id)
        if ban_result["error"] == "":
            # Ban success
            banned = True
            msg_text = TEXT[lang]["CAPTCHA_FAIL_BAN"].format(
                    user_name, max_join_retries)
            if lang != "EN":
                bilang = get_chat_config(chat_id, "BiLang")
                if bilang:
                    en_text = TEXT["EN"]["CAPTCHA_FAIL_BAN"].format(
                        user_name, max_join_retries)
                    msg_text = f"{msg_text}\n\n{en_text}"
        else:
            # Ban fail
            if ban_result["error"] == "User not found":
                # The user is not in the chat
                msg_text = TEXT[lang]["NEW_USER_BAN_NOT_IN_CHAT"].format(
                        user_name, max_join_retries)
            elif ban_result["error"] \
                    == "Not enough rights to restrict/un-restrict chat member":
                # Bot has no privileges to ban
                msg_text = TEXT[lang]["NEW_USER_BAN_NOT_RIGHTS"].format(
                        user_name, max_join_retries)
            else:
                # For other reason, the Bot can't ban
                msg_text = TEXT[lang]["BOT_CANT_BAN"].format(
                        user_name, max_join_retries)
        # Send ban notify message
        logger.info("[%s] %s", chat_id, msg_text)
        if rm_result_msg:
            await tlg_send_autodelete_msg(bot, chat_id, msg_text)
        else:
            await tlg_send_msg(bot, chat_id, msg_text)
    # Update user info (join_retries & kick_ban)
    try:
        Global.new_users[chat_id][user_id]["join_data"]["kicked_ban"] = True
        Global.new_users[chat_id][user_id]["join_data"]["join_retries"] = \
            join_retries
        # Delete user join info if ban was success
        if banned:
            del Global.new_users[chat_id][user_id]
    except KeyError:
        logger.warning(
                "[%s] %s (%d) not in new_users list (already solve captcha)",
                chat_id, user_name, user_id)


async def captcha_fail_member(bot, chat_id, user_id):
    '''
    Restrict (Kick, Ban, mute, etc) a new member that has fail to solve
    the captcha.
    '''
    user_name = Global.new_users[chat_id][user_id]["join_data"]["user_name"]
    restriction = get_chat_config(chat_id, "Fail_Restriction")
    if restriction == CMD["RESTRICTION"]["MUTE"]:
        await captcha_fail_member_mute(bot, chat_id, user_id, user_name)
    elif restriction == CMD["RESTRICTION"]["MEDIA"]:
        await captcha_fail_member_no_media(bot, chat_id, user_id, user_name)
    else:  # restriction == CMD["RESTRICTION"]["KICK"]
        await captcha_fail_member_kick(bot, chat_id, user_id, user_name)
    # Remove join messages
    try:
        logger.info("[%s] Removing msgs from user %s...", chat_id, user_name)
        join_msg = Global.new_users[chat_id][user_id]["join_msg"]
        if join_msg is not None:
            await tlg_delete_msg(bot, chat_id, join_msg)
        for msg in Global.new_users[chat_id][user_id]["msg_to_rm"]:
            await tlg_delete_msg(bot, chat_id, msg)
        Global.new_users[chat_id][user_id]["msg_to_rm"].clear()
        for msg in Global.new_users[chat_id][user_id]["msg_to_rm_on_kick"]:
            await tlg_delete_msg(bot, chat_id, msg)
        Global.new_users[chat_id][user_id]["msg_to_rm_on_kick"].clear()
        if restriction != CMD["RESTRICTION"]["KICK"]:
            del Global.new_users[chat_id][user_id]
    except KeyError:
        logger.warning(
                "[%s] %s (%d) not in new_users list (already solve captcha)",
                chat_id, user_name, user_id)


###############################################################################
# Received Telegram not-command messages handlers
###############################################################################

async def chat_bot_status_change(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Get Bot chats status changes (Bot was added to group/channel,
    started/stopped conversation in private chat, etc.) event handler.
    '''
    # Check Bot changes
    result = tlg_extract_members_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result
    # Get chat data
    bot = context.bot
    chat = update.effective_chat
    caused_by_user = update.effective_user
    if chat is None:
        return
    # Private Chat
    if chat.type == Chat.PRIVATE:
        return
    # Groups
    if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        # Bot added to group
        if not was_member and is_member:
            # Get the language of the Telegram client software the Admin
            # that has added the Bot has, to assume this is the chat
            # language and configure Bot language of this chat
            admin_language = ""
            language_code = getattr(caused_by_user, "language_code", None)
            if language_code:
                admin_language = language_code[0:2].upper()
            if admin_language not in TEXT:
                admin_language = CONST["INIT_LANG"]
            save_config_property(chat.id, "Language", admin_language)
            # Get and save chat data
            chat_link = "Unknown"
            if chat.title:
                save_config_property(chat.id, "Title", chat.title)
                chat_link = chat.title
            if chat.username:
                chat_link = f"@{chat.username}"
                save_config_property(chat.id, "Link", chat_link)
            logger.info(
                "[%s] Bot added to group %s by %s (%s)",
                chat.id, chat_link, caused_by_user.username, caused_by_user.id)
            # Check if Group is not allowed to be used by the Bot
            if not await allowed_in_this_group(bot, chat, caused_by_user):
                await tlg_leave_chat(bot, chat.id)
                return
            # Send bot join message
            await tlg_send_msg(bot, chat.id, TEXT[admin_language]["START"])
        # Bot leave/removed from group
        elif was_member and not is_member:
            # Bot leave the group
            if caused_by_user.id == bot.id:
                # Bot left the group by itself
                logger.info("[%s] Bot leave the group", chat.id)
            # Bot removed from group
            else:
                logger.info(
                        "[%d] Bot removed from group by %s",
                        chat.id, caused_by_user.username)
        return
    # Bot added to channel
    if not was_member and is_member:
        # Leave it (Bot don't allowed to be used in Channels)
        logger.info("Bot added to channel, leaving")
        await tlg_send_msg(bot, chat.id, CONST["BOT_LEAVE_CHANNEL"])
        await tlg_leave_chat(bot, chat.id)
        return
    # Bot leave/removed channel
    return


async def chat_member_status_change(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Get Members chats status changes (user join/leave/added/removed
    to/from group/channel) event handler. Note: if Bot is not an Admin,
    "chat_member" update won't be received.
    '''
    bot = context.bot
    # Get Chat data
    chat = update.chat_member.chat
    join_user = update.chat_member.new_chat_member.user
    chat_id = chat.id
    # Get User ID and Name
    join_user_id = join_user.id
    join_user_name = tlg_get_user_name(join_user, 35)
    # Ignore if it is not a new member join
    if not tlg_member_has_join_group(update.chat_member):
        # Remove "TheJoinCaptchaBot removed USER" message
        if tlg_member_has_left_group(update.chat_member):
            logger.info(
                "[%s] User %s (%s) left the group",
                chat.id, join_user_name, join_user_id)
        return
    logger.info(
            "[%s] New join detected: %s (%s)",
            chat_id, join_user_name, join_user_id)
    # Get and update chat data
    chat_title = chat.title
    if chat_title:
        save_config_property(chat_id, "Title", chat_title)
    # Add an unicode Left to Right Mark (LRM) to chat title (fix for
    # arabic, hebrew, etc.)
    chat_title = add_lrm(chat_title)
    chat_link = chat.username
    if chat_link:
        chat_link = f"@{chat_link}"
        save_config_property(chat_id, "Link", chat_link)
    # Check if the Bot should manage a Captcha process to this Group
    # and Member
    if not await should_manage_captcha(update, bot):
        return
    # Check and remove previous join messages of that user (if any)
    if chat_id in Global.new_users:
        if join_user_id in Global.new_users[chat_id]:
            if "msg_to_rm" in Global.new_users[chat_id][join_user_id]:
                for msg in \
                        Global.new_users[chat_id][join_user_id]["msg_to_rm"]:
                    await tlg_delete_msg(bot, chat_id, msg)
                Global.new_users[chat_id][join_user_id]["msg_to_rm"].clear()
    # Ignore if the captcha protection is not enable in this chat
    captcha_enable = get_chat_config(chat_id, "Enabled")
    if not captcha_enable:
        logger.info("[%s] Captcha is not enabled in this chat", chat_id)
        return
    # Determine configured language and captcha settings
    lang = get_chat_config(chat_id, "Language")
    captcha_level = get_chat_config(chat_id, "Captcha_Difficulty_Level")
    captcha_mode = get_chat_config(chat_id, "Captcha_Chars_Mode")
    captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
    if captcha_timeout < CONST["T_SECONDS_IN_MIN"]:
        timeout_str = f"{captcha_timeout} sec"
    else:
        timeout_str = f'{int(captcha_timeout / CONST["T_SECONDS_IN_MIN"])} min'
    send_problem = False
    captcha_num = ""
    if captcha_mode == "random":
        captcha_mode = choice(["nums", "math", "poll"])
        # If Captcha Mode Poll is not configured use another mode
        if captcha_mode == "poll":
            poll_question = get_chat_config(chat_id, "Poll_Q")
            poll_options = get_chat_config(chat_id, "Poll_A")
            poll_correct_option = get_chat_config(chat_id, "Poll_C_A")
            if ((poll_question == "") or
                    (num_config_poll_options(poll_options) < 2) or
                    (poll_correct_option == 0)):
                captcha_mode = choice(["nums", "math"])
    if captcha_mode == "button":
        # Send a button-only challenge
        challenge_text = TEXT[lang]["NEW_USER_BUTTON_MODE"].format(
                join_user_name, chat_title, timeout_str)
        if lang != "EN":
            bilang = get_chat_config(chat_id, "BiLang")
            if bilang:
                en_text = TEXT["EN"]["NEW_USER_BUTTON_MODE"].format(
                    join_user_name, chat_title, timeout_str)
                challenge_text = f"{challenge_text}\n\n{en_text}"
        # Prepare inline keyboard button to let user pass
        keyboard = [[
                InlineKeyboardButton(
                        TEXT[lang]["PASS_BTN_TEXT"],
                        callback_data=f"button_captcha {join_user_id}")
                ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        logger.info(
                "[%s] Sending captcha message to %s: [button]",
                chat_id, join_user_name)
        sent_result = await tlg_send_msg(
                bot, chat_id, challenge_text, reply_markup=reply_markup)
        if sent_result["msg"] is None:
            send_problem = True
    elif captcha_mode == "poll":
        poll_question = get_chat_config(chat_id, "Poll_Q")
        poll_options = get_chat_config(chat_id, "Poll_A")
        poll_correct_option = get_chat_config(chat_id, "Poll_C_A")
        if ((poll_question == "") or
                (num_config_poll_options(poll_options) < 2) or
                (poll_correct_option == 0)):
            await tlg_send_autodelete_msg(
                    bot, chat_id, TEXT[lang]["POLL_NEW_USER_NOT_CONFIG"],
                    CONST["T_FAST_DEL_MSG"])
            return
        # Remove empty strings from options list
        poll_options = list(filter(None, poll_options))
        # Send request to solve the poll text message
        poll_request_msg_text = TEXT[lang]["POLL_NEW_USER"].format(
                join_user_name, chat_title, timeout_str)
        if lang != "EN":
            bilang = get_chat_config(chat_id, "BiLang")
            if bilang:
                en_text = TEXT["EN"]["POLL_NEW_USER"].format(
                    join_user_name, chat_title, timeout_str)
                poll_request_msg_text = f"{poll_request_msg_text}\n\n{en_text}"
        sent_result = await tlg_send_autodelete_msg(
                bot, chat_id, poll_request_msg_text, captcha_timeout)
        solve_poll_request_msg_id = None
        if sent_result is not None:
            solve_poll_request_msg_id = sent_result
        # Send the Poll
        sent_result = await tlg_send_poll(
                bot, chat_id, poll_question, poll_options,
                poll_correct_option-1, captcha_timeout, False, Poll.QUIZ,
                read_timeout=20)
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
    else:  # Image captcha
        # Generate a pseudorandom captcha send it to telegram group and
        # program message
        captcha = create_image_captcha(
                chat_id, join_user_id, captcha_level, captcha_mode)
        if captcha_mode == "math":
            captcha_num = captcha["equation_result"]
            logger.info(
                    "[%s] Sending captcha message to %s: %s=%s...",
                    chat_id, join_user_name, captcha["equation_str"],
                    captcha["equation_result"])
            # Note: Img caption must be <= 1024 chars
            img_caption = TEXT[lang]["NEW_USER_MATH_CAPTION"].format(
                    join_user_name, chat_title, timeout_str)
            if lang != "EN":
                bilang = get_chat_config(chat_id, "BiLang")
                if bilang:
                    en_text = TEXT["EN"]["NEW_USER_MATH_CAPTION"].format(
                        join_user_name, chat_title, timeout_str)
                    img_caption = f"{img_caption}\n\n{en_text}"
            img_caption = img_caption[:1024]
        else:
            captcha_num = captcha["characters"]
            logger.info(
                    "[%s] Sending captcha message to %s: %s...",
                    chat_id, join_user_name, captcha_num)
            # Note: Img caption must be <= 1024 chars
            img_caption = TEXT[lang]["NEW_USER_IMG_CAPTION"].format(
                    join_user_name, chat_title, timeout_str)
            if lang != "EN":
                bilang = get_chat_config(chat_id, "BiLang")
                if bilang:
                    en_text = TEXT["EN"]["NEW_USER_IMG_CAPTION"].format(
                        join_user_name, chat_title, timeout_str)
                    img_caption = f"{img_caption}\n\n{en_text}"
            img_caption = img_caption[:1024]
        # Prepare inline keyboard button to let user request another
        # captcha
        keyboard = [[
                InlineKeyboardButton(
                        TEXT[lang]["OTHER_CAPTCHA_BTN_TEXT"],
                        callback_data=f"image_captcha {join_user_id}")
                ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send the image
        sent_result = {}
        sent_result["msg"] = None
        try:
            with open(captcha["image"], "rb") as file_image:
                sent_result = await tlg_send_image(
                        bot, chat_id, file_image, img_caption,
                        reply_markup=reply_markup, read_timeout=20)
        except Exception:
            logger.error(format_exc())
            logger.error("Fail to send image to Telegram")
            send_problem = True
        if sent_result["msg"] is None:
            send_problem = True
        # Remove sent captcha image file from file system
        if path.exists(captcha["image"]):
            remove(captcha["image"])
    if not send_problem:
        # Add sent captcha message to auto-delete list
        if sent_result["msg"] is not None:
            tlg_autodelete_msg(
                    sent_result["msg"], captcha_timeout + 10)
        # Default user join data
        join_data = {
            "user_name": join_user_name,
            "captcha_num": captcha_num,
            "captcha_mode": captcha_mode,
            "join_time": time(),
            "captcha_timeout": captcha_timeout,
            "join_retries": 1,
            "kicked_ban": False
        }
        # Create dict keys for new user
        if chat_id not in Global.new_users:
            Global.new_users[chat_id] = {}
        if join_user_id not in Global.new_users[chat_id]:
            Global.new_users[chat_id][join_user_id] = {}
        if "join_data" not in Global.new_users[chat_id][join_user_id]:
            Global.new_users[chat_id][join_user_id]["join_data"] = {}
        if "join_msg" not in Global.new_users[chat_id][join_user_id]:
            Global.new_users[chat_id][join_user_id]["join_msg"] = None
        if "msg_to_rm" not in Global.new_users[chat_id][join_user_id]:
            Global.new_users[chat_id][join_user_id]["msg_to_rm"] = []
        if "msg_to_rm_on_kick" not in Global.new_users[chat_id][join_user_id]:
            Global.new_users[chat_id][join_user_id]["msg_to_rm_on_kick"] = []
        # Check if this user was before in the chat without solve the
        # captcha and restore previous join_retries
        if len(Global.new_users[chat_id][join_user_id]["join_data"]) != 0:
            user_join_data = \
                    Global.new_users[chat_id][join_user_id]["join_data"]
            join_data["join_retries"] = user_join_data["join_retries"]
        # Add new user join data and messages to be removed
        Global.new_users[chat_id][join_user_id]["join_data"] = join_data
        if update.message:
            Global.new_users[chat_id][join_user_id]["join_msg"] = \
                    update.message.message_id
        if sent_result["msg"]:
            Global.new_users[chat_id][join_user_id]["msg_to_rm"].append(
                    sent_result["msg"].message_id)
        if ((captcha_mode == "poll") and
                (solve_poll_request_msg_id is not None)):
            Global.new_users[chat_id][join_user_id]["msg_to_rm"].append(
                    solve_poll_request_msg_id)
        # Restrict user to deny send any kind of message until captcha
        # is solve. Allow send text messages for image based captchas
        # that requires it
        if captcha_mode in ["poll", "button"]:
            await restrict_user_mute(bot, chat_id, join_user_id)
        else:  # Restrict user to only allow send text messages
            await restrict_user_media(bot, chat_id, join_user_id)
        logger.info("[%s] Captcha send process completed.", chat_id)


async def user_joined_group_msg_rx(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    New member join the group event handler.
    This handler is trigger when a "USER joined the group" message is
    received in a chat.
    '''
    # Disable unused arguments
    del context
    # Get message data
    chat_id = None
    update_msg = tlg_get_msg(update)
    if update_msg is not None:
        chat_id = getattr(update_msg, "chat_id", None)
    if (update_msg is None) or (chat_id is None):
        logger.info("Warning: Received an unexpected update.")
        logger.info(update)
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
        if chat_id not in Global.new_users:
            continue
        # Ignore if user is not expected
        if join_user.id not in Global.new_users[chat_id]:
            continue
        # If user has join the group, add the "USER joined the group"
        # message ID to new user data to be removed
        Global.new_users[chat_id][join_user.id]["join_msg"] = msg_id


async def user_left_group(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Member left a group or was removed event handler.
    This handler is trigger when a "USER left group" or
    "BOT removed USER" message is received in a chat.
    '''
    bot = context.bot
    # Get message data
    chat_id = None
    update_msg = tlg_get_msg(update)
    if update_msg is not None:
        chat_id = getattr(update_msg, "chat_id", None)
    if (update_msg is None) or (chat_id is None):
        logger.info("Warning: Received an unexpected update.")
        logger.info(update)
        return
    msg_id = getattr(update_msg, "message_id", None)
    if msg_id is None:
        return
    if update_msg.from_user.id == bot.id:
        logger.info(
            "[%s] Delete \"%s removed %s\" msg",
            chat_id, update_msg.from_user.username,
            update_msg.left_chat_member.username)
        await tlg_delete_msg(bot, chat_id, msg_id)


async def media_msg_rx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    All multimedia messages reception handler.
    Messages that trigger this handler are:
    Documents, photos, videos, audio, voice, sticker, location, contact.
    '''
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
        logger.info("Warning: Received an unexpected update.")
        logger.info(update)
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
    if chat_id not in Global.new_users:
        return
    if user_id not in Global.new_users[chat_id]:
        return
    # Get username, if has an alias, just use the alias
    user_name = update_msg.from_user.full_name
    if update_msg.from_user.username is not None:
        user_name = f"@{update_msg.from_user.username}"
    # Remove send message and notify that not text messages are not
    # allowed until solve captcha
    msg_id = update_msg.message_id
    logger.info("[%s] Removing non-text msg sent by %s", chat_id, user_name)
    await tlg_delete_msg(bot, chat_id, msg_id)
    lang = get_chat_config(chat_id, "Language")
    bot_msg = TEXT[lang]["NOT_TEXT_MSG_ALLOWED"].format(user_name)
    await tlg_send_autodelete_msg(
            bot, chat_id, bot_msg, CONST["T_FAST_DEL_MSG"],
            topic_id=tlg_get_msg_topic(update_msg))


async def text_msg_rx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Text messages reception handler.
    '''
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
        logger.info("Warning: Received an unexpected update.")
        logger.info(update)
        return
    topic_id = tlg_get_msg_topic(update_msg)
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
    # If message doesn't has text, check for caption fields (for no text
    # msgs and forward ones)
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
                    msg_text = f"{msg_text} [{url}]"
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
        chat_link = f"@{chat_link}"
        save_config_property(chat_id, "Link", chat_link)
    user_name = update_msg.from_user.full_name
    # If has an alias, just use the alias
    if update_msg.from_user.username is not None:
        user_name = f"@{update_msg.from_user.username}"
    # Set default text message if not received
    if msg_text is None:
        msg_text = "[Not a text message]"
    # Check if group is configured to deny users send URLs, and
    # remove URLs msg
    url_enable = get_chat_config(chat_id, "URL_Enabled")
    if not url_enable:
        # Ignore if message comes from an Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if is_admin:
            return
        # Get Chat configured language
        lang = get_chat_config(chat_id, "Language")
        # Check for Spam (check if the message contains any URL)
        has_url = re.findall(CONST["REGEX_URLS"], msg_text)
        if has_url:
            # Try to remove the message and notify detection
            delete_result = await tlg_delete_msg(bot, chat_id, msg_id)
            if delete_result["error"] == "":
                bot_msg = TEXT[lang]["URL_MSG_NOT_ALLOWED_DETECTED"].format(
                        user_name)
                await tlg_send_autodelete_msg(
                        bot, chat_id, bot_msg,
                        CONST["T_FAST_DEL_MSG"],
                        topic_id=topic_id)
    # Ignore if message is not from a new user that has not completed
    # the captcha yet
    if chat_id not in Global.new_users:
        return
    if user_id not in Global.new_users[chat_id]:
        return
    # Get Chat settings
    lang = get_chat_config(chat_id, "Language")
    rm_result_msg = get_chat_config(chat_id, "Rm_Result_Msg")
    captcha_mode = \
        Global.new_users[chat_id][user_id]["join_data"]["captcha_mode"]
    # Check for forwarded messages and delete it
    forward_from = getattr(update_msg, "forward_from", None)
    forward_from_chat = getattr(update_msg, "forward_from_chat", None)
    if (forward_from is not None) or (forward_from_chat is not None):
        logger.info("[%s] Spammer detected: %s.", chat_id, user_name)
        logger.info("[%s] Removing forwarded msg: %s.", chat_id, msg_text)
        delete_result = await tlg_delete_msg(bot, chat_id, msg_id)
        if delete_result["error"] == "":
            logger.info("Message removed.")
        else:
            logger.info("Message can't be deleted.")
        return
    # Check for Spam (check if the message contains any URL or alias)
    has_url = re.findall(CONST["REGEX_URLS"], msg_text)
    has_alias = tlg_alias_in_string(msg_text)
    if has_url or has_alias:
        logger.info("[%s] Spammer detected: %s.", chat_id, user_name)
        logger.info("[%s] Removing spam message: %s.", chat_id, msg_text)
        # Try to remove the message and notify detection
        delete_result = await tlg_delete_msg(bot, chat_id, msg_id)
        if delete_result["error"] == "":
            bot_msg = TEXT[lang]["SPAM_DETECTED_RM"].format(user_name)
            await tlg_send_autodelete_msg(
                    bot, chat_id, bot_msg, CONST["T_FAST_DEL_MSG"],
                    topic_id=topic_id)
        else:
            bot_msg = TEXT[lang]["SPAM_DETECTED_NOT_RM"].format(user_name)
            await tlg_send_autodelete_msg(
                    bot, chat_id, bot_msg, CONST["T_FAST_DEL_MSG"],
                    topic_id=topic_id)
            logger.info("Message can't be deleted.")
        return
    # Check group config regarding if all messages of user must be
    # removed when kick
    rm_all_msg = get_chat_config(chat_id, "RM_All_Msg")
    if rm_all_msg:
        Global.new_users[chat_id][user_id]["msg_to_rm_on_kick"].append(msg_id)
    # End here if no image captcha mode
    if captcha_mode not in {"nums", "hex", "ascii", "math"}:
        return
    logger.info(
            "[%s] Received captcha reply from %s: %s",
            chat_id, user_name, msg_text)
    # Check if the expected captcha solve number is in the message
    solve_num = Global.new_users[chat_id][user_id]["join_data"]["captcha_num"]
    if is_captcha_num_solve(captcha_mode, msg_text, solve_num):
        logger.info("[%s] Captcha solved by %s", chat_id, user_name)
        # Remove all restrictions on the user
        await tlg_unrestrict_user(bot, chat_id, user_id)
        # Remove join messages
        for msg in Global.new_users[chat_id][user_id]["msg_to_rm"]:
            await tlg_delete_msg(bot, chat_id, msg)
        Global.new_users[chat_id][user_id]["msg_to_rm"].clear()
        Global.new_users[chat_id][user_id]["msg_to_rm_on_kick"].clear()
        del Global.new_users[chat_id][user_id]
        # Remove user captcha numbers message
        await tlg_delete_msg(bot, chat_id, msg_id)
        # Send message solve message
        bot_msg = TEXT[lang]["CAPTCHA_SOLVED"].format(user_name)
        if lang != "EN":
            bilang = get_chat_config(chat_id, "BiLang")
            if bilang:
                en_text = TEXT["EN"]["CAPTCHA_SOLVED"].format(user_name)
                bot_msg = f"{bot_msg}\n\n{en_text}"
        await bot_send_msg(bot, chat_id, bot_msg, rm_result_msg)
        # Check for custom welcome message and send it
        welcome_msg = get_chat_config(chat_id, "Welcome_Msg").format(
                escape_markdown(user_name, 2))
        if welcome_msg != "-":
            # Send the message as Markdown
            rm_welcome_msg = get_chat_config(chat_id, "Rm_Welcome_Msg")
            if rm_welcome_msg:
                welcome_msg_time = get_chat_config(chat_id, "Welcome_Time")
                sent_result = await tlg_send_autodelete_msg(
                        bot, chat_id, welcome_msg, welcome_msg_time,
                        parse_mode="MARKDOWN")
            else:
                sent_result = await tlg_send_msg(
                        bot, chat_id, welcome_msg, "MARKDOWN")
            if sent_result is None:
                logger.info(
                        "[%s] Error: Can't send the welcome message.",
                        chat_id)
        # Check for send just text message option and apply user
        # restrictions
        restrict_non_text_msgs = get_chat_config(chat_id, "Restrict_Non_Text")
        # Restrict for 1 day
        if restrict_non_text_msgs == 1:
            tomorrow_epoch = get_unix_epoch() + CONST["T_RESTRICT_NO_TEXT_MSG"]
            await restrict_user_media(bot, chat_id, user_id, tomorrow_epoch)
        # Restrict forever
        elif restrict_non_text_msgs == 2:
            await restrict_user_media(bot, chat_id, user_id)
    # The provided message doesn't has the valid captcha number
    else:
        # Check if the message is for a math equation captcha
        if captcha_mode == "math":
            clueless_user = False
            # Check if message is just 4 numbers
            if is_int(msg_text) and (len(msg_text) == 4):
                clueless_user = True
            # Check if message is "NN+NN" or "NN-NN"
            elif ((len(msg_text) == 5) and (is_int(msg_text[:2])) and
                    (is_int(msg_text[3:])) and (msg_text[2] in ["+", "-"])):
                clueless_user = True
            # Tell the user that is wrong
            if clueless_user:
                tlg_autodelete_msg(update_msg)
                sent_msg_id = await tlg_send_autodelete_msg(
                        bot, chat_id, TEXT[lang]["CAPTCHA_INCORRECT_MATH"],
                        CONST["T_FAST_DEL_MSG"], topic_id=topic_id)
                Global.new_users[chat_id][user_id]["msg_to_rm"].append(
                        sent_msg_id)
                Global.new_users[chat_id][user_id]["msg_to_rm"].append(msg_id)
        # If "nums", "hex" or "ascii" captcha
        else:
            # Check if the message has 4 chars
            if len(msg_text) == 4:
                tlg_autodelete_msg(update_msg)
                sent_msg_id = await tlg_send_autodelete_msg(
                        bot, chat_id, TEXT[lang]["CAPTCHA_INCORRECT_0"],
                        CONST["T_FAST_DEL_MSG"], topic_id=topic_id)
                Global.new_users[chat_id][user_id]["msg_to_rm"].append(
                        sent_msg_id)
                Global.new_users[chat_id][user_id]["msg_to_rm"].append(msg_id)
            # Check if the message was just a 4 numbers msg
            elif is_int(msg_text):
                tlg_autodelete_msg(update_msg)
                sent_msg_id = await tlg_send_autodelete_msg(
                        bot, chat_id, TEXT[lang]["CAPTCHA_INCORRECT_1"],
                        CONST["T_FAST_DEL_MSG"], topic_id=topic_id)
                Global.new_users[chat_id][user_id]["msg_to_rm"].append(
                        sent_msg_id)
                Global.new_users[chat_id][user_id]["msg_to_rm"].append(msg_id)
    logger.info("[%s] Captcha reply process completed.", chat_id)


async def poll_answer_rx(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    User poll vote received.
    '''
    bot = context.bot
    active_polls = context.bot_data
    poll_id = update.poll_answer.poll_id
    from_user = update.poll_answer.user
    option_answer = update.poll_answer.option_ids[0] + 1
    # Ignore any Poll vote that comes from unexpected poll
    if poll_id not in active_polls:
        return
    poll_data = active_polls[poll_id]
    # Ignore Poll votes that doesn't come from expected user in captcha
    # process
    if from_user.id != poll_data["user_id"]:
        return
    # Handle poll vote
    chat_id = poll_data["chat_id"]
    user_id = poll_data["user_id"]
    poll_msg_id = poll_data["poll_msg_id"]
    poll_correct_option = poll_data["correct_option"]
    # The vote come from expected user, let's stop the Poll
    logger.info(
            "[%s] User %s select poll option %d",
            chat_id, from_user.username, option_answer)
    await tlg_stop_poll(bot, chat_id, poll_msg_id)
    # Get user name (if has an alias, just use the alias)
    user_name = from_user.full_name
    if from_user.username is not None:
        user_name = f"@{from_user.username}"
    # Get chat settings
    lang = get_chat_config(chat_id, "Language")
    rm_result_msg = get_chat_config(chat_id, "Rm_Result_Msg")
    rm_welcome_msg = get_chat_config(chat_id, "Rm_Welcome_Msg")
    welcome_msg = get_chat_config(chat_id, "Welcome_Msg").format(
            escape_markdown(user_name, 2))
    restrict_non_text_msgs = get_chat_config(chat_id, "Restrict_Non_Text")
    # Wait 3s to let poll animation be shown
    await asyncio_sleep(3)
    # Remove previous join messages
    for msg in Global.new_users[chat_id][user_id]["msg_to_rm"]:
        await tlg_delete_msg(bot, chat_id, msg)
    Global.new_users[chat_id][user_id]["msg_to_rm"].clear()
    # Check if user vote the correct option
    if option_answer == poll_correct_option:
        logger.info("[%s] User %s solve a poll challenge.", chat_id, user_name)
        # Remove all restrictions on the user
        await tlg_unrestrict_user(bot, chat_id, user_id)
        # Send captcha solved message
        bot_msg = TEXT[lang]["CAPTCHA_SOLVED"].format(user_name)
        if lang != "EN":
            bilang = get_chat_config(chat_id, "BiLang")
            if bilang:
                en_text = TEXT["EN"]["CAPTCHA_SOLVED"].format(user_name)
                bot_msg = f"{bot_msg}\n\n{en_text}"
        await bot_send_msg(bot, chat_id, bot_msg, rm_result_msg)
        del Global.new_users[chat_id][user_id]
        # Check for custom welcome message and send it
        if welcome_msg != "-":
            if rm_welcome_msg:
                welcome_msg_time = get_chat_config(chat_id, "Welcome_Time")
                sent_result = await tlg_send_autodelete_msg(
                        bot, chat_id, welcome_msg, welcome_msg_time,
                        parse_mode="MARKDOWN")
            else:
                sent_result = await tlg_send_msg(
                        bot, chat_id, welcome_msg, "MARKDOWN")
            if sent_result is None:
                logger.info(
                        "[%s] Error: Can't send the welcome message.",
                        chat_id)
        # Check for send just text message option and apply user
        # restrictions
        if restrict_non_text_msgs == 1:  # Restrict for 1 day
            tomorrow_epoch = get_unix_epoch() + CONST["T_RESTRICT_NO_TEXT_MSG"]
            await restrict_user_media(bot, chat_id, user_id, tomorrow_epoch)
        elif restrict_non_text_msgs == 2:  # Restrict forever
            await restrict_user_media(bot, chat_id, user_id)
    else:
        # Notify captcha fail
        logger.info("[%s] User %s fail poll.", chat_id, user_name)
        restriction = get_chat_config(chat_id, "Fail_Restriction")
        if restriction == CMD["RESTRICTION"]["KICK"]:
            bot_msg = TEXT[lang]["CAPTCHA_POLL_FAIL"].format(user_name)
            if lang != "EN":
                bilang = get_chat_config(chat_id, "BiLang")
                if bilang:
                    en_text = TEXT["EN"]["CAPTCHA_POLL_FAIL"].format(user_name)
                    bot_msg = f"{bot_msg}\n\n{en_text}"
            await bot_send_msg(bot, chat_id, bot_msg, rm_result_msg)
            await asyncio_sleep(10)
        # Try to punish the user
        await captcha_fail_member(bot, chat_id, user_id)
    logger.info("[%s] Poll captcha process completed.", chat_id)


async def button_press_rx(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Any Telegram Inline Keyboard Button pressed handler.
    '''
    bot = context.bot
    query = update.callback_query
    # Confirm query received
    query_ans_result = await tlg_answer_callback_query(bot, query)
    if query_ans_result["error"] != "":
        return
    # Convert query provided data into list
    button_data = query.data.split(" ")
    # Ignore if the query data is unexpected or it comes from an
    # unexpected user
    if ((len(button_data) < 2) or
            (button_data[1] != str(query.from_user.id))):
        return
    # Get type of inline keyboard button pressed and user ID associated
    # to that button
    key_pressed = button_data[0]
    # Check and handle "request new img captcha" or
    # "button captcha challenge" buttons
    if "image_captcha" in key_pressed:
        await button_request_another_captcha_press(bot, query)
    elif "button_captcha" in key_pressed:
        await button_im_not_a_bot_press(bot, query)


async def button_request_another_captcha_press(bot, query):
    '''
    Button "Another captcha" pressed handler.
    '''
    # Get query data
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    msg_id = query.message.message_id
    user_name = query.from_user.full_name
    # If has an alias, just use the alias
    if query.from_user.username is not None:
        user_name = f"@{query.from_user.username}"
    chat_title = query.message.chat.title
    # Add an unicode Left to Right Mark (LRM) to chat title
    # (fix for arabic, hebrew, etc.)
    chat_title = add_lrm(chat_title)
    # Ignore if message is not from a new user that has not
    # completed the captcha yet
    if chat_id not in Global.new_users:
        return
    if user_id not in Global.new_users[chat_id]:
        return
    # Get chat language
    lang = get_chat_config(chat_id, "Language")
    logger.info("[%s] User %s requested a new captcha.", chat_id, user_name)
    # Prepare inline keyboard button to let user request another captcha
    keyboard = [[
            InlineKeyboardButton(
                    TEXT[lang]["OTHER_CAPTCHA_BTN_TEXT"],
                    callback_data=f"image_captcha {str(query.from_user.id)}")
            ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Get captcha timeout
    captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
    if captcha_timeout < CONST["T_SECONDS_IN_MIN"]:
        timeout_str = f"{captcha_timeout} sec"
    else:
        timeout_min = int(captcha_timeout / CONST["T_SECONDS_IN_MIN"])
        timeout_str = f"{timeout_min} min"
    # Get current chat configurations
    captcha_level = get_chat_config(chat_id, "Captcha_Difficulty_Level")
    captcha_mode = \
        Global.new_users[chat_id][user_id]["join_data"]["captcha_mode"]
    # Use nums mode if captcha_mode was changed while captcha was
    # in progress
    if captcha_mode not in {"nums", "hex", "ascii", "math"}:
        captcha_mode = "nums"
    # Generate a new captcha and edit previous captcha image message
    captcha = create_image_captcha(
                chat_id, user_id, captcha_level, captcha_mode)
    if captcha_mode == "math":
        captcha_num = captcha["equation_result"]
        logger.info(
                "[%s] Sending new captcha msg: %s = %s...",
                chat_id, captcha["equation_str"], captcha_num)
        img_caption = TEXT[lang]["NEW_USER_MATH_CAPTION"].format(
                user_name, chat_title, timeout_str)
        if lang != "EN":
            bilang = get_chat_config(chat_id, "BiLang")
            if bilang:
                en_text = TEXT["EN"]["NEW_USER_MATH_CAPTION"].format(
                    user_name, chat_title, timeout_str)
                img_caption = f"{img_caption}\n\n{en_text}"
    else:
        captcha_num = captcha["characters"]
        logger.info(
                "[%s] Sending new captcha msg: %s...",
                chat_id, captcha_num)
        img_caption = TEXT[lang]["NEW_USER_IMG_CAPTION"].format(
                user_name, chat_title, timeout_str)
        if lang != "EN":
            bilang = get_chat_config(chat_id, "BiLang")
            if bilang:
                en_text = TEXT["EN"]["NEW_USER_IMG_CAPTION"].format(
                    user_name, chat_title, timeout_str)
                img_caption = f"{img_caption}\n\n{en_text}"
    # Read and send image
    edit_result = {}
    try:
        with open(captcha["image"], "rb") as file_img:
            input_media = InputMediaPhoto(media=file_img, caption=img_caption)
            edit_result = await tlg_edit_msg_media(
                    bot, chat_id, msg_id, media=input_media,
                    reply_markup=reply_markup)
        if edit_result["error"] == "":
            # Set and modified to new expected captcha number
            Global.new_users[chat_id][user_id]["join_data"]["captcha_num"] = \
                    captcha_num
            # Remove sent captcha image file from file system
            if path.exists(captcha["image"]):
                remove(captcha["image"])
    except Exception:
        logger.error(format_exc())
        logger.error("Fail to update image for Telegram")
    logger.info("[%s] New captcha request process completed.", chat_id)


async def button_im_not_a_bot_press(bot, query):
    '''
    Button "I'm not a bot" pressed handler.
    '''
    # Get query data
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    user_name = query.from_user.full_name
    # If has an alias, just use the alias
    if query.from_user.username is not None:
        user_name = f"@{query.from_user.username}"
    chat_title = query.message.chat.title
    # Add an unicode Left to Right Mark (LRM) to chat title (fix for
    # arabic, hebrew, etc.)
    chat_title = add_lrm(chat_title)
    # Ignore if request doesn't come from a new user in captcha process
    if chat_id not in Global.new_users:
        return
    if user_id not in Global.new_users[chat_id]:
        return
    # Get chat settings
    lang = get_chat_config(chat_id, "Language")
    rm_result_msg = get_chat_config(chat_id, "Rm_Result_Msg")
    # Remove previous join messages
    for msg in Global.new_users[chat_id][user_id]["msg_to_rm"]:
        await tlg_delete_msg(bot, chat_id, msg)
    # Remove user from captcha process
    del Global.new_users[chat_id][user_id]
    # Send message solve message
    logger.info(
            "[%s] User %s solved a button-only challenge.",
            chat_id, user_name)
    # Remove all restrictions on the user
    await tlg_unrestrict_user(bot, chat_id, user_id)
    # Send captcha solved message
    bot_msg = TEXT[lang]["CAPTCHA_SOLVED"].format(user_name)
    if lang != "EN":
        bilang = get_chat_config(chat_id, "BiLang")
        if bilang:
            en_text = TEXT["EN"]["CAPTCHA_SOLVED"].format(user_name)
            bot_msg = f"{bot_msg}\n\n{en_text}"
    await bot_send_msg(bot, chat_id, bot_msg, rm_result_msg)
    # Check for custom welcome message and send it
    welcome_msg = ""
    welcome_msg = get_chat_config(chat_id, "Welcome_Msg").format(
            escape_markdown(user_name, 2))
    if welcome_msg != "-":
        # Send the message as Markdown
        rm_welcome_msg = get_chat_config(chat_id, "Rm_Welcome_Msg")
        if rm_welcome_msg:
            welcome_msg_time = get_chat_config(chat_id, "Welcome_Time")
            sent_result = await tlg_send_autodelete_msg(
                    bot, chat_id, welcome_msg, welcome_msg_time,
                    parse_mode="MARKDOWN")
        else:
            sent_result = await tlg_send_msg(
                    bot, chat_id, welcome_msg, "MARKDOWN")
        if sent_result is None:
            logger.info(
                    "[%s] Error: Can't send the welcome message.",
                    chat_id)
    # Check to send just text message option and apply user restrictions
    restrict_non_text_msgs = get_chat_config(chat_id, "Restrict_Non_Text")
    # Restrict for 1 day
    if restrict_non_text_msgs == 1:
        tomorrow_epoch = get_unix_epoch() + CONST["T_RESTRICT_NO_TEXT_MSG"]
        await restrict_user_media(bot, chat_id, user_id, tomorrow_epoch)
    # Restrict forever
    elif restrict_non_text_msgs == 2:
        await restrict_user_media(bot, chat_id, user_id)
    logger.info("[%s] Button-only challenge process completed.", chat_id)


###############################################################################
# Received Telegram command messages handlers
###############################################################################

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /start message handler.
    '''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    if chat_type == "private":
        await tlg_send_msg(bot, chat_id, TEXT[lang]["START"])
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        user_id = update_msg.from_user.id
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if not is_admin:
            return
        # Send the response message
        lang = get_chat_config(chat_id, "Language")
        await tlg_send_autodelete_msg(
                bot, chat_id, TEXT[lang]["START"],
                topic_id=tlg_get_msg_topic(update_msg))


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /help message handler.
    '''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    if chat_type == "private":
        await tlg_send_msg(bot, chat_id, TEXT[lang]["HELP"])
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        user_id = update_msg.from_user.id
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Send the response message
        lang = get_chat_config(chat_id, "Language")
        await tlg_send_autodelete_msg(
                bot, chat_id, TEXT[lang]["HELP"],
                topic_id=tlg_get_msg_topic(update_msg))


async def cmd_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /commands message handler.
    '''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    lang = get_update_user_lang(update_msg.from_user)
    if chat_type == "private":
        await tlg_send_msg(bot, chat_id, TEXT[lang]["COMMANDS"])
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        user_id = update_msg.from_user.id
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Send the response message
        lang = get_chat_config(chat_id, "Language")
        await tlg_send_autodelete_msg(
                bot, chat_id, TEXT[lang]["COMMANDS"],
                topic_id=tlg_get_msg_topic(update_msg))


async def cmd_connect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /connect message handler.
    '''
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
        user_alias = f"@{user_alias}"
    lang = get_update_user_lang(update_msg.from_user)
    # Ignore if command is not in private chat
    if chat_type != "private":
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Send just allowed in private chat message
        lang = get_chat_config(chat_id, "Language")
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["CMD_JUST_IN_PRIVATE"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Check for group chat ID
    if (args is None) or (len(args) == 0):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["CONNECT_USAGE"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    group_id = args[0]
    # Add "-" if not present
    if group_id[0] != "-":
        group_id = f"-{group_id}"
    if not tlg_is_valid_group(group_id):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["INVALID_GROUP_ID"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Check if requested by the Bot owner or an Admin of the group
    if ((str(user_id) != CONST["BOT_OWNER"]) and
            (user_alias != CONST["BOT_OWNER"])):
        is_admin = await tlg_user_is_admin(bot, group_id, user_id)
        if (is_admin is None) or (is_admin is False):
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id, TEXT[lang]["CONNECT_JUST_ADMIN"],
                    topic_id=tlg_get_msg_topic(update_msg))
            return
    # Connection
    group_lang = get_chat_config(group_id, "Language")
    Global.connections[user_id] = {"group_id": group_id, "lang": group_lang}
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, TEXT[lang]["CONNECT_OK"].format(group_id),
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_disconnect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /disconnect message handler.
    '''
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
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Send just allowed in private chat message
        lang = get_chat_config(chat_id, "Language")
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["CMD_JUST_IN_PRIVATE"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Check if User is connected to some group
    if user_id not in Global.connections:
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id,
                TEXT[lang]["DISCONNECT_NOT_CONNECTED"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Disconnection
    lang = Global.connections[user_id]["lang"]
    group_id = Global.connections[user_id]["group_id"]
    del Global.connections[user_id]
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id,
            TEXT[lang]["DISCONNECT_OK"].format(group_id),
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_checkcfg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /checkcfg message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Get all group configs
    group_cfg = get_all_chat_config(group_id)
    group_cfg = json_dumps(group_cfg, indent=4, sort_keys=True)
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id,
            TEXT[lang]["CHECK_CFG"].format(escape_markdown(group_cfg, 2)),
            parse_mode="MARKDOWN", topic_id=tlg_get_msg_topic(update_msg))


async def cmd_bilanguage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /bilanguage message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["BILANG_MSG"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Get remove welcome messages config to set
    yes_or_no = args[0].lower()
    if yes_or_no == "yes":
        save_config_property(group_id, "BiLang", True)
        bot_msg = TEXT[lang]["BILANG_MSG_YES"]
    elif yes_or_no == "no":
        save_config_property(group_id, "BiLang", False)
        bot_msg = TEXT[lang]["BILANG_MSG_NO"]
    else:
        bot_msg = TEXT[lang]["BILANG_MSG"]
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /language message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        msg_text = TEXT[lang]["LANG_NOT_ARG"].format(
                CONST["SUPPORTED_LANGS_CMDS"])
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, msg_text,
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Get and configure chat to provided language
    lang_provided = args[0].upper()
    if lang_provided in TEXT:
        if (chat_type != "private") and (lang_provided == lang):
            msg_text = TEXT[lang]["LANG_SAME"].format(
                    CONST["SUPPORTED_LANGS_CMDS"])
        else:
            lang = lang_provided
            save_config_property(group_id, "Language", lang)
            if (chat_type == "private") and (user_id in Global.connections):
                Global.connections[user_id]["lang"] = lang
            msg_text = TEXT[lang]["LANG_CHANGE"]
    else:
        msg_text = TEXT[lang]["LANG_BAD_LANG"].format(
                CONST["SUPPORTED_LANGS_CMDS"])
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, msg_text,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /time message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["TIME_NOT_ARG"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Check if provided time argument is not a number
    if not is_int(args[0]):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["TIME_NOT_NUM"],
                topic_id=tlg_get_msg_topic(update_msg))
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
        new_time_str = f"{new_time} min"
        new_time = new_time * CONST["T_SECONDS_IN_MIN"]
    elif min_sec in ["s", "sec", "secs", "seconds"]:
        min_sec = "sec"
        new_time_str = f"{new_time} sec"
    else:
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["TIME_NOT_ARG"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Check if time value is out of limits (less than 10s)
    if new_time < 10:
        msg_text = TEXT[lang]["TIME_OUT_RANGE"].format(
                CONST["MAX_CONFIG_CAPTCHA_TIME"])
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, msg_text,
                topic_id=tlg_get_msg_topic(update_msg))
        return
    if new_time > CONST["MAX_CONFIG_CAPTCHA_TIME"] * CONST["T_SECONDS_IN_MIN"]:
        msg_text = TEXT[lang]["TIME_OUT_RANGE"].format(
                CONST["MAX_CONFIG_CAPTCHA_TIME"])
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, msg_text,
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Set the new captcha time
    save_config_property(group_id, "Captcha_Time", new_time)
    msg_text = TEXT[lang]["TIME_CHANGE"].format(new_time_str)
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, msg_text,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_difficulty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /difficulty message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["DIFFICULTY_NOT_ARG"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Get and configure chat to provided captcha difficulty
    if is_int(args[0]):
        new_difficulty = int(args[0])
        new_difficulty = max(new_difficulty, 1)
        new_difficulty = min(new_difficulty, 5)
        save_config_property(
                group_id, "Captcha_Difficulty_Level", new_difficulty)
        bot_msg = TEXT[lang]["DIFFICULTY_CHANGE"].format(new_difficulty)
    else:
        bot_msg = TEXT[lang]["DIFFICULTY_NOT_NUM"]
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_captcha_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /captcha_mode message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["CAPTCHA_MODE_NOT_ARG"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Get and configure chat to provided captcha mode
    new_captcha_mode = args[0].lower()
    if (new_captcha_mode in
            {"poll", "button", "nums", "hex", "ascii", "math", "random"}):
        save_config_property(group_id, "Captcha_Chars_Mode", new_captcha_mode)
        bot_msg = TEXT[lang]["CAPTCHA_MODE_CHANGE"].format(new_captcha_mode)
    else:
        bot_msg = TEXT[lang]["CAPTCHA_MODE_INVALID"]
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_restriction(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Command /restriction message handler.
    To configure type of restriction to apply on users that fails the
    captcha in a group.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        msg_text = "{}\n\n{}".format(
            TEXT[lang]["CMD_RESTRICTION_NOT_ARG"],
            TEXT[lang]["CMD_RESTRICTION_AVAILABLE_ARGS"])
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, msg_text,
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Get and configure chat to provided restriction
    restriction_type = args[0].lower()
    if (restriction_type in CMD["RESTRICTION"]["ARGV"]):
        save_config_property(group_id, "Fail_Restriction", restriction_type)
        bot_msg = TEXT[lang]["CMD_RESTRICTION_CHANGE"].format(restriction_type)
    else:
        bot_msg = "{}\n\n{}".format(
            TEXT[lang]["CMD_INVALID_PARAMETER"],
            TEXT[lang]["CMD_RESTRICTION_AVAILABLE_ARGS"])
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_welcome_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /welcome_msg message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["WELCOME_MSG_SET_NOT_ARG"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Get welcome message in markdown and remove "/Welcome_msg "
    # text from it
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
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_welcome_msg_time(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Command /welcome_msg_time message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"],
                    topic_id=tlg_get_msg_topic(update_msg))
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["WELCOME_TIME_NOT_ARG"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Check if provided time argument is not a number
    if not is_int(args[0]):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["TIME_NOT_NUM"],
                topic_id=tlg_get_msg_topic(update_msg))
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
        new_time_str = f"{new_time} min"
        new_time = new_time * CONST["T_SECONDS_IN_MIN"]
    elif min_sec in ["s", "sec", "secs", "seconds"]:
        min_sec = "sec"
        new_time_str = f"{new_time} sec"
    else:
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["WELCOME_TIME_NOT_ARG"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Check if time value is out of limits (less than 10s)
    if new_time < 10:
        msg_text = TEXT[lang]["TIME_OUT_RANGE"].format(
                CONST["MAX_CONFIG_CAPTCHA_TIME"])
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, msg_text,
                topic_id=tlg_get_msg_topic(update_msg))
        return
    if new_time > CONST["MAX_CONFIG_CAPTCHA_TIME"] * CONST["T_SECONDS_IN_MIN"]:
        msg_text = TEXT[lang]["TIME_OUT_RANGE"].format(
                CONST["MAX_CONFIG_CAPTCHA_TIME"])
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, msg_text,
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Set the new captcha time
    save_config_property(group_id, "Welcome_Time", new_time)
    msg_text = TEXT[lang]["WELCOME_TIME_CHANGE"].format(new_time_str)
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, msg_text,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_captcha_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /captcha_poll message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
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
    if (args is None) or (len(args) < 2):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, text_cmd_usage,
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Get poll message command
    poll_cmd = args[0]
    logger.info("poll_cmd: %s", poll_cmd)
    if poll_cmd not in ["question", "option", "correct_option"]:
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, text_cmd_usage,
                topic_id=tlg_get_msg_topic(update_msg))
        return
    if poll_cmd == "question":
        # get Poll Question
        poll_question = " ".join(args[1:])
        logger.info("poll_question: %s", poll_question)
        if len(poll_question) > CONST["MAX_POLL_QUESTION_LENGTH"]:
            poll_question = poll_question[:CONST["MAX_POLL_QUESTION_LENGTH"]]
        # Save Poll Question
        save_config_property(group_id, "Poll_Q", poll_question)
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id,
                TEXT[lang]["POLL_QUESTION_CONFIGURED"],
                topic_id=tlg_get_msg_topic(update_msg))
    elif poll_cmd == "correct_option":
        # get Poll correct option and check if is a number
        option_num = args[1]
        if not is_int(option_num):
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id, text_cmd_usage)
            return
        option_num = int(option_num)
        # Check if correct option number is configured
        if (option_num < 1) or (option_num > CONST["MAX_POLL_OPTIONS"]):
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id, text_cmd_usage,
                    topic_id=tlg_get_msg_topic(update_msg))
            return
        poll_options = get_chat_config(group_id, "Poll_A")
        if option_num > num_config_poll_options(poll_options):
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["POLL_CORRECT_OPTION_NOT_CONFIGURED"].format(
                            option_num),
                    topic_id=tlg_get_msg_topic(update_msg))
            return
        # Save Poll correct option number
        save_config_property(group_id, "Poll_C_A", option_num)
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id,
                TEXT[lang]["POLL_CORRECT_OPTION_CONFIGURED"].format(
                    option_num),
                topic_id=tlg_get_msg_topic(update_msg))
    elif poll_cmd == "option":
        # Check if option argument is valid
        if len(args) < 3:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id, text_cmd_usage,
                    topic_id=tlg_get_msg_topic(update_msg))
            return
        option_num = args[1]
        logger.info("option_num: %s", option_num)
        if not is_int(option_num):
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id, text_cmd_usage,
                    topic_id=tlg_get_msg_topic(update_msg))
            return
        option_num = int(option_num)
        if (option_num < 1) or (option_num > CONST["MAX_POLL_OPTIONS"]):
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id, text_cmd_usage,
                    topic_id=tlg_get_msg_topic(update_msg))
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
        logger.info("poll_option: %s", poll_option)
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
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id,
                TEXT[lang]["POLL_OPTION_CONFIGURED"].format(option_num+1),
                topic_id=tlg_get_msg_topic(update_msg))


async def cmd_restrict_non_text(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Command /restrict_non_text message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id,
                TEXT[lang]["RESTRICT_NON_TEXT_MSG_NOT_ARG"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Check for valid expected argument values
    restrict_non_text_msgs = args[0]
    if restrict_non_text_msgs not in ["enable", "disable"]:
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id,
                TEXT[lang]["RESTRICT_NON_TEXT_MSG_NOT_ARG"],
                topic_id=tlg_get_msg_topic(update_msg))
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
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_add_ignore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /add_ignore message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["IGNORE_LIST_ADD_NOT_ARG"],
                topic_id=tlg_get_msg_topic(update_msg))
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
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_remove_ignore(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Command /remove_ignore message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id,
                TEXT[lang]["IGNORE_LIST_REMOVE_NOT_ARG"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Check and remove user ID/alias form ignore list
    ignore_list = get_chat_config(group_id, "Ignore_List")
    user_id_alias = args[0]
    if list_remove_element(ignore_list, user_id_alias):
        save_config_property(group_id, "Ignore_List", ignore_list)
        bot_msg = TEXT[lang]["IGNORE_LIST_REMOVE_SUCCESS"]
    else:
        bot_msg = TEXT[lang]["IGNORE_LIST_REMOVE_NOT_IN_LIST"]
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_ignore_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /ignore_list message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
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
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_remove_solve_kick_msg(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Command /remove_solve_kick_msg message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"],
                    topic_id=tlg_get_msg_topic(update_msg))
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["RM_SOLVE_KICK_MSG"],
                topic_id=tlg_get_msg_topic(update_msg))
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
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_remove_welcome_msg(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Command /remove_welcome_msg message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Get Group Chat ID and configured language
        group_id = chat_id
        lang = get_chat_config(group_id, "Language")
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        await tlg_send_msg_type_chat(
                bot, chat_type, chat_id, TEXT[lang]["RM_WELCOME_MSG"],
                topic_id=tlg_get_msg_topic(update_msg))
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
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_remove_all_msg_kick_on(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Command /remove_all_msg_kick_on message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
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
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_remove_all_msg_kick_off(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Command /remove_all_msg_kick_off message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
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
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_url_enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /url_enable message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
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
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_url_disable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /url_disable message handler.
    '''
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
        if user_id not in Global.connections:
            await tlg_send_msg_type_chat(
                    bot, chat_type, chat_id,
                    TEXT[lang]["CMD_NEEDS_CONNECTION"])
            return
        group_id = Global.connections[user_id]["group_id"]
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
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
    await tlg_send_msg_type_chat(
            bot, chat_type, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /enable message handler.
    '''
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
        await tlg_send_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Remove command message automatically after a while
    tlg_autodelete_msg(update_msg)
    # Ignore if not requested by a group Admin
    is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
    if (is_admin is None) or (is_admin is False):
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
    await tlg_send_autodelete_msg(
            bot, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_disable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /disable message handler.
    '''
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
        await tlg_send_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Remove command message automatically after a while
    tlg_autodelete_msg(update_msg)
    # Ignore if not requested by a group Admin
    is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
    if (is_admin is None) or (is_admin is False):
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
    await tlg_send_autodelete_msg(
            bot, chat_id, bot_msg,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /chatid message handler.
    '''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    if chat_type == "private":
        msg_text = f"Your Chat ID:\n—————————\n{chat_id}"
        await tlg_send_msg(bot, chat_id, msg_text)
    else:
        msg_text = f"Group Chat ID:\n—————————\n{chat_id}"
        tlg_autodelete_msg(update_msg)
        await tlg_send_autodelete_msg(
                bot, chat_id, msg_text,
                topic_id=tlg_get_msg_topic(update_msg))


async def cmd_version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /version message handler.
    '''
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
        await tlg_send_msg(bot, chat_id, msg_text)
    else:
        # Remove command message automatically after a while
        tlg_autodelete_msg(update_msg)
        # Ignore if not requested by a group Admin
        is_admin = await tlg_user_is_admin(bot, chat_id, user_id)
        if (is_admin is None) or (is_admin is False):
            return
        # Send the message
        lang = get_chat_config(chat_id, "Language")
        msg_text = TEXT[lang]["VERSION"].format(CONST["VERSION"])
        await tlg_send_autodelete_msg(
                bot, chat_id, msg_text,
                topic_id=tlg_get_msg_topic(update_msg))


async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /about handler.
    '''
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
    msg_text = TEXT[lang]["ABOUT_MSG"].format(
            CONST["DEVELOPER"], CONST["REPOSITORY"],
            CONST["DEV_DONATION_ADDR"])
    await tlg_send_msg(
            bot, chat_id, msg_text,
            topic_id=tlg_get_msg_topic(update_msg))


async def cmd_privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /privacy handler.
    '''
    msg = getattr(update, "message", None)
    if msg is None:
        return
    await tlg_send_msg(context.bot, msg.chat_id, CONST["PRIVACY"],
                       topic_id=tlg_get_msg_topic(msg))


async def cmd_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /captcha message handler. Useful to test.
    Just Bot Owner can use it.
    '''
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
        user_alias = f"@{user.username}"
    # Remove command message automatically after a while
    tlg_autodelete_msg(update_msg)
    # Check if command was execute by Bot owner
    if ((str(user_id) != CONST["BOT_OWNER"]) and
            (user_alias != CONST["BOT_OWNER"])):
        await tlg_send_autodelete_msg(
                bot, chat_id, CONST["CMD_JUST_ALLOW_OWNER"],
                topic_id=tlg_get_msg_topic(update_msg))
        return
    # Generate a random difficulty captcha
    difficulty = randint(1, 5)
    captcha_mode = choice(["nums", "hex", "ascii", "math"])
    captcha = create_image_captcha(chat_id, user_id, difficulty, captcha_mode)
    if captcha_mode == "math":
        captcha_code = \
                f'{captcha["equation_str"]} = {captcha["equation_result"]}'
    else:
        captcha_code = captcha["characters"]
    logger.info("[%s] Sending captcha msg: %s", chat_id, captcha_code)
    # Note: Img caption must be <= 1024 chars
    img_caption = (f"Captcha Level: {difficulty}\n"
                   f"Captcha Mode: {captcha_mode}\n"
                   f"Captcha Code: {captcha_code}")
    # Send the image
    sent_result: dict = {}
    sent_result["msg"] = None
    try:
        with open(captcha["image"], "rb") as file_image:
            await tlg_send_image(
                bot, chat_id, file_image, img_caption,
                topic_id=tlg_get_msg_topic(update_msg), read_timeout=20)
    except Exception:
        logger.error(format_exc())
        logger.error("Fail to send image to Telegram")
    # Remove sent captcha image file from file system
    if path.exists(captcha["image"]):
        remove(captcha["image"])


async def cmd_allowuserlist(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
    '''
    Command /allowuserlist message handler.
    To Global allowed list blind users.
    Just Bot Owner can use it.
    '''
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
        user_alias = f"@{user.username}"
    topic_id = tlg_get_msg_topic(update_msg)
    # Check if command was execute by Bot owner
    if ((str(user_id) != CONST["BOT_OWNER"]) and
            (user_alias != CONST["BOT_OWNER"])):
        await tlg_send_autodelete_msg(
                bot, chat_id, CONST["CMD_JUST_ALLOW_OWNER"], topic_id=topic_id)
        return
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        # Show Actual Global allowed list Users
        l_white_users = file_read(CONST["F_ALLOWED_USERS"])
        bot_msg = "\n".join([str(user) for user in l_white_users])
        bot_msg = f"Global Allowed Users List:\n------------------\n{bot_msg}"
        await tlg_send_msg(
                bot, chat_id, bot_msg, topic_id=topic_id)
        await tlg_send_msg(
                bot, chat_id, CONST["ALLOWUSERLIST_USAGE"], topic_id=topic_id)
        return
    # Just one argument provided
    if len(args) == 1:
        await tlg_send_msg(
                bot, chat_id, CONST["ALLOWUSERLIST_USAGE"],
                topic_id=topic_id)
        return
    # Invalid argument provided
    if args[0] not in ["add", "rm"]:
        await tlg_send_msg(
                bot, chat_id, CONST["ALLOWUSERLIST_USAGE"],
                topic_id=topic_id)
        return
    # Expected argument provided
    add_rm = args[0]
    user = args[1]
    l_white_users = file_read(CONST["F_ALLOWED_USERS"])
    if add_rm == "add":
        if not tlg_is_valid_user_id_or_alias(user):
            await tlg_send_msg(
                    bot, chat_id,
                    "Invalid User ID/Alias.",
                    topic_id=topic_id)
            return
        if user not in l_white_users:
            file_write(CONST["F_ALLOWED_USERS"], f"{user}\n")
            await tlg_send_msg(
                    bot, chat_id,
                    "User added to Global allowed list.",
                    topic_id=topic_id)
        else:
            await tlg_send_msg(
                    bot, chat_id,
                    "The User is already in Global allowed list.",
                    topic_id=topic_id)
        return
    if add_rm == "rm":
        if not tlg_is_valid_user_id_or_alias(user):
            await tlg_send_msg(
                    bot, chat_id, "Invalid User ID/Alias.",
                    topic_id=topic_id)
            return
        if list_remove_element(l_white_users, user):
            file_write(CONST["F_ALLOWED_USERS"], l_white_users, "w")
            await tlg_send_msg(
                    bot, chat_id,
                    "User removed from Global allowed list.",
                    topic_id=topic_id)
        else:
            await tlg_send_msg(
                    bot, chat_id,
                    "The User is not in Global allowed list.",
                    topic_id=topic_id)


async def cmd_allowgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Command /allowgroup message handler. To allow Bot usage in groups
    when Bot is private.
    Just Bot Owner can use it.
    '''
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
        user_alias = f"@{user.username}"
    topic_id = tlg_get_msg_topic(update_msg)
    # Check if command was execute by Bot owner
    if ((str(user_id) != CONST["BOT_OWNER"]) and
            (user_alias != CONST["BOT_OWNER"])):
        await tlg_send_autodelete_msg(
                bot, chat_id, CONST["CMD_JUST_ALLOW_OWNER"], topic_id=topic_id)
        return
    # Check if no argument was provided with the command
    if (args is None) or (len(args) == 0):
        # Show Actual Allowed Groups
        l_allowed_groups = file_read(CONST["F_ALLOWED_GROUPS"])
        bot_msg = "\n".join([str(group) for group in l_allowed_groups])
        bot_msg = f"Allowed Groups:\n--------------------\n{bot_msg}"
        await tlg_send_msg(bot, chat_id, bot_msg, topic_id=topic_id)
        await tlg_send_msg(
                bot, chat_id, CONST["ALLOWGROUP_USAGE"], topic_id=topic_id)
        return
    # Just one arguments provided
    if len(args) == 1:
        await tlg_send_msg(
                bot, chat_id, CONST["ALLOWGROUP_USAGE"], topic_id=topic_id)
        return
    # Invalid argument provided
    if args[0] not in ["add", "rm"]:
        await tlg_send_msg(
                bot, chat_id, CONST["ALLOWGROUP_USAGE"], topic_id=topic_id)
        return
    # Expected argument provided
    add_rm = args[0]
    group = args[1]
    l_allowed_groups = file_read(CONST["F_ALLOWED_GROUPS"])
    if add_rm == "add":
        if not tlg_is_valid_group(group):
            await tlg_send_msg(
                    bot, chat_id, "Invalid Group ID.", topic_id=topic_id)
            return
        if group not in l_allowed_groups:
            file_write(CONST["F_ALLOWED_GROUPS"], f"{group}\n")
            await tlg_send_msg(
                    bot, chat_id, "Group added to allowed list.",
                    topic_id=topic_id)
        else:
            await tlg_send_msg(
                    bot, chat_id,
                    "The group is already in the allowed list.",
                    topic_id=topic_id)
        return
    if add_rm == "rm":
        if not tlg_is_valid_group(group):
            await tlg_send_msg(
                    bot, chat_id, "Invalid Group ID.",
                    topic_id=topic_id)
            return
        if list_remove_element(l_allowed_groups, group):
            file_write(CONST["F_ALLOWED_GROUPS"], l_allowed_groups, "w")
            await tlg_send_msg(
                    bot, chat_id, "Group removed from allowed list.",
                    topic_id=topic_id)
        else:
            await tlg_send_msg(
                    bot, chat_id, "The group is not in allowed list.",
                    topic_id=topic_id)


###############################################################################
# Bot automatic delete sent messages coroutine
###############################################################################

async def auto_delete_messages(bot):
    '''
    Handle remove messages sent by the Bot with the timed auto-delete
    function.
    '''
    while not Global.force_exit:
        # Release CPU sleeping on each iteration
        await asyncio_sleep(0.01)
        # Check each Bot sent message
        i = 0
        while i < len(Global.to_delete_in_time_messages_list):
            # Check for break iterating if script must exit
            if Global.force_exit:
                return
            sent_msg = Global.to_delete_in_time_messages_list[i]
            # Sleep each 100 iterations
            i = i + 1
            if (i > 1) and ((i % 1000) == 0):
                await asyncio_sleep(0.01)
            # Check if delete time has arrive for this message
            if time() - sent_msg["time"] < sent_msg["delete_time"]:
                continue
            # Delete message
            delete_result = await tlg_delete_msg(
                    bot, sent_msg["Chat_id"], sent_msg["Msg_id"])
            # The bot has no privileges to delete messages
            if delete_result["error"] == "Message can't be deleted":
                lang = get_chat_config(sent_msg["Chat_id"], "Language")
                sent_result = await tlg_send_msg(
                        bot, sent_msg["Chat_id"], TEXT[lang]["CANT_DEL_MSG"],
                        reply_to_message_id=sent_msg["Msg_id"])
                if sent_result["msg"] is not None:
                    tlg_autodelete_msg(sent_result["msg"])
            list_remove_element(
                    Global.to_delete_in_time_messages_list, sent_msg)
            await asyncio_sleep(0.01)
    logger.info("Auto-delete messages coroutine finished")


###############################################################################
# Handle captcha process timeout (time to kick/ban users) coroutine
###############################################################################

async def captcha_timeout(bot):
    '''
    Check if the time for ban new users that has not completed the
    captcha has arrived.
    '''
    while not Global.force_exit:
        # Release CPU sleeping on each iteration
        await asyncio_sleep(0.01)
        # Get all id from users in captcha process (list shallow copy)
        users_id = []
        chats_id_list = list(Global.new_users.keys()).copy()
        for chat_id in chats_id_list:
            users_id_list = list(Global.new_users[chat_id].keys()).copy()
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
                    await asyncio_sleep(0.01)
                # Check if script must exit for end coroutine
                if Global.force_exit:
                    return
                # Ignore if user is not in this chat
                if user_id not in Global.new_users[chat_id]:
                    continue
                try:
                    user_join_data = \
                            Global.new_users[chat_id][user_id]["join_data"]
                    user_join_time = user_join_data["join_time"]
                    captcha_timeout = user_join_data["captcha_timeout"]
                    if user_join_data["kicked_ban"]:
                        # Remove from new users list the remaining
                        # kicked users that have not solve the captcha
                        # in 30 mins (user ban just happen if a user try
                        # to join the group and fail to solve the
                        # captcha 5 times in the past 30 mins)
                        if time() - user_join_time < captcha_timeout + 1800:
                            continue
                        logger.info(
                                "Removing kicked user %s after 30 mins",
                                user_id)
                        del Global.new_users[chat_id][user_id]
                    else:
                        # If time for kick/ban has not arrived yet
                        if time() - user_join_time < captcha_timeout:
                            continue
                        user_name = user_join_data["user_name"]
                        logger.info(
                                "[%s] Captcha reply timeout for user %s.",
                                chat_id, user_name)
                        await captcha_fail_member(bot, chat_id, user_id)
                        await asyncio_sleep(0.01)
                except Exception:
                    logger.error(format_exc())
                    logger.error("Fail to kick/ban an user")
    logger.info("Captcha timeout coroutine finished")


###############################################################################
# Telegram Errors Callback
###############################################################################

async def tlg_error_callback(update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Telegram errors handler.
    '''
    # Disable unused arguments
    del update
    # Handle error
    try:
        raise context.error
    except BadRequest:
        logger.error("TLG Error: Bad Request")
    except ChatMigrated:
        logger.error("TLG Error: Chat Migrated")
    except Conflict:
        logger.error("TLG Error: Conflict")
    except Forbidden:
        logger.error("TLG Error: Forbidden/Unauthorized")
    except InvalidToken:
        logger.error("TLG Error: Invalid Token")
    except TimedOut:
        logger.error("TLG Error: Timeout (slow connection issue)")
    except NetworkError:
        logger.error("TLG Error: Network Problem")
    except PassportDecryptionError:
        logger.error("TLG Error: Passport Decryption Error")
    except RetryAfter:
        logger.error("TLG Error: Retry After")
    except TelegramError as error:
        logger.error("TLG Error: %s", str(error))


###############################################################################
# Bot Application Setup Function
###############################################################################

def tlg_app_setup(token: str) -> Application:
    '''
    Setup Bot Application.
    '''
    logger.info("Setting up Bot Application...")
    # Initialize Resources and restore last session
    initialize_resources()
    restore_session()
    # Create the Telegram Bot Application Builder
    # Set Bot Token
    # Set messages to be sent silently by default
    # Set Bot Application callbacks functions for Bot run start and exit
    app_builder = Application.builder()
    app_builder.token(token)
    app_builder.defaults(Defaults(disable_notification=True))
    app_builder.post_init(tlg_app_start)
    app_builder.post_shutdown(tlg_app_exit)
    # Build the Bot Application
    app = app_builder.build()
    # Set Telegram errors handler
    app.add_error_handler(tlg_error_callback)
    # Set all expected commands messages handler
    tlg_add_cmd(app, CMD["START"]["KEY"], cmd_start)
    tlg_add_cmd(app, CMD["HELP"]["KEY"], cmd_help)
    tlg_add_cmd(app, CMD["COMMANDS"]["KEY"], cmd_commands)
    tlg_add_cmd(app, CMD["CHECKCFG"]["KEY"], cmd_checkcfg)
    tlg_add_cmd(app, CMD["CONNECT"]["KEY"], cmd_connect)
    tlg_add_cmd(app, CMD["DISCONNECT"]["KEY"], cmd_disconnect)
    tlg_add_cmd(app, CMD["LANGUAGE"]["KEY"], cmd_language)
    tlg_add_cmd(app, CMD["BILANGUAGE"]["KEY"], cmd_bilanguage)
    tlg_add_cmd(app, CMD["TIME"]["KEY"], cmd_time)
    tlg_add_cmd(app, CMD["DIFFICULTY"]["KEY"], cmd_difficulty)
    tlg_add_cmd(app, CMD["CAPTCHA_MODE"]["KEY"], cmd_captcha_mode)
    tlg_add_cmd(app, CMD["RESTRICTION"]["KEY"], cmd_restriction)
    tlg_add_cmd(app, CMD["WELCOME_MSG"]["KEY"], cmd_welcome_msg)
    tlg_add_cmd(app, CMD["WELCOME_MSG_TIME"]["KEY"], cmd_welcome_msg_time)
    tlg_add_cmd(app, CMD["CAPTCHA_POLL"]["KEY"], cmd_captcha_poll)
    tlg_add_cmd(app, CMD["RESTRICT_NON_TEXT"]["KEY"], cmd_restrict_non_text)
    tlg_add_cmd(app, CMD["ADD_IGNORE"]["KEY"], cmd_add_ignore)
    tlg_add_cmd(app, CMD["REMOVE_IGNORE"]["KEY"], cmd_remove_ignore)
    tlg_add_cmd(app, CMD["IGNORE_LIST"]["KEY"], cmd_ignore_list)
    tlg_add_cmd(app, CMD["REMOVE_WELCOME_MSG"]["KEY"], cmd_remove_welcome_msg)
    tlg_add_cmd(app, CMD["REMOVE_SOLVE_KICK_MSG"]["KEY"],
                cmd_remove_solve_kick_msg)
    tlg_add_cmd(app, CMD["REMOVE_ALL_MSG_KICK_ON"]["KEY"],
                cmd_remove_all_msg_kick_on)
    tlg_add_cmd(app, CMD["REMOVE_ALL_MSG_KICK_OFF"]["KEY"],
                cmd_remove_all_msg_kick_off)
    tlg_add_cmd(app, CMD["URL_ENABLE"]["KEY"], cmd_url_enable)
    tlg_add_cmd(app, CMD["URL_DISABLE"]["KEY"], cmd_url_disable)
    tlg_add_cmd(app, CMD["ENABLE"]["KEY"], cmd_enable)
    tlg_add_cmd(app, CMD["DISABLE"]["KEY"], cmd_disable)
    tlg_add_cmd(app, CMD["CHATID"]["KEY"], cmd_chatid)
    tlg_add_cmd(app, CMD["VERSION"]["KEY"], cmd_version)
    tlg_add_cmd(app, CMD["ABOUT"]["KEY"], cmd_about)
    tlg_add_cmd(app, CMD["PRIVACY"]["KEY"], cmd_privacy)
    if CONST["BOT_OWNER"] != "XXXXXXXXX":
        tlg_add_cmd(app, CMD["CAPTCHA"]["KEY"], cmd_captcha)
        tlg_add_cmd(app, CMD["ALLOWUSERLIST"]["KEY"], cmd_allowuserlist)
    if (CONST["BOT_OWNER"] != "XXXXXXXXX") and CONST["BOT_PRIVATE"]:
        tlg_add_cmd(app, CMD["ALLOWGROUP"]["KEY"], cmd_allowgroup)
    # Set to application handler for reception of text messages
    app.add_handler(MessageHandler(filters.TEXT, text_msg_rx, block=False))
    # Set to application not text messages handler
    # pylint: disable=E1131
    app.add_handler(
            MessageHandler(
                    filters.Document.ALL | filters.PHOTO | filters.VIDEO |
                    filters.AUDIO | filters.VOICE | filters.Sticker.ALL |
                    filters.LOCATION | filters.CONTACT,
                    media_msg_rx
            )
    )
    # Set to application a new member join the group and member left the
    # group events handlers
    app.add_handler(
            ChatMemberHandler(
                    chat_bot_status_change,
                    ChatMemberHandler.MY_CHAT_MEMBER
            )
    )
    app.add_handler(
            ChatMemberHandler(
                    chat_member_status_change,
                    ChatMemberHandler.CHAT_MEMBER
            )
    )
    # Set to application "USER joined the group" messages event handlers
    app.add_handler(
            MessageHandler(
                    filters.StatusUpdate.NEW_CHAT_MEMBERS,
                    user_joined_group_msg_rx
            )
    )
    # Set to application "USER left the group" or "BOT removed USER"
    # messages event handlers
    app.add_handler(
            MessageHandler(
                    filters.StatusUpdate.LEFT_CHAT_MEMBER,
                    user_left_group
            )
    )
    # Set to application inline keyboard callback handler for new captcha
    # request and button captcha challenge
    app.add_handler(CallbackQueryHandler(button_press_rx))
    # Set to application users poll vote handler
    app.add_handler(PollAnswerHandler(poll_answer_rx, block=False))
    logger.info("Bot setup completed.")
    return app


###############################################################################
# Bot Application Setup Function
###############################################################################

def tlg_app_run(app: Application) -> None:
    '''
    Launch the Telegram Bot Application.
    The run_polling() and run_webhook() functions blocks main execution
    until Bot is requested to stop by a system signal. After any of this
    functions are called, the Application will start to be managed in a
    asyncio way through coroutines. The tlg_app_start() function will be
    called at run_polling() or run_webhook() startup, and tlg_app_exit()
    function will be called at the end.
    '''
    logger.info("Bot Application Started")
    if not CONST["USE_WEBHOOK"]:
        logger.info("Setup Bot for Polling.")
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
    else:
        logger.info("Setup Bot for Webhook.")
        app.run_webhook(
            listen=CONST["WEBHOOK_IP"],
            port=CONST["WEBHOOK_PORT"],
            url_path=CONST["WEBHOOK_PATH"],
            webhook_url=CONST["WEBHOOK_URL"],
            cert=CONST["WEBHOOK_CERT"],
            key=CONST["WEBHOOK_CERT_PRIV_KEY"],
            secret_token=CONST["WEBHOOK_SECRET_TOKEN"],
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
    logger.info("Bot Application Finished")


###############################################################################
# Bot Application Run Start Function
###############################################################################

async def tlg_app_start(app: Application) -> None:
    '''
    Telegram Bot Application initialized.
    This function is called at the startup of run_polling() or
    run_webhook() functions.'''
    # Launch delete messages and kick users coroutines
    Global.async_captcha_timeout = \
        asyncio_create_task(captcha_timeout(app.bot))
    Global.async_auto_delete_messages = \
        asyncio_create_task(auto_delete_messages(app.bot))
    logger.info("Auto-delete messages and captcha timeout coroutines started.")


###############################################################################
# Bot Application Run Exit Function
###############################################################################

async def tlg_app_exit(app: Application) -> None:
    '''
    Telegram Bot Application finished.
    This function is called at the exit of run_polling() or
    run_webhook() functions when the Bot stops it execution.'''
    # Disable unused arguments
    del app
    # Request to exit and wait to end coroutines
    logger.info("Bot stopped. Releasing resources...")
    Global.force_exit = True
    if Global.async_captcha_timeout is not None:
        if not Global.async_captcha_timeout.done():
            logger.info("Waiting coroutine end: captcha_timeout()")
            await Global.async_captcha_timeout
    if Global.async_auto_delete_messages is not None:
        if not Global.async_auto_delete_messages.done():
            logger.info("Waiting coroutine end: async_auto_delete_messages()")
            await Global.async_auto_delete_messages
    # Save current session data
    save_session()
    # Close the program
    logger.info("All resources released.")


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
    # Check if Bot Token has been set or has default value
    if CONST["TOKEN"] == "XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX":
        logger.error("Bot Token has not been set.")
        logger.info("Please add your Bot Token to settings.py file.")
        return 1
    # Check if Bot owner has been set in Private Bot mode
    if (CONST["BOT_OWNER"] == "XXXXXXXXX") and CONST["BOT_PRIVATE"]:
        logger.error("Bot Owner has not been set for Private Bot.")
        logger.info("Please add the Bot Owner to settings.py file.")
        return 1
    # Setup Bot Application
    tlg_app = tlg_app_setup(CONST["TOKEN"])
    # Launch Bot Application
    tlg_app_run(tlg_app)
    return 0


###############################################################################
# Runnable Main Script Detection
###############################################################################

if __name__ == "__main__":
    logger.info("Application start")
    return_code = main(len(sys_argv) - 1, sys_argv[1:])
    logger.info("Application exit (%d)", return_code)
    sys_exit(return_code)
