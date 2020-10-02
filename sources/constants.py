# -*- coding: utf-8 -*-

'''
Script:
    constants.py
Description:
    Constants values for join_captcha_bot.py
Author:
    Jose Rios Rubio
Creation date:
    09/09/2018
Last modified date:
    13/09/2020
Version:
    1.13.1
'''

################################################################################
### Imported modules ###

import os
from os import path

################################################################################
### Constants ###

# Actual constants.py full path directory name
SCRIPT_PATH = path.dirname(path.realpath(__file__))


# General Bots Parameters
CONST = {

    # Set if you wan't the Bot to be Public or Private
    # Public: can be used by any group
    # Private: just can be used in allowed groups (Bot owner allow them with /allow_group command)
    "BOT_PRIVATE": bool(int(os.getenv("BOT_PRIVATE", "0"))),

    # Bot Token (get it from @BotFather)
    "TOKEN": os.getenv("TOKEN", "XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"),

    # Bot Owner (i.e. "@JoseTLG" or "123456789")
    "BOT_OWNER": os.getenv("BOT_OWNER", "XXXXXXXXX"),

    # Bot Webhook Host addres (keep in None for Polling or set to a valid address for Webhook)
    "WEBHOOK_HOST": os.getenv("WEBHOOK_HOST", "None"),

    # Bot Webhook Host Port (this is not used if WEBHOOK_HOST is None)
    "WEBHOOK_PORT": int(os.getenv("WEBHOOK_PORT", "8443")),

    # Bot Webhook Certificate file path (this is not used if WEBHOOK_HOST is None)
    "WEBHOOK_CERT" : SCRIPT_PATH + "/cert.pem",

    # Bot Webhook Certificate private key file path (this is not used if WEBHOOK_HOST is None)
    "WEBHOOK_CERT_PRIV_KEY" : SCRIPT_PATH + "/private.key",

    # Languages texts files directory path
    "LANG_DIR": os.getenv("LANG_DIR", SCRIPT_PATH + "/language"),

    # Chats directory path
    "CHATS_DIR": os.getenv("CHATS_DIR", SCRIPT_PATH + "/data/chats"),

    # Directory where create/generate temporary captchas
    "CAPTCHAS_DIR": os.getenv("CAPTCHAS_DIR", SCRIPT_PATH + "/data/captchas"),

    # Global whitelist file path (to allow whitelist blind users in all groups)
    "F_WHITE_LIST": os.getenv("F_WHITE_LIST", SCRIPT_PATH + "/data/whitelist.txt"),

    # Global whitelist file path (to allow whitelist blind users in all groups)
    "F_ALLOWED_GROUPS": os.getenv("F_ALLOWED_GROUPS", SCRIPT_PATH + "/data/allowedgroups.txt"),

    # Chat configurations JSON files
    "F_CONF": os.getenv("F_CONF", "configs.json"),

    # Initial chat title at Bot start
    "INIT_TITLE": os.getenv("INIT_TITLE", "Unknown Chat"),

    # Initial chat link at Bot start
    "INIT_LINK": os.getenv("INIT_LINK", "Unknown"),

    # Initial language at Bot start
    "INIT_LANG": os.getenv("INIT_LANG", "EN"),

    # Initial enable/disable status at Bot start
    "INIT_ENABLE": bool(int(os.getenv("INIT_ENABLE", "1"))),

    # Initial captcha solve time (in minutes)
    "INIT_CAPTCHA_TIME_MIN": int(os.getenv("INIT_CAPTCHA_TIME_MIN", "5")),

    # Initial captcha difficult level
    "INIT_CAPTCHA_DIFFICULTY_LEVEL": int(os.getenv("INIT_CAPTCHA_DIFFICULTY_LEVEL", "2")),

    # Initial captcha characters mode (ascii, hex, nums, or button)
    "INIT_CAPTCHA_CHARS_MODE": os.getenv("INIT_CAPTCHA_CHARS_MODE", "nums"),

    # Initial new users just allow to send text messages
    "INIT_RESTRICT_NON_TEXT_MSG": bool(int(os.getenv("INIT_RESTRICT_NON_TEXT_MSG", "0"))),

    # Default time (in mins) to remove self-destruct sent messages from the Bot
    "T_DEL_MSG": int(os.getenv("T_DEL_MSG", "5")),

    # Auto-remove custom welcome message timeout
    "T_DEL_WELCOME_MSG": int(os.getenv("T_DEL_WELCOME_MSG", "5")),

    # Custom Welcome message max length
    "MAX_WELCOME_MSG_LENGTH": int(os.getenv("MAX_WELCOME_MSG_LENGTH", "3968")),

    # Maximum number of users allowed in each chat ignore list
    "IGNORE_LIST_MAX": int(os.getenv("IGNORE_LIST_MAX", "100")),

    # Command don't allow in private chat text (just english due in private chats we
    # don't have language configuration
    "CMD_NOT_ALLOW_PRIVATE": os.getenv("CMD_NOT_ALLOW_PRIVATE", "Can't use this command in the current chat."),

    # Command just allow for Bot owner
    "CMD_JUST_ALLOW_OWNER": os.getenv("CMD_JUST_ALLOW_OWNER", "This command just can be use by the Bot Owner"),

    # Whitelist usage
    "WHITELIST_USAGE": os.getenv("WHITELIST_USAGE", "Command usage (user ID or Alias):\n" \
        "/whitelist add @peter123\n" \
        "/whitelist rm 123456789"),

    # Allowgroup usage
    "ALLOWGROUP_USAGE": os.getenv("ALLOWGROUP_USAGE", "Command usage (group ID):\n" \
        "/allowgroup add -1001142817523\n" \
        "/allowgroup rm -1001142817523"),

    # Allowgroup usage
    "NOT_ALLOW_GROUP": os.getenv("NOT_ALLOW_GROUP", "Hi, this Bot account is private and is not allowed to be used here. " \
        "Contact to Bot account owner ({}) if you want to use the Bot in this group.\n" \
        "\n" \
        "Actual chat ID (Bot owner needs this to allow this group):\n" \
        "{}\n" \
        "\n" \
        "Also, remember that you can create your own Bot account for free:\n" \
        "{}"),

    # IANA Top-Level-Domain List (https://data.iana.org/TLD/tlds-alpha-by-domain.txt)
    "F_TLDS": os.getenv("F_TLDS", "tlds-alpha-by-domain.txt"),

    # Regular expression to detect URLs in a string based in TLD domains
    "REGEX_URLS": os.getenv("REGEX_URLS", r"((?<=[^a-zA-Z0-9])*(?:https\:\/\/|[a-zA-Z0-9]{{1,}}\.{{1}}|\b)" \
        r"(?:\w{{1,}}\.{{1}}){{1,5}}(?:{})\b/?(?!@))"),

    # List string of supported languages commands shows in invalid language set
    "SUPPORTED_LANGS_CMDS": os.getenv("SUPPORTED_LANGS_CMDS", \
        "\nArabic / Arabic\n/language ar\n" \
        "\nBasque / Euskal\n/language eu\n" \
        "\nCatalan / Català\n/language ca\n" \
        "\nChinese-Simplified / 中文\n/language zh_cn\n" \
        "\nEnglish / English\n/language en\n" \
        "\nEsperanto\n/language eo\n" \
        "\nFrench / Francais\n/language fr\n" \
        "\nGalician / Galego\n/language gl\n" \
        "\nGerman / Deutch\n/language de\n" \
        "\nIndonesian / Indonesia\n/language id\n" \
        "\nItalian / Italiano\n/language it\n" \
        "\nPolish / Polskie\n/language pl\n" \
        "\nPortuguese-Brazil / Português-Brasil\n/language pt_br\n" \
        "\nRussian / Pусский\n/language ru\n" \
        "\nSpanish / Español\n/language es\n" \
        "\nTurkish / Türkçe\n/language tr\n"),

    # Bot developer
    "DEVELOPER": os.getenv("DEVELOPER", "@JoseTLG"),

    # Bot code repository
    "REPOSITORY": os.getenv("REPOSITORY", "https://github.com/J-Rios/TLG_JoinCaptchaBot"),

    # Developer Paypal address
    "DEV_PAYPAL": os.getenv("DEV_PAYPAL", "https://www.paypal.me/josrios"),

    # Developer Bitcoin address
    "DEV_BTC": os.getenv("DEV_BTC", "3N9wf3FunR6YNXonquBeWammaBZVzTXTyR"),

    # Bot version
    "VERSION": os.getenv("VERSION", "1.13.1 (13/09/2020)"),
}


# Supported languages list
TEXT = {
    "AR": {}, # Arabic
    "CA": {}, # Catalan
    "DE": {}, # German
    "EN": {}, # English
    "EO": {}, # Esperanto
    "ES": {}, # Spanish
    "EU": {}, # Basque
    "FR": {}, # French
    "GL": {}, # Galician
    "ID": {}, # Indonesian
    "IT": {}, # Italian
    "PL": {}, # Polish
    "PT_BR": {}, # Portuguese (Brasil)
    "RU": {}, # Rusian
    "TR": {}, # Turkish
    "ZH_CN": {} # Chinese (Mainland)
}
