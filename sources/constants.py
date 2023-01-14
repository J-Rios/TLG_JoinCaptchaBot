# -*- coding: utf-8 -*-

'''
Script:
    constants.py
Description:
    Constants values for join_captcha_bot.py
Author:
    Jose Miguel Rios Rubio
Creation date:
    09/09/2018
Last modified date:
    14/01/2023
Version:
    1.29.1
'''

###############################################################################
### Imported modules ###

from os import path as os_path
from os import getenv as os_getenv
from settings import SETTINGS

###############################################################################
### Constants ###

# Actual constants.py full path directory name
SCRIPT_PATH = os_path.dirname(os_path.realpath(__file__))

# General Bots Parameters
CONST = {

    # Bot Public or Private
    "BOT_PRIVATE": \
        bool(int(os_getenv("CAPTCHABOT_PRIVATE", \
            SETTINGS["CAPTCHABOT_PRIVATE"]))),

    # Bot Token (get it from @BotFather)
    "TOKEN": \
        os_getenv("CAPTCHABOT_TOKEN", SETTINGS["CAPTCHABOT_TOKEN"]),

    # Bot Owner (i.e. "@JoseTLG" or "123456789")
    "BOT_OWNER": \
        os_getenv("CAPTCHABOT_OWNER", SETTINGS["CAPTCHABOT_OWNER"]),

    # Bot Webhook Host addres (keep in None for Polling or set to a
    # valid address for Webhook)
    "WEBHOOK_HOST": \
        os_getenv("CAPTCHABOT_WEBHOOK_HOST", \
            SETTINGS["CAPTCHABOT_WEBHOOK_HOST"]),

    # Bot Webhook Host Port (this is not used if WEBHOOK_HOST is None)
    "WEBHOOK_PORT": \
        int(os_getenv("CAPTCHABOT_WEBHOOK_PORT", \
            SETTINGS["CAPTCHABOT_WEBHOOK_PORT"])),

    # Bot Webhook Certificate file path (this is not used if
    # WEBHOOK_HOST is None)
    "WEBHOOK_CERT": \
        os_getenv("CAPTCHABOT_WEBHOOK_CERT", \
            SETTINGS["CAPTCHABOT_WEBHOOK_CERT"]),

    # Bot Webhook Certificate private key file path (this is not used
    # if WEBHOOK_HOST is None)
    "WEBHOOK_CERT_PRIV_KEY": \
        os_getenv("CAPTCHABOT_WEBHOOK_CERT_PRIV_KEY", \
            SETTINGS["CAPTCHABOT_WEBHOOK_CERT_PRIV_KEY"]),

    # Chats directory path
    "CHATS_DIR": \
        os_getenv("CAPTCHABOT_CHATS_DIR", SETTINGS["CAPTCHABOT_CHATS_DIR"]),

    # Directory where create/generate temporary captchas
    "CAPTCHAS_DIR": \
        os_getenv("CAPTCHABOT_CAPTCHAS_DIR", \
            SETTINGS["CAPTCHABOT_CAPTCHAS_DIR"]),

    # Global allowed users file path (i.e. to allow blind users)
    "F_ALLOWED_USERS": \
        os_getenv("CAPTCHABOT_F_ALLOWED_USERS", \
            SETTINGS["CAPTCHABOT_F_ALLOWED_USERS"]),

    # Allowed groups to use the Bot when it is Private
    "F_ALLOWED_GROUPS": \
        os_getenv("CAPTCHABOT_F_ALLOWED_GROUPS", \
            SETTINGS["CAPTCHABOT_F_ALLOWED_GROUPS"]),

    # Blocked groups to deny Bot usage (i.e. bad groups that misuse Bot
    # and cause overload)
    "F_BAN_GROUPS": \
        os_getenv("CAPTCHABOT_F_BAN_GROUPS", \
            SETTINGS["CAPTCHABOT_F_BAN_GROUPS"]),

    # Initial enable/disable status at Bot start
    "INIT_ENABLE": \
        bool(int(os_getenv("CAPTCHABOT_INIT_ENABLE", \
            SETTINGS["CAPTCHABOT_INIT_ENABLE"]))),

    # Initial users send URLs enable/disable at Bot start
    "INIT_URL_ENABLE": \
        bool(int(os_getenv("CAPTCHABOT_INIT_URL_ENABLE", \
            SETTINGS["CAPTCHABOT_INIT_URL_ENABLE"]))),

    # Initial config regarding remove all messages sent by a user kicked
    "INIT_RM_ALL_MSG": \
        bool(int(os_getenv("CAPTCHABOT_INIT_RM_ALL_MSG", \
            SETTINGS["CAPTCHABOT_INIT_RM_ALL_MSG"]))),

    # Initial captcha solve time
    "INIT_CAPTCHA_TIME": \
        int(os_getenv("CAPTCHABOT_INIT_CAPTCHA_TIME_MIN", \
            SETTINGS["CAPTCHABOT_INIT_CAPTCHA_TIME_MIN"])) * 60,

    # Initial captcha difficult level
    "INIT_CAPTCHA_DIFFICULTY_LEVEL": \
        int(os_getenv("CAPTCHABOT_INIT_CAPTCHA_DIFFICULTY_LEVEL", \
            SETTINGS["CAPTCHABOT_INIT_CAPTCHA_DIFFICULTY_LEVEL"])),

    # Initial captcha characters mode (ascii, hex, nums, math or button)
    "INIT_CAPTCHA_CHARS_MODE": \
        os_getenv("CAPTCHABOT_INIT_CAPTCHA_CHARS_MODE", \
            SETTINGS["CAPTCHABOT_INIT_CAPTCHA_CHARS_MODE"]),

    # Maximum configurable captcha time
    "MAX_CONFIG_CAPTCHA_TIME": \
        int(os_getenv("CAPTCHABOT_MAX_CONFIG_CAPTCHA_TIME", \
            SETTINGS["CAPTCHABOT_MAX_CONFIG_CAPTCHA_TIME"])),

    # Standard auto-remove messages sent by Bot timeout (in seconds)
    "T_DEL_MSG": \
        int(os_getenv("CAPTCHABOT_T_DEL_MSG", \
            SETTINGS["CAPTCHABOT_T_DEL_MSG"])),

    # Fast auto-remove messages sent by Bot timeout (in seconds)
    "T_FAST_DEL_MSG": \
        int(os_getenv("CAPTCHABOT_T_FAST_DEL_MSG", \
            SETTINGS["CAPTCHABOT_T_FAST_DEL_MSG"])),

    # Auto-remove custom welcome message timeout (in seconds)
    "T_DEL_WELCOME_MSG": \
        int(os_getenv("CAPTCHABOT_T_DEL_WELCOME_MSG", \
            SETTINGS["CAPTCHABOT_T_DEL_WELCOME_MSG"])),

    # Maximum number of users allowed in each chat ignore list
    "IGNORE_LIST_MAX": \
        int(os_getenv("CAPTCHABOT_IGNORE_LIST_MAX", \
            SETTINGS["CAPTCHABOT_IGNORE_LIST_MAX"])),

    # Initial new users just allow to send text messages
    "INIT_RESTRICT_NON_TEXT_MSG": \
        int(os_getenv("CAPTCHABOT_INIT_RESTRICT_NON_TEXT_MSG", \
            SETTINGS["CAPTCHABOT_INIT_RESTRICT_NON_TEXT_MSG"])),

    # Custom Welcome message max length
    "MAX_WELCOME_MSG_LENGTH": \
        int(os_getenv("CAPTCHABOT_MAX_WELCOME_MSG_LENGTH", \
            SETTINGS["CAPTCHABOT_MAX_WELCOME_MSG_LENGTH"])),

    # Initial remove result messages cgroup onfiguration
    "INIT_RM_RESULT_MSG": \
        bool(int(os_getenv("CAPTCHABOT_INIT_RM_RESULT_MSG", \
            SETTINGS["CAPTCHABOT_INIT_RM_RESULT_MSG"]))),

    # Initial remove welcome message group configuration
    "INIT_RM_WELCOME_MSG": \
        bool(int(os_getenv("CAPTCHABOT_INIT_RM_WELCOME_MSG", \
            SETTINGS["CAPTCHABOT_INIT_RM_WELCOME_MSG"]))),

    # Maximum number of allowed captcha Poll options
    "MAX_POLL_OPTIONS": \
        int(os_getenv("CAPTCHABOT_MAX_POLL_OPTIONS", \
            SETTINGS["CAPTCHABOT_MAX_POLL_OPTIONS"])),

    # Poll captcha question max length
    "MAX_POLL_QUESTION_LENGTH": \
        int(os_getenv("CAPTCHABOT_MAX_POLL_QUESTION_LENGTH", \
            SETTINGS["CAPTCHABOT_MAX_POLL_QUESTION_LENGTH"])),

    # Poll captcha question max length
    "MAX_POLL_OPTION_LENGTH": \
        int(os_getenv("CAPTCHABOT_MAX_POLL_OPTION_LENGTH", \
            SETTINGS["CAPTCHABOT_MAX_POLL_OPTION_LENGTH"])),

    # Maximum number of times a user joins a group and fail to solve the
    # captcha. If a user don't solve the captcha after this, it will be
    # ban instead kick
    "MAX_FAIL_BAN": \
        int(os_getenv("CAPTCHABOT_MAX_FAIL_BAN", \
            SETTINGS["CAPTCHABOT_MAX_FAIL_BAN"])),

    # Maximum number of times a user fail to solve a Poll captcha.
    # If a user don't solve the captcha after this, it will be ban
    # instead kick
    "MAX_FAIL_BAN_POLL": \
        int(os_getenv("CAPTCHABOT_MAX_FAIL_BAN_POLL", \
            SETTINGS["CAPTCHABOT_MAX_FAIL_BAN_POLL"])),

    # Last session restorable RAM data backup file path
    "F_SESSION": SCRIPT_PATH + "/session.pkl",

    # Languages texts files directory path
    "LANG_DIR": SCRIPT_PATH + "/language",

    # Chat configurations JSON files
    "F_CONF": "configs.json",

    # Initial chat title at Bot start
    "INIT_TITLE": "Unknown Chat",

    # Initial chat link at Bot start
    "INIT_LINK": "Unknown",

    # Initial language at Bot start
    "INIT_LANG": \
        os_getenv("CAPTCHABOT_INIT_LANG", \
            SETTINGS["CAPTCHABOT_INIT_LANG"]),

    # Time to restrict sending no-text messages
    "T_RESTRICT_NO_TEXT_MSG": \
        int(os_getenv("CAPTCHABOT_T_RESTRICT_NO_TEXT_MSG", \
            SETTINGS["CAPTCHABOT_T_RESTRICT_NO_TEXT_MSG"])),

    # Number of seconds in a minute
    "T_SECONDS_IN_MIN": 60,

    # Number of seconds in a day (60s x 60m x 24h)
    "T_SECONDS_IN_A_DAY": 86400,

    # Command just allow for Bot owner
    "CMD_JUST_ALLOW_OWNER": "This command just can be use by the Bot Owner",

    # Bot added to channel, leave text
    "BOT_LEAVE_CHANNEL": "This Bot can't be used in channels, just in groups.",

    # Allowed users list usage
    "ALLOWUSERLIST_USAGE": "Command usage (user ID or Alias):\n" \
        "/allowuserlist add @peter123\n" \
        "/allowuserlist rm 123456789",

    # Allowgroup usage
    "ALLOWGROUP_USAGE": "Command usage (group ID):\n" \
        "/allowgroup add -1001142817523\n" \
        "/allowgroup rm -1001142817523",

    # Allowgroup usage
    "NOT_ALLOW_GROUP": "Hi, this Bot account is private and is not allowed " \
        "to be used here. Contact to Bot account owner ({}) if you want to " \
        "use the Bot in this group.\n" \
        "\n" \
        "Actual chat ID (Bot owner needs this to allow this group):\n" \
        "{}\n" \
        "\n" \
        "Also, remember that you can create your own Bot account for " \
        "free:\n" \
        "{}",

    # Maximum number of users in a group to allow usage of free Bot
    "FREE_LIMIT_MAX_USER_IN_GROUP": 999,

    # Free Bot Group number of users limit reached
    "FREE_LIMIT_REACH": "WARNING:\n———————————\n" \
        "Current Group Chat ID:\n{}\n" \
        "\n" \
        "The Group has reached the free usage Limit.\n" \
        "\n" \
        "To avoid overload and keep the Bot working ok without delay, " \
        "this Bot account just can be used in groups with less than {} " \
        "members.\n" \
        "\n" \
        "If you want to use this captcha Bot without restriction in large " \
        "groups, use the \"pro Bot\" account (@pro_join_captcha_bot) " \
        "for just 5 eurs each month following next instructions:\n" \
        "https://ko-fi.com/post/JoinCaptchaBot-for-large-groups-V7V3ANADF\n" \
        "\n" \
        "Also, remember that Bot is free software and open-source, so you " \
        "can always deploy, host and maintain your own Bot instance from " \
        "source code without limitations.\n" \
        "\n" \
        "Best Regards.",

    # IANA Top-Level-Domain List
    # https://data.iana.org/TLD/tlds-alpha-by-domain.txt
    "F_TLDS": "tlds-alpha-by-domain.txt",

    # Regular expression to detect URLs in a string
    "REGEX_URLS": \
        r"((?<=[^a-zA-Z0-9])*(?:https\:\/\/|[a-zA-Z0-9]{{1,}}\.{{1}}|\b)" \
        r"(?:\w{{1,}}\.{{1}}){{1,5}}(?:{})\b/?(?!@))",

    # List string of supported languages commands shows in invalid
    # language set
    "SUPPORTED_LANGS_CMDS": \
        "\nArabic / Arabic\n/language ar\n" \
        "\nBasque / Euskal\n/language eu\n" \
        "\nBelarusian / беларуская\n/language be\n" \
        "\nCatalan / Català\n/language ca\n" \
        "\nChinese-Simplified / 中文\n/language zh_cn\n" \
        "\nDutch / Nederlands\n/language nl\n" \
        "\nEnglish / English\n/language en\n" \
        "\nEsperanto\n/language eo\n" \
        "\nFinnish / Suomi\n/language fi\n" \
        "\nFrench / Francais\n/language fr\n" \
        "\nGalician / Galego\n/language gl\n" \
        "\nGerman / Deutsch\n/language de\n" \
        "\nGreek / Ελληνικά\n/language el\n" \
        "\nHebrew / Hebrew\n/language he\n" \
        "\nIndonesian / Indonesia\n/language id\n" \
        "\nItalian / Italiano\n/language it\n" \
        "\nKannada / Kannada\n/language kn\n" \
        "\nKorean / 한국어\n/language ko\n" \
        "\nPersian\n/language fa\n" \
        "\nPolish / Polskie\n/language pl\n" \
        "\nPortuguese-Brazil / Português-Brasil\n/language pt_br\n" \
        "\nRussian / Pусский\n/language ru\n" \
        "\nSlovak / Slovenčine\n/language sk\n" \
        "\nSpanish / Español\n/language es\n" \
        "\nTurkish / Türkçe\n/language tr\n" \
        "\nUkrainian / Українську\n/language uk\n",

    # Bot developer
    "DEVELOPER": "@JoseTLG",

    # Bot code repository
    "REPOSITORY": "https://github.com/J-Rios/TLG_JoinCaptchaBot",

    # Developer Donation address
    "DEV_DONATION_ADDR": "https://ko-fi.com/joincaptchabot",

    # Bot version
    "VERSION": "1.29.1 (14/01/2023)"
}

# Supported languages list
TEXT: dict = {
    "AR": {}, # Arabic
    "BE": {}, # Belarusian
    "CA": {}, # Catalan
    "DE": {}, # German
    "EL": {}, # Greek
    "EN": {}, # English
    "EO": {}, # Esperanto
    "ES": {}, # Spanish
    "EU": {}, # Basque
    "FA": {}, # Persian
    "FI": {}, # Finnish
    "FR": {}, # French
    "GL": {}, # Galician
    "HE": {}, # Hebrew
    "ID": {}, # Indonesian
    "IT": {}, # Italian
    "KN": {}, # Kannada
    "KO": {}, # Korean
    "NL": {}, # Dutch
    "PL": {}, # Polish
    "PT_BR": {}, # Portuguese (Brasil)
    "RU": {}, # Rusian
    "SK": {}, # Slovak
    "TR": {}, # Turkish
    "UK": {}, # Ukrainian
    "ZH_CN": {} # Chinese (Mainland)
}
