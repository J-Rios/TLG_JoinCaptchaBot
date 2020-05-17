#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    join_captcha_bot.py
Description:
    Telegram Bot that send a captcha for each new user who join a group, and ban them if they 
    can not solve the captcha in a specified time. This is an approach to deny access to groups of 
    non-humans "users".
Author:
    Jose Rios Rubio
Creation date:
    09/09/2018
Last modified date:
    17/05/2020
Version:
    1.10.2
'''

####################################################################################################

### Imported modules ###
import re
from sys import exit
from signal import signal, SIGTERM, SIGINT
from os import path, remove, makedirs, listdir
from shutil import rmtree
from datetime import datetime, timedelta
from time import time, sleep, strptime, mktime, strftime
from threading import Thread, Lock
from operator import itemgetter
from collections import OrderedDict
from random import randint
from telegram import (Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup,
    ChatPermissions)
from telegram.ext import (CallbackContext, Updater, CommandHandler, MessageHandler, Filters, 
    CallbackQueryHandler, Defaults)

from constants import CONST, TEXT
from tsjson import TSjson
from lib.multicolor_captcha_generator.img_captcha_gen import CaptchaGenerator

####################################################################################################

### Globals ###
updater = None
files_config_list = []
to_delete_in_time_messages_list = []
to_delete_join_messages_list = []
new_users_list = []

# Create Captcha Generator object of specified size (2 -> 640x360)
CaptchaGen = CaptchaGenerator(2)

####################################################################################################

### Termination Signals Handler For Program Process ###

def signal_handler(signal,  frame):
    '''Termination signals (SIGINT, SIGTERM) handler for program process'''
    global updater
    printts("Termination signal received. Releasing resources (Waiting for files to be closed)...")
    # Acquire all messages and users files mutex to ensure not read/write operation on them
    for chat_config_file in files_config_list:
        chat_config_file["File"].lock.acquire()
    printts("All resources successfully released.")
    if updater is not None:
        printts("Closing Bot...")
        updater.stop()
    # Close the program
    printts("Exit")
    exit(0)


### Signals attachment ###
signal(SIGTERM, signal_handler) # SIGTERM (kill pid) to signal_handler
signal(SIGINT, signal_handler)  # SIGINT (Ctrl+C) to signal_handler

####################################################################################################

### Auxiliar Functions ###

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

####################################################################################################

### JSON Chat Config File Functions ###

def get_default_config_data():
    '''Get default config data structure'''
    config_data = OrderedDict(
    [
        ("Title", CONST["INIT_TITLE"]),
        ("Link", CONST["INIT_LINK"]),
        ("Enabled", CONST["INIT_ENABLE"]),
        ("Restrict_Non_Text", CONST["INIT_RESTRICT_NON_TEXT_MSG"]),
        ("Captcha_Time", CONST["INIT_CAPTCHA_TIME_MIN"]),
        ("Captcha_Difficulty_Level", CONST["INIT_CAPTCHA_DIFFICULTY_LEVEL"]),
        ("Captcha_Chars_Mode", CONST["INIT_CAPTCHA_CHARS_MODE"]),
        ("Language", CONST["INIT_LANG"]),
        ("Welcome_Msg", "-"),
        ("Ignore_List", [])
    ])
    return config_data


def save_config_property(chat_id, property, value):
    '''Store actual chat configuration in file'''
    fjson_config = get_chat_config_file(chat_id)
    config_data = fjson_config.read()
    if not config_data:
        config_data = get_default_config_data()
    config_data[property] = value
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

####################################################################################################

### Telegram Related Functions ###

def tlg_user_is_admin(bot, user_id, chat_id):
    '''Check if the specified user is an Administrator of a group given by IDs'''
    try:
        group_admins = bot.get_chat_administrators(chat_id)
    except Exception:
        return None
    for admin in group_admins:
        if user_id == admin.user.id:
            return True
    return False


def tlg_get_bot_admin_privileges(bot, chat_id):
    '''Get the actual Bot administration privileges'''
    try:
        bot_data = bot.get_me()
    except Exception:
        return None
    bot_admin_privileges = OrderedDict(
    [
        ("can_change_info", bot_data.can_change_info),
        ("can_delete_messages", bot_data.can_delete_messages),
        ("can_restrict_members", bot_data.can_restrict_members),
        ("can_invite_users", bot_data.can_invite_users),
        ("can_pin_messages", bot_data.can_pin_messages),
        ("can_promote_members", bot_data.can_promote_members)
    ])
    return bot_admin_privileges


def tlg_send_selfdestruct_msg(bot, chat_id, message):
    '''tlg_send_selfdestruct_msg_in() with default delete time'''
    return tlg_send_selfdestruct_msg_in(bot, chat_id, message, CONST["T_DEL_MSG"])


def tlg_msg_to_selfdestruct(message):
    '''tlg_msg_to_selfdestruct_in() with default delete time'''
    tlg_msg_to_selfdestruct_in(message, CONST["T_DEL_MSG"])


def tlg_send_selfdestruct_msg_in(bot, chat_id, message, time_delete_min):
    '''Send a telegram message that will be auto-delete in specified time'''
    sent_msg_id = None
    # Send the message
    try:
        sent_msg = bot.send_message(chat_id, message)
        tlg_msg_to_selfdestruct_in(sent_msg, time_delete_min)
        sent_msg_id = sent_msg["message_id"]
    # It has been an unsuccesfull sent
    except Exception as e:
        printts("[{}] {}".format(chat_id, str(e)))
    return sent_msg_id


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


def tlg_delete_msg(bot, chat_id, msg_id):
    '''Try to remove a telegram message'''
    return_code = 0
    if msg_id is not None:
        try:
            bot.delete_message(chat_id, msg_id)
            return_code = 1
        except Exception as e:
            printts("[{}] {}".format(chat_id, str(e)))
            # Message is already deleted
            if str(e) == "Message to delete not found":
                return_code = -1
            # The bot has no privileges to delete messages
            elif str(e) == "Message can't be deleted":
                return_code = -2
    return return_code


def tlg_ban_user(bot, chat_id, user_id):
    '''Telegram Ban a user of an specified chat'''
    return_code = 0
    try:
        user_data = bot.getChatMember(chat_id, user_id)
        if (user_data['status'] != "left") and (user_data['status'] != "kicked"):
            bot.kickChatMember(chat_id, user_id)
            return_code = 1
        else:
            return_code = -1
    except Exception as e:
        printts("[{}] {}".format(chat_id, str(e)))
        if str(e) == "Not enough rights to restrict/unrestrict chat member":
            return_code = -2
        elif str(e) == "User is an administrator of the chat":
            return_code = -3
    return return_code


def tlg_kick_user(bot, chat_id, user_id):
    '''Telegram Kick (no ban) a user of an specified chat'''
    return_code = 0
    try:
        user_data = bot.getChatMember(chat_id, user_id)
        if (user_data['status'] != "left") and (user_data['status'] != "kicked"):
            bot.kickChatMember(chat_id, user_id)
            bot.unbanChatMember(chat_id, user_id)
            return_code = 1
        else:
            return_code = -1
    except Exception as e:
        printts("[{}] {}".format(chat_id, str(e)))
        if str(e) == "Not enough rights to restrict/unrestrict chat member":
            return_code = -2
        elif str(e) == "User is an administrator of the chat":
            return_code = -3
    return return_code


def tlg_check_chat_type(bot, chat_id_or_alias):
    '''Telegram check if a chat exists and what type it is (user, group, channel).'''
    chat_type = None
    # Check if it is a group or channel
    try:
        get_chat = bot.getChat(chat_id_or_alias)
        chat_type = getattr(get_chat, "type", None)
    except Exception as e:
        if str(e) != "Chat not found":
            printts("[{}] {}".format(chat_id_or_alias, str(e)))
    return chat_type


def tlg_leave_chat(bot, chat_id):
    '''Telegram Bot try to leave a chat.'''
    left = False
    try:
        if bot.leave_chat(chat_id):
            left = True
    except Exception as e:
        printts("[{}] {}".format(chat_id, str(e)))
    return left


def tlg_restrict_user(bot, chat_id, user_id, send_msg=None, send_media=None, 
        send_stickers_gifs=None, insert_links=None, send_polls=None, 
        invite_members=None, pin_messages=None, change_group_info=None):
    '''Telegram Bot try to restrict user permissions in a group.'''
    result = False
    try:
        permissions = ChatPermissions(send_msg, send_media, send_polls, send_stickers_gifs, 
            insert_links, change_group_info, invite_members, pin_messages)
        result = bot.restrictChatMember(chat_id, user_id, permissions)
    except Exception as e:
        printts("[{}] {}".format(chat_id, str(e)))
        result = False
    return result


def is_valid_user_id_or_alias(user_id_alias):
    '''Check if given telegram ID or alias has a valid expected format.'''
    # Check if it is a valid alias (start with a @ and have 5 characters or more)
    if user_id_alias[0] == '@':
        if len(user_id_alias) > 5:
            return True
    # Check if it is a valid ID (is a number larger than 0)
    try:
        user_id = int(user_id_alias)
        if user_id > 0:
            return True
    except ValueError:
        return False
    return False

####################################################################################################

### General Functions ###

def initialize_resources():
    '''Initialize resources by populating files list with chats found files'''
    global files_config_list
    # Remove old captcha directory and create it again
    if path.exists(CONST["CAPTCHAS_DIR"]):
        rmtree(CONST["CAPTCHAS_DIR"])
    makedirs(CONST["CAPTCHAS_DIR"])
    # Create whitelist file if it does not exists
    if not path.exists(CONST["F_WHITE_LIST"]):
        file_write(CONST["F_WHITE_LIST"], "")
    # Create data directory if it does not exists
    if not path.exists(CONST["CHATS_DIR"]):
        makedirs(CONST["CHATS_DIR"])
    else:
        # If chats directory exists, check all subdirectories names (chats ID)
        files = listdir(CONST["CHATS_DIR"])
        if files:
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
    actual_script_path = path.dirname(path.realpath(__file__))
    load_urls_regex("{}/{}".format(actual_script_path, CONST["F_TLDS"]))
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
    for lang_iso_code in TEXT:
        lang_file = "{}/{}.json".format(CONST["LANG_DIR"], lang_iso_code.lower())
        json_lang_file = TSjson(lang_file)
        json_lang_texts = json_lang_file.read()
        if (json_lang_texts is None) or (json_lang_texts == {}):
            printts("Error loading language \"{}\" from {}. Language file not found or bad JSON "
                    "sintax.".format(lang_iso_code, lang_file))
            printts("Exit.\n")
            exit(0)
        TEXT[lang_iso_code] = json_lang_texts


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


def update_to_delete_join_msg_id(msg_chat_id, msg_user_id, message_id_key, new_msg_id_value):
    '''Update the msg_id_value from his key of the to_delete_join_messages_list'''
    global to_delete_join_messages_list
    i = 0
    while i < len(to_delete_join_messages_list):
        msg = to_delete_join_messages_list[i]
        if (msg["user_id"] == msg_user_id) and (msg["chat_id"] == msg_chat_id):
            msg[message_id_key] = new_msg_id_value
            list_remove_element(to_delete_join_messages_list, msg)
            to_delete_join_messages_list.append(msg)
            break
        i = i + 1


def is_user_in_white_list(user):
    '''Check if user is in global whitelist.'''
    l_white_users = file_read(CONST["F_WHITE_LIST"])
    if user.id in l_white_users:
        return True
    if user.username is not None:
        user_alias = "@{}".format(user.username)
        if user_alias in l_white_users:
            return True
    return False


def is_user_inignored_list(chat_id, user):
    '''Check if user is in ignored users list.'''
    ignored_users = get_chat_config(chat_id, "Ignore_List")
    if user.id in ignored_users:
        return True
    if user.username is not None:
        user_alias = "@{}".format(user.username)
        if user_alias in ignored_users:
            return True
    return False

####################################################################################################

### Received Telegram not-command messages handlers ###

def msg_new_user(update: Update, context: CallbackContext):
    '''New member join the group event handler'''
    global to_delete_join_messages_list
    global new_users_list
    bot = context.bot
    # Get message data
    chat_id = update.message.chat_id
    # Determine configured bot language in actual chat
    lang = get_chat_config(chat_id, "Language")
    # Leave the chat if it is a channel
    msg = getattr(update, "message", None)
    if msg.chat.type == "channel":
        printts("Bot try to be added to a channel")
        tlg_send_selfdestruct_msg_in(bot, chat_id, TEXT[lang]["BOT_LEAVE_CHANNEL"], 1)
        tlg_leave_chat(bot, chat_id)
        return
    # For each new user that join or has been added
    for join_user in update.message.new_chat_members:
        join_user_id = join_user.id
        # Get user name
        if join_user.name is not None:
            join_user_name = join_user.name
        else:
            join_user_name = join_user.full_name
        # Add an unicode Left to Right Mark (LRM) to user name (names fix for arabic, hebrew, etc.)
        join_user_name = add_lrm(join_user_name)
        # If the user name is too long, truncate it to 35 characters
        if len(join_user_name) > 35:
            join_user_name = join_user_name[0:35]
        # If the added user is myself (this Bot)
        if bot.id == join_user_id:
            # Get the language of the Telegram client software the Admin that has added the Bot 
            # has, to assume this is the chat language and configure Bot language of this chat
            admin_language = update.message.from_user.language_code[0:2].upper()
            if admin_language not in TEXT:
                admin_language = CONST["INIT_LANG"]
            save_config_property(chat_id, "Language", admin_language)
            # Get and save chat data
            chat_title = update.message.chat.title
            if chat_title:
                save_config_property(chat_id, "Title", chat_title)
            chat_link = update.message.chat.username
            if chat_link:
                chat_link = "@{}".format(chat_link)
                save_config_property(chat_id, "Link", chat_link)
            # Send bot join message
            try:
                bot.send_message(chat_id, TEXT[admin_language]["START"])
            except Exception as e:
                printts("[{}] {}".format(chat_id, str(e)))
                pass
        # The added user is not myself (not this Bot)
        else:
            printts(" ")
            printts("[{}] New join detected: {} ({})".format(chat_id, join_user_name, join_user_id))
            # Get and update chat data
            chat_title = update.message.chat.title
            if chat_title:
                save_config_property(chat_id, "Title", chat_title)
            # Add an unicode Left to Right Mark (LRM) to chat title (fix for arabic, hebrew, etc.)
            chat_title = add_lrm(chat_title)
            chat_link = update.message.chat.username
            if chat_link:
                chat_link = "@{}".format(chat_link)
                save_config_property(chat_id, "Link", chat_link)
            # Ignore Admins
            if tlg_user_is_admin(bot, join_user_id, chat_id):
                printts("[{}] User is an administrator. Skipping the captcha process.".format(chat_id))
                continue
            # Ignore if the member that has been join the group is a Bot
            if join_user.is_bot:
                printts("[{}] User is a Bot. Skipping the captcha process.".format(chat_id))
                continue
            # Ignore if the member that has joined is in chat ignore list
            if is_user_inignored_list(chat_id, join_user):
                printts("[{}] User is in ignore list. Skipping the captcha process.".format(chat_id))
                continue
            if is_user_in_white_list(join_user):
                printts("[{}] User is in global whitelist. Skipping the captcha process.".format(chat_id))
                continue
            # Check and remove previous join messages of that user (if any)
            i = 0
            while i < len(to_delete_join_messages_list):
                msg = to_delete_join_messages_list[i]
                if (msg["user_id"] == join_user_id) and (msg["chat_id"] == chat_id):
                    tlg_delete_msg(bot, msg["chat_id"], msg["msg_id_join0"].message_id)
                    tlg_delete_msg(bot, msg["chat_id"], msg["msg_id_join1"])
                    tlg_delete_msg(bot, msg["chat_id"], msg["msg_id_join2"])
                    list_remove_element(to_delete_join_messages_list, msg)
                i = i + 1
            # Ignore if the captcha protection is not enable in this chat
            captcha_enable = get_chat_config(chat_id, "Enabled")
            if not captcha_enable:
                printts("[{}] Captcha is not enabled in this chat".format(chat_id))
                continue
            # Determine configured bot language in actual chat
            captcha_level = get_chat_config(chat_id, "Captcha_Difficulty_Level")
            captcha_chars_mode = get_chat_config(chat_id, "Captcha_Chars_Mode")
            # Generate a pseudorandom captcha send it to telegram group and program message 
            # selfdestruct
            captcha = create_image_captcha(str(join_user_id), captcha_level, captcha_chars_mode)
            captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
            img_caption = TEXT[lang]["NEW_USER_CAPTCHA_CAPTION"].format(join_user_name,
                    chat_title, str(captcha_timeout))
            # Prepare inline keyboard button to let user request another catcha
            keyboard = [[InlineKeyboardButton(TEXT[lang]["OTHER_CAPTCHA_BTN_TEXT"],
                    callback_data=join_user_id)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            send_problem = False
            printts("[{}] Sending captcha message: {}...".format(chat_id, captcha["number"]))
            try:
                # Note: Img caption must be <= 1024 chars
                sent_img_msg = bot.send_photo(chat_id=chat_id, photo=open(captcha["image"],"rb"),
                        reply_markup=reply_markup, caption=img_caption, timeout=20)
            except Exception as e:
                printts("[{}] {}".format(chat_id, str(e)))
                if str(e) != "Timed out":
                    send_problem = True
                else:
                    printts("sent_img_msg: {}".format(sent_img_msg))
            # Remove sent captcha image file from file system
            if path.exists(captcha["image"]):
                remove(captcha["image"])
            if not send_problem:
                # Add sent image to self-destruct list
                if not tlg_msg_to_selfdestruct_in(sent_img_msg, captcha_timeout+0.5):
                    printts("[{}] sent_img_msg does not have all expected attributes. "
                            "Scheduled for deletion".format(chat_id))
                # Default user data
                new_user = \
                {
                    "chat_id": chat_id,
                    "user_id": join_user_id,
                    "user_name": join_user_name,
                    "captcha_num": captcha["number"],
                    "join_time": time(),
                    "join_retries": 1,
                    "kicked_ban": False
                }
                # Check if this user was before in the chat without solve the captcha
                prev_user_data = None
                for user in new_users_list:
                    if user["chat_id"] == new_user["chat_id"]:
                        if user["user_id"] == new_user["user_id"]:
                            prev_user_data = user
                if prev_user_data is not None:
                    # Keep join retries and remove previous user data from list
                    new_user["join_retries"] = prev_user_data["join_retries"]
                    prev_pos = new_users_list.index(prev_user_data)
                    new_users_list[prev_pos] = new_user
                else:
                    # Add new user data to lists
                    new_users_list.append(new_user)
                # Add join messages to delete
                msg = \
                {
                    "chat_id": chat_id,
                    "user_id": join_user_id,
                    "msg_id_join0": update.message,
                    "msg_id_join1": sent_img_msg.message_id,
                    "msg_id_join2": None
                }
                to_delete_join_messages_list.append(msg)
                printts("[{}] Captcha send process complete.".format(chat_id))
                printts(" ")


def msg_notext(update: Update, context: CallbackContext):
    '''All non-text messages handler.'''
    bot = context.bot
    # Check for normal or edited message
    msg = getattr(update, "message", None)
    if msg is None:
        msg = getattr(update, "edited_message", None)
    # Ignore if message comes from a private chat
    if msg.chat.type == "private":
        return
    # Ignore if message comes from a channel
    if msg.chat.type == "channel":
        return
    # Ignore if captcha protection is not enable int his chat
    captcha_enable = get_chat_config(msg.chat_id, "Enabled")
    if not captcha_enable:
        return
    # Get message data
    chat_id = msg.chat_id
    user_id = msg.from_user.id
    msg_id = msg.message_id
    # Determine configured bot language in actual chat
    lang = get_chat_config(chat_id, "Language")
    # Search if this user is a new user that has not completed the captcha yet
    i = 0
    while i < len(new_users_list):
        new_user = new_users_list[i]
        # If not the user of this message, continue to next iteration
        if new_user["user_id"] != user_id:
            i = i + 1
            continue
        # If not the chat for expected user captcha number
        if new_user["chat_id"] != chat_id:
            i = i + 1
            continue
        # Remove send message and notify that not text messages are not allowed until solve captcha
        printts("[{}] Removing non-text message sent by {}".format(chat_id, new_user["user_name"]))
        tlg_delete_msg(bot, chat_id, msg_id)
        bot_msg = TEXT[lang]["NOT_TEXT_MSG_ALLOWED"].format(new_user["user_name"])
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
        break


def msg_nocmd(update: Update, context: CallbackContext):
    '''Non-command text messages handler'''
    global to_delete_join_messages_list
    global new_users_list
    bot = context.bot
    # Check for normal or edited message
    msg = getattr(update, "message", None)
    if msg is None:
        msg = getattr(update, "edited_message", None)
    # Ignore if message comes from a private chat
    if msg.chat.type == "private":
        return
    # Ignore if message comes from a channel
    if msg.chat.type == "channel":
        return
    # Ignore if captcha protection is not enable in this chat
    captcha_enable = get_chat_config(msg.chat_id, "Enabled")
    if not captcha_enable:
        return
    # If message doesnt has text, check for caption fields (for no text msgs and resended ones)
    msg_text = getattr(msg, "text", None)
    if msg_text is None:
        msg_text = getattr(msg, "caption_html", None)
    if msg_text is None:
        msg_text = getattr(msg, "caption", None)
    # Check if message has a text link (embedded url in text) and get it
    msg_entities = getattr(msg, "entities", None)
    if msg_entities is not None:
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
    chat_id = msg.chat_id
    user_id = msg.from_user.id
    msg_id = msg.message_id
    # Get and update chat data
    chat_title = msg.chat.title
    if chat_title:
        save_config_property(chat_id, "Title", chat_title)
    chat_link = msg.chat.username
    if chat_link:
        chat_link = "@{}".format(chat_link)
        save_config_property(chat_id, "Link", chat_link)
    user_name = msg.from_user.full_name
    if msg.from_user.username is not None:
        user_name = "{}(@{})".format(user_name, msg.from_user.username)
    # Set default text message if not received
    if msg_text is None:
        msg_text = "[Not a text message]"
    # Determine configured bot language in actual chat
    lang = get_chat_config(chat_id, "Language")
    # Search if this user is a new user that has not completed the captcha yet
    i = 0
    while i < len(new_users_list):
        new_user = new_users_list[i]
        # If not the user of this message, continue to next iteration
        if new_user["user_id"] != user_id:
            i = i + 1
            continue
        # If not the chat for expected user captcha number
        if new_user["chat_id"] != chat_id:
            i = i + 1
            continue
        # Check if the expected captcha solve number is in the message
        printts("[{}] Received captcha reply from {}: {}".format(chat_id,
                new_user["user_name"], msg_text))
        if new_user["captcha_num"].lower() in msg_text.lower():
            # Remove join messages
            printts("[{}] Captcha solved by {}".format(chat_id, new_user["user_name"]))
            j = 0
            while j < len(to_delete_join_messages_list):
                msg_del = to_delete_join_messages_list[j]
                if (msg_del["user_id"] == user_id) and (msg_del["chat_id"] == chat_id):
                    # Uncomment next line to remove "user join" message too
                    #tlg_delete_msg(bot, msg_del["chat_id"], msg_del["msg_id_join0"].message_id)
                    tlg_delete_msg(bot, msg_del["chat_id"], msg_del["msg_id_join1"])
                    tlg_delete_msg(bot, msg_del["chat_id"], msg_del["msg_id_join2"])
                    list_remove_element(to_delete_join_messages_list, msg_del)
                    break
                j = j + 1
            # Remove user captcha numbers message
            tlg_delete_msg(bot, chat_id, msg.message_id)
            bot_msg = TEXT[lang]["CAPTCHA_SOLVED"].format(new_user["user_name"])
            # Set Bot to auto-remove captcha solved message too after 5mins
            tlg_send_selfdestruct_msg_in(bot, chat_id, bot_msg, 5)
            list_remove_element(new_users_list, new_user)
            # Check for custom welcome message and send it
            welcome_msg = get_chat_config(chat_id, "Welcome_Msg").format(new_user["user_name"])
            if welcome_msg != "-":
                tlg_send_selfdestruct_msg_in(bot, chat_id, welcome_msg, CONST["T_DEL_WELCOME_MSG"])
            # Check for send just text message option and apply user restrictions
            restrict_non_text_msgs = get_chat_config(chat_id, "Restrict_Non_Text")
            if restrict_non_text_msgs:
                tlg_restrict_user(bot, chat_id, user_id, send_msg=True, send_media=False, 
                    send_stickers_gifs=False, insert_links=False, send_polls=False, 
                    invite_members=False, pin_messages=False, change_group_info=False)
        # The provided message doesn't has the valid captcha number
        else:
            # Check if the message has 4 chars
            if len(msg_text) == 4:
                # Remove previously error message (if any)
                for msg_del in to_delete_join_messages_list:
                    if (msg_del["user_id"] == user_id) and (msg_del["chat_id"] == chat_id):
                        tlg_delete_msg(bot, msg_del["chat_id"], msg_del["msg_id_join2"])
                sent_msg_id = tlg_send_selfdestruct_msg(bot, chat_id,
                        TEXT[lang]["CAPTCHA_INCORRECT_0"])
                update_to_delete_join_msg_id(chat_id, user_id, "msg_id_join2", sent_msg_id)
                # Promise remove bad message data in one minute
                tlg_msg_to_selfdestruct_in(msg, 1)
            else:
                # Check if the message was just a 4 numbers msg
                if is_int(msg_text):
                    # Remove previously error message (if any)
                    for msg_del in to_delete_join_messages_list:
                        if (msg_del["user_id"] == user_id) and (msg_del["chat_id"] == chat_id):
                            tlg_delete_msg(bot, msg_del["chat_id"], msg_del["msg_id_join2"])
                    sent_msg_id = tlg_send_selfdestruct_msg(bot, chat_id,
                            TEXT[lang]["CAPTCHA_INCORRECT_1"])
                    update_to_delete_join_msg_id(chat_id, user_id, "msg_id_join2", sent_msg_id)
                    # Promise remove bad message data in one minute
                    tlg_msg_to_selfdestruct_in(msg, 1)
                else:
                    # Check if the message contains any URL
                    has_url = re.findall(CONST["REGEX_URLS"], msg_text)
                    # Check if the message contains any alias and if it is a group or channel alias
                    has_alias = False
                    #alias = ""
                    for word in msg_text.split():
                        if (len(word) > 1) and (word[0] == '@'):
                            has_alias = True
                            #alias = word
                            break
                    # Check if the detected alias is from a valid chat (commented due to getChat 
                    # request doesnt tell us if an alias is from an user, just group or channel)
                    #has_alias = False
                    #if has_alias:
                    #    chat_type = tlg_check_chat_type(bot, alias)
                    #    # A None value in chat_type is for not telegram chat found
                    #    if chat_type is not None:
                    #        has_alias = True
                    #    else:
                    #        has_alias = False
                    # Remove and notify if url/alias detection
                    if has_url or has_alias:
                        printts("[{}] Spammer detected: {}.".format(chat_id, new_user["user_name"]))
                        printts("[{}] Removing spam message: {}.".format(chat_id, msg_text))
                        # Try to remove the message and notify detection
                        rm_result = tlg_delete_msg(bot, chat_id, msg_id)
                        if rm_result == 1:
                            bot_msg = TEXT[lang]["SPAM_DETECTED_RM"].format(new_user["user_name"])
                        # Check if message cant be removed due to not delete msg privileges
                        if rm_result == -2:
                            bot_msg = TEXT[lang]["SPAM_DETECTED_NOT_RM"].format(new_user["user_name"])
                        # Get chat kick timeout and send spam detection message with autoremove
                        captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
                        tlg_send_selfdestruct_msg_in(bot, chat_id, bot_msg, captcha_timeout)
        printts("[{}] Captcha reply process complete.".format(chat_id))
        printts(" ")
        break


def button_request_captcha(update: Update, context: CallbackContext):
    '''Button "Other Captcha" pressed handler'''
    global new_users_list
    bot = context.bot
    query = update.callback_query
    # Ignore if the query come from an unexpected user
    if query.data != str(query.from_user.id):
        bot.answer_callback_query(query.id)
        return
    # Get query data
    chat_id = query.message.chat_id
    usr_id = query.from_user.id
    message_id = query.message.message_id
    chat_title = query.message.chat.title
    # Add an unicode Left to Right Mark (LRM) to chat title (fix for arabic, hebrew, etc.)
    chat_title = add_lrm(chat_title)
    # Get chat language
    lang = get_chat_config(chat_id, "Language")
    # Search if this user is a new user that has not completed the captcha
    i = 0
    while i < len(new_users_list):
        new_user = new_users_list[i]
        if (new_user["user_id"] == usr_id) and (new_user["chat_id"] == chat_id):
            printts("[{}] User {} requested a new captcha.".format(chat_id, new_user["user_name"]))
            # Prepare inline keyboard button to let user request another catcha
            keyboard = [[InlineKeyboardButton(TEXT[lang]["OTHER_CAPTCHA_BTN_TEXT"],
                    callback_data=str(query.from_user.id))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            # Get captcha timeout and set image caption
            captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
            img_caption = TEXT[lang]["NEW_USER_CAPTCHA_CAPTION"].format(new_user["user_name"],
                    chat_title, str(captcha_timeout))
            # Determine configured bot language in actual chat
            captcha_level = get_chat_config(chat_id, "Captcha_Difficulty_Level")
            captcha_chars_mode = get_chat_config(chat_id, "Captcha_Chars_Mode")
            # Generate a new captcha and edit previous captcha image message with this one
            captcha = create_image_captcha(str(usr_id), captcha_level, captcha_chars_mode)
            printts("[{}] Sending new captcha message: {}...".format(chat_id, captcha["number"]))
            bot.edit_message_media(chat_id, message_id, media=InputMediaPhoto(
                    media=open(captcha["image"], "rb"), caption=img_caption),
                    reply_markup=reply_markup, timeout=20)
            # Set and modified to new expected captcha number
            new_user["captcha_num"] = captcha["number"]
            new_users_list[i] = new_user
            # Remove sent captcha image file from file system
            if path.exists(captcha["image"]):
                remove(captcha["image"])
            break
        i = i + 1
    printts("[{}] New captcha request process complete.".format(chat_id))
    printts(" ")
    bot.answer_callback_query(query.id)

####################################################################################################

### Received Telegram command messages handlers ###

def cmd_start(update: Update, context: CallbackContext):
    '''Command /start message handler'''
    bot = context.bot
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    if chat_type == "private":
        bot.send_message(chat_id, TEXT[lang]["START"])
    else:
        tlg_msg_to_selfdestruct(update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["START"])


def cmd_help(update: Update, context: CallbackContext):
    '''Command /help message handler'''
    bot = context.bot
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    bot_msg = TEXT[lang]["HELP"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_commands(update: Update, context: CallbackContext):
    '''Command /commands message handler'''
    bot = context.bot
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    commands_text = TEXT[lang]["COMMANDS"]
    if chat_type == "private":
        bot.send_message(chat_id, commands_text)
    else:
        tlg_msg_to_selfdestruct(update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, commands_text)


def cmd_language(update: Update, context: CallbackContext):
    '''Command /language message handler'''
    bot = context.bot
    args = context.args
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    # Check and deny usage in private chat
    if chat_type == "private":
        bot.send_message(chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
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
        bot_msg = TEXT[lang]["LANG_NOT_ARG"].format(CONST["SUPPORTED_LANGS_CMDS"])
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
        return
    # Get and configure chat to provided language
    lang_provided = args[0].upper()
    if lang_provided in TEXT:
        if lang_provided != lang:
            lang = lang_provided
            save_config_property(chat_id, "Language", lang)
            bot_msg = TEXT[lang]["LANG_CHANGE"]
        else:
            bot_msg = TEXT[lang]["LANG_SAME"].format(CONST["SUPPORTED_LANGS_CMDS"])
    else:
        bot_msg = TEXT[lang]["LANG_BAD_LANG"].format(CONST["SUPPORTED_LANGS_CMDS"])
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_time(update: Update, context: CallbackContext):
    '''Command /time message handler'''
    bot = context.bot
    args = context.args
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    # Check and deny usage in private chat
    if chat_type == "private":
        bot.send_message(chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
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
        if new_time <= 120:
            save_config_property(chat_id, "Captcha_Time", new_time)
            bot_msg = TEXT[lang]["TIME_CHANGE"].format(new_time)
        else:
            bot_msg = TEXT[lang]["TIME_MAX_NOT_ALLOW"]
    else:
        bot_msg = TEXT[lang]["TIME_NOT_NUM"]
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_difficulty(update: Update, context: CallbackContext):
    '''Command /difficulty message handler'''
    bot = context.bot
    args = context.args
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    # Check and deny usage in private chat
    if chat_type == "private":
        bot.send_message(chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
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
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    # Check and deny usage in private chat
    if chat_type == "private":
        bot.send_message(chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
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
    if (new_captcha_mode == "nums") or (new_captcha_mode == "hex") or (new_captcha_mode == "ascii"):
        save_config_property(chat_id, "Captcha_Chars_Mode", new_captcha_mode)
        bot_msg = TEXT[lang]["CAPTCHA_MODE_CHANGE"].format(new_captcha_mode)
    else:
        bot_msg = TEXT[lang]["CAPTCHA_MODE_INVALID"]
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_welcome_msg(update: Update, context: CallbackContext):
    '''Command /welcome_msg message handler'''
    bot = context.bot
    args = context.args
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    # Check and deny usage in private chat
    if chat_type == "private":
        bot.send_message(chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
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
    # Get and configure chat to provided welcome message
    welcome_msg = " ".join(args)
    welcome_msg = welcome_msg.replace("$user", "{0}")
    welcome_msg = welcome_msg[:CONST["MAX_WELCOME_MSG_LENGTH"]]
    if welcome_msg == "disable":
        welcome_msg = '-'
        bot_msg = TEXT[lang]["WELCOME_MSG_UNSET"]
    else:
        bot_msg = TEXT[lang]["WELCOME_MSG_SET"]
    save_config_property(chat_id, "Welcome_Msg", welcome_msg)
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_restrict_non_text(update: Update, context: CallbackContext):
    '''Command /restrict_non_text message handler'''
    bot = context.bot
    args = context.args
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    # Check and deny usage in private chat
    if chat_type == "private":
        bot.send_message(chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
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
    # Enable/Disable just text messages option
    if restrict_non_text_msgs == "enable":
        save_config_property(chat_id, "Restrict_Non_Text", True)
        bot_msg = TEXT[lang]["RESTRICT_NON_TEXT_MSG_ENABLED"]
    else:
        save_config_property(chat_id, "Restrict_Non_Text", False)
        bot_msg = TEXT[lang]["RESTRICT_NON_TEXT_MSG_DISABLED"]
    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_add_ignore(update: Update, context: CallbackContext):
    '''Command /add_ignore message handler'''
    bot = context.bot
    args = context.args
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    # Check and deny usage in private chat
    if chat_type == "private":
        bot.send_message(chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
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
    if is_valid_user_id_or_alias(user_id_alias):
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
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    # Check and deny usage in private chat
    if chat_type == "private":
        bot.send_message(chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
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
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    # Check and deny usage in private chat
    if chat_type == "private":
        bot.send_message(chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
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


def cmd_enable(update: Update, context: CallbackContext):
    '''Command /enable message handler'''
    bot = context.bot
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    # Check and deny usage in private chat
    if chat_type == "private":
        bot.send_message(chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
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
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    # Check and deny usage in private chat
    if chat_type == "private":
        bot.send_message(chat_id, CONST["CMD_NOT_ALLOW_PRIVATE"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
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


def cmd_version(update: Update, context: CallbackContext):
    '''Command /version message handler'''
    bot = context.bot
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    bot_msg = TEXT[lang]["VERSION"].format(CONST["VERSION"])
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_about(update: Update, context: CallbackContext):
    '''Command /about handler'''
    bot = context.bot
    chat_id = update.message.chat_id
    lang = get_chat_config(chat_id, "Language")
    bot_msg = TEXT[lang]["ABOUT_MSG"].format(CONST["DEVELOPER"], CONST["REPOSITORY"],
        CONST["DEV_PAYPAL"], CONST["DEV_BTC"])
    bot.send_message(chat_id, bot_msg)


def cmd_captcha(update: Update, context: CallbackContext):
    '''Command /captcha message handler. Usefull to test. Just Bot Owner can use it.'''
    bot = context.bot
    chat_id = update.message.chat_id
    user = update.message.from_user
    user_id = user.id
    user_alias = ""
    if user.username is not None:
        user_alias = "@{}".format(user.username)
    # Check if command was execute by Bot owner
    if (user_id != CONST["BOT_OWNER"]) and (user_alias != CONST["BOT_OWNER"]):
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
    # Generate a random difficulty captcha
    captcha_level = randint(1, 5)
    captcha_chars_mode = randint(1, 3)
    if captcha_chars_mode == 2:
        captcha_chars_mode = "hex"
    elif captcha_chars_mode == 3:
        captcha_chars_mode = "ascii"
    else:
        captcha_chars_mode = "nums"
    captcha = create_image_captcha(str(user_id), captcha_level, captcha_chars_mode)
    printts("[{}] Sending captcha message: {}...".format(chat_id, captcha["number"]))
    img_caption = "Captcha Level: {}\nCaptcha Mode: {}\nCaptcha Code: {}".format(captcha_level,
            captcha_chars_mode, captcha["number"])
    try:
        # Note: Img caption must be <= 1024 chars
        sent_img_msg = bot.send_photo(chat_id=chat_id, photo=open(captcha["image"],"rb"),
                caption=img_caption, timeout=20)
        tlg_msg_to_selfdestruct_in(sent_img_msg, 1)
    except Exception as e:
        printts("[{}] {}".format(chat_id, str(e)))


def cmd_whitelist(update: Update, context: CallbackContext):
    '''Command /whitelist message handler. To Global Whitelist blind users.
    Just Bot Owner can use it.'''
    bot = context.bot
    args = context.args
    chat_id = update.message.chat_id
    user = update.message.from_user
    user_id = user.id
    user_alias = ""
    if user.username is not None:
        user_alias = "@{}".format(user.username)
    # Check if command was execute by Bot owner
    if (user_id != CONST["BOT_OWNER"]) and (user_alias != CONST["BOT_OWNER"]):
        bot.send_message(chat_id, CONST["CMD_JUST_ALLOW_OWNER"])
        return
    # Set user command message to be deleted by Bot in default time
    tlg_msg_to_selfdestruct(update.message)
    # Check if no argument was provided with the command
    if len(args) == 0:
        # Show Actual Global Whitelisted Users
        l_white_users = file_read(CONST["F_WHITE_LIST"])
        bot_msg = "\n".join([str(user) for user in l_white_users])
        bot_msg = "Global WhiteList:\n--------------------\n{}".format(bot_msg)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
        return
    else:
        if len(args) <= 1:
            tlg_send_selfdestruct_msg(bot, chat_id, CONST["WHITELIST_USAGE"])
            return
        if (args[0] != "add") and (args[0] != "rm"):
            tlg_send_selfdestruct_msg(bot, chat_id, CONST["WHITELIST_USAGE"])
            return
        add_rm = args[0]
        user = args[1]
        l_white_users = file_read(CONST["F_WHITE_LIST"])
        if add_rm == "add":
            if not is_valid_user_id_or_alias(user):
                tlg_send_selfdestruct_msg(bot, chat_id, "Invalid User ID/Alias.")
                return
            if user not in l_white_users:
                file_write(CONST["F_WHITE_LIST"], "{}\n".format(user))
                tlg_send_selfdestruct_msg(bot, chat_id, "User added to Global Whitelist.")
            else:
                tlg_send_selfdestruct_msg(bot, chat_id, "The User is already in Global Whitelist.")
            return
        if add_rm == "rm":
            if list_remove_element(l_white_users, user):
                file_write(CONST["F_WHITE_LIST"], l_white_users, "w")
                tlg_send_selfdestruct_msg(bot, chat_id, "User removed from Global Whitelist.")
            else:
                tlg_send_selfdestruct_msg(bot, chat_id, "The User is not in Global Whitelist.")

####################################################################################################

### Main Loop Functions ###

def handle_remove_and_kicks(bot):
    '''Handle remove of sent messages and not verify new users ban'''
    while True:
        # Handle self-messages delete
        selfdestruct_messages(bot)
        # Check time for ban new users that has not completed the captcha
        check_time_to_kick_not_verify_users(bot)
        # Wait 10s (release CPU usage)
        sleep(10)


def selfdestruct_messages(bot):
    '''Handle remove messages sent by the Bot with the timed self-delete function'''
    global to_delete_in_time_messages_list
    # Check each Bot sent message
    i = 0
    while i < len(to_delete_in_time_messages_list):
        sent_msg = to_delete_in_time_messages_list[i]
        # If actual time is equal or more than the expected sent msg delete time
        if time() >= sent_msg["delete_time"]:
            printts("[{}] Scheduled deletion time for message: {}".format(
                    sent_msg["Chat_id"], sent_msg["Msg_id"]))
            try:
                if bot.delete_message(sent_msg["Chat_id"], sent_msg["Msg_id"]):
                    list_remove_element(to_delete_in_time_messages_list, sent_msg)
            except Exception as e:
                printts("[{}] {}".format(sent_msg["Chat_id"], str(e)))
                # The bot has no privileges to delete messages
                if str(e) == "Message can't be deleted":
                    lang = get_chat_config(sent_msg["Chat_id"], "Language")
                    try:
                        cant_del_msg = bot.send_message(sent_msg["Chat_id"],
                                TEXT[lang]["CANT_DEL_MSG"], reply_to_message_id=sent_msg["Msg_id"])
                        tlg_msg_to_selfdestruct(cant_del_msg)
                    except Exception as ee:
                        printts(str(e))
                        printts(str(ee))
                        pass
                list_remove_element(to_delete_in_time_messages_list, sent_msg)
        i = i + 1


def check_time_to_kick_not_verify_users(bot):
    '''Check if the time for ban new users that has not completed the captcha has arrived'''
    global to_delete_join_messages_list
    global new_users_list
    i = 0
    while i < len(new_users_list):
        new_user = new_users_list[i]
        captcha_timeout = get_chat_config(new_user["chat_id"], "Captcha_Time")
        if new_user["kicked_ban"]:
            # Remove from new users list the remaining kicked users that have not solve the captcha 
            # in 1 hour (user ban just happen if a user try to join the group and fail to solve the 
            # captcha 5 times in the past hour)
            if time() >= (new_user["join_time"] + captcha_timeout*60) + 3600:
                # Remove user from new users list
                list_remove_element(new_users_list, new_user)
        else:
            # If time for kick/ban has not arrived yet
            if time() < new_user["join_time"] + captcha_timeout*60:
                i = i + 1
                continue
            # The time has come for this user
            chat_id = new_user["chat_id"]
            lang = get_chat_config(chat_id, "Language")
            printts("[{}] Captcha reply timed out for user {}.".format(chat_id, new_user["user_name"]))
            # Check if this "user" has not join this chat more than 5 times (just kick)
            if new_user["join_retries"] < 5:
                printts("[{}] Captcha not solved, kicking {} ({})...".format(chat_id,
                        new_user["user_name"], new_user["user_id"]))
                # Try to kick the user
                kick_result = tlg_kick_user(bot, new_user["chat_id"], new_user["user_id"])
                if kick_result == 1:
                    # Kick success
                    bot_msg = TEXT[lang]["NEW_USER_KICK"].format(new_user["user_name"])
                    # Increase join retries
                    new_user["join_retries"] = new_user["join_retries"] + 1
                    printts("[{}] Increased join_retries to {}".format(chat_id,
                            new_user["join_retries"]))
                    # Set to auto-remove the kick message too, after a while
                    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
                else:
                    # Kick fail
                    printts("[{}] Unable to kick".format(chat_id))
                    if kick_result == -1:
                        # The user is not in the chat
                        bot_msg = TEXT[lang]['NEW_USER_KICK_NOT_IN_CHAT'].format(
                                new_user["user_name"])
                        # Set to auto-remove the kick message too, after a while
                        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
                    elif kick_result == -2:
                        # Bot has no privileges to ban
                        bot_msg = TEXT[lang]['NEW_USER_KICK_NOT_RIGHTS'].format(
                                new_user["user_name"])
                        # Send no rights for kick message without auto-remove
                        try:
                            bot.send_message(chat_id, bot_msg)
                        except Exception as e:
                            printts("[{}] {}".format(chat_id, str(e)))
                    else:
                        # For other reason, the Bot can't ban
                        bot_msg = TEXT[lang]['BOT_CANT_KICK'].format(new_user["user_name"])
                        # Set to auto-remove the kick message too, after a while
                        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
            # The user has join this chat 5 times and never succes to solve the captcha (ban)
            else:
                printts("[{}] Captcha not solved, banning {} ({})...".format(chat_id,
                        new_user["user_name"], new_user["user_id"]))
                # Try to ban the user and notify Admins
                ban_result = tlg_ban_user(bot, chat_id, new_user["user_id"])
                # Remove user from new users list
                list_remove_element(new_users_list, new_user)
                if ban_result == 1:
                    # Ban success
                    bot_msg = TEXT[lang]["NEW_USER_BAN"].format(new_user["user_name"])
                else:
                    # Ban fail
                    if ban_result == -1:
                        # The user is not in the chat
                        bot_msg = TEXT[lang]['NEW_USER_BAN_NOT_IN_CHAT'].format(
                                new_user["user_name"])
                    elif ban_result == -2:
                        # Bot has no privileges to ban
                        bot_msg = TEXT[lang]['NEW_USER_BAN_NOT_RIGHTS'].format(
                                new_user["user_name"])
                    else:
                        # For other reason, the Bot can't ban
                        bot_msg = TEXT[lang]['BOT_CANT_BAN'].format(new_user["user_name"])
                # Send ban notify message
                printts("[{}] {}".format(chat_id, bot_msg))
                try:
                    bot.send_message(chat_id, bot_msg)
                except Exception as e:
                    printts("[{}] {}".format(chat_id, str(e)))
            # Update user info (join_retries & kick_ban)
            new_user["kicked_ban"] = True
            if new_user in new_users_list:
                pos = new_users_list.index(new_user)
                new_users_list[pos] = new_user
            # Remove join messages
            printts("[{}] Removing messages from user {}...".format(chat_id, new_user["user_name"]))
            j = 0
            while j < len(to_delete_join_messages_list):
                msg = to_delete_join_messages_list[j]
                if msg["user_id"] == new_user["user_id"]:
                    if msg["chat_id"] == new_user["chat_id"]:
                        # Uncomment next line to remove "user join" message too
                        #tlg_delete_msg(bot, msg["chat_id"], msg["msg_id_join0"].message_id)
                        tlg_delete_msg(bot, msg["chat_id"], msg["msg_id_join1"])
                        tlg_delete_msg(bot, msg["chat_id"], msg["msg_id_join2"])
                        tlg_msg_to_selfdestruct(msg["msg_id_join0"])
                        list_remove_element(to_delete_join_messages_list, msg)
                        break
                j = j + 1
            printts("[{}] Kick/Ban process complete".format(chat_id))
            printts(" ")
        i = i + 1

####################################################################################################

### Main Function ###

def main():
    '''Main Function'''
    global updater
    # Check if Bot Token has been set or has default value
    if CONST["TOKEN"] == "XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX":
        printts("Error: Bot Token has not been set.")
        printts("Please add your Bot Token to constants.py file.")
        printts("Exit.\n")
        exit(0)
    printts("Bot started.")
    # Initialize resources by populating files list and configs with chats found files
    initialize_resources()
    printts("Resources initialized.")
    # Set messages to be sent silently by default
    msgs_defaults = Defaults(disable_notification=True)
    # Create an event handler (updater) for a Bot with the given Token and get the dispatcher
    updater = Updater(CONST["TOKEN"], use_context=True, defaults=msgs_defaults)
    dp = updater.dispatcher
    # Set to dispatcher all expected commands messages handler
    dp.add_handler(CommandHandler("start", cmd_start))
    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("commands", cmd_commands))
    dp.add_handler(CommandHandler("language", cmd_language, pass_args=True))
    dp.add_handler(CommandHandler("time", cmd_time, pass_args=True))
    dp.add_handler(CommandHandler("difficulty", cmd_difficulty, pass_args=True))
    dp.add_handler(CommandHandler("captcha_mode", cmd_captcha_mode, pass_args=True))
    dp.add_handler(CommandHandler("welcome_msg", cmd_welcome_msg, pass_args=True))
    dp.add_handler(CommandHandler("restrict_non_text", cmd_restrict_non_text, pass_args=True))
    dp.add_handler(CommandHandler("add_ignore", cmd_add_ignore, pass_args=True))
    dp.add_handler(CommandHandler("remove_ignore", cmd_remove_ignore, pass_args=True))
    dp.add_handler(CommandHandler("ignore_list", cmd_ignore_list))
    dp.add_handler(CommandHandler("enable", cmd_enable))
    dp.add_handler(CommandHandler("disable", cmd_disable))
    dp.add_handler(CommandHandler("version", cmd_version))
    dp.add_handler(CommandHandler("about", cmd_about))
    dp.add_handler(CommandHandler("whitelist", cmd_whitelist, pass_args=True))
    dp.add_handler(CommandHandler("captcha", cmd_captcha))
    # Set to dispatcher a not-command text messages handler
    dp.add_handler(MessageHandler(Filters.text, msg_nocmd))
    # Set to dispatcher not text messages handler
    dp.add_handler(MessageHandler(Filters.photo | Filters.audio | Filters.voice |
            Filters.video | Filters.sticker | Filters.document | Filters.location |
            Filters.contact, msg_notext))
    # Set to dispatcher a new member join the group and member left the group events handlers
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, msg_new_user))
    # Set to dispatcher request new captcha button callback handler
    dp.add_handler(CallbackQueryHandler(button_request_captcha))
    # Launch the Bot ignoring pending messages (clean=True) and get all updates (cllowed_uptades=[])
    updater.start_polling(clean=True, allowed_updates=[])
    printts("Bot setup completed. Bot is now running.")
    # Handle remove of sent messages and not verify new users ban (main loop)
    handle_remove_and_kicks(updater.bot)


if __name__ == "__main__":
    main()

### End Of Code ###
