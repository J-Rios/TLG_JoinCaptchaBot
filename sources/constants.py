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
    14/08/2019
Version:
    1.5.1
'''

####################################################################################################

### Imported modules ###

from os import path

####################################################################################################

### Constants ###

SCRIPT_PATH = path.dirname(path.realpath(__file__)) # Actual constant.py full path directory name

CONST = {
    'TOKEN' : 'XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', # Bot Token (get it from @BotFather)
    'LANG_DIR' : SCRIPT_PATH + '/language', # Languages texts files directory path
    'DATA_DIR' : SCRIPT_PATH + '/data', # Data directory path
    'CHATS_DIR' : SCRIPT_PATH + '/data/chats', # Chats directory path
    'CAPTCHAS_DIR' : './data/captchas', # Directory where create/generate temporary captchas images
    'F_CONF' : 'configs.json', # Chat configurations JSON files name
    'INIT_TITLE' : 'Unknown Chat', # Initial chat title at Bot start
    'INIT_LINK' : 'Unknown', # Initial chat link at Bot start
    'INIT_LANG' : 'EN', # Initial language at Bot start
    'INIT_ENABLE' : True, # Initial enable/disable status at Bot start
    'INIT_CAPTCHA_TIME_MIN' : 5, # Initial captcha solve time (in minutes)
    'INIT_CAPTCHA_DIFFICULTY_LEVEL' : 2, # Initial captcha difficult level
    'INIT_CAPTCHA_CHARS_MODE' : "nums", # Initial captcha characters mode (nums, hex or ascci)
    'T_DEL_MSG' : 5, # Default time (in mins) to remove self-destruct sent messages from the Bot
    'F_TLDS' : 'tlds-alpha-by-domain.txt', # IANA TLD list (https://data.iana.org/TLD/tlds-alpha-by-domain.txt)
    'REGEX_URLS' : r'((?<=[^a-zA-Z0-9])*(?:https\:\/\/|[a-zA-Z0-9]{{1,}}\.{{1}}|\b)(?:\w{{1,}}\.{{1}}){{1,5}}(?:{})\b/?(?!@))',
    'DEVELOPER' : '@JoseTLG', # Bot developer
    'REPOSITORY' : 'https://github.com/J-Rios/TLG_JoinCaptchaBot', # Bot code repository
    'DEV_PAYPAL' : 'https://www.paypal.me/josrios', # Developer Paypal address
    'DEV_BTC' : '3N9wf3FunR6YNXonquBeWammaBZVzTXTyR', # Developer Bitcoin address
    'VERSION' : '1.5.1 (14/08/2019)' # Bot version
}

TEXT = {
    'EN' : None,
    'ES' : None,
    'CA' : None,
    'GL' : None,
    'PT_BR' : None,
    'ZH_CN' : None
}
