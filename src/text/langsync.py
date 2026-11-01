#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Language texts JSON files sync script to ensure all language files
have the same keys as the english language file (reference file).
'''

###############################################################################
# Imported modules
###############################################################################

# JSON Library
import json

# Operating System Library
import os

# System Library
import sys


###############################################################################
# Constants
###############################################################################

# Actual script full path directory name
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

# Language texts files directory path
LANG_DIR = os.path.join(SCRIPT_PATH, "language")


###############################################################################
# Auxiliary Functions
###############################################################################

def sync_language_file(file_path, reference_lang):
    '''Add missing keys from the reference language to one language file.'''
    with open(file_path, encoding="utf8") as file_lang:
        language = json.load(file_lang)
    missing_keys = [key for key in reference_lang if key not in language]
    if not missing_keys:
        return []
    for key in missing_keys:
        language[key] = reference_lang[key]
    with open(file_path, "w", encoding="utf8") as file_lang:
        json.dump(language, file_lang, ensure_ascii=False, indent=4)
        file_lang.write("\n")
    return missing_keys


###############################################################################
# Main Function
###############################################################################

def main():
    '''Main Function.'''
    file_path_en = os.path.join(LANG_DIR, "en.json")
    with open(file_path_en, encoding="utf8") as file_en:
        reference_lang = json.load(file_en)
    updated_files = 0
    for lang in sorted(os.listdir(LANG_DIR)):
        if not lang.endswith(".json") or lang == "en.json":
            continue
        file_path_lang = os.path.join(LANG_DIR, lang)
        missing_keys = sync_language_file(file_path_lang, reference_lang)
        if missing_keys:
            updated_files += 1
            print(f"{lang}: added {len(missing_keys)} missing key(s)")
    if updated_files == 0:
        print("All language files already contain the keys from en.json.")
    return 0


###############################################################################
# Runnable Main Script Detection
###############################################################################

if __name__ == "__main__":
    sys.exit(main())
