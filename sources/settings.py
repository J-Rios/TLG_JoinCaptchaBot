# -*- coding: utf-8 -*-

from os import path as os_path

# Actual settings.py full path directory name
SCRIPT_PATH = os_path.dirname(os_path.realpath(__file__))

###############################################################################

SETTINGS = {

    # Set if you wan't the Bot to be Public or Private
    # Public: can be used by any group
    # Private: just can be used in allowed groups (Bot owner allow them
    # with /allow_group command)
    "CAPTCHABOT_PRIVATE": True,

    # Bot Token (get it from @BotFather)
    "CAPTCHABOT_TOKEN": "XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",

    # Bot Owner (i.e. "@JoseTLG" or "123456789")
    "CAPTCHABOT_OWNER": "XXXXXXXXX",

    # Bot Webhook Host addres (keep in None for Polling or set to a
    # valid address for Webhook)
    "CAPTCHABOT_WEBHOOK_HOST": "None",

    # Bot Webhook Host Port (this is not used if WEBHOOK_HOST is None)
    "CAPTCHABOT_WEBHOOK_PORT": 8443,

    # Bot Webhook Certificate file path (this is not used if
    # WEBHOOK_HOST is None)
    "CAPTCHABOT_WEBHOOK_CERT" : SCRIPT_PATH + "/cert.pem",

    # Bot Webhook Certificate private key file path (this is not used
    # if WEBHOOK_HOST is None)
    "CAPTCHABOT_WEBHOOK_CERT_PRIV_KEY" : SCRIPT_PATH + "/private.key",

    # Chats directory path
    "CAPTCHABOT_CHATS_DIR": SCRIPT_PATH + "/data/chats",

    # Directory where create/generate temporary captchas
    "CAPTCHABOT_CAPTCHAS_DIR": SCRIPT_PATH + "/data/captchas",

    # Global allowed users file path (i.e. to allow blind users)
    "CAPTCHABOT_F_ALLOWED_USERS": SCRIPT_PATH + "/data/allowedusers.txt",

    # Allowed groups to use the Bot when it is Private
    "CAPTCHABOT_F_ALLOWED_GROUPS": SCRIPT_PATH + "/data/allowedgroups.txt",

    # Blocked groups to deny Bot usage (i.e. bad groups that misuse Bot and
    # cause overload)
    "CAPTCHABOT_F_BAN_GROUPS": SCRIPT_PATH + "/data/bannedgroups.txt",

    # Initial language at Bot start
    "CAPTCHABOT_INIT_LANG": "EN",

    # Initial enable/disable status at Bot start
    "CAPTCHABOT_INIT_ENABLE": True,

    # Initial captcha solve time (in minutes)
    "CAPTCHABOT_INIT_CAPTCHA_TIME_MIN": 5,

    # Initial captcha difficult level
    "CAPTCHABOT_INIT_CAPTCHA_DIFFICULTY_LEVEL": 2,

    # Initial captcha characters mode (ascii, hex, nums, or button)
    "CAPTCHABOT_INIT_CAPTCHA_CHARS_MODE": "nums",

    # Default time (in mins) to remove self-destruct sent messages from
    # the Bot
    "CAPTCHABOT_T_DEL_MSG": 5,

    # Auto-remove custom welcome message timeout
    "CAPTCHABOT_T_DEL_WELCOME_MSG": 5,

    # Maximum number of users allowed in each chat ignore list
    "CAPTCHABOT_IGNORE_LIST_MAX": 100,

    # Initial new users just allow to send text messages
    "CAPTCHABOT_INIT_RESTRICT_NON_TEXT_MSG": 0,

    # Custom Welcome message max length
    "CAPTCHABOT_MAX_WELCOME_MSG_LENGTH": 3968
}
