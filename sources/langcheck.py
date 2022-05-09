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
        langname = "{}   ".format(langname)
    if len(l_missing_keys) == 0:
        if len(l_brackets_missmatch_keys) == 0:
            print("{} - OK".format(langname))
            return "Success"
        else:
            return ""{} - FAIL - Brackets Missmatch in Keys: {}".format(langname,
                    l_brackets_missmatch_keys)"
    else:
        return "{} - FAIL - Missing Keys: {}".format(langname, l_missing_keys)

###############################################################################
### Main Function

def main():
    with open(os.path.join(CONST["LANG_DIR"], "en.json")) as enfile:
        en = json.load(enfile)
    errs = ""
    for lang in os.listdir(CONST["LANG_DIR"]):
        if not lang.endswith('.json'):
            continue
        if lang == 'en.json':
            continue
        with open(os.path.join(CONST["LANG_DIR"], lang)) as langfile:
            try:
                valid_or_not = is_valid(lang.split('.')[0], json.load(langfile), en)
                if valid_or_not != "Success":
                    errs = valid_or_not
            except json.decoder.JSONDecodeError:
                errs = "JSON Decoding error"
                print("{} is not valid json".format(lang))
    if errs != "":
        sys.exit(errs)
    exit(0)


if __name__ == '__main__':
    main()
