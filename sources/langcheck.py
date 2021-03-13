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
    missing = []
    for key in englang:
        if key not in lang:
            missing.append(key)
    if len(missing) == 0:
        print("{} is complete".format(langname))
        return True
    else:
        print("{} is missing these keys: {}".format(langname, missing))
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
                print("{} is not valid json".format(lang))
    if errs:
        exit(1)


if __name__ == '__main__':
    main()
