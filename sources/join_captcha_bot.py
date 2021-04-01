#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    join_captcha_bot.py
Description:
    Telegram Bot that send a captcha for each new user who join a group, and ban them if they
    can not solve the captcha in a specified time. This is an approach to deny access to groups of
    non-humans "users"
Author:
    Jose Rios Rubio
Creation date:
    09/09/2018
Last modified date:
    31/03/2021
Version:
    1.19.1
'''

###############################################################################
### Imported modules

import logging
import re

from sys import exit
from signal import signal, SIGTERM, SIGINT, SIGUSR1
from os import kill, getpid, path, remove, makedirs, listdir
from shutil import rmtree
from datetime import datetime, timedelta
from time import time, sleep, strptime, mktime, strftime
from threading import Thread, Lock
from operator import itemgetter
from collections import OrderedDict
from random import choice, randint

from tsjson import TSjson
from multicolorcaptcha import CaptchaGenerator

from telegram import (
    Update, InputMediaPhoto, InlineKeyboardButton,
    InlineKeyboardMarkup, ChatPermissions, Poll
)

from telegram.ext import (
    CallbackContext, Updater, CommandHandler,
    MessageHandler, Filters, CallbackQueryHandler,
    PollAnswerHandler, Defaults
)

from telegram.ext.dispatcher import (
    run_async
)

from telegram.utils.helpers import (
    escape_markdown
)

from telegram.error import (
    TelegramError, Unauthorized, BadRequest,
    TimedOut, ChatMigrated, NetworkError
)

from commons import (
    printts, is_int, add_lrm, file_write,
    file_read, list_remove_element, get_unix_epoch
)

from tlgbotutils import (
    tlg_send_msg, tlg_send_image, tlg_send_poll, tlg_stop_poll,
    tlg_answer_callback_query, tlg_delete_msg, tlg_edit_msg_media,
    tlg_ban_user, tlg_kick_user, tlg_user_is_admin, tlg_leave_chat,
    tlg_restrict_user, tlg_is_valid_user_id_or_alias, tlg_is_valid_group,
    tlg_alias_in_string
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
th_0 = None
th_1 = None
force_exit = False

# Create Captcha Generator object of specified size (2 -> 640x360)
CaptchaGen = CaptchaGenerator(2)

###############################################################################
### Setup Bot Logger

log_level=logging.INFO
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)
#logger = logging.getLogger("CaptchaBot")

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
        ("Captcha_Chars_Mode", CONST["INIT_CAPTCHA_CHARS_MODE"]),
        ("Captcha_Time", CONST["INIT_CAPTCHA_TIME_MIN"]),
        ("Captcha_Difficulty_Level", CONST["INIT_CAPTCHA_DIFFICULTY_LEVEL"]),
        ("Restrict_Non_Text", CONST["INIT_RESTRICT_NON_TEXT_MSG"]),
        ("Rm_Result_Msg", CONST["INIT_RM_RESULT_MSG"]),
        ("Rm_Welcome_Msg", CONST["INIT_RM_WELCOME_MSG"]),
        ("Poll_Q", ""),
        ("Poll_A", []),
        ("Poll_C_A", 0),
        ("Welcome_Msg", "-"),
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

def tlg_send_selfdestruct_msg(bot, chat_id, message):
    '''tlg_send_selfdestruct_msg_in() with default delete time'''
    return tlg_send_selfdestruct_msg_in(bot, chat_id, message, CONST["T_DEL_MSG"])


def tlg_msg_to_selfdestruct(message):
    '''tlg_msg_to_selfdestruct_in() with default delete time'''
    tlg_msg_to_selfdestruct_in(message, CONST["T_DEL_MSG"])


def tlg_send_selfdestruct_msg_in(bot, chat_id, message, time_delete_min, **kwargs_for_send_message):
    '''Send a telegram message that will be auto-delete in specified time'''
    sent_result = tlg_send_msg(bot, chat_id, message, **kwargs_for_send_message)
    if sent_result["msg"] is None:
        return None
    tlg_msg_to_selfdestruct_in(sent_result["msg"], time_delete_min)
    return sent_result["msg"].message_id


def tlg_msg_to_selfdestruct_in(message, time_delete_min):
    '''Add a telegram message to be auto-delete in specified time'''
    global to_delete_in_time_messages_list
    # Check if provided message has all necessary attributtes
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
    destroy_time = time() + (time_delete_min*60)
    # Add sent message data to to-delete messages list
    sent_msg_data = OrderedDict([("Chat_id", None), ("User_id", None),
            ("Msg_id", None), ("delete_time", None)])
    sent_msg_data["Chat_id"] = chat_id
    sent_msg_data["User_id"] = user_id
    sent_msg_data["Msg_id"] = msg_id
    sent_msg_data["delete_time"] = destroy_time
    to_delete_in_time_messages_list.append(sent_msg_data)
    return True

###############################################################################
### General Functions

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
                    "sintax.".format(lang_iso_code, lang_file))
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


def create_image_captcha(img_file_name, difficult_level, chars_mode):
    '''Generate an image captcha from pseudo numbers'''
    image_file_path = "{}/{}.png".format(CONST["CAPTCHAS_DIR"], img_file_name)
    # If it doesn't exists, create captchas folder to store generated captchas
    if not path.exists(CONST["CAPTCHAS_DIR"]):
        makedirs(CONST["CAPTCHAS_DIR"])
    else:
        # If the captcha file exists remove it
        if path.exists(image_file_path):
            remove(image_file_path)
    # Generate and save the captcha with a random captcha background mono-color or multi-color
    captcha = CaptchaGen.gen_captcha_image(difficult_level, chars_mode, bool(randint(0, 1)))
    image = captcha["image"]
    image.save(image_file_path, "png")
    # Return a dictionary with captcha file path and captcha resolve characters
    generated_captcha = {"image": "", "number": ""}
    generated_captcha["image"] = image_file_path
    generated_captcha["number"] = captcha["characters"]
    return generated_captcha


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

###############################################################################
### Received Telegram not-command messages handlers

@run_async
def new_member_join(update: Update, context: CallbackContext):
    '''New member join the group event handler'''
    global new_users
    bot = context.bot
    # Get message data
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        printts("Warning: Received an unexpected new user update.")
        printts(update)
        return
    chat_id = getattr(update_msg, "chat_id", None)
    if chat_id is None:
        printts("Warning: Received an unexpected new user update without chat id.")
        printts(update)
        return
    chat = getattr(update_msg, "chat", None)
    if chat is None:
        printts("Warning: Received an unexpected new user update without chat.")
        printts(update)
        return
    # Leave the chat if it is a channel
    if chat.type == "channel":
        printts("Bot try to be added to a channel")
        tlg_send_msg(bot, chat_id, CONST["BOT_LEAVE_CHANNEL"])
        tlg_leave_chat(bot, chat_id)
        return
    # Check if Group is allowed to be used by the Bot
    if not is_group_in_allowed_list(chat_id):
        printts("Warning: Bot added to not allowed group.")
        from_user_name = ""
        if update_msg.from_user.name is not None:
            from_user_name = update_msg.from_user.name
        else:
            from_user_name = update_msg.from_user.full_name
        chat_link = ""
        if chat.username:
            chat_link = "@{}".format(chat.username)
        printts("{}, {}, {}, {}".format(chat_id, from_user_name, chat.title, chat_link))
        msg_text = CONST["NOT_ALLOW_GROUP"].format(CONST["BOT_OWNER"], chat_id, CONST["REPOSITORY"])
        tlg_send_msg(bot, chat_id, msg_text)
        tlg_leave_chat(bot, chat_id)
        return
    if is_group_in_banned_list(chat_id):
        printts("Warning: Bot added to banned group: {}".format(chat_id))
        tlg_leave_chat(bot, chat_id)
        return
    # For each new user that join or has been added
    for join_user in update_msg.new_chat_members:
        join_user_id = join_user.id
        # Get user name
        if join_user.name is not None:
            join_user_name = join_user.name
        else:
            join_user_name = join_user.full_name
        # If the user name is too long, truncate it to 35 characters
        if len(join_user_name) > 35:
            join_user_name = join_user_name[0:35]
        # Add an unicode Left to Right Mark (LRM) to user name (names fix for arabic, hebrew, etc.)
        user_name_lrm = add_lrm(join_user_name)
        # If the added user is myself (this Bot)
        if bot.id == join_user_id:
            # Get the language of the Telegram client software the Admin that has added the Bot
            # has, to assume this is the chat language and configure Bot language of this chat
            admin_language = ""
            msg_from_user = getattr(update_msg, "from_user", None)
            if msg_from_user:
                language_code = getattr(msg_from_user, "language_code", None)
                if language_code:
                    admin_language = language_code[0:2].upper()
            if admin_language not in TEXT:
                admin_language = CONST["INIT_LANG"]
            save_config_property(chat_id, "Language", admin_language)
            # Get and save chat data
            chat_title = chat.title
            if chat_title:
                save_config_property(chat_id, "Title", chat_title)
            chat_link = chat.username
            if chat_link:
                chat_link = "@{}".format(chat_link)
                save_config_property(chat_id, "Link", chat_link)
            # Send bot join message
            tlg_send_msg(bot, chat_id, TEXT[admin_language]["START"])
        # The added user is not myself (not this Bot)
        else:
            printts(" ")
            printts("[{}] New join detected: {} ({})".format(chat_id, join_user_name, join_user_id))
            # Get and update chat data
            chat_title = chat.title
            if chat_title:
                save_config_property(chat_id, "Title", chat_title)
            # Add an unicode Left to Right Mark (LRM) to chat title (fix for arabic, hebrew, etc.)
            chat_title = add_lrm(chat_title)
            chat_link = chat.username
            if chat_link:
                chat_link = "@{}".format(chat_link)
                save_config_property(chat_id, "Link", chat_link)
            # Ignore Admins
            if tlg_user_is_admin(bot, join_user_id, chat_id):
                printts("[{}] User is an administrator.".format(chat_id))
                printts("Skipping the captcha process.")
                continue
            # Ignore Members added by an Admin
            join_by = getattr(update_msg, "from_user", None)
            if join_by:
                join_by_id = update_msg.from_user.id
                if tlg_user_is_admin(bot, join_by_id, chat_id):
                    printts("[{}] User has been added by an administrator.".format(chat_id))
                    printts("Skipping the captcha process.")
                    continue
            # Ignore if the member that has been join the group is a Bot
            if join_user.is_bot:
                printts("[{}] User is a Bot.".format(chat_id))
                printts("Skipping the captcha process.")
                continue
            # Ignore if the member that has joined is in chat ignore list
            if is_user_in_ignored_list(chat_id, join_user):
                printts("[{}] User is in ignore list.".format(chat_id))
                printts("Skipping the captcha process.")
                continue
            if is_user_in_allowed_list(join_user):
                printts("[{}] User is in global allowed list.".format(chat_id))
                printts("Skipping the captcha process.")
                continue
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
                continue
            # Determine configured language and captcha settings
            lang = get_chat_config(chat_id, "Language")
            captcha_level = get_chat_config(chat_id, "Captcha_Difficulty_Level")
            captcha_mode = get_chat_config(chat_id, "Captcha_Chars_Mode")
            # selfdestruct
            captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
            send_problem = False
            captcha_num = ""
            if captcha_mode == "button":
                # Send a button-only challenge
                challenge_text = TEXT[lang]["NEW_USER_BUTTON_MODE"].format(user_name_lrm,
                        chat_title, str(captcha_timeout))
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
                    tlg_send_selfdestruct_msg(bot, chat_id,
                            TEXT[lang]["POLL_NEW_USER_NOT_CONFIG"])
                    continue
                # Send request to solve the poll text message
                poll_request_msg_text = TEXT[lang]["POLL_NEW_USER"].format(user_name_lrm,
                    chat_title, str(captcha_timeout))
                sent_result = tlg_send_selfdestruct_msg(bot, chat_id, poll_request_msg_text)
                solve_poll_request_msg_id = None
                if sent_result is not None:
                    solve_poll_request_msg_id = sent_result
                # Send the Poll
                sent_result = tlg_send_poll(bot, chat_id, poll_question,
                        poll_options, poll_correct_option-1, captcha_timeout*60,
                        False, Poll.QUIZ)
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
                # Generate a pseudorandom captcha send it to telegram group and program message
                captcha = create_image_captcha(str(join_user_id), captcha_level, captcha_mode)
                captcha_num = captcha["number"]
                # Note: Img caption must be <= 1024 chars
                img_caption = TEXT[lang]["NEW_USER_CAPTCHA_CAPTION"].format(user_name_lrm,
                        chat_title, str(captcha_timeout))
                # Prepare inline keyboard button to let user request another catcha
                keyboard = [[InlineKeyboardButton(TEXT[lang]["OTHER_CAPTCHA_BTN_TEXT"],
                        callback_data="image_captcha {}".format(join_user_id))]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                printts("[{}] Sending captcha message to {}: {}...".format(chat_id, join_user_name, \
                        captcha_num))
                sent_result = tlg_send_image(bot, chat_id, open(captcha["image"],"rb"), img_caption,
                        reply_markup=reply_markup)
                if sent_result["msg"] is None:
                    send_problem = True
                # Remove sent captcha image file from file system
                if path.exists(captcha["image"]):
                    remove(captcha["image"])
            if not send_problem:
                # Add sent captcha message to self-destruct list
                if sent_result["msg"] is not None:
                    tlg_msg_to_selfdestruct_in(sent_result["msg"], captcha_timeout+0.5)
                # Default user join data
                join_data = \
                {
                    "user_name": join_user_name,
                    "captcha_num": captcha_num,
                    "join_time": time(),
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
                # Check if this user was before in the chat without solve the captcha
                # and restore previous join_retries
                if len(new_users[chat_id][join_user_id]["join_data"]) != 0:
                    join_data["join_retries"] = new_users[chat_id][join_user_id]["join_data"]["join_retries"]
                # Add new user join data and messages to be removed
                new_users[chat_id][join_user_id]["join_data"] = join_data
                new_users[chat_id][join_user_id]["join_msg"] = update_msg.message_id
                if sent_result["msg"]:
                    new_users[chat_id][join_user_id]["msg_to_rm"].append(sent_result["msg"].message_id)
                if (captcha_mode == "poll") and (solve_poll_request_msg_id is not None):
                    new_users[chat_id][join_user_id]["msg_to_rm"].append(solve_poll_request_msg_id)
                printts("[{}] Captcha send process complete.".format(chat_id))
                printts(" ")


def msg_notext(update: Update, context: CallbackContext):
    '''All non-text messages handler.'''
    bot = context.bot
    # Get message data
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        update_msg = getattr(update, "edited_message", None)
    if update_msg is None:
        update_msg = getattr(update, "channel_post", None)
        if update_msg is not None:
            chat = getattr(update_msg, "chat", None)
            if chat is not None:
                return
        print("Warning: Received an unexpected no-text update.")
        print(update)
        return
    chat_id = getattr(update_msg, "chat_id", None)
    if chat_id is None:
        print("Warning: Received an unexpected no-text update without chat id.")
        print(update)
        return
    chat = getattr(update_msg, "chat", None)
    if chat is None:
        print("Warning: Received an unexpected no-text update without chat.")
        print(update)
        return
    # Ignore if message comes from a private chat
    if chat.type == "private":
        return
    # Ignore if message comes from a channel
    if chat.type == "channel":
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
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


@run_async
def msg_nocmd(update: Update, context: CallbackContext):
    '''Non-command text messages handler'''
    global new_users
    bot = context.bot
    # Get message data
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        update_msg = getattr(update, "edited_message", None)
    if update_msg is None:
        update_msg = getattr(update, "channel_post", None)
        if update_msg is not None:
            chat = getattr(update_msg, "chat", None)
            if chat is not None:
                return
        print("Warning: Received an unexpected no-command update.")
        print(update)
        return
    chat_id = getattr(update_msg, "chat_id", None)
    if chat_id is None:
        print("Warning: Received an unexpected no-command update without chat id.")
        print(update)
        return
    chat = getattr(update_msg, "chat", None)
    if chat is None:
        print("Warning: Received an unexpected no-command update without chat.")
        print(update)
        return
    # Ignore if message comes from a private chat
    if chat.type == "private":
        return
    # Ignore if message comes from a channel
    if chat.type == "channel":
        return
    # Ignore if captcha protection is not enable in this chat
    captcha_enable = get_chat_config(chat_id, "Enabled")
    if not captcha_enable:
        return
    # If message doesnt has text, check for caption fields (for no text msgs and resended ones)
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
    # Ignore if message is not from a new user that has not completed the captcha yet
    if chat_id not in new_users:
        return
    if user_id not in new_users[chat_id]:
        return
    # Get Chat settings
    lang = get_chat_config(chat_id, "Language")
    rm_result_msg = get_chat_config(chat_id, "Rm_Result_Msg")
    captcha_mode = get_chat_config(chat_id, "Captcha_Chars_Mode")
    # Check for Spam (check if the message contains any URL or alias)
    has_url = re.findall(CONST["REGEX_URLS"], msg_text)
    has_alias = tlg_alias_in_string(msg_text)
    if has_url or has_alias:
        printts("[{}] Spammer detected: {}.".format(chat_id, user_name))
        printts("[{}] Removing spam message: {}.".format(chat_id, msg_text))
        captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
        # Try to remove the message and notify detection
        delete_result = tlg_delete_msg(bot, chat_id, msg_id)
        if delete_result["error"] == "":
            bot_msg = TEXT[lang]["SPAM_DETECTED_RM"].format(user_name)
            tlg_send_selfdestruct_msg_in(bot, chat_id, bot_msg, captcha_timeout)
        # Check if message cant be removed due to not delete msg privileges
        elif delete_result["error"] == "Message can't be deleted":
            bot_msg = TEXT[lang]["SPAM_DETECTED_NOT_RM"].format(user_name)
            tlg_send_selfdestruct_msg_in(bot, chat_id, bot_msg, captcha_timeout)
        else:
            printts("Message can't be deleted.")
        return
    # End here if no image captcha mode
    if captcha_mode not in { "nums", "hex", "ascii" }:
        return
    # Check if the expected captcha solve number is in the message
    printts("[{}] Received captcha reply from {}: {}".format(chat_id, user_name, msg_text))
    if new_users[chat_id][user_id]["join_data"]["captcha_num"].lower() in msg_text.lower():
        # Remove join messages
        printts("[{}] Captcha solved by {}".format(chat_id, user_name))
        for msg in new_users[chat_id][user_id]["msg_to_rm"]:
            tlg_delete_msg(bot, chat_id, msg)
        new_users[chat_id][user_id]["msg_to_rm"].clear()
        del new_users[chat_id][user_id]
        # Remove user captcha numbers message
        tlg_delete_msg(bot, chat_id, msg_id)
        bot_msg = TEXT[lang]["CAPTCHA_SOLVED"].format(user_name)
        # Send message solve message
        if rm_result_msg:
            tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
        else:
            tlg_send_msg(bot, chat_id, bot_msg)
        # Check for custom welcome message and send it
        welcome_msg = get_chat_config(chat_id, "Welcome_Msg").format(escape_markdown(user_name))
        if welcome_msg != "-":
            # Send the message as Markdown
            rm_welcome_msg = get_chat_config(chat_id, "Rm_Welcome_Msg")
            if rm_welcome_msg:
                sent_result = tlg_send_selfdestruct_msg_in(bot, chat_id, welcome_msg,
                        CONST["T_DEL_WELCOME_MSG"], parse_mode="MARKDOWN")
            else:
                sent_result = tlg_send_msg(bot, chat_id, welcome_msg, "MARKDOWN")
            if sent_result is None:
                printts("[{}] Error: Can't send the welcome message.".format(chat_id))
        # Check for send just text message option and apply user restrictions
        restrict_non_text_msgs = get_chat_config(chat_id, "Restrict_Non_Text")
        # Restrict for 1 day
        if restrict_non_text_msgs == 1:
            tomorrow_epoch = get_unix_epoch() + CONST["T_SECONDS_IN_A_DAY"]
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
        # Check if the message has 4 chars
        if len(msg_text) == 4:
            sent_msg_id = tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAPTCHA_INCORRECT_0"])
            new_users[chat_id][user_id]["msg_to_rm"].append(msg_id)
            new_users[chat_id][user_id]["msg_to_rm"].append(sent_msg_id)
        else:
            # Check if the message was just a 4 numbers msg
            if is_int(msg_text):
                sent_msg_id = tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAPTCHA_INCORRECT_1"])
                new_users[chat_id][user_id]["msg_to_rm"].append(msg_id)
                new_users[chat_id][user_id]["msg_to_rm"].append(sent_msg_id)
    printts("[{}] Captcha reply process complete.".format(chat_id))
    printts(" ")


@run_async
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
    welcome_msg = get_chat_config(chat_id, "Welcome_Msg").format(escape_markdown(user_name))
    restrict_non_text_msgs = get_chat_config(chat_id, "Restrict_Non_Text")
    # Remove previous join messages
    for msg in new_users[chat_id][user_id]["msg_to_rm"]:
        tlg_delete_msg(bot, chat_id, msg)
    new_users[chat_id][user_id]["msg_to_rm"].clear()
    # Check if user vote the correct option
    if option_answer == poll_correct_option:
        printts("[{}] User {} solved a poll challenge.".format(chat_id, user_name))
        bot_msg = TEXT[lang]["CAPTCHA_SOLVED"].format(user_name)
        if rm_result_msg:
            tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
        else:
            tlg_send_msg(bot, chat_id, bot_msg)
        del new_users[chat_id][user_id]
        # Check for custom welcome message and send it
        if welcome_msg != "-":
            if rm_welcome_msg:
                sent_result = tlg_send_selfdestruct_msg_in(bot, chat_id, welcome_msg,
                        CONST["T_DEL_WELCOME_MSG"], parse_mode="MARKDOWN")
            else:
                sent_result = tlg_send_msg(bot, chat_id, welcome_msg, "MARKDOWN")
            if sent_result is None:
                printts("[{}] Error: Can't send the welcome message.".format(chat_id))
        # Check for send just text message option and apply user restrictions
        if restrict_non_text_msgs == 1: # Restrict for 1 day
            tomorrow_epoch = get_unix_epoch() + CONST["T_SECONDS_IN_A_DAY"]
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
        bot_msg = TEXT[lang]["CAPTCHA_POLL_FAIL_0"].format(user_name)
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
        kick_result = tlg_kick_user(bot, chat_id, user_id)
        if kick_result["error"] == "":
            # Kick success
            msg_text = TEXT[lang]["CAPTCHA_POLL_FAIL_1"].format(user_name)
            # Send kicked message
            if rm_result_msg:
                tlg_send_selfdestruct_msg(bot, chat_id, msg_text)
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
                    tlg_send_selfdestruct_msg(bot, chat_id, msg_text)
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
                    tlg_send_selfdestruct_msg(bot, chat_id, msg_text)
                else:
                    tlg_send_msg(bot, chat_id, msg_text)
        # Remove user from captcha process
        del new_users[chat_id][user_id]
        # Remove fail message
        if sent_msg_id is not None:
            tlg_delete_msg(bot, chat_id, sent_msg_id)
    printts("[{}] Poll captcha process complete.".format(chat_id))
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
    # Add an unicode Left to Right Mark (LRM) to chat title (fix for arabic, hebrew, etc.)
    chat_title = add_lrm(chat_title)
    # Ignore if message is not from a new user that has not completed the captcha yet
    if chat_id not in new_users:
        return
    if user_id not in new_users[chat_id]:
        return
    # Get chat language
    lang = get_chat_config(chat_id, "Language")
    printts("[{}] User {} requested a new captcha.".format(chat_id, user_name))
    # Prepare inline keyboard button to let user request another catcha
    keyboard = [[InlineKeyboardButton(TEXT[lang]["OTHER_CAPTCHA_BTN_TEXT"],
            callback_data="image_captcha {}".format(str(query.from_user.id)))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Get captcha timeout and set image caption
    captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
    img_caption = TEXT[lang]["NEW_USER_CAPTCHA_CAPTION"].format(user_name,
            chat_title, str(captcha_timeout))
    # Get current chat configurations
    captcha_level = get_chat_config(chat_id, "Captcha_Difficulty_Level")
    captcha_mode = get_chat_config(chat_id, "Captcha_Chars_Mode")
    # Use nums mode if captcha_mode was changed while captcha was in progress
    if captcha_mode not in { "nums", "hex", "ascii" }:
        captcha_mode = "nums"
    # Generate a new captcha and edit previous captcha image message with this one
    captcha = create_image_captcha(str(user_id), captcha_level, captcha_mode)
    printts("[{}] Sending new captcha message: {}...".format(chat_id, captcha["number"]))
    input_media = InputMediaPhoto(media=open(captcha["image"], "rb"), caption=img_caption)
    edit_result = tlg_edit_msg_media(bot, chat_id, msg_id, media=input_media,
        reply_markup=reply_markup, timeout=20)
    if edit_result["error"] == "":
        # Set and modified to new expected captcha number
        new_users[chat_id][user_id]["join_data"]["captcha_num"] = captcha["number"]
        # Remove sent captcha image file from file system
        if path.exists(captcha["image"]):
            remove(captcha["image"])
    printts("[{}] New captcha request process complete.".format(chat_id))
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
    new_users[chat_id][user_id]["msg_to_rm"].clear()
    # Send message solve message
    printts("[{}] User {} solved a button-only challenge.".format(chat_id, user_name))
    bot_msg = TEXT[lang]["CAPTCHA_SOLVED"].format(user_name)
    if rm_result_msg:
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
    else:
        tlg_send_msg(bot, chat_id, bot_msg)
    del new_users[chat_id][user_id]
    # Check for custom welcome message and send it
    welcome_msg = get_chat_config(chat_id, "Welcome_Msg").format(escape_markdown(user_name))
    if welcome_msg != "-":
        # Send the message as Markdown
        rm_welcome_msg = get_chat_config(chat_id, "Rm_Welcome_Msg")
        if rm_welcome_msg:
            sent_result = tlg_send_selfdestruct_msg_in(bot, chat_id, welcome_msg,
                    CONST["T_DEL_WELCOME_MSG"], parse_mode="MARKDOWN")
        else:
            sent_result = tlg_send_msg(bot, chat_id, welcome_msg, "MARKDOWN")
        if sent_result is None:
            printts("[{}] Error: Can't send the welcome message.".format(chat_id))
    # Check for send just text message option and apply user restrictions
    restrict_non_text_msgs = get_chat_config(chat_id, "Restrict_Non_Text")
    # Restrict for 1 day
    if restrict_non_text_msgs == 1:
        tomorrow_epoch = get_unix_epoch() + CONST["T_SECONDS_IN_A_DAY"]
        tlg_restrict_user(bot, chat_id, user_id, send_msg=True, send_media=False,
            send_stickers_gifs=False, insert_links=False, send_polls=False,
            invite_members=False, pin_messages=False, change_group_info=False,
            until_date=tomorrow_epoch)
    # Restrict forever
    elif restrict_non_text_msgs == 2:
        tlg_restrict_user(bot, chat_id, user_id, send_msg=True, send_media=False,
            send_stickers_gifs=False, insert_links=False, send_polls=False,
            invite_members=False, pin_messages=False, change_group_info=False)
    printts("[{}] Button-only challenge pass request process complete.".format(chat_id))
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
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, TEXT["EN"]["START"])
    else:
        lang = get_chat_config(chat_id, "Language")
        tlg_msg_to_selfdestruct(update_msg)
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
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, TEXT["EN"]["HELP"])
    else:
        lang = get_chat_config(chat_id, "Language")
        tlg_msg_to_selfdestruct(update_msg)
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
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, TEXT["EN"]["COMMANDS"])
    else:
        lang = get_chat_config(chat_id, "Language")
        tlg_msg_to_selfdestruct(update_msg)
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["COMMANDS"])


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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
    # Check if no argument was provided with the command
    if len(args) == 0:
        msg_text = TEXT[lang]["LANG_NOT_ARG"].format(CONST["SUPPORTED_LANGS_CMDS"])
        tlg_send_selfdestruct_msg(bot, chat_id, msg_text)
        return
    # Get and configure chat to provided language
    lang_provided = args[0].upper()
    if lang_provided in TEXT:
        if lang_provided != lang:
            lang = lang_provided
            save_config_property(chat_id, "Language", lang)
            msg_text = TEXT[lang]["LANG_CHANGE"]
        else:
            msg_text = TEXT[lang]["LANG_SAME"].format(CONST["SUPPORTED_LANGS_CMDS"])
    else:
        msg_text = TEXT[lang]["LANG_BAD_LANG"].format(CONST["SUPPORTED_LANGS_CMDS"])
    tlg_send_selfdestruct_msg(bot, chat_id, msg_text)


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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["TIME_NOT_ARG"])
        return
    # Get and configure chat to provided captcha time
    if is_int(args[0]):
        new_time = int(args[0])
        if new_time < 1:
            new_time = 1
        if new_time <= 20:
            save_config_property(chat_id, "Captcha_Time", new_time)
            msg_text = TEXT[lang]["TIME_CHANGE"].format(new_time)
        else:
            msg_text = TEXT[lang]["TIME_MAX_NOT_ALLOW"]
    else:
        msg_text = TEXT[lang]["TIME_NOT_NUM"]
    tlg_send_selfdestruct_msg(bot, chat_id, msg_text)


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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["DIFFICULTY_NOT_ARG"])
        return
    # Get and configure chat to provided captcha difficulty
    if is_int(args[0]):
        new_difficulty = int(args[0])
        if new_difficulty < 1:
            new_difficulty = 1
        if new_difficulty > 5:
            new_difficulty = 5
        save_config_property(chat_id, "Captcha_Difficulty_Level", new_difficulty)
        bot_msg = TEXT[lang]["DIFFICULTY_CHANGE"].format(new_difficulty)
    else:
        bot_msg = TEXT[lang]["DIFFICULTY_NOT_NUM"]
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAPTCHA_MODE_NOT_ARG"])
        return
    # Get and configure chat to provided captcha mode
    new_captcha_mode = args[0]
    if new_captcha_mode in { "poll", "button", "nums", "hex", "ascii" }:
        save_config_property(chat_id, "Captcha_Chars_Mode", new_captcha_mode)
        bot_msg = TEXT[lang]["CAPTCHA_MODE_CHANGE"].format(new_captcha_mode)
    else:
        bot_msg = TEXT[lang]["CAPTCHA_MODE_INVALID"]
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["WELCOME_MSG_SET_NOT_ARG"])
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
    save_config_property(chat_id, "Welcome_Msg", welcome_msg)
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id,
                TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
    # Format command usage text
    text_cmd_usage = TEXT[lang]["CAPTCHA_POLL_USAGE"].format(
            CONST["MAX_POLL_QUESTION_LENGTH"],
            CONST["MAX_POLL_OPTION_LENGTH"],
            CONST["MAX_POLL_OPTIONS"])
    # Check if no argument was provided with the command
    if len(args) < 2:
        tlg_send_selfdestruct_msg(bot, chat_id, text_cmd_usage)
        return
    # Get poll message command
    poll_cmd = args[0]
    print("poll_cmd: {}".format(poll_cmd))
    if poll_cmd not in ["question", "option", "correct_option"]:
        tlg_send_selfdestruct_msg(bot, chat_id, text_cmd_usage)
        return
    if poll_cmd == "question":
        # get Poll Question
        poll_question = " ".join(args[1:])
        print("poll_question: {}".format(poll_question))
        if len(poll_question) > CONST["MAX_POLL_QUESTION_LENGTH"]:
            poll_question = poll_question[:CONST["MAX_POLL_QUESTION_LENGTH"]]
        # Save Poll Question
        save_config_property(chat_id, "Poll_Q", poll_question)
        tlg_send_selfdestruct_msg(bot, chat_id,
                TEXT[lang]["POLL_QUESTION_CONFIGURED"])
    elif poll_cmd == "correct_option":
        # get Poll correct option and check if is a number
        option_num = args[1]
        if not is_int(option_num):
            tlg_send_selfdestruct_msg(bot, chat_id, text_cmd_usage)
            return
        option_num = int(option_num)
        # Check if correct option number is configured
        if (option_num < 1) or (option_num > CONST["MAX_POLL_OPTIONS"]):
            tlg_send_selfdestruct_msg(bot, chat_id, text_cmd_usage)
            return
        poll_options = get_chat_config(chat_id, "Poll_A")
        if option_num > num_config_poll_options(poll_options):
            tlg_send_selfdestruct_msg(bot, chat_id,
                    TEXT[lang]["POLL_CORRECT_OPTION_NOT_CONFIGURED"].format(
                    option_num))
            return
        # Save Poll correct option number
        save_config_property(chat_id, "Poll_C_A", option_num)
        tlg_send_selfdestruct_msg(bot, chat_id,
                TEXT[lang]["POLL_CORRECT_OPTION_CONFIGURED"].format(
                option_num))
    elif poll_cmd == "option":
        # Check if option argument is valid
        if len(args) < 3:
            tlg_send_selfdestruct_msg(bot, chat_id, text_cmd_usage)
            return
        option_num = args[1]
        print("option_num: {}".format(option_num))
        if not is_int(option_num):
            tlg_send_selfdestruct_msg(bot, chat_id, text_cmd_usage)
            return
        option_num = int(option_num)
        if (option_num < 1) or (option_num > CONST["MAX_POLL_OPTIONS"]):
            tlg_send_selfdestruct_msg(bot, chat_id, text_cmd_usage)
            return
        option_num = option_num - 1
        # Resize poll options list if missing options slots
        poll_options = get_chat_config(chat_id, "Poll_A")
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
        # Save Poll option
        poll_options[option_num] = poll_option
        save_config_property(chat_id, "Poll_A", poll_options)
        tlg_send_selfdestruct_msg(bot, chat_id,
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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["RESTRICT_NON_TEXT_MSG_NOT_ARG"])
        return
    # Check for valid expected argument values
    restrict_non_text_msgs = args[0]
    if restrict_non_text_msgs != "enable" and restrict_non_text_msgs != "disable":
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["RESTRICT_NON_TEXT_MSG_NOT_ARG"])
        return
    # Check for forever restriction argument
    restrict_forever = False
    if (len(args) > 1) and (args[1] == "forever"):
        restrict_forever = True
    # Enable/Disable just text messages option
    if restrict_non_text_msgs == "enable":
        if restrict_forever:
            save_config_property(chat_id, "Restrict_Non_Text", 2)
        else:
            save_config_property(chat_id, "Restrict_Non_Text", 1)
        bot_msg = TEXT[lang]["RESTRICT_NON_TEXT_MSG_ENABLED"]
    else:
        save_config_property(chat_id, "Restrict_Non_Text", 0)
        bot_msg = TEXT[lang]["RESTRICT_NON_TEXT_MSG_DISABLED"]
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["IGNORE_LIST_ADD_NOT_ARG"])
        return
    # Check and add user ID/alias form ignore list
    user_id_alias = args[0]
    if tlg_is_valid_user_id_or_alias(user_id_alias):
        ignore_list = get_chat_config(chat_id, "Ignore_List")
        # Ignore list limit enforcement
        if len(ignore_list) < CONST["IGNORE_LIST_MAX"]:
            if user_id_alias not in ignore_list:
                ignore_list.append(user_id_alias)
                save_config_property(chat_id, "Ignore_List", ignore_list)
                bot_msg = TEXT[lang]["IGNORE_LIST_ADD_SUCCESS"]
            else:
                bot_msg = TEXT[lang]["IGNORE_LIST_ADD_DUPLICATED"]
        else:
            bot_msg = TEXT[lang]["IGNORE_LIST_ADD_LIMIT_EXCEEDED"]
    else:
        bot_msg = TEXT[lang]["IGNORE_LIST_ADD_INVALID"]
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["IGNORE_LIST_REMOVE_NOT_ARG"])
        return
    # Check and remove user ID/alias form ignore list
    ignore_list = get_chat_config(chat_id, "Ignore_List")
    user_id_alias = args[0]
    if list_remove_element(ignore_list, user_id_alias):
        save_config_property(chat_id, "Ignore_List", ignore_list)
        bot_msg = TEXT[lang]["IGNORE_LIST_REMOVE_SUCCESS"]
    else:
        bot_msg = TEXT[lang]["IGNORE_LIST_REMOVE_NOT_IN_LIST"]
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
    # Get and show Ignore list
    ignore_list = get_chat_config(chat_id, "Ignore_List")
    if not ignore_list:
        bot_msg = TEXT[lang]["IGNORE_LIST_EMPTY"]
    else:
        bot_msg = "\n".join([str(x) for x in ignore_list])
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["RM_SOLVE_KICK_MSG"])
        return
    # Get remove solve/kick messages config to set
    yes_or_no = args[0].lower()
    if yes_or_no == "yes":
        save_config_property(chat_id, "Rm_Result_Msg", True)
        bot_msg = TEXT[lang]["RM_SOLVE_KICK_MSG_YES"]
    elif yes_or_no == "no":
        save_config_property(chat_id, "Rm_Result_Msg", False)
        bot_msg = TEXT[lang]["RM_SOLVE_KICK_MSG_NO"]
    else:
        bot_msg = TEXT[lang]["RM_SOLVE_KICK_MSG"]
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
    # Check if no argument was provided with the command
    if len(args) == 0:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["RM_WELCOME_MSG"])
        return
    # Get remove welcome messages config to set
    yes_or_no = args[0].lower()
    if yes_or_no == "yes":
        save_config_property(chat_id, "Rm_Welcome_Msg", True)
        bot_msg = TEXT[lang]["RM_WELCOME_MSG_YES"]
    elif yes_or_no == "no":
        save_config_property(chat_id, "Rm_Welcome_Msg", False)
        bot_msg = TEXT[lang]["RM_WELCOME_MSG_NO"]
    else:
        bot_msg = TEXT[lang]["RM_WELCOME_MSG"]
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
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
    # Check and deny usage in private chat
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Get actual chat configured language
    lang = get_chat_config(chat_id, "Language")
    # Check if command was execute by an Admin
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin is None:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CAN_NOT_GET_ADMINS"])
        return
    if not is_admin:
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["CMD_NOT_ALLOW"])
        return
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
    '''Command /version message handler'''
    bot = context.bot
    # Ignore command if it was a edited message
    update_msg = getattr(update, "message", None)
    if update_msg is None:
        return
    chat_id = update_msg.chat_id
    chat_type = update_msg.chat.type
    msg_text = "Current Chat ID:\n———————————\n{}".format(chat_id)
    if chat_type == "private":
        tlg_send_msg(bot, chat_id, msg_text)
    else:
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
    if chat_type == "private":
        msg_text = TEXT["EN"]["VERSION"].format(CONST["VERSION"])
        tlg_send_msg(bot, chat_id, msg_text)
    else:
        lang = get_chat_config(chat_id, "Language")
        msg_text = TEXT[lang]["VERSION"].format(CONST["VERSION"])
        tlg_msg_to_selfdestruct(update_msg)
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
    if chat_type == "private":
        msg_text = TEXT["EN"]["ABOUT_MSG"].format(CONST["DEVELOPER"], CONST["REPOSITORY"],
        CONST["DEV_PAYPAL"], CONST["DEV_BTC"])
    else:
        lang = get_chat_config(chat_id, "Language")
        msg_text = TEXT[lang]["ABOUT_MSG"].format(CONST["DEVELOPER"], CONST["REPOSITORY"],
            CONST["DEV_PAYPAL"], CONST["DEV_BTC"])
    tlg_send_msg(bot, chat_id, msg_text)


def cmd_captcha(update: Update, context: CallbackContext):
    '''Command /captcha message handler. Usefull to test. Just Bot Owner can use it.'''
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
    # Check if command was execute by Bot owner
    if (str(user_id) != CONST["BOT_OWNER"]) and (user_alias != CONST["BOT_OWNER"]):
        tlg_send_selfdestruct_msg(bot, chat_id, CONST["CMD_JUST_ALLOW_OWNER"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Generate a random difficulty captcha
    captcha_level = randint(1, 5)
    captcha_chars_mode = choice(["nums", "hex", "ascii"]) # "button" doesn't generate an image
    captcha = create_image_captcha(str(user_id), captcha_level, captcha_chars_mode)
    printts("[{}] Sending captcha message: {}...".format(chat_id, captcha["number"]))
    # Note: Img caption must be <= 1024 chars
    img_caption = "Captcha Level: {}\nCaptcha Mode: {}\nCaptcha Code: {}".format(captcha_level,
            captcha_chars_mode, captcha["number"])
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
    # Check if command was execute by Bot owner
    if (str(user_id) != CONST["BOT_OWNER"]) and (user_alias != CONST["BOT_OWNER"]):
        tlg_send_selfdestruct_msg(bot, chat_id, CONST["CMD_JUST_ALLOW_OWNER"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Check if no argument was provided with the command
    if len(args) == 0:
        # Show Actual Global allowed list Users
        l_white_users = file_read(CONST["F_ALLOWED_USERS"])
        bot_msg = "\n".join([str(user) for user in l_white_users])
        bot_msg = "Global Allowed Users List:\n--------------------\n{}".format(bot_msg)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
        tlg_send_selfdestruct_msg(bot, chat_id, CONST["ALLOWUSERLIST_USAGE"])
        return
    else:
        if len(args) <= 1:
            tlg_send_selfdestruct_msg(bot, chat_id, CONST["ALLOWUSERLIST_USAGE"])
            return
        if (args[0] != "add") and (args[0] != "rm"):
            tlg_send_selfdestruct_msg(bot, chat_id, CONST["ALLOWUSERLIST_USAGE"])
            return
        add_rm = args[0]
        user = args[1]
        l_white_users = file_read(CONST["F_ALLOWED_USERS"])
        if add_rm == "add":
            if not tlg_is_valid_user_id_or_alias(user):
                tlg_send_selfdestruct_msg(bot, chat_id, "Invalid User ID/Alias.")
                return
            if user not in l_white_users:
                file_write(CONST["F_ALLOWED_USERS"], "{}\n".format(user))
                tlg_send_selfdestruct_msg(bot, chat_id, "User added to Global allowed list.")
            else:
                tlg_send_selfdestruct_msg(bot, chat_id, "The User is already in Global allowed list.")
            return
        if add_rm == "rm":
            if not tlg_is_valid_user_id_or_alias(user):
                tlg_send_selfdestruct_msg(bot, chat_id, "Invalid User ID/Alias.")
                return
            if list_remove_element(l_white_users, user):
                file_write(CONST["F_ALLOWED_USERS"], l_white_users, "w")
                tlg_send_selfdestruct_msg(bot, chat_id, "User removed from Global allowed list.")
            else:
                tlg_send_selfdestruct_msg(bot, chat_id, "The User is not in Global allowed list.")


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
    # Check if command was execute by Bot owner
    if (str(user_id) != CONST["BOT_OWNER"]) and (user_alias != CONST["BOT_OWNER"]):
        tlg_send_selfdestruct_msg(bot, chat_id, CONST["CMD_JUST_ALLOW_OWNER"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update_msg)
    # Check if no argument was provided with the command
    if len(args) == 0:
        # Show Actual Allowed Groups
        l_allowed_groups = file_read(CONST["F_ALLOWED_GROUPS"])
        bot_msg = "\n".join([str(group) for group in l_allowed_groups])
        bot_msg = "Allowed Groups:\n--------------------\n{}".format(bot_msg)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
        tlg_send_selfdestruct_msg(bot, chat_id, CONST["ALLOWGROUP_USAGE"])
        return
    else:
        if len(args) <= 1:
            tlg_send_selfdestruct_msg(bot, chat_id, CONST["ALLOWGROUP_USAGE"])
            return
        if (args[0] != "add") and (args[0] != "rm"):
            tlg_send_selfdestruct_msg(bot, chat_id, CONST["ALLOWGROUP_USAGE"])
            return
        add_rm = args[0]
        group = args[1]
        l_allowed_groups = file_read(CONST["F_ALLOWED_GROUPS"])
        if add_rm == "add":
            if not tlg_is_valid_group(group):
                tlg_send_selfdestruct_msg(bot, chat_id, "Invalid Group ID.")
                return
            if group not in l_allowed_groups:
                file_write(CONST["F_ALLOWED_GROUPS"], "{}\n".format(group))
                tlg_send_selfdestruct_msg(bot, chat_id, "Group added to allowed list.")
            else:
                tlg_send_selfdestruct_msg(bot, chat_id, "The group is already in the allowed list.")
            return
        if add_rm == "rm":
            if not tlg_is_valid_group(group):
                tlg_send_selfdestruct_msg(bot, chat_id, "Invalid Group ID.")
                return
            if list_remove_element(l_allowed_groups, group):
                file_write(CONST["F_ALLOWED_GROUPS"], l_allowed_groups, "w")
                tlg_send_selfdestruct_msg(bot, chat_id, "Group removed from allowed list.")
            else:
                tlg_send_selfdestruct_msg(bot, chat_id, "The group is not in allowed list.")

###############################################################################
### Bot automatic remove sent messages thread

def th_selfdestruct_messages(bot):
    '''Handle remove messages sent by the Bot with the timed self-delete function'''
    global to_delete_in_time_messages_list
    while not force_exit:
        # Thread sleep for each iteration
        sleep(0.1)
        # Check each Bot sent message
        i = 0
        while i < len(to_delete_in_time_messages_list):
            # Check for break iterating if script must exit
            if force_exit:
                return
            sent_msg = to_delete_in_time_messages_list[i]
            # Sleep each 100 iterations
            i = i + 1
            if i > 100:
                i = 0
                sleep(0.01)
            # If actual time is equal or more than the expected sent msg delete time
            if time() >= sent_msg["delete_time"]:
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
        sleep(0.1)
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
                # Sleep each 100 iterations
                i = i + 1
                if i > 100:
                    i = 0
                    sleep(0.01)
                # Check for end thread when iterating if script must exit
                if force_exit:
                    return
                # Ignore if user is not in this chat
                if user_id not in new_users[chat_id]:
                    continue
                captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
                try:
                    user_join_time = new_users[chat_id][user_id]["join_data"]["join_time"]
                    if new_users[chat_id][user_id]["join_data"]["kicked_ban"]:
                        # Remove from new users list the remaining kicked users that have not solve
                        # the captcha in 1 hour (user ban just happen if a user try to join the group
                        # and fail to solve the captcha 5 times in the past 10 mins)
                        if time() - user_join_time < (captcha_timeout*60) + 600:
                            continue
                        printts("Removing kicked user {} after 10 mins".format(user_id))
                        del new_users[chat_id][user_id]
                    else:
                        # If time for kick/ban has not arrived yet
                        if time() - user_join_time < captcha_timeout*60:
                            continue
                        # The time has come for this user
                        lang = get_chat_config(chat_id, "Language")
                        user_name = new_users[chat_id][user_id]["join_data"]["user_name"]
                        join_retries = new_users[chat_id][user_id]["join_data"]["join_retries"]
                        printts("[{}] Captcha reply timed out for user {}.".format(chat_id, user_name))
                        # Get current group remove kick/ban messages config
                        rm_result_msg = get_chat_config(chat_id, "Rm_Result_Msg")
                        # Check if this "user" has not join this chat more than 5 times (just kick)
                        if join_retries < 5:
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
                                    tlg_send_selfdestruct_msg(bot, chat_id, msg_text)
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
                                        tlg_send_selfdestruct_msg(bot, chat_id, msg_text)
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
                                        tlg_send_selfdestruct_msg(bot, chat_id, msg_text)
                                    else:
                                        tlg_send_msg(bot, chat_id, msg_text)
                        # The user has join this chat 5 times and never succes to solve the captcha (ban)
                        else:
                            printts("[{}] Captcha not solved, banning {} ({})...".format(chat_id,
                                    user_name, user_id))
                            # Try to ban the user and notify Admins
                            ban_result = tlg_ban_user(bot, chat_id, user_id)
                            if ban_result["error"] == "":
                                # Ban success
                                msg_text = TEXT[lang]["NEW_USER_BAN"].format(user_name)
                            else:
                                # Ban fail
                                if ban_result["error"] == "User not found":
                                    # The user is not in the chat
                                    msg_text = TEXT[lang]["NEW_USER_BAN_NOT_IN_CHAT"].format(user_name)
                                elif ban_result["error"] == "Not enough rights to restrict/unrestrict chat member":
                                    # Bot has no privileges to ban
                                    msg_text = TEXT[lang]["NEW_USER_BAN_NOT_RIGHTS"].format(user_name)
                                else:
                                    # For other reason, the Bot can't ban
                                    msg_text = TEXT[lang]["BOT_CANT_BAN"].format(user_name)
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
                        tlg_delete_msg(bot, chat_id, new_users[chat_id][user_id]["join_msg"])
                        for msg in new_users[chat_id][user_id]["msg_to_rm"]:
                            tlg_delete_msg(bot, chat_id, msg)
                        new_users[chat_id][user_id]["msg_to_rm"].clear()
                        # Delete user join info if was ban
                        if join_retries >= 5:
                            del new_users[chat_id][user_id]
                        printts("[{}] Kick/Ban process complete".format(chat_id))
                        printts(" ")
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
    # Set messages to be sent silently by default
    msgs_defaults = Defaults(disable_notification=True)
    # Create an event handler (updater) for a Bot with the given Token and get the dispatcher
    updater = Updater(CONST["TOKEN"], workers=12, use_context=True, defaults=msgs_defaults)
    dp = updater.dispatcher
    # Set Telegram errors handler
    dp.add_error_handler(tlg_error_callback)
    # Set to dispatcher all expected commands messages handler
    dp.add_handler(CommandHandler("start", cmd_start))
    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("commands", cmd_commands))
    dp.add_handler(CommandHandler("language", cmd_language, pass_args=True))
    dp.add_handler(CommandHandler("time", cmd_time, pass_args=True))
    dp.add_handler(CommandHandler("difficulty", cmd_difficulty, pass_args=True))
    dp.add_handler(CommandHandler("captcha_mode", cmd_captcha_mode, pass_args=True))
    dp.add_handler(CommandHandler("welcome_msg", cmd_welcome_msg, pass_args=True))
    dp.add_handler(CommandHandler("captcha_poll", cmd_captcha_poll, pass_args=True))
    dp.add_handler(CommandHandler("restrict_non_text", cmd_restrict_non_text, pass_args=True))
    dp.add_handler(CommandHandler("add_ignore", cmd_add_ignore, pass_args=True))
    dp.add_handler(CommandHandler("remove_ignore", cmd_remove_ignore, pass_args=True))
    dp.add_handler(CommandHandler("ignore_list", cmd_ignore_list))
    dp.add_handler(CommandHandler("remove_solve_kick_msg", cmd_remove_solve_kick_msg, pass_args=True))
    dp.add_handler(CommandHandler("remove_welcome_msg", cmd_remove_welcome_msg, pass_args=True))
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
    dp.add_handler(MessageHandler(Filters.text, msg_nocmd))
    # Set to dispatcher not text messages handler
    dp.add_handler(MessageHandler(Filters.photo | Filters.audio | Filters.voice |
            Filters.video | Filters.sticker | Filters.document | Filters.location |
            Filters.contact, msg_notext))
    # Set to dispatcher a new member join the group and member left the group events handlers
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member_join))
    # Set to dispatcher inline keyboard callback handler for new captcha request and
    # button captcha challenge
    dp.add_handler(CallbackQueryHandler(key_inline_keyboard))
    # Set to dispatcher users poll vote handler
    dp.add_handler(PollAnswerHandler(receive_poll_answer))
    # Launch the Bot ignoring pending messages (clean=True) and get all updates (allowed_uptades=[])
    if CONST["WEBHOOK_HOST"] == "None":
        printts("Setup Bot for Polling.")
        updater.start_polling(
            clean=True,
            allowed_updates=[]
        )
    else:
        printts("Setup Bot for Webhook.")
        updater.start_webhook(
            clean=True, listen="0.0.0.0", port=CONST["WEBHOOK_PORT"], url_path=CONST["TOKEN"],
            key=CONST["WEBHOOK_CERT_PRIV_KEY"], cert=CONST["WEBHOOK_CERT"],
            webhook_url="https://{}:{}/{}".format(CONST["WEBHOOK_HOST"], CONST["WEBHOOK_PORT"],
            CONST["TOKEN"])
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
    kill(getpid(), SIGUSR1)
    sleep(1)
    printts("Exit 1")
    exit(1)


if __name__ == "__main__":
    main()
