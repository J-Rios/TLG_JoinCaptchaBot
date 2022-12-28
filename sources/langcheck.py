#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    langcheck.py
Description:
    Join Captcha Bot language texts JSON files validator to verify of the JSON
    of all language files are valid and all languages has the same keys as the
    english language file (reference file).
Author:
    Jose Miguel Rios Rubio
Creation date:
    02/10/2020
Last modified date:
    28/12/2022
Version:
    1.1.0
'''

###############################################################################
### Imported modules

# JSON Library
import json

# Operating System Library
import os

# System Library
from sys import exit as sys_exit

# Local Constants Library
from constants import CONST

###############################################################################
### Auxiliary Functions

def is_valid(lang_name, lang_to_check, reference_lang):
    '''
    Validate JSON language texts with a reference language (i.e. english).
    It checks for mismatch keys or  number of brackets in key values.
    '''
    l_missing_keys = []
    l_brackets_mismatch_keys = []
    for key in reference_lang:
        if key not in lang_to_check:
            l_missing_keys.append(key)
        num_expected_brackets = reference_lang[key].count("{}")
        num_brackets = lang_to_check[key].count("{}")
        if num_brackets != num_expected_brackets:
            l_brackets_mismatch_keys.append(key)
    if len(lang_name) == 2:
        lang_name = f"{lang_name}   "
    if len(l_missing_keys) != 0:
        print(f"{lang_name} - FAIL - Missing Keys: {l_missing_keys}")
        return False
    if len(l_brackets_mismatch_keys) != 0:
        miss_key = l_brackets_mismatch_keys
        print(f"{lang_name} - FAIL - Brackets Mismatch in Keys: {miss_key}")
        return False
    print(f"{lang_name} - OK")
    return True

###############################################################################
### Main Function

def main():
    '''Main Function.'''
    file_path_en = os.path.join(CONST["LANG_DIR"], "en.json")
    with open(file_path_en, encoding="utf8") as file_en:
        json_en = json.load(file_en)
    errs = False
    for lang in os.listdir(CONST["LANG_DIR"]):
        if not lang.endswith(".json"):
            continue
        if lang == "en.json":
            continue
        file_path_lang = os.path.join(CONST["LANG_DIR"], lang)
        with open(file_path_lang, encoding="utf8") as file_lang:
            try:
                lang_name = lang.split(".")[0]
                json_lang = json.load(file_lang)
                if not is_valid(lang_name, json_lang, json_en):
                    errs = True
            except json.decoder.JSONDecodeError:
                errs = True
                print(f"{lang} is not valid json")
    if errs:
        return 1
    return 0


###############################################################################
### Runnable Main Script Detection

if __name__ == "__main__":
    sys_exit(main())
