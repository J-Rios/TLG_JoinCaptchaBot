#!/bin/bash

rm -f ./data/captchas/*

exec python3 -u join_captcha_bot.py
