# -*- coding: utf-8 -*-

'''
Script:
    settings.py
Description:
    This script ease to configure join_captcha_bot.
    Note: If environment variables are used, them have more priority
    than the ones specified in this file.
Author:
    Jose Miguel Rios Rubio
Creation date:
    07/11/2020
Last modified date:
    29/12/2022
Version:
    1.0.0
'''

###############################################################################

from os import path as os_path
# from os import environ as os_environ

# Actual settings.py full path directory name
SCRIPT_PATH = os_path.dirname(os_path.realpath(__file__))

###############################################################################

SETTINGS = {

    # Set if you wan't the Bot to be Public or Private
    # Public: can be used by any group
    # Private: just can be used in allowed groups (Bot owner allow them
    # with /allow_group command)
    "CAPTCHABOT_PRIVATE": False,

    # Bot Token (get it from @BotFather)
    "CAPTCHABOT_TOKEN": "XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",

    # Bot Owner (i.e. "@JoseTLG" or "123456789")
    "CAPTCHABOT_OWNER": "XXXXXXXXX",

    # Enable Bot Webhook connection (False - Polling; True - Webhook)
    # Set to True, to configure Bot for webhook connection mode
    "CAPTCHABOT_USE_WEBHOOK": False,

    # Bot Webhook Listen address
    # Note: only used if CAPTCHABOT_USE_WEBHOOK is True
    "CAPTCHABOT_WEBHOOK_IP": "0.0.0.0",

    # Bot Webhook Listen Port
    # For Heroku, use the following: os_environ.get("PORT", "80")
    # Note: only used if CAPTCHABOT_USE_WEBHOOK is True
    "CAPTCHABOT_WEBHOOK_PORT": 8443,

    # Bot Webhook URL
    # This is the address that the Telegram server should use in case a
    # reverse proxy is used between Telegram and the Bot.
    # If you are using a reverse proxy, set this configuration.
    # Note: only used if CAPTCHABOT_USE_WEBHOOK is True
    "CAPTCHABOT_WEBHOOK_URL": None,

    # Bot Webhook Path
    # Note: only used if CAPTCHABOT_USE_WEBHOOK is True
    "CAPTCHABOT_WEBHOOK_PATH": "/TLG_JoinCaptchaBot",

    # Bot Webhook Certificate file path
    # Note: only used if CAPTCHABOT_USE_WEBHOOK is True
    "CAPTCHABOT_WEBHOOK_CERT": SCRIPT_PATH + "/cert.pem",

    # Bot Webhook Certificate private key file path
    # Note: only used if CAPTCHABOT_USE_WEBHOOK is True
    "CAPTCHABOT_WEBHOOK_CERT_PRIV_KEY": SCRIPT_PATH + "/private.key",

    # Bot Webhook Secret Token to verify request from Telegram Server
    # (don't use the Bot Token, for security reason it must be other)
    # Note: only used if CAPTCHABOT_USE_WEBHOOK is True
    "CAPTCHABOT_WEBHOOK_SECRET_TOKEN": None,

    # Chats directory path
    "CAPTCHABOT_CHATS_DIR": SCRIPT_PATH + "/data/chats",

    # Directory where create/generate temporary captchas
    "CAPTCHABOT_CAPTCHAS_DIR": SCRIPT_PATH + "/data/captchas",

    # Global allowed users file path (i.e. to allow blind users)
    "CAPTCHABOT_F_ALLOWED_USERS": SCRIPT_PATH + "/data/allowedusers.txt",

    # Allowed groups to use the Bot when it is Private
    "CAPTCHABOT_F_ALLOWED_GROUPS": SCRIPT_PATH + "/data/allowedgroups.txt",

    # Blocked groups to deny Bot usage (i.e. bad groups that misuse Bot
    # and cause overload)
    "CAPTCHABOT_F_BAN_GROUPS": SCRIPT_PATH + "/data/bannedgroups.txt",

    # Initial language at Bot start
    "CAPTCHABOT_INIT_LANG": "EN",

    # Initial Bilanguage config value at Bot start
    "CAPTCHABOT_INIT_BILANG": False,

    # Initial enable/disable status at Bot start
    "CAPTCHABOT_INIT_ENABLE": True,

    # Initial users send URLs enable/disable at Bot start
    "CAPTCHABOT_INIT_URL_ENABLE": True,

    # Initial config regarding remove all messages sent by a user kicked
    "CAPTCHABOT_INIT_RM_ALL_MSG": False,

    # Initial captcha solve time (in minutes)
    "CAPTCHABOT_INIT_CAPTCHA_TIME_MIN": 5,

    # Maximum configurable captcha time (in minutes)
    "CAPTCHABOT_MAX_CONFIG_CAPTCHA_TIME": 10,

    # Initial captcha difficult level
    "CAPTCHABOT_INIT_CAPTCHA_DIFFICULTY_LEVEL": 3,

    # Initial captcha characters mode (ascii, hex, nums, math, poll, or
    # button)
    "CAPTCHABOT_INIT_CAPTCHA_CHARS_MODE": "nums",

    # Initial remove result messages group configuration
    "CAPTCHABOT_INIT_RM_RESULT_MSG": True,

    # Initial remove welcome message group configuration
    "CAPTCHABOT_INIT_RM_WELCOME_MSG": True,

    # Maximum number of allowed captcha Poll options
    "CAPTCHABOT_MAX_POLL_OPTIONS": 6,

    # Poll captcha question max length
    # Telegram maximum Poll Question length is 300
    "CAPTCHABOT_MAX_POLL_QUESTION_LENGTH": 300,

    # Poll captcha question max length
    # Telegram maximum Poll Option length is 100
    "CAPTCHABOT_MAX_POLL_OPTION_LENGTH": 100,

    # Standard auto-remove messages sent by Bot timeout (in seconds)
    "CAPTCHABOT_T_DEL_MSG": 60,

    # Fast auto-remove messages sent by Bot timeout (in seconds)
    "CAPTCHABOT_T_FAST_DEL_MSG": 20,

    # Auto-remove custom welcome message timeout (in seconds)
    "CAPTCHABOT_T_DEL_WELCOME_MSG": 60,

    # Time to restrict sending no-text msgs (in seconds, default 24h)
    "CAPTCHABOT_T_RESTRICT_NO_TEXT_MSG": 86400,

    # Maximum number of users allowed in each chat ignore list
    "CAPTCHABOT_IGNORE_LIST_MAX": 100,

    # Initial new users just allow to send text messages
    "CAPTCHABOT_INIT_RESTRICT_NON_TEXT_MSG": 0,

    # Custom Welcome message max length
    "CAPTCHABOT_MAX_WELCOME_MSG_LENGTH": 3968,

    # Maximum number of times a user joins a group and don't solve the
    # captcha. If a user don't solve the captcha after this, it will be
    # ban instead kick
    "CAPTCHABOT_MAX_FAIL_BAN": 10,

    # Maximum number of times a user fail to solve a Poll captcha.
    # If a user don't solve the captcha after this, it will be ban
    # instead kick
    "CAPTCHABOT_MAX_FAIL_BAN_POLL": 3
}
