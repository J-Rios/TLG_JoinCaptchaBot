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
    12/04/2019
Version:
    1.2.0
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
from telegram import MessageEntity, ParseMode, InputMediaPhoto,  InlineKeyboardButton, \
                     InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, \
                         ConversationHandler, CallbackQueryHandler
from random import randint

from constants import CONST, TEXT
from tsjson import TSjson
from img_captcha_gen import CaptchaGenerator

####################################################################################################

### Globals ###
files_config_list = []
to_delete_in_time_messages_list = []
to_delete_join_messages_list = []
new_users_list = []

# Create Captcha Generator object of specified size (2 -> 640x360)
CaptchaGen = CaptchaGenerator(2)

####################################################################################################

### Termination signals handler for program process ###
def signal_handler(signal, frame):
    '''Termination signals (SIGINT, SIGTERM) handler for program process'''
    # Acquire all messages and users files mutex to ensure not read/write operation on them
    for chat_config_file in files_config_list:
        chat_config_file["File"].lock.acquire()
    # Close the program
    exit(0)


### Signals attachment ###
signal(SIGTERM, signal_handler) # SIGTERM (kill pid) to signal_handler
signal(SIGINT, signal_handler)  # SIGINT (Ctrl+C) to signal_handler

####################################################################################################

### General functions ###

def initialize_resources():
    '''Initialize resources by populating files list with chats found files'''
    global files_config_list
    # Remove old captcha directory and create it again
    if path.exists(CONST["CAPTCHAS_DIR"]):
        rmtree(CONST["CAPTCHAS_DIR"])
    makedirs(CONST["CAPTCHAS_DIR"])
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
                files_config_list.append(OrderedDict([("ID", f_chat_id), \
                    ("File", TSjson(file_path))]))
                # Create default configuration file if it does not exists
                if not path.exists(file_path):
                    default_conf = get_default_config_data()
                    for key, value in default_conf.items():
                        save_config_property(f_chat_id, key, value)
    # Load and generate URL detector regex from TLD list file
    load_urls_regex(CONST["F_TLDS"])


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
        printts("Error when opening file \"{}\". {}".format(file_path, str(e)))
    if len(list_file_lines) > 0:
        tlds_str = "".join(list_file_lines)
    CONST["REGEX_URLS"] = CONST["REGEX_URLS"].format(tlds_str)


def create_image_captcha(img_file_name):
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
    captcha = CaptchaGen.gen_captcha_image(multicolor=bool(randint(0, 1)))
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
        if msg["user_id"] == msg_user_id:
            if msg["chat_id"] == msg_chat_id:
                msg[message_id_key] = new_msg_id_value
                to_delete_join_messages_list.remove(msg)
                to_delete_join_messages_list.append(msg)
                break
        i = i + 1


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

####################################################################################################

### JSON chat config file functions ###

def get_default_config_data():
    '''Get default config data structure'''
    config_data = OrderedDict( \
    [ \
        ("Title", CONST["INIT_TITLE"]), \
        ("Link", CONST["INIT_LINK"]), \
        ("Enabled", CONST["INIT_ENABLE"]), \
        ("Captcha_Time", CONST["INIT_CAPTCHA_TIME_MIN"]), \
        ("Language", CONST["INIT_LANG"]) \
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
        if not config_data:
            config_data = get_default_config_data()
    else:
        config_data = get_default_config_data()
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
    except:
        return None
    for admin in group_admins:
        if user_id == admin.user.id:
            return True
    return False


def tlg_get_bot_admin_privileges(bot, chat_id):
    '''Get the actual Bot administration privileges'''
    try:
        bot_data = bot.get_me()
    except:
        return None
    bot_admin_privileges = OrderedDict( \
    [ \
        ("can_change_info", bot_data.can_change_info), \
        ("can_delete_messages", bot_data.can_delete_messages), \
        ("can_restrict_members", bot_data.can_restrict_members), \
        ("can_invite_users", bot_data.can_invite_users), \
        ("can_pin_messages", bot_data.can_pin_messages), \
        ("can_promote_members", bot_data.can_promote_members) \
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
        tlg_msg_to_selfdestruct(sent_msg)
        sent_msg_id = sent_msg["message_id"]
    # It has been an unsuccesfull sent
    except Exception as e:
        printts("[{}] - {}".format(chat_id, str(e)))
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
    sent_msg_data = OrderedDict([("Chat_id", None), ("User_id", None), \
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
            printts("[{}] - {}".format(chat_id, str(e)))
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
        printts("[{}] - {}".format(chat_id, str(e)))
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
        printts("[{}] - {}".format(chat_id, str(e)))
        if str(e) == "Not enough rights to restrict/unrestrict chat member":
            return_code = -2
        elif str(e) == "User is an administrator of the chat":
            return_code = -3
    return return_code

####################################################################################################

### Received Telegram not-command messages handlers ###

def msg_new_user(bot, update):
    '''New member join the group event handler'''
    global to_delete_join_messages_list
    global new_users_list
    # Get message data
    chat_id = update.message.chat_id
    # Determine configured bot language in actual chat
    lang = get_chat_config(chat_id, "Language")
    # For each new user that join or has been added
    for join_user in update.message.new_chat_members:
        join_user_id = join_user.id
        # Get user name
        if join_user.name != None:
            join_user_name = join_user.name
        else:
            join_user_name = join_user.full_name
        # If the user name is too long, truncate it to 35 characters
        if len(join_user_name) > 35:
            join_user_name = join_user_name[0:35]
        # If the added user is myself (this Bot)
        if bot.id == join_user_id:
            # Get the language of the Telegram client software the Admin that has added the Bot 
            # has, to assume this is the chat language and configure Bot language of this chat
            admin_language = update.message.from_user.language_code[0:2].upper()
            if admin_language not in TEXT:
                admin_language = "EN"
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
                printts("[{}] - {}".format(chat_id, str(e)))
                pass
        # The added user is not myself (this Bot)
        else:
            printts(" ")
            printts("[{}] - A new user has join the group: {} ({})".format(chat_id, join_user_name, \
                                                                         join_user_id))
            # Get and update chat data
            chat_title = update.message.chat.title
            if chat_title:
                save_config_property(chat_id, "Title", chat_title)
            chat_link = update.message.chat.username
            if chat_link:
                chat_link = "@{}".format(chat_link)
                save_config_property(chat_id, "Link", chat_link)
            # Ignore Admins
            if tlg_user_is_admin(bot, join_user_id, chat_id) != True:
                # Check and remove previous join messages of that user (if any)
                i = 0
                while i < len(to_delete_join_messages_list):
                    msg = to_delete_join_messages_list[i]
                    if msg["user_id"] == join_user_id:
                        if msg["chat_id"] == chat_id:
                            tlg_delete_msg(bot, msg["chat_id"], msg["msg_id_join0"].message_id)
                            tlg_delete_msg(bot, msg["chat_id"], msg["msg_id_join1"])
                            tlg_delete_msg(bot, msg["chat_id"], msg["msg_id_join2"])
                            to_delete_join_messages_list.remove(msg)
                    i = i + 1
                # If the captcha protection is enabled
                captcha_enable = get_chat_config(chat_id, "Enabled")
                if captcha_enable:
                    # If the member that has been join the group is not a Bot
                    if not join_user.is_bot:
                        # Generate a pseudorandom captcha send it to telegram group and program 
                        # message selfdestruct
                        captcha = create_image_captcha(str(join_user_id))
                        captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
                        img_caption = TEXT[lang]["NEW_USER_CAPTCHA_CAPTION"].format(join_user_name,\
                                                                             chat_title, \
                                                                             str(captcha_timeout))
                        # Prepare inline keyboard button to let user request another catcha
                        keyboard = [[InlineKeyboardButton(TEXT[lang]["OTHER_CAPTCHA_BTN_TEXT"], \
                                                          callback_data=join_user_id)]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        send_problem = False
                        printts("[{}] - Sending captcha message...".format(chat_id))
                        try:
                            # Note: Img caption must be <= 1024 chars
                            sent_img_msg = bot.send_photo(chat_id=chat_id, photo=open( \
                                                          captcha["image"],"rb"), \
                                                          reply_markup=reply_markup, \
                                                          caption=img_caption, timeout=20)
                            printts("[{}] - OK".format(chat_id))
                        except Exception as e:
                            printts("[{}] - {}".format(chat_id, str(e)))
                            if str(e) != "Timed out":
                                send_problem = True
                            else:
                                printts("sent_img_msg: {}".format(sent_img_msg))
                        # Remove sent captcha image file from file system
                        if path.exists(captcha["image"]):
                            remove(captcha["image"])
                        if not send_problem:
                            # Add sent image to self-destruct list
                            printts("[{}] - Adding captcha message to self-destruct..." \
                                  .format(chat_id))
                            if not tlg_msg_to_selfdestruct_in(sent_img_msg, captcha_timeout+0.5):
                                printts("[{}] - sent_img_msg has not all the expected attributtes " \
                                      "to be deleted".format(chat_id))
                            else:
                                printts("[{}] - OK".format(chat_id))
                            # Default user data
                            new_user = \
                            {
                                "chat_id": chat_id,
                                "user_id" : join_user_id,
                                "user_name": join_user_name,
                                "captcha_num" : captcha["number"],
                                "join_time" : time(),
                                "join_retries" : 1,
                                "kicked_ban" : False
                            }
                            # Check if this user was before in the chat without solve the captcha
                            prev_user_data = None
                            for user in new_users_list:
                                if user["chat_id"] == new_user["chat_id"]:
                                    if user["user_id"] == new_user["user_id"]:
                                        prev_user_data = user
                            if prev_user_data is not None:
                                # Increase join retries and remove previous user data from list
                                new_user["join_retries"] = prev_user_data["join_retries"] + 1
                                printts("[{}] - User was kicked before. Increasing join retries..." \
                                      .format(chat_id))
                                printts("[{}] - Actual join retries {}".format(chat_id, \
                                      new_user["join_retries"]))
                                new_users_list.remove(prev_user_data)
                            # Add new user data to lists
                            printts("[{}] - Adding user to new users list...".format(chat_id))
                            new_users_list.append(new_user)
                            printts("[{}] - OK".format(chat_id))
                            printts("[{}] - Adding join messages to messages delete list..." \
                                  .format(chat_id))
                            # Add join messages to delete
                            msg = \
                            {
                                "chat_id": chat_id,
                                "user_id" : join_user_id,
                                "msg_id_join0": update.message,
                                "msg_id_join1": sent_img_msg.message_id,
                                "msg_id_join2" : None
                            }
                            to_delete_join_messages_list.append(msg)
                            printts("[{}] - OK".format(chat_id))
                            printts(" ")


def msg_nocmd(bot, update):
    '''All Not-command messages handler'''
    global to_delete_join_messages_list
    global new_users_list
    # Get message data
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    user_id = update.message.from_user.id
    msg_text = update.message.text
    msg_id = update.message.message_id
    # Verify if we are in a group
    if chat_type != "private":
        # Get and update chat data
        chat_title = update.message.chat.title
        if chat_title:
            save_config_property(chat_id, "Title", chat_title)
        chat_link = update.message.chat.username
        if chat_link:
            chat_link = "@{}".format(chat_link)
            save_config_property(chat_id, "Link", chat_link)
        user_name = update.message.from_user.full_name
        if update.message.from_user.username != None:
            user_name = "{}(@{})".format(user_name, update.message.from_user.username)
        if msg_text is None:
            msg_text = "[Not a text message]"
        # Check if captcha protection is enabled
        captcha_enable = get_chat_config(chat_id, "Enabled")
        if captcha_enable:
            # Determine configured bot language in actual chat
            lang = get_chat_config(chat_id, "Language")
            # Search if this user is a new user that has not completed the captcha
            i = 0
            while i < len(new_users_list):
                new_user = new_users_list[i]
                if new_user["user_id"] == user_id:
                    # Check if the expected captcha solve number is in the message
                    if new_user["captcha_num"] in msg_text:
                        # Remove join messages
                        printts(" ")
                        printts("[{}] - Captcha solved by {}".format(chat_id, \
                              new_user["user_name"]))
                        printts("[{}] - Removing messages...".format(chat_id))
                        j = 0
                        while j < len(to_delete_join_messages_list):
                            msg = to_delete_join_messages_list[j]
                            if msg["user_id"] == user_id:
                                if msg["chat_id"] == chat_id:
                                    # Uncomment next line to remove "user join" message too
                                    #tlg_delete_msg(bot, msg["chat_id"], \
                                    #               msg["msg_id_join0"].message_id)
                                    tlg_delete_msg(bot, msg["chat_id"], msg["msg_id_join1"])
                                    tlg_delete_msg(bot, msg["chat_id"], msg["msg_id_join2"])
                                    to_delete_join_messages_list.remove(msg)
                                    break
                            j = j + 1
                        # Remove user captcha numbers message
                        tlg_delete_msg(bot, chat_id, update.message.message_id)
                        printts("[{}] - OK".format(chat_id))
                        # Send captcha solved message and program selfdestruct in 5 minutes
                        bot_msg = TEXT[lang]["CAPTHA_SOLVED"].format(new_user["user_name"])
                        # Uncomment and use next first line instead the second, if we want Bot to 
                        # auto-remove the kick message too after a while
                        #tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
                        bot.send_message(chat_id, bot_msg)
                        new_users_list.remove(new_user)
                    # The provided message doesn't has the valid captcha number
                    else:
                        # Check if the message was just a 4 numbers msg
                        if is_int(msg_text):
                            # Remove previously error message (if any)
                            for msg in to_delete_join_messages_list:
                                if msg["user_id"] == user_id:
                                    if msg["chat_id"] == chat_id:
                                        tlg_delete_msg(bot, msg["chat_id"], msg["msg_id_join2"])
                            # Check if the message has 4 digits
                            if len(msg_text) == 4:
                                sent_msg_id = tlg_send_selfdestruct_msg(bot, chat_id, \
                                                          TEXT[lang]["CAPTCHA_INCORRECT_0"])
                                update_to_delete_join_msg_id(chat_id, user_id, "msg_id_join2", \
                                                             sent_msg_id)
                            else:
                                sent_msg_id = tlg_send_selfdestruct_msg(bot, chat_id, \
                                                          TEXT[lang]["CAPTCHA_INCORRECT_1"])
                                update_to_delete_join_msg_id(chat_id, user_id, "msg_id_join2", \
                                                             sent_msg_id)
                        else:
                            # Check if the message contains any URL
                            has_url = re.findall(CONST["REGEX_URLS"], msg_text)
                            if has_url:
                                printts("[{}] - Spammer detected: {}.".format(chat_id, \
                                        new_user["user_name"]))
                                printts("[{}] - Removing spam message: {}.".format(chat_id, \
                                        msg_text))
                                # Try to remove the message and notify detection
                                rm_result = tlg_delete_msg(bot, chat_id, msg_id)
                                if rm_result == 1:
                                    bot_msg = TEXT[lang]["SPAM_DETECTED_RM"].format( \
                                              new_user["user_name"])
                                # Check if message cant be removed due to not delete msg privileges
                                if rm_result == -2:
                                    bot_msg = TEXT[lang]["SPAM_DETECTED_NOT_RM"].format( \
                                              new_user["user_name"])
                                tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
                    break
                i = i + 1


def button_request_captcha(bot, update):
    '''Button "Other Captcha" pressed handler'''
    global new_users_list
    query = update.callback_query
    # If the query come from the expected user (the query data is the user ID of )
    if query.data == str(query.from_user.id):
        # Get query data
        chat_id = query.message.chat_id
        usr_id = query.from_user.id
        message_id = query.message.message_id
        chat_title = query.message.chat.title
        # Get chat language
        lang = get_chat_config(chat_id, "Language")
        # Search if this user is a new user that has not completed the captcha
        i = 0
        while i < len(new_users_list):
            new_user = new_users_list[i]
            if new_user["user_id"] == usr_id:
                if new_user["chat_id"] == chat_id:
                    # Prepare inline keyboard button to let user request another catcha
                    keyboard = [[InlineKeyboardButton(TEXT[lang]["OTHER_CAPTCHA_BTN_TEXT"], \
                                 callback_data=str(query.from_user.id))]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    # Get captcha timeout and set image caption
                    captcha_timeout = get_chat_config(chat_id, "Captcha_Time")
                    img_caption = TEXT[lang]["NEW_USER_CAPTCHA_CAPTION"].format( \
                                        new_user["user_name"], chat_title, str(captcha_timeout))
                    # Generate a new captcha and edit previous captcha image message with this one
                    captcha = create_image_captcha(str(usr_id))
                    bot.edit_message_media(chat_id, message_id, media=InputMediaPhoto( \
                                           media=open(captcha["image"], "rb"), \
                                           caption=img_caption), reply_markup=reply_markup, \
                                           timeout=20)
                    # Set and modified to new expected captcha number
                    new_user["captcha_num"] = captcha["number"]
                    new_users_list[i] = new_user
                    # Remove sent captcha image file from file system
                    if path.exists(captcha["image"]):
                        remove(captcha["image"])
                    break
            i = i + 1
    bot.answer_callback_query(query.id)

####################################################################################################

### Received Telegram command messages handlers ###

def cmd_start(bot, update):
    '''Command /start message handler'''
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    if chat_type == "private":
        bot.send_message(chat_id, TEXT[lang]["START"])
    else:
        tlg_msg_to_selfdestruct(update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["START"])


def cmd_help(bot, update):
    '''Command /help message handler'''
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    bot_msg = TEXT[lang]["HELP"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_commands(bot, update):
    '''Command /commands message handler'''
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    if chat_type == "private":
        bot.send_message(chat_id, TEXT[lang]["COMMANDS"])
    else:
        tlg_msg_to_selfdestruct(update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, TEXT[lang]["COMMANDS"])


def cmd_language(bot, update, args):
    '''Command /language message handler'''
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    allow_command = True
    if chat_type != "private":
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if is_admin == False:
            allow_command = False
    if allow_command:
        if len(args) == 1:
            lang_provided = args[0].upper()
            if lang_provided in TEXT:
                if lang_provided != lang:
                    lang = lang_provided
                    save_config_property(chat_id, "Language", lang)
                    bot_msg = TEXT[lang]["LANG_CHANGE"]
                else:
                    bot_msg = TEXT[lang]["LANG_SAME"]
            else:
                bot_msg = TEXT[lang]["LANG_BAD_LANG"]
        else:
            bot_msg = TEXT[lang]["LANG_NOT_ARG"]
    elif is_admin == False:
        bot_msg = TEXT[lang]["CMD_NOT_ALLOW"]
    else:
        bot_msg = TEXT[lang]["CAN_NOT_GET_ADMINS"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_time(bot, update, args):
    '''Command /time message handler'''
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    allow_command = True
    if chat_type != "private":
        is_admin = tlg_user_is_admin(bot, user_id, chat_id)
        if is_admin == False:
            allow_command = False
    if allow_command:
        if len(args) == 1:
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
        else:
            bot_msg = TEXT[lang]["TIME_NOT_ARG"]
    elif is_admin == False:
        bot_msg = TEXT[lang]["CMD_NOT_ALLOW"]
    else:
        bot_msg = TEXT[lang]["CAN_NOT_GET_ADMINS"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_enable(bot, update):
    '''Command /enable message handler'''
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    enable = get_chat_config(chat_id, "Enabled")
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin == True:
        if enable:
            bot_msg = TEXT[lang]["ALREADY_ENABLE"]
        else:
            enable = True
            save_config_property(chat_id, "Enabled", enable)
            bot_msg = TEXT[lang]["ENABLE"]
    elif is_admin == False:
        bot_msg = TEXT[lang]["CMD_NOT_ALLOW"]
    else:
        bot_msg = TEXT[lang]["CAN_NOT_GET_ADMINS"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_disable(bot, update):
    '''Command /disable message handler'''
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    enable = get_chat_config(chat_id, "Enabled")
    is_admin = tlg_user_is_admin(bot, user_id, chat_id)
    if is_admin == True:
        if enable:
            enable = False
            save_config_property(chat_id, "Enabled", enable)
            bot_msg = TEXT[lang]["DISABLE"]
        else:
            bot_msg = TEXT[lang]["ALREADY_DISABLE"]
    elif is_admin == False:
        bot_msg = TEXT[lang]["CMD_NOT_ALLOW"]
    else:
        bot_msg = TEXT[lang]["CAN_NOT_GET_ADMINS"]
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_version(bot, update):
    '''Command /version message handler'''
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    lang = get_chat_config(chat_id, "Language")
    bot_msg = TEXT[lang]["VERSION"].format(CONST["VERSION"])
    if chat_type == "private":
        bot.send_message(chat_id, bot_msg)
    else:
        tlg_msg_to_selfdestruct(update.message)
        tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)


def cmd_about(bot, update):
    '''Command /about handler'''
    chat_id = update.message.chat_id
    lang = get_chat_config(chat_id, "Language")
    bot_msg = TEXT[lang]["ABOUT_MSG"].format(CONST["DEVELOPER"], CONST["REPOSITORY"], \
        CONST["DEV_PAYPAL"], CONST["DEV_BTC"])
    bot.send_message(chat_id, bot_msg)


def cmd_captcha(bot, update):
    '''Command /captcha handler'''
    chat_id = update.message.chat_id
    captcha = create_image_captcha(chat_id)
    sent_img_msg = bot.send_photo(chat_id=chat_id, photo=open(captcha["image"], "rb"))
    tlg_msg_to_selfdestruct_in(sent_img_msg, 1)


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
            try:
                printts(" ")
                printts("[{}] - Mesage to be delete cause it is his time: {}".format( \
                      sent_msg["Chat_id"], sent_msg["Msg_id"]))
                if bot.delete_message(sent_msg["Chat_id"], sent_msg["Msg_id"]):
                    to_delete_in_time_messages_list.remove(sent_msg)
                    printts("[{}] - OK".format(sent_msg["Chat_id"]))
            except Exception as e:
                printts("[{}] - {}".format(sent_msg["Chat_id"], str(e)))
                # The bot has no privileges to delete messages
                if str(e) == "Message can't be deleted":
                    lang = get_chat_config(sent_msg["Chat_id"], "Language")
                    try:
                        cant_del_msg = bot.send_message(sent_msg["Chat_id"], \
                                                        TEXT[lang]["CANT_DEL_MSG"], \
                                                        reply_to_message_id=sent_msg["Msg_id"])
                        tlg_msg_to_selfdestruct(cant_del_msg)
                    except:
                        printts(str(e))
                        pass
                to_delete_in_time_messages_list.remove(sent_msg)
        i = i + 1


def check_time_to_kick_not_verify_users(bot):
    '''Check if the time for ban new users that has not completed the captcha has arrived'''
    global to_delete_join_messages_list
    global new_users_list
    i = 0
    while i < len(new_users_list):
        new_user = new_users_list[i]
        captcha_timeout = get_chat_config(new_user["chat_id"], "Captcha_Time")
        # Remove from new users list the remaining kicked users that have not solve the captcha in 
        # 1 hour (user ban just happen if a user try to join the group and fail to solve the 
        # captcha 3 times in the past hour)
        if time() >= (new_user["join_time"] + captcha_timeout*60) + 3600:
            # Remove user from new users list
            new_users_list.remove(new_user)
        if new_user["kicked_ban"] == False:
            # If time for kick/ban has arrived
            if time() >= new_user["join_time"] + captcha_timeout*60:
                chat_id = new_user["chat_id"]
                lang = get_chat_config(chat_id, "Language")
                printts(" ")
                # Check if this "user" has join this chat 3 times and never get solve the captcha
                if new_user["join_retries"] < 3:
                    printts("[{}] - Captcha not solved, kicking {} ({})...".format(chat_id, \
                        new_user["user_name"], new_user["user_id"]))
                    # Try to kick the user
                    kick_result = tlg_kick_user(bot, new_user["chat_id"], new_user["user_id"])
                    if kick_result == 1:
                        # Kick success
                        bot_msg = TEXT[lang]["NEW_USER_KICK"].format(new_user["user_name"])
                        printts("[{}] - OK".format(chat_id))
                    else:
                        # Kick fail
                        printts("[{}] - Can't kick".format(chat_id))
                        if kick_result == -1:
                            # The user is not in the chat
                            bot_msg = TEXT[lang]['NEW_USER_KICK_NOT_IN_CHAT'].format( \
                                    new_user["user_name"])
                        elif kick_result == -2:
                            # Bot has no privileges to ban
                            bot_msg = TEXT[lang]['NEW_USER_KICK_NOT_RIGHTS'].format( \
                                    new_user["user_name"])
                        else:
                            # For other reason, the Bot can't ban
                            bot_msg = TEXT[lang]['BOT_CANT_KICK'].format(new_user["user_name"])
                    # Set to auto-remove the kick message too, after a while
                    tlg_send_selfdestruct_msg(bot, chat_id, bot_msg)
                else:
                    printts("[{}] - Captcha not solved, banning {} ({})...".format(chat_id, \
                        new_user["user_name"], new_user["user_id"]))
                    # Try to ban the user and notify Admins
                    ban_result = tlg_ban_user(bot, chat_id, new_user["user_id"])
                    printts(ban_result)
                    # Remove user from new users list
                    new_users_list.remove(new_user)
                    if ban_result == 1:
                        # Ban success
                        bot_msg = TEXT[lang]["NEW_USER_BAN"].format(new_user["user_name"])
                        printts("[{}] - OK".format(chat_id))
                    else:
                        # Ban fail
                        printts("[{}] - Can't ban".format(chat_id))
                        if ban_result == -1:
                            # The user is not in the chat
                            bot_msg = TEXT[lang]['NEW_USER_BAN_NOT_IN_CHAT'].format( \
                                    new_user["user_name"])
                        elif ban_result == -2:
                            # Bot has no privileges to ban
                            bot_msg = TEXT[lang]['NEW_USER_BAN_NOT_RIGHTS'].format( \
                                    new_user["user_name"])
                        else:
                            # For other reason, the Bot can't ban
                            bot_msg = TEXT[lang]['BOT_CANT_BAN'].format(new_user["user_name"])
                    # Send ban notify message
                    printts(bot_msg)
                    bot.send_message(chat_id, bot_msg)
                # Update kick_ban
                new_user["kicked_ban"] = True
                new_users_list[i] = new_user
                # Remove join messages
                printts("[{}] - Removing messages from user...".format(chat_id))
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
                            to_delete_join_messages_list.remove(msg)
                            break
                    j = j + 1
                printts("[{}] - end".format(chat_id))
        i = i + 1

####################################################################################################

### Main Function ###

def main():
    '''Main Function'''
    # Initialize resources by populating files list and configs with chats found files
    initialize_resources()
    # Create an event handler (updater) for a Bot with the given Token and get the dispatcher
    updater = Updater(CONST["TOKEN"])
    dp = updater.dispatcher
    # Set to dispatcher a not-command text messages handler
    dp.add_handler(MessageHandler(Filters.text, msg_nocmd))
    # Set to dispatcher a new member join the group and member left the group events handlers
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, msg_new_user))
    # Set to dispatcher request new captcha button callback handler
    dp.add_handler(CallbackQueryHandler(button_request_captcha))
    # Set to dispatcher all expected commands messages handler
    dp.add_handler(CommandHandler("start", cmd_start))
    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("commands", cmd_commands))
    dp.add_handler(CommandHandler("language", cmd_language, pass_args=True))
    dp.add_handler(CommandHandler("time", cmd_time, pass_args=True))
    dp.add_handler(CommandHandler("enable", cmd_enable))
    dp.add_handler(CommandHandler("disable", cmd_disable))
    dp.add_handler(CommandHandler("version", cmd_version))
    dp.add_handler(CommandHandler("about", cmd_about))
    # Next /captcha cmd just for test (use it in release can be a potentially DoS vulnerability)
    #dp.add_handler(CommandHandler("captcha", cmd_captcha))
    # Launch the Bot ignoring pending messages (clean=True)
    updater.start_polling(clean=True)
    # Handle remove of sent messages and not verify new users ban (main loop)
    handle_remove_and_kicks(updater.bot)


if __name__ == "__main__":
    main()

### End Of Code ###
