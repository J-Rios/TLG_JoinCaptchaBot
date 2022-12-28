#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
### Imported modules

import json
import os

from constants import CONST

###############################################################################
### Auxiliary Functions

def is_valid(langname, lang, englang):
    l_missing_keys = []
    l_brackets_missmatch_keys = []
    for key in englang:
        if key not in lang:
            l_missing_keys.append(key)
        num_expected_brackets = englang[key].count("{}")
        num_brackets = lang[key].count("{}")
        if num_brackets != num_expected_brackets:
            l_brackets_missmatch_keys.append(key)
    if len(langname) == 2:
        langname = f"{langname}   "
    if len(l_missing_keys) == 0:
        if len(l_brackets_missmatch_keys) == 0:
            print(f"{langname} - OK")
            return True
        else:
            print(
                    f"{langname} - FAIL - Brackets Missmatch in Keys: " \
                    f"{l_brackets_missmatch_keys}")
            return False
    else:
        print(f"{langname} - FAIL - Missing Keys: {l_missing_keys}")
        return False

###############################################################################
### Main Function

def main():
    with open(os.path.join(CONST["LANG_DIR"], "en.json")) as enfile:
        en = json.load(enfile)
    errs = False
    for lang in os.listdir(CONST["LANG_DIR"]):
        if not lang.endswith('.json'):
            continue
        if lang == 'en.json':
            continue
        with open(os.path.join(CONST["LANG_DIR"], lang)) as langfile:
            try:
                if not is_valid(lang.split('.')[0], json.load(langfile), en):
                    errs = True
            except json.decoder.JSONDecodeError:
                errs = True
                print(f"{lang} is not valid json")
    if errs:
        exit(1)
    exit(0)


if __name__ == '__main__':
    main()
