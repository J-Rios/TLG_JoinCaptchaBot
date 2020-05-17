# -*- coding: utf-8 -*-

'''
Script:
    constants.py
Description:
    Constants values for join_captcha_bot.py.
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

from os import path

####################################################################################################

### Constants ###

# Actual constants.py full path directory name
SCRIPT_PATH = path.dirname(path.realpath(__file__))


# General Bots Parameters
CONST = {

    # Bot Token (get it from @BotFather)
    "TOKEN": "XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",

    # Bot Owner (i.e. "@JoseTLG" or "123456789")
    "BOT_OWNER": "XXXXXXXXX",

    # Languages texts files directory path
    "LANG_DIR": SCRIPT_PATH + "/language",

    # Chats directory path
    "CHATS_DIR": SCRIPT_PATH + "/data/chats",

    # Directory where create/generate temporary captchas
    "CAPTCHAS_DIR": SCRIPT_PATH + "/data/captchas",

    # Global whitelist file path (to allow whitelist blind users in all groups)
    "F_WHITE_LIST": SCRIPT_PATH + "/data/whitelist.txt",

    # Chat configurations JSON files
    "F_CONF": "configs.json",

    # Initial chat title at Bot start
    "INIT_TITLE": "Unknown Chat",

    # Initial chat link at Bot start
    "INIT_LINK": "Unknown",

    # Initial language at Bot start
    "INIT_LANG": "EN",

    # Initial enable/disable status at Bot start
    "INIT_ENABLE": True,

    # Initial captcha solve time (in minutes)
    "INIT_CAPTCHA_TIME_MIN": 5,

    # Initial captcha difficult level
    "INIT_CAPTCHA_DIFFICULTY_LEVEL": 2,

    # Initial captcha characters mode (nums, hex or ascci)
    "INIT_CAPTCHA_CHARS_MODE": "nums",

    # Initial new users just allow to send text messages
    "INIT_RESTRICT_NON_TEXT_MSG": False,

    # Default time (in mins) to remove self-destruct sent messages from the Bot
    "T_DEL_MSG": 5,

    # Auto-remove custom welcome message timeout
    "T_DEL_WELCOME_MSG": 5,

    # Custom Welcome message max length
    "MAX_WELCOME_MSG_LENGTH": 3968,

    # Maximum number of users allowed in each chat ignore list
    "IGNORE_LIST_MAX": 100,

    # Command don't allow in private chat text (just english due in private chats we 
    # don't have language configuration
    "CMD_NOT_ALLOW_PRIVATE": "Can't use this command in the current chat.",

    # Command just allow for Bot owner
    "CMD_JUST_ALLOW_OWNER": "This command just can be use by the Bot Owner",

    # Whitelist usage
    "WHITELIST_USAGE": "Command usage (user ID or Alias):\n" \
        "/whitelist add @peter123\n" \
        "/whitelist rm 123456789",

    # IANA Top-Level-Domain List (https://data.iana.org/TLD/tlds-alpha-by-domain.txt)
    "F_TLDS": "tlds-alpha-by-domain.txt",

    # Regular expression to detect URLs in a string based in TLD domains
    "REGEX_URLS": r"((?<=[^a-zA-Z0-9])*(?:https\:\/\/|[a-zA-Z0-9]{{1,}}\.{{1}}|\b)" \
        r"(?:\w{{1,}}\.{{1}}){{1,5}}(?:{})\b/?(?!@))",

    # List string of supported languages commands shows in invalid language set
    "SUPPORTED_LANGS_CMDS": \
        "\nEnglish / English\n/language en\n" \
        "\nSpanish / Español\n/language es\n" \
        "\nFrench / Francais\n/language fr\n" \
        "\nGerman / Deutch\n/language de\n" \
        "\nItalian / Italiano\n/language it\n" \
        "\nRussian / Pусский\n/language ru\n" \
        "\nIndonesian / Indonesia\n/language id\n" \
        "\nCatalan / Català\n/language ca\n" \
        "\nBasque / Euskal\n/language eu\n" \
        "\nGalician / Galego\n/language gl\n" \
        "\nPortuguese-Brazil / Português-Brasil\n/language pt_br\n" \
        "\nTurkish / Türkçe\n/language tr\n" \
        "\nChinese-Simplified / 中文\n/language zh_cn",

    # Bot developer
    "DEVELOPER": "@JoseTLG",

    # Bot code repository
    "REPOSITORY": "https://github.com/J-Rios/TLG_JoinCaptchaBot",

    # Developer Paypal address
    "DEV_PAYPAL": "https://www.paypal.me/josrios",

    # Developer Bitcoin address
    "DEV_BTC": "3N9wf3FunR6YNXonquBeWammaBZVzTXTyR",

    # Bot version
    "VERSION": "1.10.2 (17/05/2020)"
}


# Supported languages list
TEXT = {
    "EN": None, # English
    "DE": None, # German
    "FR": None, # French
    "ID": None, # Indonesian
    "IT": None, # Italian
    "ES": None, # Spanish
    "CA": None, # Catalan
    "GL": None, # Galician
    "EU": None, # Basque
    "RU": None, # Rusian
    "PT_BR": None, # Portuguese (Brasil)
    #"FA": None, # Persian (The json file is broken or json parser library doesn't support it)
    "TR": None, # Turkish
    "ZH_CN": None # Chinese (Mainland)
}
